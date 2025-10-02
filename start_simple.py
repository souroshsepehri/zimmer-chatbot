#!/usr/bin/env python3
"""
Simple unified startup script for Render
Builds frontend and starts backend with frontend serving
"""
import os
import sys
import subprocess
from pathlib import Path

def build_frontend():
    """Build the frontend"""
    frontend_dir = Path("frontend")
    
    print("🔨 Building frontend...")
    try:
        # Install dependencies
        print("📦 Installing npm dependencies...")
        subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
        
        # Build for production
        print("🏗️ Building frontend...")
        subprocess.run(["npm", "run", "build"], cwd=frontend_dir, check=True)
        
        print("✅ Frontend built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Frontend build failed: {e}")
        return False
    except FileNotFoundError:
        print("❌ npm not found, skipping frontend build")
        return False

def main():
    """Main startup function"""
    print("🚀 Starting Persian Chatbot (Unified)...")
    
    # Build frontend
    build_frontend()
    
    # Change to backend directory
    os.chdir("backend")
    
    # Start the unified backend
    print("🌐 Starting unified server...")
    import uvicorn
    from app_unified import app
    
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"📱 Frontend will be available at the root URL")
    print(f"🔌 API will be available at /api")
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
