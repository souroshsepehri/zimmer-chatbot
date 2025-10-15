from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.chat import ChatRequest, ChatResponse
from services.chain import chat_chain
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
    """Process chat message and return response"""
    start_time = time.time()
    session_id = getattr(request, 'session_id', 'default_session')
    
    try:
        # Process message through chain
        result = chat_chain.process_message(
            message=request.message,
            db=db,
            debug=request.debug,
            category_filter=request.category_filter
        )
        
        # Log the chat interaction
        print(f"DEBUG: Starting to log chat interaction for message: {request.message}")
        try:
            # Prepare notes with additional metadata
            notes_data = {
                "intent": result.get("intent", {}),
                "source": result.get("source", "unknown"),
                "unanswered_in_db": result.get("unanswered_in_db", False),
                "retrieval_count": len(result.get("retrieval_results", []))
            }
            
            # Create chat log entry
            chat_log = ChatLog(
                user_text=request.message,
                ai_text=result["answer"],
                intent=result.get("intent", {}).get("label"),
                source=result.get("source", "unknown"),
                confidence=result.get("intent", {}).get("confidence"),
                success=result.get("success", False),
                matched_faq_id=result.get("matched_faq_id"),
                notes=json.dumps(notes_data, ensure_ascii=False)
            )
            
            db.add(chat_log)
            db.commit()
            print(f"Chat logged successfully: ID {chat_log.id}")
            
        except Exception as log_error:
            print(f"Logging error (non-critical): {log_error}")
            # Don't fail the chat if logging fails
            pass
        
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
        
        return ChatResponse(
            answer=answer,
            debug_info=result.get("debug_info"),
            # Enhanced fields from smart intent detection
            intent=result.get("intent", {}).get("label") if isinstance(result.get("intent"), dict) else result.get("intent"),
            confidence=result.get("intent", {}).get("confidence") if isinstance(result.get("intent"), dict) else result.get("confidence"),
            context=result.get("context"),
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
