#!/usr/bin/env python3
"""
Test script to verify server startup with API key
"""

import os
import sys

def test_server_startup():
    print("🚀 Testing Server Startup Configuration")
    print("=" * 50)
    
    # Check API key from environment
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY environment variable not set!")
        print("Please set your OpenAI API key in environment variables.")
        return False
    
    print("✅ API Key set in environment")
    
    # Test config loading
    try:
        from core.config import settings
        print("✅ Config loaded successfully")
        print(f"   Model: {settings.openai_model}")
        print(f"   API Key configured: {bool(settings.openai_api_key)}")
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False
    
    # Test intent system
    try:
        from services.intent import intent_detector
        print("✅ Intent detector initialized")
        
        # Test intent detection
        result = intent_detector.detect("سلام")
        print(f"✅ Intent test: {result['label']} (confidence: {result['confidence']:.2f})")
        
    except Exception as e:
        print(f"❌ Intent system error: {e}")
        return False
    
    # Test chain system
    try:
        from services.chain import chat_chain
        print("✅ Chat chain initialized")
    except Exception as e:
        print(f"❌ Chat chain error: {e}")
        return False
    
    # Test app import
    try:
        import app
        print("✅ App module imported successfully")
    except Exception as e:
        print(f"❌ App import error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! Server should start successfully.")
    print("=" * 50)
    return True

if __name__ == "__main__":
    success = test_server_startup()
    sys.exit(0 if success else 1)
