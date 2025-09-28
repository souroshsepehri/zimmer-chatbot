#!/usr/bin/env python3
"""
Test semantic search through API
"""

import requests
import json

def test_api_semantic():
    print("🔍 TESTING SEMANTIC SEARCH VIA API")
    print("=" * 50)
    
    try:
        # Test 1: Try to build the FAQ index first
        print("1️⃣ Building FAQ index...")
        try:
            reindex_response = requests.post("http://localhost:8000/api/faqs/reindex")
            if reindex_response.status_code == 200:
                print("   ✅ FAQ index built successfully!")
            else:
                print(f"   ⚠️  Reindexing failed: {reindex_response.status_code}")
                print(f"   Error: {reindex_response.text}")
        except Exception as e:
            print(f"   ⚠️  Reindexing error: {e}")
        
        # Test 2: Test semantic search with debug info
        print("\n2️⃣ Testing semantic search with different queries...")
        
        test_queries = [
            "چطور می‌تونم سفارش بدم؟",
            "ساعات کاری شما چیه؟",
            "چطور با پشتیبانی تماس بگیرم؟",
            "خرید محصول",
            "تماس با ما"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n   Query {i}: {query}")
            
            response = requests.post("http://localhost:8000/api/chat", json={
                "message": query,
                "debug": True
            })
            
            if response.status_code == 200:
                data = response.json()
                debug_info = data.get('debug_info', {})
                source = debug_info.get('source', 'unknown')
                retrieval_results = debug_info.get('retrieval_results', [])
                
                print(f"   Source: {source}")
                print(f"   Answer: {data['answer'][:80]}{'...' if len(data['answer']) > 80 else ''}")
                
                if retrieval_results:
                    print(f"   📊 Found {len(retrieval_results)} retrieval results:")
                    for j, result in enumerate(retrieval_results[:3]):
                        print(f"     {j+1}. Score: {result.get('score', 0):.3f}")
                        print(f"        Q: {result.get('question', '')[:50]}...")
                        print(f"        A: {result.get('answer', '')[:50]}...")
                else:
                    print("   ⚠️  No retrieval results found")
            else:
                print(f"   ❌ Error: {response.status_code} - {response.text}")
        
        # Test 3: Check if we can see the debug output from server logs
        print(f"\n3️⃣ Testing with very specific queries...")
        
        specific_queries = [
            "من می‌خوام سفارش بدم",
            "کی می‌تونم تماس بگیرم",
            "راه‌های ارتباط",
            "کمک می‌خوام"
        ]
        
        for i, query in enumerate(specific_queries, 1):
            print(f"\n   Specific Query {i}: {query}")
            
            response = requests.post("http://localhost:8000/api/chat", json={
                "message": query,
                "debug": True
            })
            
            if response.status_code == 200:
                data = response.json()
                debug_info = data.get('debug_info', {})
                source = debug_info.get('source', 'unknown')
                retrieval_results = debug_info.get('retrieval_results', [])
                
                print(f"   Source: {source}")
                if retrieval_results:
                    best_score = retrieval_results[0].get('score', 0)
                    print(f"   Best Score: {best_score:.3f}")
                    print(f"   Answer: {data['answer'][:60]}...")
                else:
                    print(f"   Answer: {data['answer'][:60]}...")
            else:
                print(f"   ❌ Error: {response.status_code}")
        
        print("\n" + "=" * 50)
        print("🎯 SEMANTIC SEARCH API TEST COMPLETED!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server.")
        print("   Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_api_semantic()
