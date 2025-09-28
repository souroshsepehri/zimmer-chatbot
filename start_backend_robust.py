#!/usr/bin/env python3
"""
Robust Backend Server Starter
Handles server stability issues and keeps it running
"""

import os
import sys
import time
import subprocess
import signal
import threading
from pathlib import Path

def start_backend():
    """Start the backend server with proper error handling"""
    print("🚀 Starting Backend Server...")
    
    # Set API key from environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set!")
        print("Please set it with: $env:OPENAI_API_KEY='your_api_key_here'")
        return
    os.environ["OPENAI_API_KEY"] = api_key
    
    # Change to backend directory
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"🔑 API Key set: {api_key[:20]}...")
    
    # Start server with uvicorn directly
    try:
        print("🔄 Starting server on port 8002...")
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app:app", 
            "--host", "127.0.0.1", 
            "--port", "8002", 
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("🔄 Retrying in 5 seconds...")
        time.sleep(5)
        start_backend()

if __name__ == "__main__":
    start_backend()
