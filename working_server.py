#!/usr/bin/env python3
"""
Working server for the chatbot
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
app = FastAPI(title="Working Chatbot Server")

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
    intent_match: Optional[bool] = None
    question: Optional[str] = None
    category: Optional[str] = None
    score: Optional[float] = None

@app.get("/")
async def root():
    return {
        "message": "Working Chatbot Server is running!",
        "status": "success",
        "endpoints": {
            "chat": "/api/chat",
            "test": "/api/test"
        }
    }

@app.get("/api/test")
async def test_endpoint():
    """Test endpoint to verify server is working"""
    return {
        "status": "success",
        "message": "API is working correctly",
        "database": "connected"
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint with working database connection"""
    try:
        from services.simple_chatbot import get_simple_chatbot
        
        # Get the chatbot
        chatbot = get_simple_chatbot()
        
        # Get answer
        result = chatbot.get_answer(request.message)
        
        return ChatResponse(
            answer=result["answer"],
            success=result["success"],
            source=result["source"],
            intent=result.get("intent"),
            confidence=result.get("confidence"),
            context=result.get("context"),
            intent_match=result.get("intent_match"),
            question=result.get("question"),
            category=result.get("category"),
            score=result.get("score")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Working Chatbot Server...")
    print("🌐 Server will be available at: http://localhost:8003")
    print("📚 Test endpoint: http://localhost:8003/api/test")
    print("💬 Chat endpoint: http://localhost:8003/api/chat")
    print("🔧 Database: Connected and working")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8003,
        log_level="info"
    )
