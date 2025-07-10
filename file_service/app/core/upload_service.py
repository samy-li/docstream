from fastapi import UploadFile

from app.interfaces.interfaces import FileStorage, ParserClient
from app.utils.file_validator import validate_file


class UploadService:
    def __init__(self, storage: FileStorage, parser: ParserClient):
        self.storage = storage
        self.parser = parser

    async def handle_upload(self, file: UploadFile, user_id: str):
        """
               Handles file validation, saving to MinIO, and sending to parser.

               Args:
                   file: The uploaded file.
                   user_id: User ID to scope the file path.

               Returns:
                   dict: { filename, path, parser_response }
        """
        content = await file.read()
        validate_file(content)

        # Scoped filename prevents collisions between users
        scoped_filename = f"{user_id}/{file.filename}"

        path = self.storage.save_file(scoped_filename, content)
        response = self.parser.send_to_parser(path)

        return {
            "filename": file.filename,
            "path": path,
            "parser_response": response
        }
