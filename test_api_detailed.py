#!/usr/bin/env python3
"""
Detailed API test
"""

import requests
import json

def test_api_detailed():
    """Test API with detailed response analysis"""
    print("🔍 Detailed API Test")
    print("=" * 50)
    
    test_queries = ["قیمت", "گارانتی", "سفارش", "تماس"]
    
    for query in test_queries:
        print(f"\n🧪 Testing: '{query}'")
        print("-" * 30)
        
        try:
            response = requests.post("http://localhost:8002/api/chat", json={
                "message": query,
                "debug": True
            }, timeout=10)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"Response Keys: {list(data.keys())}")
                print(f"Success: {data.get('success', 'NOT_FOUND')}")
                print(f"Source: {data.get('source', 'NOT_FOUND')}")
                print(f"Intent: {data.get('intent', 'NOT_FOUND')}")
                print(f"Confidence: {data.get('confidence', 'NOT_FOUND')}")
                print(f"Answer: {data.get('answer', 'NOT_FOUND')[:50]}...")
                
                # Check debug info
                debug_info = data.get('debug_info')
                if debug_info:
                    print(f"Debug Info Keys: {list(debug_info.keys())}")
                    intent_info = debug_info.get('intent', {})
                    print(f"Debug Intent: {intent_info}")
                    retrieval_results = debug_info.get('retrieval_results', [])
                    print(f"Retrieval Results Count: {len(retrieval_results)}")
                    
                    if retrieval_results:
                        print("Retrieval Results:")
                        for i, result in enumerate(retrieval_results[:3], 1):
                            print(f"  {i}. {result.get('question', 'No question')[:50]}... (score: {result.get('score', 0)})")
                
                if data.get('success'):
                    print("✅ SUCCESS: Found answer")
                else:
                    print("❌ FAILED: No answer found")
                    
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_api_detailed()
