from fastapi import HTTPException
import magic
from app.config.settings import get_settings

import logging
logger = logging.getLogger(__name__)

settings = get_settings()


def validate_file_size(content: bytes) -> bool:
    """
       Validates that the uploaded file does not exceed the max allowed size.

       Args:
           content (bytes): The raw file content.

       Returns:
           bool: True if size is within limits, False otherwise.
    """
    if len(content) > settings.max_file_size:
        logger.warning(
            f"File rejected: size={len(content)} exceeds max={settings.max_file_size}")
        return False
    return True

def validate_file_type(content: bytes) -> bool:
    """
       Validates the MIME type of the file using libmagic.

       Args:
           content (bytes): The raw file content.

       Returns:
           bool: True if the MIME type is allowed, False otherwise.
    """
    mime = magic.from_buffer(content, mime=True)
    if mime not in settings.allowed_mime_types:
        logger.warning(f"File rejected: MIME type '{mime}' not allowed")
        return False
    return True

def validate_file(content: bytes) -> bool:
    """
        Validates both the size and MIME of a file.

        Raises:
            HTTPException: 413 if file too large, 400 if unsupported MIME type.

        Returns:
            bool: True if all validations pass.
    """
    if not validate_file_size(content):
        raise HTTPException(status_code=413,
                            detail="File too large")
    if not validate_file_type(content):
        raise HTTPException(status_code=400,
                            detail="Invalid file type")
    return True



