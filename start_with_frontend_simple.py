#!/usr/bin/env python3
"""
Simple startup script that serves both backend and frontend
"""
import os
import sys
import uvicorn
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

def main():
    """Main startup function"""
    print("🚀 Starting Persian Chatbot (Backend + Frontend)...")
    
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
    
    # Check if frontend is built
    frontend_out = Path("../frontend/out")
    if frontend_out.exists():
        print("✅ Frontend found, serving both backend and frontend")
        # Mount static files
        unified_app.mount("/static", StaticFiles(directory=str(frontend_out)), name="static")
        
        @unified_app.get("/")
        async def serve_frontend():
            index_file = frontend_out / "index.html"
            if index_file.exists():
                return FileResponse(str(index_file))
            else:
                return {"message": "Frontend not found"}
        
        @unified_app.get("/{path:path}")
        async def serve_frontend_routes(path: str):
            # If it's an API route, let the backend handle it
            if path.startswith("api/"):
                return {"error": "API route not found"}
            
            # Try to serve frontend file
            frontend_file = frontend_out / path
            if frontend_file.exists() and frontend_file.is_file():
                return FileResponse(str(frontend_file))
            
            # For SPA routing, serve index.html
            index_file = frontend_out / "index.html"
            if index_file.exists():
                return FileResponse(str(index_file))
            
            return {"error": "Not found"}
    else:
        print("⚠️ Frontend not built, serving backend only")
        @unified_app.get("/")
        async def root():
            return {
                "message": "Persian Chatbot API is running",
                "frontend": "Not available - frontend not built",
                "api_docs": "/api/docs",
                "chat_api": "/api/chat"
            }
    
    # Get port and host
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    if frontend_out.exists():
        print(f"📱 Frontend available at root URL")
        print(f"🔌 API available at /api")
    else:
        print(f"🔌 API available at /api")
        print(f"📚 API docs at /api/docs")
    
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
