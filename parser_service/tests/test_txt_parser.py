import pytest
from parser_service.app.parsers.txt_parser import TxtParser

def test_txt_standard(tmp_path):
    txt_path = tmp_path / "file.txt"
    txt_path.write_text("Some text", encoding="utf-8")
    assert "Some text" in TxtParser().extract_text(str(txt_path))

def test_txt_empty(tmp_path):
    txt_path = tmp_path / "file.txt"
    txt_path.write_text("", encoding="utf-8")
    assert TxtParser().extract_text(str(txt_path)) == ""

def test_txt_wrong_extension(tmp_path):
    path = tmp_path / "file.pdf"
    path.write_text("Should not work", encoding="utf-8")
    with pytest.raises(ValueError):
        TxtParser().extract_text(str(path))

def test_txt_no_extension(tmp_path):
    path = tmp_path / "file"
    path.write_text("No extension", encoding="utf-8")
    with pytest.raises(ValueError):
        TxtParser().extract_text(str(path))

def test_txt_directory(tmp_path):
    with pytest.raises(IsADirectoryError):
        TxtParser().extract_text(str(tmp_path))

def test_txt_non_utf8(tmp_path):
    path = tmp_path / "latin1.txt"
    path.write_bytes("Some text".encode("latin1"))
    with pytest.raises(UnicodeDecodeError):
        TxtParser().extract_text(str(path))
