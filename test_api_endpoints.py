#!/usr/bin/env python3
"""
Test API endpoints for dashboard
"""

import requests
import json

def test_endpoints():
    base_url = "http://127.0.0.1:8002"
    
    print("🧪 Testing API Endpoints")
    print("=" * 40)
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"  Response: {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
    
    # Test logs stats
    try:
        response = requests.get(f"{base_url}/api/logs/stats")
        print(f"Logs stats: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Total logs: {data.get('total_logs', 0)}")
            print(f"  Success rate: {data.get('success_rate', 0):.1f}%")
            print(f"  Today chats: {data.get('today_chats', 0)}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"Logs stats failed: {e}")
    
    # Test FAQs
    try:
        response = requests.get(f"{base_url}/api/faqs")
        print(f"FAQs: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'items' in data:
                print(f"  FAQ count: {len(data['items'])}")
            else:
                print(f"  FAQ count: {len(data) if isinstance(data, list) else 0}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"FAQs failed: {e}")
    
    # Test categories
    try:
        response = requests.get(f"{base_url}/api/categories")
        print(f"Categories: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Category count: {len(data)}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"Categories failed: {e}")

if __name__ == "__main__":
    test_endpoints()
