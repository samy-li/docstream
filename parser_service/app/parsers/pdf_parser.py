import logging
from .parser import Parser
import pdfplumber

from .exceptions.parser_error import ParserError

logger = logging.getLogger(__name__)


class PDFParser(Parser):
    def extract_text(self, file_path: str) -> str:
        try:
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page_number, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text()
                        text += page_text if page_text else ""
                    except Exception as e:
                        logger.warning(
                            f"Failed to extract page {page_number + 1} "
                            f"from PDF '{file_path}': {e}"
                        )
                if not text.strip():
                    logger.warning(
                        f"PDF file '{file_path}' was parsed but contains no extractable text.")
                    raise ParserError("PDF file contains no extractable text.")
                return text
        except FileNotFoundError as e:
            logger.error(f"PDF file {file_path} not found")
            raise ParserError("PDF file not found.") from e
        except PermissionError as e:
            logger.error(f"No permission to read PDF file: '{file_path}'.")
            raise  ParserError("No permission to read PDF file.") from e
        except IsADirectoryError as e:
            logger.error(f"Expected a file but got a directory: '{file_path}'.")
            raise ParserError("Expected a file but got a directory.") from e
        except Exception as e:
            logger.critical(
                f"Unexpected error while parsing PDF file '{file_path}': {e}",
                exc_info=True)
            raise ParserError(
                "Unknown error occurred during PDF parsing.") from e


