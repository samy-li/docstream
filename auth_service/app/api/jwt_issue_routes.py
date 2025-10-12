import jwt
import time
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.config.settings import get_settings
from Crypto.PublicKey import RSA

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/issue")
def issue_token(payload: dict = None):
    """
    Issues an RS256-signed JWT using an RSA private key
    """
    settings = get_settings()

    try:
        # Import RSA key
        private_key = RSA.import_key(settings.private_key_str.encode())

        now = int(time.time())
        exp = now + settings.token_expiry_seconds
        subject = (payload or {}).get("sub", "docstream-client")

        claims = {
            "iss": settings.issuer_url,
            "sub": subject,
            "aud": settings.jwt_audience,
            "iat": now,
            "exp": exp,
        }

        token = jwt.encode(
            claims,
            private_key.export_key(),
            algorithm=settings.jwt_algorithm,
            headers={"kid": settings.key_id},
        )

        response = {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": settings.token_expiry_seconds,
        }

        logger.info("Issued JWT for sub=%s exp=%d", subject, exp)
        return JSONResponse(content=response)

    except Exception as e:
        logger.exception("Token issuance failed: %s", str(e))
        raise HTTPException(status_code=500, detail="Failed to issue token")
