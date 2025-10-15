#!/usr/bin/env python3
"""
Test the simple chat endpoint specifically
"""

import requests
import json

def test_simple_endpoint():
    """Test the simple chat endpoint"""
    
    test_queries = [
        "سفارش",
        "ساعات کاری", 
        "تماس",
        "قیمت",
        "گارانتی"
    ]
    
    print("🧪 Testing Simple Chat Endpoint")
    print("=" * 50)
    
    for query in test_queries:
        try:
            print(f"\nTesting: '{query}'")
            
            response = requests.post("http://localhost:8002/api/simple-chat", json={
                "message": query
            })
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Status: 200")
                print(f"  📝 Answer: {data.get('answer', 'No answer')}")
                print(f"  🔍 Source: {data.get('source', 'unknown')}")
                print(f"  ✅ Success: {data.get('success', False)}")
                print(f"  📊 FAQ ID: {data.get('faq_id', 'None')}")
                print(f"  📋 Question: {data.get('question', 'None')}")
                print(f"  🏷️  Category: {data.get('category', 'None')}")
                print(f"  📈 Score: {data.get('score', 'None')}")
            else:
                print(f"  ❌ Status: {response.status_code}")
                print(f"  ❌ Error: {response.text}")
                
        except Exception as e:
            print(f"  ❌ Exception: {e}")

if __name__ == "__main__":
    test_simple_endpoint()
