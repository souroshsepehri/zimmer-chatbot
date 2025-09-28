from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import Optional, List
from datetime import datetime, date
from models.log import ChatLog
from schemas.log import LogFilters, LogListResponse, ChatLog as ChatLogSchema
from core.db import get_db
import math

router = APIRouter()


@router.get("/logs", response_model=LogListResponse)
async def get_logs(
    success: Optional[bool] = Query(None, description="Filter by success status"),
    intent: Optional[str] = Query(None, description="Filter by intent"),
    unanswered_only: Optional[bool] = Query(None, description="Show only unanswered questions"),
    from_date: Optional[datetime] = Query(None, description="Filter from date"),
    to_date: Optional[datetime] = Query(None, description="Filter to date"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get paginated chat logs with optional filters"""
    query = db.query(ChatLog)
    
    # Apply filters
    if success is not None:
        query = query.filter(ChatLog.success == success)
    
    if intent:
        query = query.filter(ChatLog.intent == intent)
    
    if unanswered_only:
        query = query.filter(ChatLog.notes.contains("unanswered_in_db"))
    
    if from_date:
        query = query.filter(ChatLog.timestamp >= from_date)
    
    if to_date:
        query = query.filter(ChatLog.timestamp <= to_date)
    
    # Order by timestamp (newest first)
    query = query.order_by(desc(ChatLog.timestamp))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    logs = query.offset(offset).limit(page_size).all()
    
    # Calculate total pages
    total_pages = math.ceil(total / page_size)
    
    return LogListResponse(
        items=logs,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/logs/stats")
async def get_log_stats(db: Session = Depends(get_db)):
    """Get chat log statistics"""
    total_logs = db.query(ChatLog).count()
    successful_logs = db.query(ChatLog).filter(ChatLog.success == True).count()
    
    # Count unanswered logs - simplified approach
    unanswered_logs = db.query(ChatLog).filter(
        ChatLog.notes.contains("unanswered_in_db")
    ).count()
    
    # Get today's logs
    from sqlalchemy import func
    today = date.today()
    today_logs = db.query(ChatLog).filter(
        func.date(ChatLog.timestamp) == today
    ).count()
    
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
        "total_logs": total_logs,
        "total_chats": total_logs,  # Alias for frontend compatibility
        "successful_logs": successful_logs,
        "success_rate": (successful_logs / total_logs * 100) if total_logs > 0 else 0,
        "unanswered_logs": unanswered_logs,
        "unanswered_rate": (unanswered_logs / total_logs * 100) if total_logs > 0 else 0,
        "today_chats": today_logs,
        "intent_distribution": {intent: count for intent, count in intent_stats},
        "source_distribution": {source: count for source, count in source_stats}
    }


@router.delete("/logs/{log_id}")
async def delete_log(
    log_id: int,
    db: Session = Depends(get_db)
):
    """Delete a specific chat log"""
    log = db.query(ChatLog).filter(ChatLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    
    db.delete(log)
    db.commit()
    
    return {"message": "Log deleted successfully"}
