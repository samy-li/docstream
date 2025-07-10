import os
from fastapi import APIRouter, File, UploadFile, Depends
from typing import Annotated

from app.config.settings import get_settings
from app.auth.gateway_user_provider import get_current_user_id
from app.core.upload_service import UploadService
from app.schemas.responses import UploadResponse
from app.dependencies.upload_service_di import get_upload_service

router = APIRouter()

settings = get_settings()

UPLOAD_DIR = settings.upload_dir
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload",
             response_model=UploadResponse,
             summary="Upload a document for processing",
             response_description="Uploaded file processing status",
             tags=["Document Upload"]
             )
async def upload_file(file: Annotated[UploadFile, File(...)],
                      user_id: Annotated[str, Depends(get_current_user_id)],
                      upload_service: Annotated[UploadService, Depends(
                          get_upload_service)]
                      ) -> UploadResponse:
    """
     Uploads a document, stores it, and sends it for parsing.

     The document is received, validated, saved,
     then forwarded to the parser-service.

     Args:
         file: Supported formats: PDF, DOCX, TXT,...etc.
         user_id: extracted from gateway header.
         upload_service: Service responsible for file upload workflow.

     Returns:
         UploadResponse: Object containing file name and parser response.
     """
    response = await upload_service.handle_upload(file, user_id)

    return UploadResponse(filename=response["filename"],
                          parser_response=response["parser_response"])


@router.get("/health",
            summary="Service health check",
            response_description="Returns OK status if service is running",
            tags=["System"]
            )
def health():
    """
       Returns OK if service is up, otherwise an error is raised.

       Returns:
           dict: { "status": "ok" }
       """
    return {"status": "ok"}
