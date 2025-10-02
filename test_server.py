#!/usr/bin/env python3
"""
Test script to check what the server is serving
"""
import requests
import sys

def test_server(base_url):
    """Test what the server is serving"""
    print(f"🧪 Testing server at: {base_url}")
    
    try:
        # Test root endpoint
        print("\n1. Testing root endpoint (/)...")
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'Unknown')}")
        
        if response.status_code == 200:
            content = response.text
            if "بات هوشمند زیمر" in content:
                print("   ✅ Chatbot interface found!")
            elif "message" in content.lower():
                print("   ⚠️ JSON response instead of HTML")
                print(f"   Response: {content[:200]}...")
            else:
                print("   ❓ Unknown response")
                print(f"   Response: {content[:200]}...")
        else:
            print(f"   ❌ Error: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
    
    try:
        # Test API endpoint
        print("\n2. Testing API endpoint (/api/chat)...")
        response = requests.post(
            f"{base_url}/api/chat",
            json={"message": "سلام"},
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API working! Response: {data.get('answer', 'No answer')[:100]}...")
        else:
            print(f"   ❌ API error: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ API connection error: {e}")
    
    try:
        # Test health endpoint
        print("\n3. Testing health endpoint (/health)...")
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Health check: {response.json()}")
        else:
            print(f"   ❌ Health check error: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Health check error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8000"
    
    test_server(base_url)
