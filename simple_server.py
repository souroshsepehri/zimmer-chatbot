#!/usr/bin/env python3
"""
Simple server to test chatbot database reading
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

# Create FastAPI app
app = FastAPI(title="Simple Chatbot Test")

class ChatRequest(BaseModel):
    message: str
    debug: Optional[bool] = False

class ChatResponse(BaseModel):
    answer: str
    success: bool
    source: str
    intent: Optional[str] = None
    confidence: Optional[float] = None
    context: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Simple Chatbot Server is running!"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Simple chat endpoint to test database reading"""
    try:
        from services.simple_chatbot import get_simple_chatbot
        
        chatbot = get_simple_chatbot()
        result = chatbot.get_answer(request.message)
        
        return ChatResponse(
            answer=result["answer"],
            success=result["success"],
            source=result["source"],
            intent=result.get("intent"),
            confidence=result.get("confidence"),
            context=result.get("context")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/test-db")
async def test_database():
    """Test database connection"""
    try:
        from core.db import get_db
        from models.faq import FAQ
        
        db = next(get_db())
        faq_count = db.query(FAQ).count()
        db.close()
        
        return {
            "status": "success",
            "faq_count": faq_count,
            "message": f"Database connected successfully. Found {faq_count} FAQs."
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Database error: {str(e)}"
        }

if __name__ == "__main__":
    print("🚀 Starting Simple Chatbot Server...")
    print("🌐 Server will be available at: http://localhost:8003")
    print("📚 Test endpoint: http://localhost:8003/test-db")
    print("💬 Chat endpoint: http://localhost:8003/chat")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8003,
        log_level="info"
    )
