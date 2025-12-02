from fastapi import Header, HTTPException, status
from app.config import get_settings


async def verify_admin_token(x_admin_token: str = Header(..., alias="X-Admin-Token")):
    settings = get_settings()
    if x_admin_token != settings.ADMIN_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin token"
        )
    return True















