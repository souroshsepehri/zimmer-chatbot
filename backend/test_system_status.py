#!/usr/bin/env python3
"""
Test system status endpoints
"""

import requests
import json

def test_system_status():
    base_url = "http://127.0.0.1:8002"
    
    print("🧪 Testing System Status Endpoints")
    print("=" * 40)
    
    # Test health endpoint
    try:
        print("Testing /health endpoint...")
        response = requests.get(f"{base_url}/health")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Health check: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.text}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test logs stats
    try:
        print(f"\nTesting /api/logs/stats endpoint...")
        response = requests.get(f"{base_url}/api/logs/stats")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Logs stats: {data.get('total_logs', 0)} logs")
        else:
            print(f"❌ Logs stats failed: {response.text}")
    except Exception as e:
        print(f"❌ Logs stats error: {e}")
    
    # Test FAQs endpoint
    try:
        print(f"\nTesting /api/faqs endpoint...")
        response = requests.get(f"{base_url}/api/faqs")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            count = len(data) if isinstance(data, list) else len(data.get('items', []))
            print(f"✅ FAQs: {count} items")
        else:
            print(f"❌ FAQs failed: {response.text}")
    except Exception as e:
        print(f"❌ FAQs error: {e}")
    
    # Test categories endpoint
    try:
        print(f"\nTesting /api/categories endpoint...")
        response = requests.get(f"{base_url}/api/categories")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            count = len(data) if isinstance(data, list) else 0
            print(f"✅ Categories: {count} items")
        else:
            print(f"❌ Categories failed: {response.text}")
    except Exception as e:
        print(f"❌ Categories error: {e}")
    
    # Test chat endpoint
    try:
        print(f"\nTesting /api/chat endpoint...")
        response = requests.post(f"{base_url}/api/chat", 
                               json={"message": "test"},
                               headers={"Content-Type": "application/json"})
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Chat endpoint working")
        else:
            print(f"❌ Chat endpoint failed: {response.text}")
    except Exception as e:
        print(f"❌ Chat endpoint error: {e}")
    
    print(f"\n🎉 System status test completed!")

if __name__ == "__main__":
    test_system_status()
