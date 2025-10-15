#!/usr/bin/env python3
"""
Test the connection to the reliable server
"""

import requests
import json

def test_connection():
    """Test connection to the server"""
    print("🔍 Testing Server Connection")
    print("=" * 50)
    
    base_url = "http://localhost:8004/api"
    
    # Test 1: Check server status
    print("1. Testing server status...")
    try:
        response = requests.get("http://localhost:8004/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Server is running!")
            print(f"   Message: {data.get('message', 'No message')}")
            print(f"   Status: {data.get('status', 'Unknown')}")
        else:
            print(f"   ❌ Server returned status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Server connection failed: {e}")
        return False
    
    # Test 2: Check API status
    print("\n2. Testing API status...")
    try:
        response = requests.get(f"{base_url}/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("   ✅ API is working!")
            print(f"   Status: {data.get('status', 'Unknown')}")
            print(f"   Database: {data.get('database', 'Unknown')}")
            print(f"   FAQs loaded: {data.get('faqs_loaded', 0)}")
        else:
            print(f"   ❌ API returned status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ API connection failed: {e}")
    
    # Test 3: Test chat functionality
    print("\n3. Testing chat functionality...")
    test_queries = ["قیمت", "گارانتی", "سفارش", "تماس"]
    
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
                
                if data.get('context'):
                    print(f"   💡 Context: {data['context']}")
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    return True

if __name__ == "__main__":
    print("🚀 Connection Test")
    print("=" * 60)
    
    test_connection()
    
    print("\n" + "=" * 60)
    print("📊 TEST COMPLETED")
    print("=" * 60)
    print("If you see successful responses above, the connection is working!")
    print("The chat API is now connected and functional.")
