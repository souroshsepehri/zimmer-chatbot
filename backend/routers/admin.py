from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, date, timedelta
from pathlib import Path
from models.log import ChatLog
from models.faq import FAQ, Category
from core.db import get_db

router = APIRouter()

# Admin credentials
ADMIN_USERNAME = "zimmer_admin"
ADMIN_PASSWORD = "admin1234"
ADMIN_SESSION_COOKIE = "zimmer_admin_session"
ADMIN_SESSION_VALUE = "zimmer_admin_active"

# Static directory path
STATIC_DIR = Path(__file__).parent.parent / "static"
ADMIN_PANEL_FILE = STATIC_DIR / "admin_panel.html"


def require_admin(request: Request):
    """
    Helper function to check if user is authenticated as admin.
    Raises HTTPException with 302 redirect if not authenticated.
    """
    session = request.cookies.get(ADMIN_SESSION_COOKIE)
    if session != ADMIN_SESSION_VALUE:
        # not logged in
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            headers={"Location": "/admin/login"},
        )


@router.get("/admin/login", response_class=HTMLResponse)
async def admin_login_form():
    """Show the simple HTML login form"""
    return """
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8" />
        <title>ورود مدیر زیمر</title>
        <style>
            body {
                font-family: sans-serif;
                background: #f5f5f5;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
            }
            .box {
                background: white;
                padding: 24px 28px;
                border-radius: 12px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.08);
                width: 320px;
            }
            .box h1 {
                font-size: 18px;
                margin-bottom: 16px;
                text-align: center;
            }
            label {
                display: block;
                margin-top: 12px;
                margin-bottom: 4px;
                font-size: 13px;
            }
            input[type="text"],
            input[type="password"] {
                width: 100%;
                padding: 8px 10px;
                border-radius: 6px;
                border: 1px solid #ddd;
                font-size: 14px;
            }
            button {
                margin-top: 16px;
                width: 100%;
                padding: 10px 12px;
                border-radius: 8px;
                border: none;
                background: #4f46e5;
                color: white;
                font-size: 14px;
                cursor: pointer;
            }
            .error {
                margin-top: 8px;
                color: #b91c1c;
                font-size: 13px;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>ورود مدیر زیمر</h1>
            <form method="post" action="/admin/login">
                <label for="username">نام کاربری</label>
                <input type="text" id="username" name="username" />

                <label for="password">رمز عبور</label>
                <input type="password" id="password" name="password" />

                <button type="submit">ورود</button>
            </form>
        </div>
    </body>
    </html>
    """


@router.post("/admin/login")
async def admin_login_submit(
    username: str = Form(...),
    password: str = Form(...),
):
    """Handle admin login submission"""
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        # Successful login → set cookie and redirect to /admin
        response = RedirectResponse(url="/admin", status_code=302)
        response.set_cookie(
            ADMIN_SESSION_COOKIE,
            ADMIN_SESSION_VALUE,
            httponly=True,
            secure=False,
            samesite="lax",
        )
        return response
    else:
        # Wrong credentials: return 401 error
        return HTMLResponse(
            """
            <!DOCTYPE html>
            <html lang="fa" dir="rtl">
            <head>
                <meta charset="UTF-8" />
                <title>ورود مدیر زیمر</title>
            </head>
            <body>
                <p style="color:#b91c1c; text-align:center;">نام کاربری یا رمز عبور اشتباه است.</p>
                <p style="text-align:center;"><a href="/admin/login">بازگشت به صفحه ورود</a></p>
            </body>
            </html>
            """,
            status_code=401,
        )


@router.get("/admin")
async def admin_panel(request: Request):
    """
    Admin dashboard entry point.
    Requires a valid zimmer_admin_session cookie.
    Serves the static admin_panel.html file.
    """
    session = request.cookies.get(ADMIN_SESSION_COOKIE)
    if session != ADMIN_SESSION_VALUE:
        # redirect to login
        return RedirectResponse(url="/admin/login", status_code=302)

    if not ADMIN_PANEL_FILE.exists():
        # for safety, return a simple message instead of 500
        return HTMLResponse("admin_panel.html not found on server", status_code=500)

    return FileResponse(str(ADMIN_PANEL_FILE))


@router.get("/admin/faqs", response_class=HTMLResponse)
async def admin_faqs(request: Request):
    """Serve the FAQ management page"""
    session = request.cookies.get(ADMIN_SESSION_COOKIE)
    if session != ADMIN_SESSION_VALUE:
        return RedirectResponse(url="/admin/login", status_code=302)
    
    faqs_path = STATIC_DIR / "admin_faqs.html"
    if faqs_path.exists():
        return FileResponse(str(faqs_path))
    else:
        return HTMLResponse(content="<h1>FAQ management page not found</h1>", status_code=404)


