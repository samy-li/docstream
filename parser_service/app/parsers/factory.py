from .docx_parser import DocxParser
from .pdf_parser import PDFParser
from .txt_parser import TxtParser
import magic


class ParserFactory:
    @staticmethod
    def get_parser(file_path: str):
        ext = file_path.lower().split('.')[-1]

        # Detect MIME type
        mime = magic.from_file(file_path, mime=True)

        # Decide based on MIME and extension
        if ext == "pdf" and mime == "application/pdf":
            return PDFParser()
        elif ext == "docx" and mime in [
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            return DocxParser()
        elif ext == "txt" and mime in ["text/plain"]:
            return TxtParser()
        else:
            raise ValueError(f"Error: Unsupported file format: {ext}")
