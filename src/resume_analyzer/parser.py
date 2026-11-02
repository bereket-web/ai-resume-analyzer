"""Local resume text extraction. No upload is saved to disk or sent externally."""

from __future__ import annotations

import io
import re
from pathlib import PurePosixPath

from docx import Document
from pypdf import PdfReader

MAX_FILE_BYTES = 5 * 1024 * 1024
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}

SECTION_ALIASES = {
    "summary": {"summary", "professional summary", "profile", "objective", "career summary"},
    "experience": {"experience", "work experience", "employment", "professional experience", "work history"},
    "education": {"education", "academic background", "qualifications"},
    "skills": {"skills", "technical skills", "core skills", "competencies", "technical competencies"},
    "projects": {"projects", "selected projects", "personal projects"},
    "certifications": {"certifications", "certificates", "licenses", "licences"},
}
HEADING_LOOKUP = {alias: section for section, aliases in SECTION_ALIASES.items() for alias in aliases}


class ResumeParseError(ValueError):
    """Raised when a resume cannot be safely extracted."""


def _extract_pdf(payload: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(payload), strict=False)
        if reader.is_encrypted:
            try:
                if not reader.decrypt(""):
                    raise ResumeParseError("Encrypted PDFs are not supported. Export an unlocked copy first.")
            except Exception as exc:
                if isinstance(exc, ResumeParseError):
                    raise
                raise ResumeParseError(
                    "Encrypted PDFs are not supported. Export an unlocked copy first."
                ) from exc
        pages = [page.extract_text(extraction_mode="layout") or "" for page in reader.pages]
    except ResumeParseError:
        raise
    except Exception as exc:
        raise ResumeParseError("Could not read this PDF. Check that it is a valid, text-based PDF.") from exc
    if not pages:
        raise ResumeParseError("This PDF has no pages.")
    if not any(page.strip() for page in pages):
        raise ResumeParseError(
            "No selectable text was found. Scanned-image OCR is not included in this release."
        )
    return "\n\n".join(pages).strip()


def _extract_docx(payload: bytes) -> str:
    try:
        document = Document(io.BytesIO(payload))
    except Exception as exc:
        raise ResumeParseError(
            "Could not read this DOCX file. Check that it is a valid Word document."
        ) from exc
    parts = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
    for table in document.tables:
        for row in table.rows:
            parts.append(" | ".join(cell.text.strip() for cell in row.cells if cell.text.strip()))
    text = "\n".join(parts).strip()
    if not text:
        raise ResumeParseError("No text was found in this DOCX file.")
    return text


def extract_text(filename: str, payload: bytes) -> str:
    """Extract text from a size-limited PDF, DOCX, or TXT payload."""
    extension = PurePosixPath(filename.replace("\\", "/")).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise ResumeParseError("Unsupported file type. Upload a PDF, DOCX, or TXT resume.")
    if not payload:
        raise ResumeParseError("The uploaded file is empty.")
    if len(payload) > MAX_FILE_BYTES:
        raise ResumeParseError("The resume exceeds the 5 MB upload limit.")
    if extension == ".pdf":
        return _extract_pdf(payload)
    if extension == ".docx":
        return _extract_docx(payload)
    try:
        text = payload.decode("utf-8-sig").strip()
    except UnicodeDecodeError as exc:
        raise ResumeParseError("TXT files must use UTF-8 encoding.") from exc
    if not text:
        raise ResumeParseError("No text was found in this TXT file.")
    return text


def extract_sections(text: str) -> dict[str, list[str]]:
    """Group lines under common resume headings; preserve unclassified lines."""
    sections: dict[str, list[str]] = {"other": []}
    current = "other"
    for line in text.splitlines():
        cleaned = re.sub(r"^[\s#•*-]+|[\s:]+$", "", line).strip()
        normalized = re.sub(r"\s+", " ", cleaned.casefold())
        section = HEADING_LOOKUP.get(normalized)
        if section:
            current = section
            sections.setdefault(current, [])
        elif cleaned:
            sections.setdefault(current, []).append(cleaned)
    return {name: lines for name, lines in sections.items() if lines}
