import jwt
import logging
import json
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse
from jwt import ExpiredSignatureError, InvalidTokenError
from Crypto.PublicKey import RSA
from pydantic import BaseModel
from app.config.settings import get_settings

router = APIRouter()
logger = logging.getLogger(__name__)


class TokenRequest(BaseModel):
    token: str | None = None


def verify_jwt(token: str) -> dict:
    settings = get_settings()
    public_key = RSA.import_key(settings.public_key_str.encode())

    return jwt.decode(
        token,
        key=public_key.export_key(),
        algorithms=[settings.jwt_algorithm],
        audience=settings.jwt_audience,
        issuer=settings.issuer_url,
    )

# Route definition
@router.post("/verify")
async def verify_token(request: Request, body: TokenRequest | None = None):
    """
    Verifies a JWT using an RSA public key
    """

    # Extract token from header or validated body
    token = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    elif body and body.token:
        token = body.token

    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Missing token")

    try:
        decoded = verify_jwt(token)
        logger.info(json.dumps({
            "event": "token_verified",
            "sub": decoded.get("sub"),
            "aud": decoded.get("aud"),
            "exp": decoded.get("exp"),
            "status": "success"
        }))
        return JSONResponse(content={"valid": True, "claims": decoded})

    except ExpiredSignatureError:
        logger.warning(json.dumps({"event": "token_verify",
                                   "status": "expired"}))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token expired")

    except InvalidTokenError as e:
        logger.warning(json.dumps({"event": "token_verify", "status": "invalid",
                                   "reason": str(e)}))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid token")

    except Exception as e:
        logger.exception("Unexpected verification error: %s", str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Internal server error")
