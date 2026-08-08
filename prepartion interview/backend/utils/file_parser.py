# backend/utils/file_parser.py
"""
Utility to extract plain text from uploaded PDF, DOCX, or TXT files.
"""
import io
from fastapi import UploadFile


async def extract_text(file: UploadFile) -> str:
    """Read an uploaded file and return its text content."""
    filename = (file.filename or "").lower()
    content = await file.read()

    if filename.endswith(".pdf"):
        return _parse_pdf(content)
    elif filename.endswith(".docx"):
        return _parse_docx(content)
    elif filename.endswith(".txt"):
        return content.decode("utf-8", errors="ignore")
    else:
        # Attempt plain text fallback
        return content.decode("utf-8", errors="ignore")


def _parse_pdf(data: bytes) -> str:
    """Extract text from a PDF using PyMuPDF."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=data, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except Exception as e:
        return f"[PDF parse error: {e}]"


def _parse_docx(data: bytes) -> str:
    """Extract text from a DOCX file using python-docx."""
    try:
        from docx import Document
        doc = Document(io.BytesIO(data))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except Exception as e:
        return f"[DOCX parse error: {e}]"
