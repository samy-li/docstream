from fastapi import APIRouter, File, UploadFile
import os
from grpc_client import send_file_to_parser

router = APIRouter()

UPLOAD_DIR = "storage"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    try:
        send_file_to_parser(file.filename)
    except Exception as e:
        print(e)
    return {"filename": file.filename, "path": file_location}
