#!/usr/bin/env python3
"""
Minimal working server
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

# Create FastAPI app
app = FastAPI()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str
    success: bool
    source: str

@app.get("/")
async def root():
    return {"message": "Minimal server is running!", "status": "ok"}

@app.get("/api/status")
async def status():
    return {
        "status": "online",
        "database": "connected",
        "faqs_loaded": 15,
        "server": "running"
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Simple chat endpoint"""
    try:
        from services.simple_chatbot import get_simple_chatbot
        
        chatbot = get_simple_chatbot()
        result = chatbot.get_answer(request.message)
        
        return ChatResponse(
            answer=result["answer"],
            success=result["success"],
            source=result["source"]
        )
        
    except Exception as e:
        return ChatResponse(
            answer=f"خطا: {str(e)}",
            success=False,
            source="error"
        )

if __name__ == "__main__":
    print("🚀 Starting Minimal Server on port 8005...")
    uvicorn.run(app, host="0.0.0.0", port=8005)
