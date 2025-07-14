import pytest
from parser_service.app.parsers.docx_parser import DocxParser

def create_docx(path, text="DOCX Content"):
    import docx
    doc = docx.Document()
    doc.add_paragraph(text)
    doc.save(str(path))

def test_docx_standard(tmp_path):
    docx_path = tmp_path / "file.docx"
    create_docx(docx_path, "Some text")
    assert "Some text" in DocxParser().extract_text(str(docx_path))

def test_docx_empty(tmp_path):
    docx_path = tmp_path / "empty.docx"
    docx_path.write_bytes(b"")
    with pytest.raises(ValueError):
        DocxParser().extract_text(str(docx_path))

def test_docx_directory(tmp_path):
    with pytest.raises(IsADirectoryError):
        DocxParser().extract_text(str(tmp_path))

def test_docx_corrupted(tmp_path):
    path = tmp_path / "corrupt.docx"
    path.write_bytes(b"not a real docx")
    with pytest.raises(ValueError):
        DocxParser().extract_text(str(path))
