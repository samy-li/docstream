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
    assert "Some Text" in PDFParser().extract_text(str(path))

def test_pdf_empty(tmp_path):
    path = tmp_path / "empty.pdf"
    path.write_bytes(b"")
    with pytest.raises(ValueError):
        PDFParser().extract_text(str(path))

def test_pdf_wrong_extension(tmp_path):
    path = tmp_path / "file.txt"
    create_pdf(path, "Wrong Ext")
    with pytest.raises(ValueError):
        PDFParser().extract_text(str(path))

def test_pdf_no_extension(tmp_path):
    path = tmp_path / "file"
    create_pdf(path, "No Ext")
    with pytest.raises(ValueError):
        PDFParser().extract_text(str(path))

def test_pdf_directory(tmp_path):
    with pytest.raises(IsADirectoryError):
        PDFParser().extract_text(str(tmp_path))

def test_pdf_corrupted(tmp_path):
    path = tmp_path / "corrupt.pdf"
    path.write_bytes(b"Some corrupt PDF text")
    with pytest.raises(ValueError):
        PDFParser().extract_text(str(path))

