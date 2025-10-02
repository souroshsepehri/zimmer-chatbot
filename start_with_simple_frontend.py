#!/usr/bin/env python3
"""
Startup script that serves backend + simple HTML frontend
"""
import os
import sys
import uvicorn
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse

def main():
    """Main startup function"""
    print("🚀 Starting Persian Chatbot (Backend + Simple Frontend)...")
    
    # Create necessary directories
    directories = ["backend/vectorstore", "backend/logs"]
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {dir_path}")
    
    # Change to backend directory to import the app
    os.chdir("backend")
    
    # Import the backend app
    try:
        from app import app as backend_app
        print("✅ Backend app imported successfully")
    except ImportError as e:
        print(f"❌ Backend import error: {e}")
        sys.exit(1)
    
    # Create a new unified app
    unified_app = FastAPI(
        title="Persian Chatbot - Unified",
        description="Persian chatbot with integrated frontend and backend",
        version="1.0.0"
    )
    
    # Mount the backend API
    unified_app.mount("/api", backend_app)
    
    # Serve simple HTML frontend
    @unified_app.get("/")
    async def serve_frontend():
        html_file = Path("../simple-chatbot.html")
        if html_file.exists():
            return FileResponse(str(html_file))
        else:
            return {
                "message": "Persian Chatbot API is running",
                "frontend": "Simple HTML frontend not found",
                "api_docs": "/api/docs",
                "chat_api": "/api/chat"
            }
    
    # Get port and host
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"📱 Simple chatbot interface available at root URL")
    print(f"🔌 API available at /api")
    print(f"🌐 Server starting on {host}:{port}")
    
    # Start the server
    uvicorn.run(
        unified_app,
        host=host,
        port=port,
        workers=1,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()
