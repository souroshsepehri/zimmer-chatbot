#!/usr/bin/env python3
"""
Test API response structure to see what's happening with intent detection
"""

import requests
import json

def test_api_response():
    """Test the API response structure"""
    print("🔍 Testing API Response Structure")
    print("=" * 50)
    
    base_url = "http://localhost:8002/api"
    
    try:
        # Test the chat endpoint
        response = requests.post(f"{base_url}/chat", json={
            "message": "قیمت",
            "debug": True
        }, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ API Response received!")
            print(f"Status Code: {response.status_code}")
            print()
            
            print("📊 Response Structure:")
            print(f"  Keys: {list(data.keys())}")
            print()
            
            print("🎯 Intent Information:")
            print(f"  Intent: {data.get('intent', 'NOT_FOUND')}")
            print(f"  Intent Type: {type(data.get('intent'))}")
            if isinstance(data.get('intent'), dict):
                print(f"  Intent Dict: {data.get('intent')}")
            print()
            
            print("📈 Other Fields:")
            print(f"  Answer: {data.get('answer', 'NOT_FOUND')[:50]}...")
            print(f"  Source: {data.get('source', 'NOT_FOUND')}")
            print(f"  Success: {data.get('success', 'NOT_FOUND')}")
            print(f"  Confidence: {data.get('confidence', 'NOT_FOUND')}")
            print(f"  Context: {data.get('context', 'NOT_FOUND')}")
            print(f"  Intent Match: {data.get('intent_match', 'NOT_FOUND')}")
            print()
            
            print("🔍 Debug Info:")
            debug_info = data.get('debug_info')
            if debug_info:
                print(f"  Debug Info Keys: {list(debug_info.keys())}")
                print(f"  Debug Intent: {debug_info.get('intent', 'NOT_FOUND')}")
            else:
                print("  No debug info found")
            print()
            
            # Save full response for inspection
            with open('api_response_debug.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("💾 Full response saved to: api_response_debug.json")
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Error: {response.text}")
    
    except Exception as e:
        print(f"❌ Request Error: {e}")

if __name__ == "__main__":
    test_api_response()
