from pydantic import BaseModel

class UploadResponse(BaseModel):
    filename: str
    parser_response: str