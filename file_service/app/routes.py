from fastapi import APIRouter, File, UploadFile, Header, HTTPException, Depends
import os
from .auth.jwt_utils import verify_token, create_token
from .utils.file_validator import validate_file
from .grpc_client import send_file_to_parser

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


@router.post("/token")
def get_token(username: str):
    return {"access_token": create_token(username), "token_type": "bearer"}


@router.post("/upload")
async def upload_file(file: UploadFile = File(...), user_id: str = Depends(get_current_user)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    response = ""
    content = await file.read()
    validate_file(content)
    with open(file_location, "wb") as buffer:
            buffer.write(content)
    try:
        response = send_file_to_parser(file.filename)
    except Exception as e:
        print(e)
    return {"filename": file.filename, "path": file_location, "parser_response": response}

@router.get("/health")
def health():
    return {"status": "ok"}

