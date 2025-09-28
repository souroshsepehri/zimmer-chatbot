#!/usr/bin/env python3
"""
Test OpenAI API integration and semantic search functionality
"""

import requests
import json
import time

def test_openai_integration():
    print("🤖 TESTING OPENAI API INTEGRATION")
    print("=" * 50)
    
    try:
        # Test 1: Check if semantic search is working
        print("1️⃣ Testing semantic search with OpenAI embeddings...")
        
        # Test with a question that should trigger semantic search
        test_queries = [
            "چطور می‌تونم سفارش بدم؟",
            "ساعات کاری",
            "پشتیبانی",
            "خرید محصول",
            "تماس با ما"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🧪 Test {i}: {query}")
            
            response = requests.post("http://localhost:8000/api/chat", json={
                "message": query,
                "debug": True
            })
            
            if response.status_code == 200:
                data = response.json()
                debug_info = data.get('debug_info', {})
                source = debug_info.get('source', 'unknown')
                success = debug_info.get('success', False)
                retrieval_results = debug_info.get('retrieval_results', [])
                
                print(f"   Source: {source}")
                print(f"   Success: {success}")
                print(f"   Answer: {data['answer'][:100]}{'...' if len(data['answer']) > 100 else ''}")
                
                if retrieval_results:
                    print(f"   📊 Found {len(retrieval_results)} retrieval results:")
                    for j, result in enumerate(retrieval_results[:3]):
                        print(f"      {j+1}. Score: {result.get('score', 0):.3f}")
                        print(f"         Q: {result.get('question', '')[:60]}...")
                        print(f"         A: {result.get('answer', '')[:60]}...")
                else:
                    print("   ⚠️  No retrieval results found")
            else:
                print(f"   ❌ Error: {response.status_code} - {response.text}")
        
        # Test 2: Check if we can build the FAQ index with OpenAI
        print(f"\n2️⃣ Testing FAQ index building with OpenAI...")
        
        try:
            # Try to trigger reindexing
            reindex_response = requests.post("http://localhost:8000/api/faqs/reindex")
            if reindex_response.status_code == 200:
                print("   ✅ FAQ reindexing successful - OpenAI embeddings working!")
            else:
                print(f"   ⚠️  Reindexing failed: {reindex_response.status_code} - {reindex_response.text}")
        except Exception as e:
            print(f"   ⚠️  Reindexing error: {e}")
        
        # Test 3: Test with more complex semantic queries
        print(f"\n3️⃣ Testing complex semantic queries...")
        
        complex_queries = [
            "من می‌خوام یه محصول بخرم",
            "کی می‌تونم با شما تماس بگیرم؟",
            "راه‌های ارتباط با پشتیبانی",
            "چطور می‌تونم کمک بگیرم؟"
        ]
        
        for i, query in enumerate(complex_queries, 1):
            print(f"\n🧪 Complex Test {i}: {query}")
            
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
                    best_match = retrieval_results[0]
                    print(f"   Best Match Score: {best_match.get('score', 0):.3f}")
                    print(f"   Best Match Q: {best_match.get('question', '')[:50]}...")
                else:
                    print("   ⚠️  No semantic matches found")
            else:
                print(f"   ❌ Error: {response.status_code}")
        
        print("\n" + "=" * 50)
        print("🎯 OPENAI INTEGRATION TEST COMPLETED!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server.")
        print("   Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_openai_integration()
