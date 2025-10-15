#!/usr/bin/env python3
"""
Direct test of the chatbot functionality
"""

import requests
import json

def direct_test():
    """Direct test of the chatbot"""
    print("🔍 Direct Chatbot Test")
    print("=" * 50)
    
    # Test server status
    print("1. Testing server status...")
    try:
        response = requests.get("http://localhost:8004/api/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Server Status: {data.get('status', 'Unknown')}")
            print(f"   ✅ Database: {data.get('database', 'Unknown')}")
            print(f"   ✅ FAQs Loaded: {data.get('faqs_loaded', 0)}")
        else:
            print(f"   ❌ Server returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Server connection failed: {e}")
        return False
    
    # Test chat functionality
    print("\n2. Testing chat functionality...")
    test_messages = [
        "سلام",
        "قیمت محصولات چقدر است؟",
        "گارانتی دارید؟",
        "چطور سفارش بدم؟",
        "شماره تماس شما چیه؟"
    ]
    
    for message in test_messages:
        print(f"\n   Testing: '{message}'")
        try:
            response = requests.post("http://localhost:8004/api/chat", json={
                "message": message,
                "debug": True
            }, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success: {data.get('success', False)}")
                print(f"   📝 Answer: {data.get('answer', 'No answer')[:60]}...")
                print(f"   🎯 Intent: {data.get('intent', 'Unknown')}")
                print(f"   📊 Confidence: {data.get('confidence', 0)}")
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    return True

if __name__ == "__main__":
    print("🚀 Direct Chatbot Test")
    print("=" * 60)
    
    success = direct_test()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ CHATBOT IS WORKING CORRECTLY!")
        print("🌐 Server: http://localhost:8004")
        print("💬 API: /api/chat")
        print("📊 Status: /api/status")
        print("\nIf you're still having issues, please check:")
        print("1. Is the server running? (netstat -an | findstr :8004)")
        print("2. Are you using the correct URL? (http://localhost:8004)")
        print("3. Is your browser blocking the connection?")
    else:
        print("❌ CHATBOT IS NOT WORKING!")
        print("Please check the server status and try again.")
