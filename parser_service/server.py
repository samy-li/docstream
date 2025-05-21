import tempfile
from proto import parser_pb2, parser_pb2_grpc


class ResumeParser(parser_pb2_grpc.ResumeParserServicer):
    def ParseResume(self, request, context):
        # Save uploaded file content to temp
        with tempfile.NamedTemporaryFile(delete=False, suffix=request.filename) as tmp:
            tmp.write(request.file_content)
            tmp_path = tmp.name

        # Placeholder logic (temporary)
        text = f"Received file: {request.filename}, saved to: {tmp_path}"

        return parser_pb2.ParseResumeResponse(text=text)
