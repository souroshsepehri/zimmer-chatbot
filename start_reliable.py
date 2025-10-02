#!/usr/bin/env python3
"""
Reliable startup script for Render
Simple and guaranteed to work
"""
import os
import sys
import uvicorn
from pathlib import Path

def main():
    """Main startup function"""
    print("🚀 Starting Persian Chatbot...")
    
    # Create necessary directories
    directories = ["backend/vectorstore", "backend/logs"]
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {dir_path}")
    
    # Change to backend directory
    os.chdir("backend")
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Import the app
    try:
        from app import app
        print("✅ App imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        sys.exit(1)
    
    # Get port and host
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"🌐 Starting server on {host}:{port}")
    print(f"🔌 API will be available at /api")
    print(f"📚 API docs will be available at /docs")
    
    # Start the server
    uvicorn.run(
        app,
        host=host,
        port=port,
        workers=1,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()
