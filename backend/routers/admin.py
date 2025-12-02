from pathlib import Path

from fastapi import APIRouter, Request, Form, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse

router = APIRouter()

# --- Admin credentials ---
ADMIN_USERNAME = "zimmer_admin"
ADMIN_PASSWORD = "admin1234"

# --- Session cookie settings ---
SESSION_COOKIE_NAME = "zimmer_admin_session"
SESSION_COOKIE_VALUE = "zimmer_admin_active"
SESSION_COOKIE_MAX_AGE = 300  # seconds (5 minutes)

# --- Admin panel file path ---
# Adjust this path if your static directory is different
BASE_DIR = Path(__file__).resolve().parent.parent
ADMIN_PANEL_PATH = BASE_DIR / "static" / "admin_panel.html"


def is_admin_authenticated(request: Request) -> bool:
    """Check if the admin cookie is present and valid."""
    session_value = request.cookies.get(SESSION_COOKIE_NAME)
    return session_value == SESSION_COOKIE_VALUE


@router.get("/admin/login", response_class=HTMLResponse)
async def admin_login_get(request: Request) -> HTMLResponse:
    """Render the login form (Farsi, RTL)."""
    error = request.query_params.get("error")
    error_html = ""
    if error:
        error_html = """
        <p style="color:#b91c1c; text-align:center;">
            نام کاربری یا رمز عبور اشتباه است.
        </p>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8" />
        <title>ورود مدیر زیمر</title>
    </head>
    <body>
        <h1 style="text-align:center;">ورود مدیر زیمر</h1>
        {error_html}
        <form method="post" action="/admin/login" style="max-width:320px; margin:0 auto; text-align:right;">
            <label for="username">نام کاربری:</label><br />
            <input type="text" id="username" name="username" style="width:100%;" /><br /><br />

            <label for="password">رمز عبور:</label><br />
            <input type="password" id="password" name="password" style="width:100%;" /><br /><br />

            <button type="submit" style="width:100%;">ورود</button>
        </form>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@router.post("/admin/login")
async def admin_login_post(
    username: str = Form(...),
    password: str = Form(...),
):
    """Handle login form submission."""
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        # Successful login: set cookie and redirect to /admin
        response = RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=SESSION_COOKIE_VALUE,
            max_age=SESSION_COOKIE_MAX_AGE,  # 5 minutes
            httponly=True,
            samesite="lax",
        )
        return response

    # Invalid credentials: redirect back to login with error flag
    return RedirectResponse(
        url="/admin/login?error=1", status_code=status.HTTP_302_FOUND
    )


@router.get("/admin")
async def admin_page(request: Request):
    """Protected admin panel route."""
    if not is_admin_authenticated(request):
        # No or invalid cookie: redirect to login
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    # Ensure the admin panel HTML exists
    if not ADMIN_PANEL_PATH.is_file():
        raise HTTPException(
            status_code=500,
            detail=f"Admin panel HTML file not found at {ADMIN_PANEL_PATH}",
        )

    # Serve the static HTML admin panel and refresh the cookie expiration
    response = FileResponse(ADMIN_PANEL_PATH)

    # Sliding session expiration: refresh cookie on each valid access
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=SESSION_COOKIE_VALUE,
        max_age=SESSION_COOKIE_MAX_AGE,
        httponly=True,
        samesite="lax",
    )

    return response


@router.get("/admin/logout")
async def admin_logout():
    """Logout handler - clears the admin session cookie."""
    response = RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(SESSION_COOKIE_NAME, path="/admin")
    return response
