#!/usr/bin/env python3
"""
Test API directly with curl-like requests
"""

import requests
import json

def test_api_direct():
    try:
        print("🧪 Testing API directly...")
        
        # Test health first
        print("1. Testing health endpoint...")
        response = requests.get("http://localhost:8000/health")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error: {response.text}")
            return
        
        # Test chat endpoint
        print("\n2. Testing chat endpoint...")
        test_data = {
            "message": "چطور می‌تونم سفارش بدم؟",
            "debug": True
        }
        
        response = requests.post(
            "http://localhost:8000/api/chat",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Answer: {data['answer']}")
            print(f"   Source: {data.get('debug_info', {}).get('source', 'unknown')}")
            print(f"   Success: {data.get('debug_info', {}).get('success', False)}")
            
            if data.get('debug_info', {}).get('retrieval_results'):
                print(f"   Retrieval Results: {len(data['debug_info']['retrieval_results'])}")
                for i, ret in enumerate(data['debug_info']['retrieval_results'][:2]):
                    print(f"     {i+1}. {ret.get('question', '')[:50]}... (score: {ret.get('score', 0):.3f})")
        else:
            print(f"   Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_direct()
