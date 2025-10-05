"""
Simple chat router for reliable database reading
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.simple_chatbot import get_simple_chatbot
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class SimpleChatRequest(BaseModel):
    message: str

class SimpleChatResponse(BaseModel):
    answer: str
    source: str
    success: bool
    faq_id: Optional[int] = None
    question: Optional[str] = None
    category: Optional[str] = None
    score: Optional[float] = None

@router.post("/simple-chat", response_model=SimpleChatResponse)
async def simple_chat(request: SimpleChatRequest):
    """Simple chat endpoint that reliably reads from database"""
    try:
        chatbot = get_simple_chatbot()
        result = chatbot.get_answer(request.message)
        
        return SimpleChatResponse(
            answer=result["answer"],
            source=result["source"],
            success=result["success"],
            faq_id=result.get("faq_id"),
            question=result.get("question"),
            category=result.get("category"),
            score=result.get("score")
        )
        
    except Exception as e:
        logger.error(f"Error in simple chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/simple-stats")
async def get_simple_stats():
    """Get simple chatbot statistics"""
    try:
        chatbot = get_simple_chatbot()
        stats = chatbot.get_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-database")
async def test_database():
    """Test database connection and data"""
    try:
        chatbot = get_simple_chatbot()
        
        # Test loading FAQs
        if chatbot.load_faqs_from_db():
            return {
                "status": "success",
                "message": "Database connection successful",
                "faq_count": len(chatbot.faqs),
                "sample_faqs": [
                    {
                        "id": faq["id"],
                        "question": faq["question"][:100] + "..." if len(faq["question"]) > 100 else faq["question"],
                        "category": faq["category"]
                    }
                    for faq in chatbot.faqs[:3]
                ]
            }
        else:
            return {
                "status": "error",
                "message": "Failed to load FAQs from database",
                "faq_count": 0
            }
            
    except Exception as e:
        logger.error(f"Database test failed: {e}")
        return {
            "status": "error",
            "message": f"Database test failed: {str(e)}",
            "faq_count": 0
        }
