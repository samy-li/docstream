from parser_service.app.parsers.parser import Parser
import docx
import logging

logger = logging.getLogger(__name__)


class DocxParser(Parser):
    def extract_text(self, file_path: str) -> str:
        try:
            doc = docx.Document(file_path)
            text = [p.text for p in doc.paragraphs if p.text]

            # Extract tables
            for table in doc.tables:
                for row in table.rows:
                    row_text = [cell.text.strip() for cell in row.cells if
                                cell.text.strip()]
                    if row_text:
                        text.append(" | ".join(row_text))

            full_text = "\n".join(text)

            if not full_text.strip():
                logger.error(
                    f"DOCX file '{file_path}' parsed but contained no extractable text.")
                raise ValueError("Could not extract text from DOCX file.")
            return full_text
        except FileNotFoundError:
            logger.error(f"DOCX file '{file_path}' not found.")
            raise
        except PermissionError:
            logger.error(f"No permission to read DOCX file: '{file_path}'.")
            raise
        except IsADirectoryError:
            logger.error(f"Expected a file but got a directory: '{file_path}'.")
            raise
        except Exception as e:
            logger.error(
                f"Failed to extract text from DOCX file '{file_path}': {e}",
                exc_info=True)
            raise ValueError("Corrupted or unreadable DOCX file.") from e
