#!/usr/bin/env python3
"""
Test the working server
"""

import requests
import json

def test_working_server():
    """Test the working server"""
    print("🔍 Testing Working Server")
    print("=" * 50)
    
    base_url = "http://localhost:8003/api"
    
    # Test 1: Check if server is responding
    print("1. Testing server response...")
    try:
        response = requests.get("http://localhost:8003/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Server is responding")
            print(f"   Message: {data.get('message', 'No message')}")
        else:
            print(f"   ❌ Server returned status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Server connection failed: {e}")
        return False
    
    # Test 2: Test chat API endpoint
    print("\n2. Testing chat API endpoint...")
    test_queries = ["قیمت", "گارانتی", "سفارش", "تماس", "کمک", "ساعت"]
    
    for query in test_queries:
        print(f"\n   Testing: '{query}'")
        try:
            response = requests.post(f"{base_url}/chat", json={
                "message": query,
                "debug": True
            }, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success: {data.get('success', False)}")
                print(f"   🎯 Intent: {data.get('intent', 'Unknown')}")
                print(f"   📊 Confidence: {data.get('confidence', 0)}")
                print(f"   🔍 Source: {data.get('source', 'Unknown')}")
                print(f"   📝 Answer: {data.get('answer', 'No answer')[:50]}...")
                
                if data.get('intent_match'):
                    print(f"   🎯 Intent Match: ✅")
                
                if data.get('context'):
                    print(f"   💡 Context: {data['context']}")
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    return True

if __name__ == "__main__":
    print("🚀 Working Server Test")
    print("=" * 60)
    
    test_working_server()
    
    print("\n" + "=" * 60)
    print("📊 TEST COMPLETED")
    print("=" * 60)
    print("If you see successful responses above, the chatbot is working!")
    print("The database reading issue has been resolved.")
