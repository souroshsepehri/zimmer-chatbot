#!/usr/bin/env python3
"""
Startup script that serves both backend and frontend
Uses pre-built frontend to avoid vulnerabilities
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
    print("🚀 Starting Persian Chatbot (Backend + Frontend)...")
    
    # Setup directories
    setup_directories()
    
    # Check if frontend is built
    frontend_out = Path("frontend/out")
    if frontend_out.exists():
        print("✅ Frontend found, serving both backend and frontend")
        # Use the unified app that serves both
        os.chdir("backend")
        try:
            from app_unified import app
            print("✅ Using unified app (backend + frontend)")
        except ImportError:
            from app import app
            print("✅ Using backend app (frontend will be served separately)")
    else:
        print("⚠️ Frontend not found, serving backend only")
        os.chdir("backend")
        from app import app
    
    # Start the server
    import uvicorn
    
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    if frontend_out.exists():
        print(f"📱 Frontend available at root URL")
        print(f"🔌 API available at /api")
    else:
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
