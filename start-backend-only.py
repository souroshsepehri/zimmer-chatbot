#!/usr/bin/env python3
"""
Backend-only startup script for Render
No frontend, no vulnerabilities
"""
import os
import sys
from pathlib import Path

def setup_directories():
    """Create necessary directories"""
    directories = [
        "backend/vectorstore",
        "backend/logs",
        "backend/__pycache__"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {dir_path}")

def main():
    """Main startup function"""
    print("🚀 Starting Persian Chatbot Backend (No Vulnerabilities)...")
    
    # Setup directories
    setup_directories()
    
    # Change to backend directory
    os.chdir("backend")
    
    # Import and start the app
    try:
        from main import app
        print("✅ Backend app loaded successfully")
    except ImportError as e:
        print(f"❌ Failed to import app: {e}")
        sys.exit(1)
    
    # Start the server
    import uvicorn
    
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"🔌 API available at /api")
    print(f"📚 API docs at /docs")
    print(f"🌐 Server starting on {host}:{port}")
    
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
