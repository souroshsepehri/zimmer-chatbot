"""
Smart Chat Router - Uses intent detection for better answers
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

from services.smart_chatbot import get_smart_chatbot
from core.db import get_db

logger = logging.getLogger(__name__)

router = APIRouter()

class SmartChatRequest(BaseModel):
    message: str
    include_explanation: bool = False
    debug: bool = False

class SmartChatResponse(BaseModel):
    answer: str
    source: str
    success: bool
    faq_id: Optional[int] = None
    question: Optional[str] = None
    category: Optional[str] = None
    score: Optional[float] = None
    intent: Optional[str] = None
    confidence: Optional[float] = None
    context: Optional[str] = None
    intent_match: Optional[bool] = None
    suggested_actions: Optional[list] = None
    alternative_answers: Optional[list] = None
    explanation: Optional[str] = None
    debug_info: Optional[Dict[str, Any]] = None

@router.post("/smart-chat", response_model=SmartChatResponse)
async def smart_chat(request: SmartChatRequest):
    """
    Smart chat endpoint that uses intent detection to provide the best single answer
    """
    try:
        chatbot = get_smart_chatbot()
        
        if request.include_explanation:
            result = chatbot.get_answer_with_explanation(request.message)
        else:
            result = chatbot.get_smart_answer(request.message)
        
        # Prepare debug info if requested
        debug_info = None
        if request.debug:
            debug_info = {
                "message": request.message,
                "intent_detection": True,
                "smart_ranking": True,
                "processing_time": "N/A"  # Could add timing if needed
            }
        
        return SmartChatResponse(
            answer=result["answer"],
            source=result["source"],
            success=result["success"],
            faq_id=result.get("faq_id"),
            question=result.get("question"),
            category=result.get("category"),
            score=result.get("score"),
            intent=result.get("intent"),
            confidence=result.get("confidence"),
            context=result.get("context"),
            intent_match=result.get("intent_match"),
            suggested_actions=result.get("suggested_actions"),
            alternative_answers=result.get("alternative_answers"),
            explanation=result.get("explanation"),
            debug_info=debug_info
        )
        
    except Exception as e:
        logger.error(f"Error in smart chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/smart-chat/intents")
async def get_available_intents():
    """
    Get list of available intents that the system can detect
    """
    try:
        from services.smart_intent_detector import IntentType
        
        intents = []
        for intent in IntentType:
            intents.append({
                "name": intent.value,
                "description": intent.name.replace("_", " ").title()
            })
        
        return {
            "intents": intents,
            "total": len(intents)
        }
        
    except Exception as e:
        logger.error(f"Error getting intents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/smart-chat/test-intent")
async def test_intent(request: SmartChatRequest):
    """
    Test intent detection for a message
    """
    try:
        from services.smart_intent_detector import get_smart_intent_detector
        
        detector = get_smart_intent_detector()
        intent_result = detector.detect_intent(request.message)
        
        return {
            "message": request.message,
            "intent": intent_result.intent.value,
            "confidence": intent_result.confidence,
            "keywords": intent_result.keywords,
            "context": intent_result.context,
            "suggested_actions": intent_result.suggested_actions
        }
        
    except Exception as e:
        logger.error(f"Error testing intent: {e}")
        raise HTTPException(status_code=500, detail=str(e))
