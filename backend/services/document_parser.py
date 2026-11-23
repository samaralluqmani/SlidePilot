import io

import fitz
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph


SUPPORTED_EXTENSIONS = {"pdf", "docx", "txt"}


def extract_text(filename: str, file_bytes: bytes) -> str:
    extension = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

    if extension == "pdf":
        return extract_pdf(file_bytes)
    if extension == "docx":
        return extract_docx(file_bytes)
    if extension == "txt":
        return extract_txt(file_bytes)

    raise ValueError("Unsupported file type. Please upload PDF, DOCX, or TXT.")


def extract_pdf(file_bytes: bytes) -> str:
    text_parts: list[str] = []
    with fitz.open(stream=file_bytes, filetype="pdf") as document:
        for number, page in enumerate(document, start=1):
            page_text = page.get_text("text", sort=True).strip()
            if page_text:
                text_parts.append(f"[PDF page {number}]\n{page_text}")
    return "\n\n".join(text_parts)


def extract_docx(file_bytes: bytes) -> str:
    document = Document(io.BytesIO(file_bytes))
    text_parts: list[str] = []

    for block in document.iter_inner_content():
        if isinstance(block, Paragraph):
            value = block.text.strip()
            if value:
                heading = block.style and block.style.name.startswith("Heading")
                text_parts.append(f"[Heading] {value}" if heading else value)
        elif isinstance(block, Table):
            rows = []
            for row in block.rows:
                cells = [cell.text.strip() for cell in row.cells]
                if any(cells):
                    rows.append(" | ".join(cells))
            if rows:
                text_parts.append("[Table]\n" + "\n".join(rows))

    return "\n\n".join(text_parts)


def extract_txt(file_bytes: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            return file_bytes.decode(encoding).strip()
        except UnicodeDecodeError:
            continue
    raise ValueError("Could not decode the text file.")
