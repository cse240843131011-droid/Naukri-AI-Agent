"""utils/file_handler.py — File upload helpers and text extraction"""
import os
import uuid
from flask import current_app


def allowed_file(filename: str) -> bool:
    """Return True if the file extension is in ALLOWED_EXTENSIONS."""
    allowed = current_app.config.get("ALLOWED_EXTENSIONS", {"pdf", "docx", "doc", "txt"})
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


def save_upload(file, subfolder: str = "resumes") -> dict:
    """
    Save an uploaded FileStorage object under uploads/<subfolder>/.
    Returns a dict with keys: filename, original_name, file_path, file_type.
    """
    original_name = file.filename
    ext = original_name.rsplit(".", 1)[-1].lower() if "." in original_name else "bin"
    unique_name = f"{uuid.uuid4().hex}.{ext}"

    dest_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], subfolder)
    os.makedirs(dest_dir, exist_ok=True)

    file_path = os.path.join(dest_dir, unique_name)
    file.save(file_path)

    return {
        "filename": unique_name,
        "original_name": original_name,
        "file_path": file_path,
        "file_type": ext,
    }


def extract_text(file_path: str) -> str:
    """
    Extract plain text from a PDF, DOCX, DOC, or TXT file.
    Returns empty string on failure.
    """
    ext = file_path.rsplit(".", 1)[-1].lower() if "." in file_path else ""

    try:
        if ext == "pdf":
            return _extract_pdf(file_path)
        elif ext in ("docx",):
            return _extract_docx(file_path)
        elif ext == "txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
    except Exception:
        pass
    return ""


def _extract_pdf(path: str) -> str:
    try:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
        return "\n".join(pages).strip()
    except ImportError:
        pass

    # Fallback to PyPDF2
    try:
        import PyPDF2
        text_parts = []
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text_parts.append(page.extract_text() or "")
        return "\n".join(text_parts).strip()
    except Exception:
        return ""


def _extract_docx(path: str) -> str:
    try:
        from docx import Document
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs).strip()
    except Exception:
        return ""
