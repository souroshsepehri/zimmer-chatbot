from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.chat import ChatRequest, ChatResponse
from services.chain import chat_chain
from models.log import ChatLog
from core.db import get_db
from datetime import datetime
import json

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Process chat message and return response"""
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
        
        return ChatResponse(
            answer=answer,
            debug_info=result["debug_info"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing error: {str(e)}")
