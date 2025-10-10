import base64
import logging
from fastapi import APIRouter, HTTPException
from Crypto.PublicKey import RSA
from app.config.settings import get_settings

router = APIRouter()

logger = logging.getLogger(__name__)

@router.get("/.well-known/openid-configuration")
def openid_config():
    """
    OIDC discovery endpoint.
    Provides issuer metadata and JWKS URI for Kong.
    """
    settings = get_settings()

    try:
        config = {
            "issuer": settings.issuer_url,
            "jwks_uri": f"{settings.issuer_url}/.well-known/jwks.json",
            "token_endpoint": f"{settings.issuer_url}/issue",
            "response_types_supported": ["token"],
            "subject_types_supported": ["public"],
            "id_token_signing_alg_values_supported": [settings.jwt_algorithm],
        }

        logger.info("OpenID configuration served successfully.")
        return config

    except Exception as e:
        logger.exception("Failed to serve OpenID configuration: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/.well-known/jwks.json")
def jwks_issue():
    """
    JWKS endpoint.
    Publishes the RSA public key in JSON Web Key Set format.
    Kong fetches this automatically when discovery = true.
    """
    settings = get_settings()

    try:
        with open(settings.public_key_path, "rb") as f:
            key = RSA.import_key(f.read())

        # Convert key modulus and exponent to base64url
        n = base64.urlsafe_b64encode(
            key.n.to_bytes((key.n.bit_length() + 7) // 8, "big")
        ).decode().rstrip("=")

        e = base64.urlsafe_b64encode(
            key.e.to_bytes((key.e.bit_length() + 7) // 8, "big")
        ).decode().rstrip("=")

        jwks = {
            "keys": [
                {
                    "kty": "RSA",
                    "use": "sig",
                    "kid": settings.key_id,
                    "alg": settings.jwt_algorithm,
                    "n": n,
                    "e": e,
                }
            ]
        }

        logger.info("JWKS served successfully for key ID: %s", settings.key_id)
        return jwks

    except FileNotFoundError:
        logger.error("Public key file not found at path: %s", settings.public_key_path)
        raise HTTPException(status_code=500, detail="Public key not found")

    except Exception as e:
        logger.exception("Failed to load JWKS: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")
