#!/usr/bin/env python3
"""
Direct test of OpenAI API key
"""

import sys
import os
sys.path.append('backend')

from backend.core.config import settings
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI

def test_openai_direct():
    print("🔑 TESTING OPENAI API KEY DIRECTLY")
    print("=" * 50)
    
    try:
        print(f"API Key: {settings.openai_api_key[:20]}...")
        
        # Test 1: Test embeddings
        print("\n1️⃣ Testing OpenAI Embeddings...")
        try:
            embeddings = OpenAIEmbeddings(
                model=settings.embedding_model,
                openai_api_key=settings.openai_api_key
            )
            
            # Test with a simple text
            test_text = "چطور می‌تونم سفارش بدم؟"
            result = embeddings.embed_query(test_text)
            print(f"   ✅ Embeddings working! Vector length: {len(result)}")
            print(f"   First 5 values: {result[:5]}")
            
        except Exception as e:
            print(f"   ❌ Embeddings failed: {e}")
            return False
        
        # Test 2: Test Chat API
        print("\n2️⃣ Testing OpenAI Chat API...")
        try:
            llm = ChatOpenAI(
                model=settings.openai_model,
                openai_api_key=settings.openai_api_key,
                temperature=0.1
            )
            
            # Test with a simple prompt
            response = llm.invoke("سلام، چطور می‌تونم کمکتون کنم؟")
            print(f"   ✅ Chat API working!")
            print(f"   Response: {response.content[:100]}...")
            
        except Exception as e:
            print(f"   ❌ Chat API failed: {e}")
            return False
        
        print("\n" + "=" * 50)
        print("🎉 OPENAI API KEY IS WORKING PERFECTLY!")
        print("✅ Embeddings: Working")
        print("✅ Chat API: Working")
        print("✅ The issue might be in the retriever configuration")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

if __name__ == "__main__":
    test_openai_direct()
