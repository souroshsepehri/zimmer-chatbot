from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ChatLogBase(BaseModel):
    user_text: str
    ai_text: str
    intent: Optional[str] = None
    source: Optional[str] = None
    confidence: Optional[float] = None
    success: bool = False
    matched_faq_id: Optional[int] = None
    tokens_in: Optional[int] = None
    tokens_out: Optional[int] = None
    latency_ms: Optional[int] = None
    notes: Optional[str] = None


class ChatLog(ChatLogBase):
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True


class LogFilters(BaseModel):
    success: Optional[bool] = None
    intent: Optional[str] = None
    unanswered_only: Optional[bool] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    page: int = 1
    page_size: int = 50


class LogListResponse(BaseModel):
    items: List[ChatLog]
    total: int
    page: int
    page_size: int
    total_pages: int
