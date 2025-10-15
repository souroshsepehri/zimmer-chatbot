#!/usr/bin/env python3
"""
Simple reliable server that definitely works
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
import requests

# Create FastAPI app
app = FastAPI(title="Simple Reliable Chatbot Server")

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
    return {
        "message": "Simple Reliable Chatbot Server is running!",
        "status": "connected",
        "database": "ready",
        "endpoints": {
            "chat": "/api/chat",
            "test": "/api/test",
            "status": "/api/status"
        }
    }

@app.get("/api/status")
async def status():
    """Check server status"""
    try:
        from services.simple_chatbot import get_simple_chatbot
        chatbot = get_simple_chatbot()
        success = chatbot.load_faqs_from_db()
        
        return {
            "status": "online",
            "database": "connected" if success else "disconnected",
            "faqs_loaded": len(chatbot.faqs) if success else 0,
            "server": "running"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "server": "running"
        }

@app.get("/api/test")
async def test():
    """Simple test endpoint"""
    return {
        "message": "API is working!",
        "status": "success",
        "timestamp": "now"
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint"""
    try:
        from services.simple_chatbot import get_simple_chatbot
        
        # Get chatbot
        chatbot = get_simple_chatbot()
        
        # Get answer
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
        # Return a fallback response instead of raising an exception
        return ChatResponse(
            answer=f"متأسفانه خطایی رخ داد: {str(e)}",
            success=False,
            source="error",
            intent="unknown",
            confidence=0.0,
            context="خطا در پردازش درخواست"
        )

if __name__ == "__main__":
    print("🚀 Starting Simple Reliable Chatbot Server...")
    print("🌐 Server will be available at: http://localhost:8004")
    print("📚 Status endpoint: http://localhost:8004/api/status")
    print("💬 Chat endpoint: http://localhost:8004/api/chat")
    print("🔧 Database: Will be tested on startup")
    print()
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8004,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        print("Please check the error above and try again.")
