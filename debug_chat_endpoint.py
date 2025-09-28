#!/usr/bin/env python3
"""
Debug the chat endpoint to see why logging isn't working
"""

import requests
import json

def test_chat_with_debug():
    print("🔍 Testing Chat Endpoint with Debug")
    print("=" * 50)
    
    # Test chat endpoint
    try:
        response = requests.post('http://localhost:8002/api/chat', 
                               json={'message': 'تست لاگ جدید', 'debug': True})
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_chat_with_debug()
