#!/usr/bin/env python3
"""
Test specific queries to debug the search issue
"""

import requests
import json

def test_specific_queries():
    """Test specific queries that should work"""
    
    test_queries = [
        "قیمت محصولات شما چقدر است؟",
        "آیا گارانتی دارید؟",
        "گارانتی محصولات چقدر طول می‌کشه؟",
        "قیمت",
        "گارانتی"
    ]
    
    print("🧪 Testing Specific Queries")
    print("=" * 50)
    
    for query in test_queries:
        try:
            print(f"\nTesting: '{query}'")
            
            response = requests.post("http://localhost:8002/api/chat", json={
                "message": query,
                "debug": True
            })
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('answer', 'No answer')
                source = data.get('debug_info', {}).get('source', 'unknown')
                success = data.get('debug_info', {}).get('success', False)
                retrieval_results = data.get('debug_info', {}).get('retrieval_results', [])
                
                print(f"  ✅ Status: 200")
                print(f"  📝 Answer: {answer[:100]}{'...' if len(answer) > 100 else ''}")
                print(f"  🔍 Source: {source}")
                print(f"  ✅ Success: {success}")
                print(f"  📊 Retrieval results: {len(retrieval_results)}")
                
                if retrieval_results:
                    print("  📋 Top matches:")
                    for i, result in enumerate(retrieval_results[:3], 1):
                        print(f"    {i}. {result.get('question', 'No question')[:50]}... (score: {result.get('score', 0):.3f})")
                
            else:
                print(f"  ❌ Status: {response.status_code}")
                print(f"  ❌ Error: {response.text}")
                
        except Exception as e:
            print(f"  ❌ Exception: {e}")

if __name__ == "__main__":
    test_specific_queries()
