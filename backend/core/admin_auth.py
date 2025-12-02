"""
Simple admin authentication module.

This is a minimal, hardcoded admin login system that can be easily replaced
with a proper authentication system later.
"""

from datetime import datetime, timedelta, timezone
from fastapi import Request, HTTPException, status
from typing import Tuple

# Hardcoded credentials
ADMIN_USERNAME = "zimmer admin"
ADMIN_PASSWORD = "admin1234"
ADMIN_SESSION_KEY = "admin_logged_in"
ADMIN_LAST_ACTIVITY_KEY = "admin_last_activity"
ADMIN_INACTIVITY_MINUTES = 5


def is_admin_authenticated(request: Request) -> Tuple[bool, bool]:
    """
    Returns (authenticated, expired).

    - authenticated: True if the session has a valid admin login and is not expired.
    - expired: True if there WAS a login but it is now expired due to inactivity.
    """
    session = request.session
    logged_in = session.get(ADMIN_SESSION_KEY, False)
    last_activity_iso = session.get(ADMIN_LAST_ACTIVITY_KEY)

    if not logged_in:
        return False, False

    now = datetime.now(timezone.utc)

    if not last_activity_iso:
        # logged_in but no last activity: treat as authenticated and set now
        session[ADMIN_LAST_ACTIVITY_KEY] = now.isoformat()
        return True, False

    try:
        last_activity = datetime.fromisoformat(last_activity_iso)
    except Exception:
        # corrupt timestamp -> force logout
        session.clear()
        return False, True

    if now - last_activity > timedelta(minutes=ADMIN_INACTIVITY_MINUTES):
        # expired
        session.clear()
        return False, True

    # update last activity
    session[ADMIN_LAST_ACTIVITY_KEY] = now.isoformat()
    return True, False


def login_admin(request: Request) -> None:
    now = datetime.now(timezone.utc)
    request.session[ADMIN_SESSION_KEY] = True
    request.session[ADMIN_LAST_ACTIVITY_KEY] = now.isoformat()


def logout_admin(request: Request) -> None:
    request.session.pop(ADMIN_SESSION_KEY, None)
    request.session.pop(ADMIN_LAST_ACTIVITY_KEY, None)


def require_admin(request: Request):
    """
    Dependency function to require admin authentication for API routes.
    
    Raises:
        HTTPException: If not authenticated
    """
    authenticated, expired = is_admin_authenticated(request)
    if not authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin authentication required"
        )
    return None
