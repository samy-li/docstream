import logging
from .parser import Parser
import pdfplumber


logger = logging.getLogger("__name__")


class PDFParser(Parser):
    def extract_text(self, file_path: str) -> str:
        try:
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    logger.error(
                        f"PDF file '{file_path}' parsed but contained no extractable text.")
                    text += page.extract_text() or ""
            if text == "":
                raise ValueError("Could not extract text from PDF file")
            else:
                return text
        except FileNotFoundError:
            logger.error(f"PDF file {file_path} not found")
            raise
        except PermissionError:
            logger.error(f"No permission to read PDF file: '{file_path}'.")
            raise
        except IsADirectoryError:
            logger.error(f"Expected a file but got a directory: '{file_path}'.")
            raise
        except Exception as e:
            logger.error(
                f"Failed to extract text from PDF file '{file_path}': {e}",
                exc_info=True)
            raise ValueError("Corrupted or unreadable PDF file.") from e

