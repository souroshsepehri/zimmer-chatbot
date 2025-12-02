#!/usr/bin/env python3
"""
Simple startup script for Persian Chatbot
"""
import os
import sys
from pathlib import Path

# Change to backend directory
backend_dir = Path(__file__).parent / "backend"
os.chdir(backend_dir)

# Import and run the app
if __name__ == "__main__":
    import uvicorn
    from core.config import settings
    
    port = int(os.environ.get("PORT", settings.server_port))
    host = os.environ.get("HOST", settings.server_host)
    
    print(f"🚀 Starting Persian Chatbot API")
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"🌐 Server: http://{host}:{port}")
    print(f"📚 API Docs: http://{host}:{port}/docs")
    print(f"🎛️  Admin Panel: http://{host}:{port}/admin")
    print("=" * 60)
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )











