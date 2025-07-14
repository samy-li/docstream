from .exceptions.parser_error import ParserError
from ..utils.file_type_control import detect_file_type
from ..config.settings import get_settings

class ParserFactory:
    @staticmethod
    def get_parser(file_path: str):
        settings = get_settings()
        ext, mime = detect_file_type(file_path)

        if ext not in settings.supported_types:
            raise ParserError(f"Unsupported file extension: .{ext}")

        if mime not in settings.supported_types[ext]:
            raise ParserError(
                f"Extension .{ext} does not match MIME type {mime}")

        parser = settings.parser_map.get(ext)
        if not parser:
            raise ParserError(f"No parser registered for extension: .{ext}")

        return parser()