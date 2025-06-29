from parser_service.app.parsers.pdf_parser import PDFParser
import pytest


def create_pdf(path, text="PDF Content"):
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(str(path))
    c.drawString(100, 750, text)
    c.save()

def test_pdf_standard(tmp_path):
    path = tmp_path / "file.pdf"
    create_pdf(path, "Some text")
    assert "Some text" in PDFParser().extract_text(str(path))

def test_pdf_empty(tmp_path):
    path = tmp_path / "empty.pdf"
    path.write_bytes(b"")
    with pytest.raises(ValueError):
        PDFParser().extract_text(str(path))

def test_pdf_directory(tmp_path):
    with pytest.raises(IsADirectoryError):
        PDFParser().extract_text(str(tmp_path))

def test_pdf_corrupted(tmp_path):
    path = tmp_path / "corrupt.pdf"
    path.write_bytes(b"not a real pdf")
    with pytest.raises(ValueError):
        PDFParser().extract_text(str(path))

def test_pdf_file_not_found():
    with pytest.raises(FileNotFoundError):
        PDFParser().extract_text("/tmp/notfound.pdf")

