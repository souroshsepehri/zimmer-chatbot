from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.chat import ChatRequest, ChatResponse
from services.chat_orchestrator import chat_orchestrator
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.debugger import debugger
from models.log import ChatLog
from core.db import get_db
from datetime import datetime
import json
import time
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Unified chat endpoint that routes to SmartAIAgent or baseline answering_agent.
    
    This endpoint uses the ChatOrchestrator to intelligently route messages:
    - SmartAIAgent: When page_url is present or mode is "smart_agent" (uses web + FAQ + LLM)
    - Baseline: When mode is "baseline" or SmartAIAgent fails (uses FAQ-based answering_agent)
    
    The orchestrator provides automatic fallback to baseline if SmartAIAgent fails.
    """
    start_time = time.time()
    session_id = getattr(request, 'session_id', 'default_session')
    user_id = getattr(request, 'user_id', None)
    
    try:
        # Merge request context with any provided context
        context = request.context or {}
        context.update({
            "session_id": session_id or context.get("session_id"),
            "debug": request.debug,
            "category_filter": request.category_filter,
        })
        
        # Use orchestrator to route the message
        result = await chat_orchestrator.route_message(
            message=request.message,
            context=context,
            mode=request.mode or "auto",
            user_id=user_id,
            db=db,
        )
        
        # Ensure answer is properly encoded
        answer = result.get("answer", "")
        if isinstance(answer, str):
            answer = answer.encode('utf-8').decode('utf-8')
        
        # Log to debugger
        response_time = time.time() - start_time
        intent_value = result.get("intent")
        if isinstance(intent_value, dict):
            intent_value = intent_value.get("label", "unknown")
        
        debugger.log_request(
            session_id=session_id,
            user_message=request.message,
            response=answer,
            response_time=response_time,
            intent_detected=intent_value,
            faq_matches=result.get("debug_info", {}).get("retrieval_results", []),
            search_scores=[],
            debug_info=result.get("debug_info", {})
        )
        
        # Convert context to string if it's a dict
        context_value = result.get("context")
        if isinstance(context_value, dict):
            context_value = json.dumps(context_value, ensure_ascii=False)
        
        return ChatResponse(
            answer=answer,
            debug_info=result.get("debug_info"),
            intent=result.get("intent"),
            confidence=result.get("confidence"),
            context=context_value,
            intent_match=result.get("intent_match"),
            source=result.get("source"),
            success=result.get("success"),
            matched_faq_id=result.get("matched_faq_id"),
            question=result.get("question"),
            category=result.get("category"),
            score=result.get("score")
        )
        
    except Exception as e:
        # Log error to debugger
        logger.exception("Chat endpoint error: %s", e)
        response_time = time.time() - start_time
        debugger.log_request(
            session_id=session_id,
            user_message=request.message,
            response="",
            response_time=response_time,
            error_message=str(e)
        )
        # Return error response instead of raising HTTPException to maintain compatibility
        return ChatResponse(
            answer="متأسفانه در حال حاضر سیستم با مشکل مواجه شده است. لطفاً چند دقیقه دیگر دوباره تلاش کنید.",
            source="error",
            success=False,
            intent="error",
            confidence=0.0,
            context=None,
            intent_match=False,
            matched_faq_id=None,
            question=request.message,
            category=None,
            score=0.0,
            debug_info={"error": str(e)}
        )
