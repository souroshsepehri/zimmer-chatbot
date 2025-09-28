#!/usr/bin/env python3
"""
Test chat endpoint and check if logging is working
"""

import requests
import json

def test_chat_endpoint():
    print("🔍 Testing Chat Endpoint")
    print("=" * 50)
    
    # Test chat endpoint
    try:
        response = requests.post('http://localhost:8002/api/chat', 
                               json={'message': 'تست لاگ از طریق API'})
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_chat_endpoint()
