from .parser import Parser
import pdfplumber

class PDFParser(Parser):
    def extract_text(self, file_path:str) -> str:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
