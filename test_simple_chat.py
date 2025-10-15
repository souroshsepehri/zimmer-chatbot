#!/usr/bin/env python3
"""
Simple chat test to see debug output
"""

import requests
import time

def test_simple_chat():
    try:
        print("🧪 Testing simple chat...")
        
        # Wait a moment for server to be ready
        time.sleep(2)
        
        # Test with a simple message
        response = requests.post("http://localhost:8002/api/chat", json={
            "message": "سفارش",
            "debug": True
        })
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Answer: {data['answer']}")
            print(f"Source: {data.get('debug_info', {}).get('source', 'unknown')}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_simple_chat()
