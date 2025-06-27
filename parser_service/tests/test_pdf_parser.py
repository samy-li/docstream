from parser_service.app.parsers.pdf_parser import PDFParser

def test_pdf_parser_simple(tmp_path):
    from reportlab.pdfgen import canvas

    pdf_path = tmp_path / "resume.pdf"
    c = canvas.Canvas(str(pdf_path))
    c.drawString(100, 750, "This is a test PDF resume.")
    c.save()

    parser = PDFParser()
    text = parser.extract_text(str(pdf_path))

    assert "test PDF resume" in text
