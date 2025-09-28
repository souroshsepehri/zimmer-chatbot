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
