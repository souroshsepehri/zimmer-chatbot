#!/usr/bin/env python3
"""
Test the enhanced chatbot with intent detection via API
"""

import requests
import json
import time

def test_enhanced_chatbot():
    """Test the enhanced chatbot with intent detection"""
    print("🧠 Testing Enhanced Chatbot with Intent Detection")
    print("=" * 60)
    
    # Test queries that should show intent detection
    test_queries = [
        {
            "message": "قیمت",
            "expected_intent": "pricing",
            "description": "Simple pricing query"
        },
        {
            "message": "گارانتی",
            "expected_intent": "warranty", 
            "description": "Simple warranty query"
        },
        {
            "message": "سفارش",
            "expected_intent": "order",
            "description": "Simple order query"
        },
        {
            "message": "تماس",
            "expected_intent": "contact",
            "description": "Simple contact query"
        },
        {
            "message": "کمک",
            "expected_intent": "support",
            "description": "Simple support query"
        },
        {
            "message": "ساعت",
            "expected_intent": "hours",
            "description": "Simple hours query"
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
            # Test the regular chat endpoint (which now has enhanced intent detection)
            response = requests.post(f"{base_url}/chat", json={
                "message": test["message"],
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
                
                if data.get('context'):
                    print(f"    💡 Context: {data['context']}")
                
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
    print("📊 ENHANCED CHATBOT TEST SUMMARY")
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
    with open('enhanced_chatbot_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Detailed results saved to: enhanced_chatbot_test_results.json")
    
    return results

if __name__ == "__main__":
    print("🚀 Starting Enhanced Chatbot Tests")
    print("=" * 60)
    
    # Test enhanced chatbot
    test_enhanced_chatbot()
    
    print("\n✅ Tests completed!")
    print("=" * 60)
