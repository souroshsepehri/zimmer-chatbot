"""
Simple admin authentication module.

This module provides cookie-based admin authentication that is unified
with the admin login system in routers/admin.py.
"""

from fastapi import Request, HTTPException, status

# Import cookie constants from routers.admin to keep them in sync
from routers.admin import SESSION_COOKIE_NAME, SESSION_COOKIE_VALUE


def is_admin_authenticated(request: Request) -> tuple[bool, bool]:
    """
    Returns (authenticated, expired).

    - authenticated: True if the cookie is present and valid.
    - expired: Always False for now, since we rely on cookie max_age for expiration.

    Args:
        request: FastAPI request object

    Returns:
        Tuple of (authenticated: bool, expired: bool)
    """
    # Read the cookie from request.cookies
    cookie_value = request.cookies.get(SESSION_COOKIE_NAME)
    
    # If the cookie value equals SESSION_COOKIE_VALUE, return (True, False)
    if cookie_value == SESSION_COOKIE_VALUE:
        return True, False
    
    # If the cookie is missing or invalid, return (False, False)
    return False, False


def require_admin(request: Request):
    """
    Dependency function to require admin authentication for API routes.
    
    Raises:
        HTTPException: If not authenticated (401 Unauthorized)
    
    Returns:
        True if authenticated (used as a dependency gate)
    """
    authenticated, expired = is_admin_authenticated(request)
    
    if not authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin authentication required",
        )
    
    # If authenticated, return True (or any non-None value)
    return True
