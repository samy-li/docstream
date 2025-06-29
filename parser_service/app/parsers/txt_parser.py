import logging
from parser_service.app.parsers.parser import Parser


logger = logging.getLogger(__name__)

class TxtParser(Parser):
    def extract_text(self, file: str) -> str:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                text = f.read()
                return text
        except FileNotFoundError:
            logger.error(f"File not found: {file}")
            raise FileNotFoundError(f"File not found: {file}")
        except PermissionError:
            logger.error(f"No permission to read file: {file}")
            raise PermissionError(f"No permission to read file: {file}")
        except IsADirectoryError:
            logger.error(f"Expected a file but got a directory: {file}")
            raise IsADirectoryError(f"Expected a file but got a directory: {file}")
        except UnicodeDecodeError:
            logger.error(f"File is not valid UTF-8: {file}")
            raise ValueError(f"File is not a valid UTF-8 text file: {file}")
        except OSError as e:
            logger.error(f"OS error for file {file}: {e}")
            raise OSError(f"Error reading file {file}: {e}")
        except Exception as e:
            logger.error(f"Unknown error for file {file}: {e}")
            raise RuntimeError(f"Unknown error: {e}")