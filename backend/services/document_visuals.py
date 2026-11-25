import hashlib
import io
import re
import struct
from dataclasses import dataclass
from pathlib import PurePath
from zipfile import BadZipFile

import fitz
from docx import Document
from docx.opc.exceptions import PackageNotFoundError
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph
from lxml.etree import XMLSyntaxError
from PIL import Image, ImageOps


MAX_DOCUMENT_VISUALS = 12
MAX_PDF_PAGES = 80
MAX_IMAGE_SIDE = 1600
MAX_IMAGE_BYTES = 750_000
MAX_SOURCE_IMAGE_BYTES = 15_000_000
MAX_SOURCE_PIXELS = 24_000_000

_CAPTION_PREFIX = re.compile(
    r"^(?:fig(?:ure)?\.?|chart|image|illustration|الشكل|شكل|الصورة|صورة|الرسم|المخطط|مخطط)"
    r"\s*\(?\s*\d+",
    re.IGNORECASE,
)
_PDF_ERRORS = (fitz.mupdf.FzErrorBase, OSError, RuntimeError, ValueError)
_IMAGE_ERRORS = (Image.DecompressionBombError, OSError, ValueError, SyntaxError, struct.error)


@dataclass(frozen=True)
class DocumentVisual:
    id: str
    page: int | None
    image_bytes: bytes
    caption: str | None
    width: int
    height: int


def _description(text: str) -> str | None:
    clean = " ".join(text.split())
    return clean[:160] or None


def _large_enough(width: float, height: float) -> bool:
    return min(width, height) >= 80 and max(width, height) >= 140


def _encode(image: Image.Image) -> tuple[bytes, int, int] | None:
    image.thumbnail((MAX_IMAGE_SIDE, MAX_IMAGE_SIDE))
    transparent = "A" in image.getbands() or "transparency" in image.info
    image = image.convert("RGBA" if transparent else "RGB")

    output = io.BytesIO()
    image.save(output, format="PNG", compress_level=3)
    if output.tell() <= MAX_IMAGE_BYTES:
        return output.getvalue(), image.width, image.height

    if transparent:
        background = Image.new("RGB", image.size, "white")
        background.paste(image, mask=image.getchannel("A"))
        image = background
    for quality in (86, 74, 62):
        output = io.BytesIO()
        image.save(output, format="JPEG", quality=quality, optimize=True)
        if output.tell() <= MAX_IMAGE_BYTES:
            return output.getvalue(), image.width, image.height
    return None


def _encode_blob(blob: bytes) -> tuple[bytes, int, int] | None:
    if len(blob) > MAX_SOURCE_IMAGE_BYTES:
        return None
    try:
        with Image.open(io.BytesIO(blob)) as source:
            if not _large_enough(*source.size) or source.width * source.height > MAX_SOURCE_PIXELS:
                return None
            return _encode(ImageOps.exif_transpose(source))
    except _IMAGE_ERRORS:
        return None


def _pdf_caption(rect: fitz.Rect, text_blocks: list) -> str | None:
    candidates = []
    for x0, y0, x1, y1, text, *_ in text_blocks:
        caption = _description(text)
        if not caption or not _CAPTION_PREFIX.match(caption):
            continue
        if min(x1, rect.x1) <= max(x0, rect.x0):
            continue
        gap = max(y0 - rect.y1, rect.y0 - y1, 0)
        if gap <= 30:
            candidates.append((gap, caption))
    return min(candidates)[1] if candidates else None


def _pdf_images(file_bytes: bytes):
    try:
        with fitz.open(stream=file_bytes, filetype="pdf") as document:
            seen_images = set()
            for page_index in range(min(len(document), MAX_PDF_PAGES)):
                try:
                    page = document[page_index]
                    page_rect = page.rect
                    images = page.get_image_info(hashes=True)
                    blocks = page.get_text("blocks", flags=fitz.TEXTFLAGS_BLOCKS & ~fitz.TEXT_PRESERVE_IMAGES)
                    for item in sorted(images, key=lambda figure: (figure["bbox"][1], figure["bbox"][0])):
                        source_rect = fitz.Rect(item["bbox"])
                        clip = (source_rect * page.rotation_matrix) & page_rect
                        if (
                            clip.is_empty
                            or min(clip.width, clip.height) < 38
                            or clip.get_area() < page_rect.get_area() * 0.018
                            or not _large_enough(item["width"], item["height"])
                            or item["digest"] in seen_images
                        ):
                            continue
                        caption = _pdf_caption(source_rect, blocks)
                        if clip.get_area() > page_rect.get_area() * 0.9 and caption is None:
                            continue
                        try:
                            scale = min(2, (MAX_IMAGE_SIDE - 2) / max(clip.width, clip.height))
                            raster = page.get_pixmap(matrix=fitz.Matrix(scale, scale), clip=clip, colorspace=fitz.csRGB)
                            image = Image.frombytes("RGB", (raster.width, raster.height), raster.samples)
                            encoded = _encode(image)
                        except _PDF_ERRORS + _IMAGE_ERRORS:
                            continue
                        if encoded:
                            seen_images.add(item["digest"])
                            yield page_index + 1, caption, encoded
                except _PDF_ERRORS:
                    continue
    except _PDF_ERRORS:
        return


def _docx_caption(paragraph: Paragraph) -> str | None:
    previous = paragraph._p.getprevious()
    following = paragraph._p.getnext()
    for element in (following, previous):
        if element is None or element.tag != qn("w:p"):
            continue
        adjacent = Paragraph(element, paragraph._parent)
        text = _description(adjacent.text)
        style = adjacent.style
        if text and ((style and style.style_id == "Caption") or _CAPTION_PREFIX.match(text)):
            return text
    return None


def _docx_images(file_bytes: bytes):
    try:
        document = Document(io.BytesIO(file_bytes))
    except (BadZipFile, KeyError, OSError, PackageNotFoundError, ValueError, XMLSyntaxError):
        return

    related_parts = document.part.related_parts
    seen_relations = set()
    for element in document.element.body.iter(qn("w:p")):
        drawings = element.xpath(".//w:drawing")
        if not drawings:
            continue
        caption = _docx_caption(Paragraph(element, document))
        for drawing in drawings:
            metadata = drawing.xpath(".//wp:docPr")
            alt_text = metadata[0].get("descr", "") if metadata else ""
            for blip in drawing.xpath(".//a:blip"):
                relationship = blip.get(qn("r:embed"))
                part = related_parts.get(relationship)
                if part is None or relationship in seen_relations or not part.content_type.startswith("image/"):
                    continue
                seen_relations.add(relationship)
                encoded = _encode_blob(part.blob)
                if encoded:
                    yield None, caption or _description(alt_text), encoded


def extract_document_visuals(filename: str, file_bytes: bytes) -> list[DocumentVisual]:
    """Return a bounded, deduplicated inventory of source raster figures."""
    extension = PurePath(filename).suffix.lower()
    if extension == ".pdf":
        images = _pdf_images(file_bytes)
    elif extension == ".docx":
        images = _docx_images(file_bytes)
    else:
        return []

    visuals = []
    seen = set()
    for page, caption, (image_bytes, width, height) in images:
        digest = hashlib.sha256(image_bytes).digest()
        if digest in seen:
            continue
        seen.add(digest)
        visuals.append(DocumentVisual(
            id=f"figure-{len(visuals) + 1:02d}",
            page=page,
            image_bytes=image_bytes,
            caption=caption,
            width=width,
            height=height,
        ))
        if len(visuals) == MAX_DOCUMENT_VISUALS:
            break
    return visuals
