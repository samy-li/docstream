import os
import tempfile
import logging
import grpc
from parser_service.app.proto import parser_pb2, parser_pb2_grpc
from parser_service.app.parsers.factory import ParserFactory
from .app.parsers.exceptions.parser_error import ParserError

logger = logging.getLogger(__name__)


class DocumentParser(parser_pb2_grpc.ResumeParserServicer):
    def ParseResume(self, request, context):
        # 1. Save uploaded content to a temp file
        try:
            suffix = os.path.splitext(request.filename)[-1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(request.file_content)
                tmp_path = tmp.name
        except Exception as e:
            logger.error("Failed to write uploaded file to disk", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Failed to write uploaded file to disk.")
            return parser_pb2.ParseResumeResponse()

        # 2. Parse file using ParserFactory
        try:
            parser = ParserFactory.get_parser(tmp_path)
            text = parser.extract_text(tmp_path)
        except ParserError as e:
            logger.warning(f"Parser error: {e}")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return parser_pb2.ParseResumeResponse()
        except Exception as e:
            logger.error("Unexpected error during parsing", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Internal server error during parsing.")
            return parser_pb2.ParseResumeResponse()
        finally:
            try:
                os.remove(tmp_path)
            except Exception:
                logger.warning(f"Failed to clean up temp file: {tmp_path}")

        return parser_pb2.ParseResumeResponse(text=text)
