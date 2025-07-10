from fastapi import UploadFile
from app.utils.file_validator import validate_file
from app.interfaces.interfaces import FileStorage, ParserClient

class UploadService:
    def __init__(self, storage: FileStorage, parser: ParserClient):
        self.storage = storage
        self.parser = parser

    async def handle_upload(self, file: UploadFile, user_id: str):
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
