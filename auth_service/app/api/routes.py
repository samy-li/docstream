from fastapi import APIRouter, HTTPException, Request
from app.services.auth_service import login
from app.core.logger import logger

router = APIRouter()

@router.post("/login")
async def login_route(data: dict, request: Request):
    logger.info("Received login request from %s", request.client.host)
    token = login(data["username"], data["password"])
    if not token:
        logger.error("Unauthorized login attempt for user '%s'", data["username"])
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": token, "token_type": "Bearer"}
