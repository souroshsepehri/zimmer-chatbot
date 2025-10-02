#!/usr/bin/env python3
"""
Fixed startup script for Render deployment
Handles common deployment issues
"""
import os
import sys
import subprocess
from pathlib import Path

def check_and_build_frontend():
    """Check and build frontend if needed"""
    frontend_dir = Path("frontend")
    out_dir = frontend_dir / "out"
    
    if not out_dir.exists() and frontend_dir.exists():
        print("🔨 Frontend not built, building now...")
        try:
            # Install dependencies
            print("📦 Installing npm dependencies...")
            subprocess.run(["npm", "install", "--production=false"], 
                         cwd=frontend_dir, check=True, capture_output=True)
            
            # Build for production
            print("🏗️ Building frontend...")
            subprocess.run(["npm", "run", "build"], 
                         cwd=frontend_dir, check=True, capture_output=True)
            
            print("✅ Frontend built successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Frontend build failed: {e}")
            print("🔄 Continuing with API only mode...")
            return False
        except FileNotFoundError:
            print("❌ npm not found, skipping frontend build")
            return False
    else:
        print("✅ Frontend already built or not needed")
        return True

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
    print("🚀 Starting Persian Chatbot (Fixed)...")
    
    # Setup directories
    setup_directories()
    
    # Check and build frontend
    check_and_build_frontend()
    
    # Change to backend directory
    os.chdir("backend")
    
    # Import and start the app
    try:
        from app_unified import app
        print("✅ Using unified app")
    except ImportError:
        try:
            from app import app
            print("✅ Using standard app")
        except ImportError as e:
            print(f"❌ Failed to import app: {e}")
            sys.exit(1)
    
    # Start the server
    import uvicorn
    
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
