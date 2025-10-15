#!/usr/bin/env python3
"""
Test Smart Chatbot with Intent Detection
"""

import requests
import json
import time

def test_smart_chatbot():
    """Test the smart chatbot with various queries"""
    print("🧠 Testing Smart Chatbot with Intent Detection")
    print("=" * 60)
    
    # Test queries with different intents
    test_queries = [
        {
            "message": "سلام",
            "expected_intent": "greeting",
            "description": "Greeting test"
        },
        {
            "message": "قیمت محصولات شما چقدر است؟",
            "expected_intent": "pricing",
            "description": "Pricing question"
        },
        {
            "message": "گارانتی دارید؟",
            "expected_intent": "warranty",
            "description": "Warranty question"
        },
        {
            "message": "چطور سفارش بدم؟",
            "expected_intent": "order",
            "description": "Order question"
        },
        {
            "message": "ساعات کاری شما چیه؟",
            "expected_intent": "hours",
            "description": "Working hours question"
        },
        {
            "message": "چطور می‌تونم با شما تماس بگیرم؟",
            "expected_intent": "contact",
            "description": "Contact question"
        },
        {
            "message": "کمک می‌خوام",
            "expected_intent": "support",
            "description": "Support request"
        },
        {
            "message": "محصولات شما چه ویژگی‌هایی دارن؟",
            "expected_intent": "product_info",
            "description": "Product information question"
        }
    ]
    
    base_url = "http://localhost:8002/api"
    
    print(f"🌐 Testing against: {base_url}")
    print()
    
    results = []
    
    for i, test in enumerate(test_queries, 1):
        print(f"{i:2d}. Testing: '{test['message']}'")
        print(f"    Expected Intent: {test['expected_intent']}")
        print(f"    Description: {test['description']}")
        
        try:
            # Test smart chat endpoint
            response = requests.post(f"{base_url}/smart-chat", json={
                "message": test["message"],
                "include_explanation": True,
                "debug": True
            }, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"    ✅ Status: {response.status_code}")
                print(f"    🎯 Detected Intent: {data.get('intent', 'unknown')}")
                print(f"    📊 Confidence: {data.get('confidence', 0):.2f}")
                print(f"    🔍 Source: {data.get('source', 'unknown')}")
                print(f"    ✅ Success: {data.get('success', False)}")
                print(f"    📝 Answer: {data.get('answer', '')[:100]}...")
                
                if data.get('intent_match'):
                    print(f"    🎯 Intent Match: ✅")
                else:
                    print(f"    🎯 Intent Match: ❌")
                
                if data.get('explanation'):
                    print(f"    💡 Explanation: {data['explanation']}")
                
                # Check if intent matches expected
                intent_match = data.get('intent') == test['expected_intent']
                if intent_match:
                    print(f"    ✅ Intent Correct!")
                else:
                    print(f"    ❌ Intent Mismatch! Expected: {test['expected_intent']}, Got: {data.get('intent')}")
                
                results.append({
                    "query": test["message"],
                    "expected_intent": test["expected_intent"],
                    "detected_intent": data.get('intent'),
                    "confidence": data.get('confidence', 0),
                    "success": data.get('success', False),
                    "intent_correct": intent_match,
                    "answer_length": len(data.get('answer', ''))
                })
                
            else:
                print(f"    ❌ Status: {response.status_code}")
                print(f"    Error: {response.text}")
                results.append({
                    "query": test["message"],
                    "expected_intent": test["expected_intent"],
                    "detected_intent": "error",
                    "confidence": 0,
                    "success": False,
                    "intent_correct": False,
                    "answer_length": 0
                })
        
        except requests.exceptions.RequestException as e:
            print(f"    ❌ Request Error: {e}")
            results.append({
                "query": test["message"],
                "expected_intent": test["expected_intent"],
                "detected_intent": "error",
                "confidence": 0,
                "success": False,
                "intent_correct": False,
                "answer_length": 0
            })
        
        except Exception as e:
            print(f"    ❌ Error: {e}")
            results.append({
                "query": test["message"],
                "expected_intent": test["expected_intent"],
                "detected_intent": "error",
                "confidence": 0,
                "success": False,
                "intent_correct": False,
                "answer_length": 0
            })
        
        print()
        time.sleep(0.5)  # Small delay between requests
    
    # Summary
    print("=" * 60)
    print("📊 SMART CHATBOT TEST SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    successful_requests = sum(1 for r in results if r['detected_intent'] != 'error')
    correct_intents = sum(1 for r in results if r['intent_correct'])
    successful_answers = sum(1 for r in results if r['success'])
    
    print(f"Total Tests: {total_tests}")
    print(f"Successful Requests: {successful_requests}/{total_tests} ({successful_requests/total_tests*100:.1f}%)")
    print(f"Correct Intent Detection: {correct_intents}/{total_tests} ({correct_intents/total_tests*100:.1f}%)")
    print(f"Successful Answers: {successful_answers}/{total_tests} ({successful_answers/total_tests*100:.1f}%)")
    
    # Intent accuracy
    if successful_requests > 0:
        intent_accuracy = correct_intents / successful_requests * 100
        print(f"Intent Detection Accuracy: {intent_accuracy:.1f}%")
    
    # Average confidence
    confidences = [r['confidence'] for r in results if r['confidence'] > 0]
    if confidences:
        avg_confidence = sum(confidences) / len(confidences)
        print(f"Average Confidence: {avg_confidence:.2f}")
    
    # Save results
    with open('smart_chatbot_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Detailed results saved to: smart_chatbot_test_results.json")
    
    return results

def test_intent_detection():
    """Test intent detection separately"""
    print("\n🎯 Testing Intent Detection")
    print("=" * 40)
    
    base_url = "http://localhost:8002/api"
    
    test_messages = [
        "قیمت",
        "گارانتی",
        "سفارش",
        "تماس",
        "کمک",
        "ساعت",
        "محصول"
    ]
    
    for message in test_messages:
        try:
            response = requests.post(f"{base_url}/smart-chat/test-intent", json={
                "message": message
            }, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print(f"'{message}' → {data['intent']} (confidence: {data['confidence']:.2f})")
            else:
                print(f"'{message}' → Error: {response.status_code}")
        
        except Exception as e:
            print(f"'{message}' → Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Smart Chatbot Tests")
    print("=" * 60)
    
    # Test intent detection
    test_intent_detection()
    
    # Test smart chatbot
    test_smart_chatbot()
    
    print("\n✅ Tests completed!")
    print("=" * 60)
