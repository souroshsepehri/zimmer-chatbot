from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatRequest(BaseModel):
    message: str
    debug: Optional[bool] = False
    category_filter: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    debug_info: Optional[Dict[str, Any]] = None
    # Enhanced fields from smart intent detection
    intent: Optional[str] = None
    confidence: Optional[float] = None
    context: Optional[str] = None
    intent_match: Optional[bool] = None
    source: Optional[str] = None
    success: Optional[bool] = None
    matched_faq_id: Optional[int] = None
    question: Optional[str] = None
    category: Optional[str] = None
    score: Optional[float] = None


class IntentResult(BaseModel):
    label: str
    confidence: float
    reasoning: Optional[str] = None
    graph_trace: Optional[int] = None


class RetrievalResult(BaseModel):
    faq_id: int
    question: str
    answer: str
    score: float
    category: Optional[str] = None


class DebugInfo(BaseModel):
    intent: IntentResult
    source: str  # faq, rag, llm, fallback
    retrieval_results: List[RetrievalResult]
    tokens_in: Optional[int] = None
    tokens_out: Optional[int] = None
    latency_ms: Optional[int] = None
    success: bool
    unanswered_in_db: bool = False
