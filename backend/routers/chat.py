from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.chat import ChatRequest, ChatResponse
from services.chat_orchestrator import chat_orchestrator
from services.sites_service import resolve_site_by_host
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
    # Get user_id from request or context
    user_id = request.user_id or (request.context.get("user_id") if request.context else None)
    # Get session_id from context or use default
    session_id = (request.context.get("session_id") if request.context else None) or 'default_session'
    # Use channel if provided, otherwise fall back to source
    channel = request.channel or request.source or "unknown"
    
    try:
        # Resolve site from site_host if provided
        tracked_site = None
        if request.site_host:
            tracked_site = resolve_site_by_host(db, request.site_host)
            if tracked_site:
                logger.info(f"Resolved site: {tracked_site.name} (domain: {tracked_site.domain}) for host: {request.site_host}")
            else:
                logger.warning(f"No tracked site found for host: {request.site_host}")
        
        # Merge request context with any provided context
        context = request.context or {}
        context.update({
            "session_id": session_id or context.get("session_id"),
            "source": channel,  # Use channel as source
            "channel": channel,  # Also include channel explicitly
            "debug": request.debug,
            "category_filter": request.category_filter,
            "tracked_site_id": tracked_site.id if tracked_site else None,
            "tracked_site": tracked_site,  # Pass the full site object for use in orchestrator
            "site_host": request.site_host,  # Pass site_host explicitly in context
        })
        
        # Use orchestrator to route the message
        result = await chat_orchestrator.route_message(
            message=request.message,
            context=context,
            mode=request.mode or "auto",
            user_id=user_id,
            site_host=request.site_host,  # Pass site_host explicitly
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
        
        # Log to debugger with site information
        debug_info_with_site = result.get("debug_info", {})
        if tracked_site:
            debug_info_with_site["tracked_site_id"] = tracked_site.id
            debug_info_with_site["tracked_site_name"] = tracked_site.name
            debug_info_with_site["tracked_site_domain"] = tracked_site.domain
        if request.site_host:
            debug_info_with_site["site_host"] = request.site_host
        
        debugger.log_request(
            session_id=session_id,
            user_message=request.message,
            response=answer,
            response_time=response_time,
            intent_detected=intent_value,
            faq_matches=result.get("debug_info", {}).get("retrieval_results", []),
            search_scores=[],
            debug_info=debug_info_with_site
        )
        
        # Log site information to application logger
        if tracked_site:
            logger.info(
                f"Chat request processed for site: {tracked_site.name} (id: {tracked_site.id}, domain: {tracked_site.domain})"
            )
        elif request.site_host:
            logger.info(f"Chat request processed for unknown site_host: {request.site_host}")
        
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
