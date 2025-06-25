from fastapi import APIRouter, File, UploadFile, Header, HTTPException
import os
from file_service.app.auth.jwt_utils import verify_token
from grpc_client import send_file_to_parser

router = APIRouter()

UPLOAD_DIR = "storage"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.split(" ")[1]
    try:
        return verify_token(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    response = ""
    with open(file_location, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    try:
        response = send_file_to_parser(file.filename)
    except Exception as e:
        print(e)
    return {"filename": file.filename, "path": file_location, "parser_response": response}
