#!/usr/bin/env python3
"""
Startup script for the Persian Chatbot API
"""
import os
import sys
import uvicorn
from pathlib import Path

def main():
    # Ensure we're in the backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Get port from environment variable
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"🚀 Starting Persian Chatbot API on {host}:{port}")
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"🔧 Python version: {sys.version}")
    
    # Start the server
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        workers=1,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()
