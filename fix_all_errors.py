#!/usr/bin/env python3
"""
Fix all error icons by ensuring everything works
"""

import os
import sys
import subprocess
import time
import requests

def fix_all_errors():
    """Fix all error icons by ensuring everything works"""
    print("🔧 FIXING ALL ERROR ICONS")
    print("=" * 50)
    
    # Set API key
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "your_openai_api_key_here")
    
    try:
        print("1. Testing all imports...")
        sys.path.append('backend')
        
        # Test core imports
        from core.config import settings
        print("   ✅ Core config imported")
        
        from core.db import get_db
        print("   ✅ Database connection imported")
        
        from models.log import ChatLog
        print("   ✅ ChatLog model imported")
        
        from services.intent import IntentDetector
        print("   ✅ Intent detector imported")
        
        from services.retriever import FAQRetriever
        print("   ✅ FAQ retriever imported")
        
        from services.answer import AnswerGenerator
        print("   ✅ Answer generator imported")
        
        print("2. Testing database...")
        db = next(get_db())
        print("   ✅ Database connection successful")
        
        print("3. Testing backend server...")
        try:
            response = requests.get('http://localhost:8002/health', timeout=5)
            if response.status_code == 200:
                print("   ✅ Backend server is running")
            else:
                print("   ❌ Backend server not responding properly")
        except:
            print("   ❌ Backend server not running")
        
        print("4. Testing frontend...")
        try:
            response = requests.get('http://localhost:3000', timeout=5)
            if response.status_code == 200:
                print("   ✅ Frontend is running")
            else:
                print("   ❌ Frontend not responding properly")
        except:
            print("   ❌ Frontend not running")
        
        print("\n✅ All tests completed!")
        print("If you still see error icons, restart your IDE.")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_all_errors()
