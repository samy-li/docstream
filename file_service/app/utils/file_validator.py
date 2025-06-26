from fastapi import HTTPException
import magic
from file_service.app.config import MAX_FILE_SIZE, ALLOWED_MIME_TYPES

def validate_file_size(content: bytes):
    if len(content) > MAX_FILE_SIZE:
        return False
    else:
        return True

def validate_file_type(content: bytes):
    mime = magic.from_buffer(content, mime=True)
    if mime not in ALLOWED_MIME_TYPES:
        return False
    else:
        return True

def validate_file(content: bytes):
    if not validate_file_size(content):
        raise HTTPException(status_code=413,
                            detail="content too large")
    if not validate_file_type(content):
        raise HTTPException(status_code=400,
                            detail="Invalid content type")
    return True



