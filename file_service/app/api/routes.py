import os
from app.config.settings import Settings
from fastapi import APIRouter, File, UploadFile, Depends
from lxml.parser import filename

from app.core.upload_service import UploadService
from app.schemas.responses import UploadResponse
from dependencies.upload_service_di import get_upload_service
from app.auth.gateway_user_provider import get_current_user_id

router = APIRouter()

UPLOAD_DIR = Settings.UPLOAD_DIR
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...),
                      user_id: str = Depends(get_current_user_id),
                      upload_service: UploadService = Depends(
                          get_upload_service)
                      ) -> UploadResponse:
    response = await upload_service.handle_upload(file, user_id)

    return UploadResponse(filename=response["filename"], parser_response=response["parser_response"])


@router.get("/health")
def health():
    return {"status": "ok"}
