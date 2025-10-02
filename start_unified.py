#!/usr/bin/env python3
"""
Unified startup script for Render deployment
Starts both backend API and serves frontend static files
"""
import os
import sys
import uvicorn
import subprocess
import threading
import time
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

def build_frontend():
    """Build the frontend if not already built"""
    frontend_dir = Path("frontend")
    out_dir = frontend_dir / "out"
    
    if not out_dir.exists():
        print("🔨 Building frontend...")
        try:
            # Install dependencies
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
            # Build for production
            subprocess.run(["npm", "run", "build"], cwd=frontend_dir, check=True)
            print("✅ Frontend built successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Frontend build failed: {e}")
            return False
    else:
        print("✅ Frontend already built")
    
    return True

def create_unified_app():
    """Create FastAPI app that serves both API and frontend"""
    # Import the original app
    sys.path.append("backend")
    from backend.app import app as backend_app
    
    # Create a new unified app
    unified_app = FastAPI(
        title="Persian Chatbot - Unified",
        description="Persian chatbot with integrated frontend and backend",
        version="1.0.0"
    )
    
    # Add CORS middleware
    unified_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Mount the backend API
    unified_app.mount("/api", backend_app)
    
    # Mount static files (frontend)
    frontend_out = Path("frontend/out")
    if frontend_out.exists():
        unified_app.mount("/static", StaticFiles(directory=str(frontend_out)), name="static")
        print("✅ Static files mounted")
    else:
        print("⚠️ Frontend not built, API only mode")
    
    # Serve frontend files
    @unified_app.get("/")
    async def serve_frontend():
        index_file = frontend_out / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        else:
            return {"message": "Persian Chatbot API is running", "frontend": "Not available"}
    
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
    
    return unified_app

def main():
    """Main startup function"""
    print("🚀 Starting Unified Persian Chatbot...")
    
    # Get environment variables
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"🔧 Python version: {sys.version}")
    print(f"🌐 Starting on {host}:{port}")
    
    # Build frontend
    if not build_frontend():
        print("⚠️ Continuing with API only mode")
    
    # Create unified app
    try:
        app = create_unified_app()
        print("✅ Unified app created successfully")
    except Exception as e:
        print(f"❌ Failed to create unified app: {e}")
        print("🔄 Falling back to backend only...")
        # Fallback to backend only
        sys.path.append("backend")
        from backend.app import app
    
    # Start the server
    print(f"🌐 Server starting on {host}:{port}")
    print("📱 Frontend will be available at the root URL")
    print("🔌 API will be available at /api")
    
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
