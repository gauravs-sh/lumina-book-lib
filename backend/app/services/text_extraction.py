from __future__ import annotations

from io import BytesIO
from typing import Tuple


def extract_text(filename: str, content: bytes) -> Tuple[str, str]:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return _extract_pdf_text(content), "application/pdf"
    return content.decode("utf-8", errors="ignore"), "text/plain"


def _extract_pdf_text(content: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(BytesIO(content))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)
