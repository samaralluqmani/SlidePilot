import io

import fitz
from docx import Document


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
        for page in document:
            page_text = page.get_text("text").strip()
            if page_text:
                text_parts.append(page_text)
    return "\n\n".join(text_parts)


def extract_docx(file_bytes: bytes) -> str:
    document = Document(io.BytesIO(file_bytes))
    text_parts: list[str] = []

    for paragraph in document.paragraphs:
        value = paragraph.text.strip()
        if value:
            text_parts.append(value)

    # Preserve useful table content because comparison tables often become slides.
    for table in document.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            if any(cells):
                text_parts.append(" | ".join(cells))

    return "\n\n".join(text_parts)


def extract_txt(file_bytes: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            return file_bytes.decode(encoding).strip()
        except UnicodeDecodeError:
            continue
    raise ValueError("Could not decode the text file.")
