#!/usr/bin/env python3
"""
Test logs API endpoint specifically
"""

import requests
import json

def test_logs_api():
    base_url = "http://127.0.0.1:8002"
    
    print("🧪 Testing Logs API Endpoint")
    print("=" * 40)
    
    # Test logs endpoint
    try:
        print("Testing /api/logs endpoint...")
        response = requests.get(f"{base_url}/api/logs")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response received")
            print(f"  Type: {type(data)}")
            
            if isinstance(data, dict):
                print(f"  Keys: {list(data.keys())}")
                if 'items' in data:
                    print(f"  Items count: {len(data['items'])}")
                    if data['items']:
                        print(f"  First item keys: {list(data['items'][0].keys())}")
                else:
                    print(f"  Direct data count: {len(data) if isinstance(data, list) else 'N/A'}")
            elif isinstance(data, list):
                print(f"  List length: {len(data)}")
                if data:
                    print(f"  First item keys: {list(data[0].keys())}")
            
            print(f"  Sample data: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    # Test logs stats endpoint
    try:
        print(f"\nTesting /api/logs/stats endpoint...")
        response = requests.get(f"{base_url}/api/logs/stats")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stats received")
            print(f"  Total logs: {data.get('total_logs', 0)}")
            print(f"  Success rate: {data.get('success_rate', 0):.1f}%")
            print(f"  Today chats: {data.get('today_chats', 0)}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    test_logs_api()
