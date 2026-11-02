from io import BytesIO

import pytest
from docx import Document
from pypdf import PdfWriter

from resume_analyzer.parser import ResumeParseError, extract_sections, extract_text


def _minimal_text_pdf(text: str) -> bytes:
    """Create a tiny valid PDF content stream for parser tests without external fixtures."""
    escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        f"<< /Length {len(('BT /F1 12 Tf 72 720 Td (' + escaped + ') Tj ET').encode())} >>\nstream\nBT /F1 12 Tf 72 720 Td ({escaped}) Tj ET\nendstream".encode(),
    ]
    payload = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, 1):
        offsets.append(len(payload))
        payload.extend(f"{index} 0 obj\n".encode() + obj + b"\nendobj\n")
    xref_offset = len(payload)
    payload.extend(f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        payload.extend(f"{offset:010d} 00000 n \n".encode())
    payload.extend(
        f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode()
    )
    return bytes(payload)


def test_extract_utf8_text():
    assert extract_text("resume.txt", b"Python and SQL") == "Python and SQL"


def test_extract_docx_paragraphs_and_tables():
    document = Document()
    document.add_paragraph("Python experience")
    table = document.add_table(rows=1, cols=1)
    table.cell(0, 0).text = "SQL"
    buffer = BytesIO()
    document.save(buffer)
    text = extract_text("resume.docx", buffer.getvalue())
    assert "Python experience" in text
    assert "SQL" in text


def test_extract_pdf_text():
    assert "Python and SQL" in extract_text("resume.pdf", _minimal_text_pdf("Python and SQL"))


def test_reject_unsupported_extension_and_oversized_payload():
    with pytest.raises(ResumeParseError, match="Unsupported"):
        extract_text("resume.rtf", b"anything")
    with pytest.raises(ResumeParseError, match="5 MB"):
        extract_text("resume.txt", b"x" * (5 * 1024 * 1024 + 1))


def test_scanned_or_empty_pdf_returns_clear_error():
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    buffer = BytesIO()
    writer.write(buffer)
    with pytest.raises(ResumeParseError, match="No selectable text"):
        extract_text("scan.pdf", buffer.getvalue())


def test_resume_sections_group_lines_by_heading():
    sections = extract_sections("Rita\nSKILLS\nPython\nWORK EXPERIENCE\nBuilt APIs")
    assert sections["skills"] == ["Python"]
    assert sections["experience"] == ["Built APIs"]
    assert sections["other"] == ["Rita"]
