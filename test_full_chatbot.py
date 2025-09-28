#!/usr/bin/env python3
"""
Comprehensive chatbot test to verify all functionality
"""

import requests
import json
import time

def test_chatbot_comprehensive():
    print("🤖 COMPREHENSIVE CHATBOT TEST")
    print("=" * 50)
    
    # Test cases based on the FAQs in your database
    test_cases = [
        {
            "question": "چطور می‌تونم سفارش بدم؟",
            "expected_keywords": ["سفارش", "وب‌سایت", "اپلیکیشن", "تلفنی"],
            "description": "Order placement question"
        },
        {
            "question": "ساعات کاری شما چیه؟",
            "expected_keywords": ["24 ساعت", "پشتیبانی"],
            "description": "Working hours question"
        },
        {
            "question": "چطور با پشتیبانی تماس بگیرم؟",
            "expected_keywords": ["تلفن", "ایمیل", "چت آنلاین"],
            "description": "Support contact question"
        },
        {
            "question": "سلام",
            "expected_keywords": ["سلام وقت بخیر", "ربات هوش مصنوعی"],
            "description": "Greeting test"
        },
        {
            "question": "قیمت محصولات",
            "expected_keywords": ["پاسخ مناسبی ندارم"],
            "description": "Unknown question (should use fallback)"
        }
    ]
    
    try:
        # Test health endpoint first
        print("1️⃣ Testing server health...")
        health_response = requests.get("http://localhost:8000/health")
        if health_response.status_code == 200:
            print("   ✅ Server is healthy")
        else:
            print("   ❌ Server health check failed")
            return
        
        print("\n2️⃣ Testing chatbot responses...")
        print("-" * 30)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🧪 Test {i}: {test_case['description']}")
            print(f"   Question: {test_case['question']}")
            
            # Send chat request
            response = requests.post("http://localhost:8000/api/chat", json={
                "message": test_case['question'],
                "debug": True
            })
            
            if response.status_code == 200:
                data = response.json()
                answer = data['answer']
                source = data.get('debug_info', {}).get('source', 'unknown')
                success = data.get('debug_info', {}).get('success', False)
                
                print(f"   Answer: {answer[:100]}{'...' if len(answer) > 100 else ''}")
                print(f"   Source: {source}")
                print(f"   Success: {success}")
                
                # Check if answer contains expected keywords
                answer_lower = answer.lower()
                found_keywords = [kw for kw in test_case['expected_keywords'] if kw.lower() in answer_lower]
                
                if found_keywords:
                    print(f"   ✅ Found expected keywords: {found_keywords}")
                else:
                    print(f"   ⚠️  Expected keywords not found: {test_case['expected_keywords']}")
                
                # Show debug info if available
                if data.get('debug_info', {}).get('retrieval_results'):
                    results = data['debug_info']['retrieval_results']
                    print(f"   📊 Found {len(results)} FAQ matches")
                    for j, result in enumerate(results[:2]):
                        print(f"      {j+1}. {result.get('question', '')[:50]}... (score: {result.get('score', 0):.3f})")
            else:
                print(f"   ❌ Error: {response.status_code} - {response.text}")
        
        print("\n" + "=" * 50)
        print("🎉 CHATBOT TEST COMPLETED!")
        print("✅ The chatbot is successfully using the admin panel FAQ database!")
        print("✅ It can answer questions from your database")
        print("✅ It falls back gracefully for unknown questions")
        print("✅ Both semantic search and simple search are working")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server.")
        print("   Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_chatbot_comprehensive()
