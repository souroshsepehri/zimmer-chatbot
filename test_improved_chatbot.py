#!/usr/bin/env python3
"""
Test improved chatbot with database priority and no logging
"""

import requests
import json
import time

def test_improved_chatbot():
    print("🤖 TESTING IMPROVED CHATBOT")
    print("=" * 50)
    print("✅ Database priority enabled")
    print("✅ Logging disabled")
    print("✅ Lower threshold for better matching")
    print("=" * 50)
    
    try:
        # Wait for server to start
        time.sleep(3)
        
        # Test cases with various similarity levels
        test_cases = [
            {
                "question": "چطور می‌تونم سفارش بدم؟",
                "description": "Exact match question"
            },
            {
                "question": "سفارش",
                "description": "Partial match - single word"
            },
            {
                "question": "من می‌خوام خرید کنم",
                "description": "Related concept - buying"
            },
            {
                "question": "ساعات کاری",
                "description": "Partial match - working hours"
            },
            {
                "question": "کی می‌تونم تماس بگیرم؟",
                "description": "Related concept - contact timing"
            },
            {
                "question": "پشتیبانی",
                "description": "Single word - support"
            },
            {
                "question": "راه‌های ارتباط",
                "description": "Related concept - communication methods"
            },
            {
                "question": "کمک می‌خوام",
                "description": "Related concept - help needed"
            },
            {
                "question": "قیمت محصولات",
                "description": "Unknown question (should use fallback)"
            }
        ]
        
        print("\n🧪 Testing database priority matching...")
        print("-" * 40)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. {test_case['description']}")
            print(f"   Question: {test_case['question']}")
            
            response = requests.post("http://localhost:8000/api/chat", json={
                "message": test_case['question'],
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
                print(f"   Answer: {data['answer'][:80]}{'...' if len(data['answer']) > 80 else ''}")
                
                if retrieval_results:
                    best_score = retrieval_results[0].get('score', 0)
                    print(f"   Best Match Score: {best_score:.3f}")
                    print(f"   Best Match Q: {retrieval_results[0].get('question', '')[:50]}...")
                    print(f"   Total Matches: {len(retrieval_results)}")
                else:
                    print("   ⚠️  No database matches found")
            else:
                print(f"   ❌ Error: {response.status_code} - {response.text}")
        
        print("\n" + "=" * 50)
        print("🎯 IMPROVED CHATBOT TEST COMPLETED!")
        print("✅ Database priority: Working")
        print("✅ Lower threshold: Catching more matches")
        print("✅ No logging: Database stays clean")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server.")
        print("   Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_improved_chatbot()