@router.get("/admin/categories", response_class=HTMLResponse)
async def admin_categories(request: Request):
    """Serve the categories management page"""
    session = request.cookies.get(ADMIN_SESSION_COOKIE)
    if session != ADMIN_SESSION_VALUE:
        return RedirectResponse(url="/admin/login", status_code=302)
    
    categories_path = STATIC_DIR / "admin_categories.html"
    if categories_path.exists():
        return FileResponse(str(categories_path))
    else:
        return HTMLResponse(content="<h1>Categories management page not found</h1>", status_code=404)


@router.get("/admin/logs", response_class=HTMLResponse)
async def admin_logs(request: Request):
    """Serve the logs/reports page"""
    session = request.cookies.get(ADMIN_SESSION_COOKIE)
    if session != ADMIN_SESSION_VALUE:
        return RedirectResponse(url="/admin/login", status_code=302)
    
    logs_path = STATIC_DIR / "admin_logs.html"
    if logs_path.exists():
        return FileResponse(str(logs_path))
    else:
        return HTMLResponse(content="<h1>Logs page not found</h1>", status_code=404)


@router.get("/admin/stats")
async def get_admin_stats(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get comprehensive admin statistics"""
    session = request.cookies.get(ADMIN_SESSION_COOKIE)
    if session != ADMIN_SESSION_VALUE:
        return RedirectResponse(url="/admin/login", status_code=302)
    
    try:
        # Total questions/chats
        total_questions = db.query(ChatLog).count()
        
        # Success rate
        successful_logs = db.query(ChatLog).filter(ChatLog.success == True).count()
        success_rate = (successful_logs / total_questions * 100) if total_questions > 0 else 0
        
        # Active users (unique sessions or IPs - simplified as total unique user_text patterns)
        # For a more accurate count, you'd need a user_id or session_id field
        active_users = db.query(func.count(func.distinct(ChatLog.user_text))).scalar() or 0
        
        # Average response time
        avg_latency = db.query(func.avg(ChatLog.latency_ms)).scalar() or 0
        response_time_seconds = (avg_latency / 1000) if avg_latency else 0
        
        # Total FAQs
        total_faqs = db.query(FAQ).count()
        
        # Recent activity (last 24 hours)
        yesterday = datetime.now() - timedelta(days=1)
        recent_questions = db.query(ChatLog).filter(ChatLog.timestamp >= yesterday).count()
        
        # Intent distribution
        intent_stats = db.query(
            ChatLog.intent,
            func.count(ChatLog.id).label('count')
        ).group_by(ChatLog.intent).all()
        
        # Source distribution
        source_stats = db.query(
            ChatLog.source,
            func.count(ChatLog.id).label('count')
        ).group_by(ChatLog.source).all()
        
        return {
            "total_questions": total_questions,
            "success_rate": round(success_rate, 1),
            "active_users": active_users,
            "response_time": round(response_time_seconds, 2),
            "total_faqs": total_faqs,
            "recent_questions": recent_questions,
            "intent_distribution": {intent or "unknown": count for intent, count in intent_stats},
            "source_distribution": {source or "unknown": count for source, count in source_stats},
            "successful_logs": successful_logs,
            "failed_logs": total_questions - successful_logs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")


@router.get("/admin/dashboard-stats")
async def get_dashboard_stats(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get dashboard statistics for the admin panel"""
    session = request.cookies.get(ADMIN_SESSION_COOKIE)
    if session != ADMIN_SESSION_VALUE:
        return RedirectResponse(url="/admin/login", status_code=302)
    
    try:
        # Basic counts
        total_faqs = db.query(FAQ).count()
        total_logs = db.query(ChatLog).count()
        total_categories = db.query(Category).count()
        
        # Success metrics
        successful_logs = db.query(ChatLog).filter(ChatLog.success == True).count()
        success_rate = (successful_logs / total_logs * 100) if total_logs > 0 else 0
        
        # Today's activity
        today = date.today()
        today_logs = db.query(ChatLog).filter(
            func.date(ChatLog.timestamp) == today
        ).count()
        
        # Average response time
        avg_latency = db.query(func.avg(ChatLog.latency_ms)).scalar() or 0
        avg_response_time = (avg_latency / 1000) if avg_latency else 0
        
        return {
            "total_faqs": total_faqs,
            "total_logs": total_logs,
            "total_categories": total_categories,
            "success_rate": round(success_rate, 1),
            "today_logs": today_logs,
            "avg_response_time": round(avg_response_time, 2),
            "successful_logs": successful_logs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard stats: {str(e)}")


@router.get("/admin/recent-logs")
async def get_recent_logs(
    request: Request,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get recent chat logs"""
    session = request.cookies.get(ADMIN_SESSION_COOKIE)
    if session != ADMIN_SESSION_VALUE:
        return RedirectResponse(url="/admin/login", status_code=302)
    
    try:
        logs = db.query(ChatLog).order_by(desc(ChatLog.timestamp)).limit(limit).all()
        return {
            "logs": [
                {
                    "id": log.id,
                    "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                    "user_text": log.user_text,
                    "ai_text": log.ai_text,
                    "intent": log.intent,
                    "source": log.source,
                    "success": log.success,
                    "confidence": log.confidence
                }
                for log in logs
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recent logs: {str(e)}")
