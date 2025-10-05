#!/usr/bin/env python3
"""
Start the chatbot with URL agent functionality
"""

import uvicorn
import os
import sys
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def main():
    """Start the server with URL agent support"""
    print("🚀 Starting Persian Chatbot with URL Agent...")
    print("📡 URL Agent can read websites and use them as a second database")
    print("🌐 Enhanced interface available at: http://localhost:8002")
    print("📚 Simple interface available at: http://localhost:8002/simple")
    print("🔧 API documentation at: http://localhost:8002/docs")
    print()
    
    # Set environment variables if not already set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set. Please set it for full functionality.")
        print("   You can set it with: set OPENAI_API_KEY=your_key_here")
        print()
    
    # Start the server
    port = int(os.environ.get("PORT", 8002))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
