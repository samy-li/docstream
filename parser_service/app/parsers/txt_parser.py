import logging

from parser_service.app.exceptions.parser_error import ParserError
from parser_service.app.parsers.parser import Parser


logger = logging.getLogger(__name__)

class TxtParser(Parser):
    def extract_text(self, file: str) -> str:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                text = f.read()
                if not text.strip():
                    logger.warning(
                        f"TXT file '{file}' was empty or had no readable content.")
                    raise ParserError("TXT file contains no extractable text.")
                return text
        except FileNotFoundError as e:
            logger.error(f"File not found: {file}")
            raise ParserError("File not found.") from e
        except PermissionError as e:
            logger.error(f"No permission to read file: {file}")
            raise ParserError("No permission to read file.") from e
        except IsADirectoryError as e:
            logger.error(f"Expected a file but got a directory: {file}")
            raise ParserError("Expected a file but got a directory.") from e
        except UnicodeDecodeError as e:
            logger.error(f"File is not valid UTF-8: {file}")
            raise ParserError(f"File is not a valid UTF-8 text file.") \
                from e
        except OSError as e:
            logger.error(f"OS error for file {file}: {e}")
            raise ParserError(f"OS-level error while reading file.") from e
        except Exception as e:
            logger.critical(
                f"Unexpected error while parsing TXT file '{file}': {e}",
                exc_info=True)
            raise ParserError(
                "Unknown error occurred during TXT parsing.") from e
