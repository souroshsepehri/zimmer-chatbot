from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.chat import ChatRequest, ChatResponse
from services.answering_agent import answer_user_query
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.debugger import debugger
from models.log import ChatLog
from core.db import get_db
from datetime import datetime
import json
import time

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Process chat message and return response.
    
    This endpoint uses the Answering Agent to process user queries.
    The agent handles normalization, intent detection, data retrieval,
    and answer composition.
    """
    start_time = time.time()
    session_id = getattr(request, 'session_id', 'default_session')
    user_id = getattr(request, 'user_id', None)
    
    try:
        # Use the new Answering Agent
        context = {
            "session_id": session_id,
            "debug": request.debug,
            "category_filter": request.category_filter
        }
        
        agent_result = answer_user_query(
            user_id=user_id,
            message=request.message,
            context=context,
            db=db
        )
        
        # Handle validation errors gracefully
        if agent_result.get("source") == "validation_error":
            # Return a proper response for validation errors
            return ChatResponse(
                answer=agent_result["answer"],
                source="validation_error",
                success=False,
                matched_faq_id=None,
                unanswered_in_db=True,
                intent=agent_result.get("intent", "validation_error"),  # intent is a string in ChatResponse
                confidence=0.0,
                context=str(agent_result.get("metadata", {})),  # context is Optional[str]
                intent_match=False,
                question=None,
                category=None,
                score=0.0
            )
        
        # Convert agent result to ChatResponse format
        result = {
            "answer": agent_result["answer"],
            "source": agent_result["source"],
            "success": agent_result["success"],
            "matched_faq_id": agent_result["matched_ids"][0] if agent_result.get("matched_ids") else None,
            "unanswered_in_db": not agent_result["success"],
            "retrieval_results": [],  # Can be populated from metadata if needed
            "intent": {
                "label": agent_result.get("intent", "unknown"),
                "confidence": agent_result.get("confidence", 0.0)
            },
            "context": agent_result.get("metadata", {}),
            "intent_match": agent_result["success"],
            "score": agent_result.get("confidence", 0.0),
            "question": agent_result.get("metadata", {}).get("matched_question"),
            "category": None,  # Can be extracted from matched FAQ if needed
        }
        
        # Note: Logging is handled by the Answering Agent
        # Ensure answer is properly encoded
        answer = result["answer"]
        if isinstance(answer, str):
            # Ensure the answer is properly encoded for JSON response
            answer = answer.encode('utf-8').decode('utf-8')
        
        # Log to debugger
        response_time = time.time() - start_time
        debugger.log_request(
            session_id=session_id,
            user_message=request.message,
            response=answer,
            response_time=response_time,
            intent_detected=result.get("intent", {}).get("label") if isinstance(result.get("intent"), dict) else result.get("intent"),
            faq_matches=result.get("retrieval_results", []),
            search_scores=[r.get("score", 0) for r in result.get("retrieval_results", [])],
            debug_info=result.get("debug_info", {})
        )
        
        # Convert intent dict to string if needed
        intent_value = result.get("intent")
        if isinstance(intent_value, dict):
            intent_value = intent_value.get("label", "unknown")
        
        # Convert context to string if it's a dict
        context_value = result.get("context")
        if isinstance(context_value, dict):
            import json
            context_value = json.dumps(context_value, ensure_ascii=False)
        
        return ChatResponse(
            answer=answer,
            debug_info=result.get("debug_info"),
            # Enhanced fields from smart intent detection
            intent=intent_value,
            confidence=result.get("intent", {}).get("confidence") if isinstance(result.get("intent"), dict) else result.get("confidence"),
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
        response_time = time.time() - start_time
        debugger.log_request(
            session_id=session_id,
            user_message=request.message,
            response="",
            response_time=response_time,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Chat processing error: {str(e)}")
