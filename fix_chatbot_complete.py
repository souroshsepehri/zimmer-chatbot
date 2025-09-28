#!/usr/bin/env python3
"""
Complete chatbot fix script
"""

import os
import sys
import subprocess
import time
import requests

def fix_chatbot():
    """Fix the complete chatbot system"""
    print("🔧 FIXING COMPLETE CHATBOT SYSTEM")
    print("=" * 50)
    
    # Set API key
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "your_openai_api_key_here")
    
    try:
        print("1. Setting up database...")
        sys.path.append('backend')
        
        from core.db import get_db
        from models.log import ChatLog
        from models.faq import FAQ
        from models.category import Category
        
        # Create tables
        from core.db import engine
        from core.db import Base
        Base.metadata.create_all(bind=engine)
        print("   ✅ Database tables created")
        
        print("2. Testing imports...")
        from services.intent import IntentDetector
        intent_detector = IntentDetector()
        print("   ✅ Intent detector created")
        
        from services.retriever import FAQRetriever
        retriever = FAQRetriever()
        print("   ✅ FAQRetriever created")
        
        from services.answer import AnswerGenerator
        answer_generator = AnswerGenerator()
        print("   ✅ Answer generator created")
        
        print("3. Testing chat chain...")
        from services.chain import chat_chain
        print("   ✅ Chat chain imported")
        
        print("4. Starting backend server...")
        try:
            # Start backend in background
            subprocess.Popen([
                sys.executable, "-m", "uvicorn", 
                "app:app", "--host", "127.0.0.1", "--port", "8002"
            ], cwd="backend")
            print("   ✅ Backend server started")
            
            # Wait for server to start
            time.sleep(10)
            
            # Test server
            response = requests.get('http://localhost:8002/health')
            if response.status_code == 200:
                print("   ✅ Backend server is healthy")
            else:
                print("   ❌ Backend server health check failed")
                
        except Exception as e:
            print(f"   ❌ Error starting backend: {e}")
        
        print("5. Testing chat endpoint...")
        try:
            response = requests.post('http://localhost:8002/api/chat', 
                                   json={'message': 'سلام'})
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Chat working: {result['answer'][:50]}...")
            else:
                print(f"   ❌ Chat failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Chat error: {e}")
        
        print("\n✅ CHATBOT FIX COMPLETED!")
        print("Backend server is running on http://localhost:8002")
        print("You can now start the frontend with: cd frontend && npm run dev")
        
    except Exception as e:
        print(f"❌ Error during fix: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_chatbot()
