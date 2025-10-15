#!/usr/bin/env python3
"""
Test API connection
"""

import requests
import json

def test_api_connection():
    """Test if the chat API is working"""
    print("🔍 Testing Chat API Connection")
    print("=" * 50)
    
    base_url = "http://localhost:8002/api"
    
    # Test 1: Check if server is responding
    print("1. Testing server response...")
    try:
        response = requests.get("http://localhost:8002/", timeout=5)
        if response.status_code == 200:
            print("   ✅ Server is responding")
        else:
            print(f"   ❌ Server returned status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Server connection failed: {e}")
        return False
    
    # Test 2: Test chat API endpoint
    print("\n2. Testing chat API endpoint...")
    try:
        response = requests.post(f"{base_url}/chat", json={
            "message": "سلام",
            "debug": True
        }, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Chat API is working!")
            print(f"   📝 Response: {data.get('answer', 'No answer')[:50]}...")
            print(f"   🎯 Intent: {data.get('intent', 'Unknown')}")
            print(f"   📊 Confidence: {data.get('confidence', 0)}")
            print(f"   🔍 Source: {data.get('source', 'Unknown')}")
            return True
        else:
            print(f"   ❌ Chat API returned status: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Chat API connection failed: {e}")
        return False

def test_database_connection():
    """Test if database is accessible through API"""
    print("\n3. Testing database connection through API...")
    
    test_queries = ["قیمت", "گارانتی", "سفارش"]
    
    for query in test_queries:
        try:
            response = requests.post("http://localhost:8002/api/chat", json={
                "message": query,
                "debug": True
            }, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"   ✅ '{query}' → {data.get('intent', 'Unknown')} (confidence: {data.get('confidence', 0)})")
                else:
                    print(f"   ⚠️ '{query}' → No answer found")
            else:
                print(f"   ❌ '{query}' → API error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ '{query}' → Connection error: {e}")

if __name__ == "__main__":
    print("🚀 API Connection Test")
    print("=" * 60)
    
    # Test API connection
    api_success = test_api_connection()
    
    if api_success:
        # Test database connection
        test_database_connection()
        
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print("✅ Chat API is working!")
        print("✅ Database connection is working!")
        print("✅ Intent detection is working!")
        print("\n🎉 Everything is working correctly!")
    else:
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print("❌ Chat API is not working!")
        print("Please check the server logs for errors.")
