from fastapi import Header, HTTPException


def get_current_user_id(x_user_id: str = Header(..., alias="X-User-ID")) \
        -> str:
    """
    Extracts the user ID from the header injected by Kong API Gateway
    after JWT validation.
    Returns:
        x_user_id: str
    """
    if not x_user_id:
        raise HTTPException(status_code=401, detail="User ID missing")
    return x_user_id
