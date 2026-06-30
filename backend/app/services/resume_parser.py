from pathlib import Path

from docx import Document
from fastapi import HTTPException, UploadFile, status
from PyPDF2 import PdfReader


ALLOWED_EXTENSIONS = {".pdf", ".docx"}


def validate_resume_file(file: UploadFile) -> str:
    filename = file.filename or ""
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and DOCX resume files are supported.",
        )
    return extension


def extract_text_from_pdf(file_path: Path) -> str:
    try:
        reader = PdfReader(str(file_path))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(page.strip() for page in pages if page.strip())
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not extract text from PDF: {exc}",
        ) from exc


def extract_text_from_docx(file_path: Path) -> str:
    try:
        document = Document(str(file_path))
        paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs]
        return "\n".join(text for text in paragraphs if text)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not extract text from DOCX: {exc}",
        ) from exc


def extract_resume_text(file_path: Path) -> str:
    extension = file_path.suffix.lower()
    if extension == ".pdf":
        return extract_text_from_pdf(file_path)
    if extension == ".docx":
        return extract_text_from_docx(file_path)
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Unsupported resume format.",
    )
