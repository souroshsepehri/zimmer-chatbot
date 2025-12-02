from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional
from datetime import datetime, date, timedelta
from pathlib import Path
from models.log import ChatLog
from models.faq import FAQ, Category
from core.db import get_db
from core.admin_auth import (
    require_admin, 
    login_admin, 
    logout_admin,
    is_admin_authenticated,
    ADMIN_USERNAME, 
    ADMIN_PASSWORD
)

# Admin credentials constants
ADMIN_USERNAME_MAIN = "zimmer_admin"
ADMIN_USERNAME_ALT = "zimmer admin"
ADMIN_PASSWORD = "admin1234"

def verify_admin_credentials(username: str, password: str) -> bool:
    # Normalize username to avoid whitespace and case issues
    normalized = username.strip().lower()
    allowed_usernames = {
        ADMIN_USERNAME_MAIN.lower(),
        ADMIN_USERNAME_ALT.lower(),
    }
    return (normalized in allowed_usernames) and (password == ADMIN_PASSWORD)

router = APIRouter()

# Initialize Jinja2 templates
# Templates directory is at backend/templates relative to this file (backend/routers/admin.py)
templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


# Login routes are now handled in main.py with cookie-based authentication
# Removed to avoid conflicts


@router.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request):
    """Serve the admin panel HTML"""
    authenticated, expired = is_admin_authenticated(request)
    if not authenticated:
        return RedirectResponse(url="/admin/login", status_code=302)
    
    admin_panel_path = Path(__file__).parent.parent / "static" / "admin_panel.html"
    if admin_panel_path.exists():
        return FileResponse(admin_panel_path)
    else:
        return HTMLResponse(content="<h1>Admin panel not found</h1>", status_code=404)


@router.get("/admin/faqs", response_class=HTMLResponse)
async def admin_faqs(request: Request):
    """Serve the FAQ management page"""
    authenticated, expired = is_admin_authenticated(request)
    if not authenticated:
        return RedirectResponse(url="/admin/login", status_code=302)
    
    faqs_path = Path(__file__).parent.parent / "static" / "admin_faqs.html"
    if faqs_path.exists():
        return FileResponse(faqs_path)
    else:
        return HTMLResponse(content="<h1>FAQ management page not found</h1>", status_code=404)


@router.get("/admin/categories", response_class=HTMLResponse)
async def admin_categories(request: Request):
    """Serve the categories management page"""
    authenticated, expired = is_admin_authenticated(request)
    if not authenticated:
        return RedirectResponse(url="/admin/login", status_code=302)
    
    categories_path = Path(__file__).parent.parent / "static" / "admin_categories.html"
    if categories_path.exists():
        return FileResponse(categories_path)
    else:
        return HTMLResponse(content="<h1>Categories management page not found</h1>", status_code=404)


@router.get("/admin/logs", response_class=HTMLResponse)
async def admin_logs(request: Request):
    """Serve the logs/reports page"""
    authenticated, expired = is_admin_authenticated(request)
    if not authenticated:
        return RedirectResponse(url="/admin/login", status_code=302)
    
    logs_path = Path(__file__).parent.parent / "static" / "admin_logs.html"
    if logs_path.exists():
        return FileResponse(logs_path)
    else:
        return HTMLResponse(content="<h1>Logs page not found</h1>", status_code=404)


@router.get("/admin/stats")
async def get_admin_stats(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get comprehensive admin statistics"""
    authenticated, expired = is_admin_authenticated(request)
    if not authenticated:
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
    authenticated, expired = is_admin_authenticated(request)
    if not authenticated:
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
    authenticated, expired = is_admin_authenticated(request)
    if not authenticated:
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

