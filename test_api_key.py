#!/usr/bin/env python3
"""
Test script to verify OpenAI API key is working
"""

import os
import sys

def test_api_key():
    print("🔑 Testing OpenAI API Key Configuration")
    print("=" * 50)
    
    # Check environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    print(f"Environment variable set: {bool(api_key)}")
    if api_key:
        print(f"Key length: {len(api_key)} characters")
        print(f"Key starts with: {api_key[:10]}...")
    
    # Test config loading
    try:
        from core.config import settings
        print(f"Config loaded: ✅")
        print(f"API Key in config: {bool(settings.openai_api_key)}")
        print(f"Model: {settings.openai_model}")
        
        if settings.openai_api_key:
            print(f"Config key length: {len(settings.openai_api_key)}")
            print(f"Config key starts with: {settings.openai_api_key[:10]}...")
        
    except Exception as e:
        print(f"Config error: {e}")
    
    # Test OpenAI connection
    try:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(
            model=settings.openai_model,
            api_key=api_key or settings.openai_api_key,
            temperature=0.1
        )
        
        response = llm.invoke("Hello, this is a test. Please respond with 'API key working!'")
        print(f"OpenAI test: ✅")
        print(f"Response: {response.content}")
        
    except Exception as e:
        print(f"OpenAI test failed: {e}")

if __name__ == "__main__":
    test_api_key()
