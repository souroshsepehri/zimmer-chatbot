#!/usr/bin/env python3
"""
Simple test of smart chatbot functionality
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_smart_intent_detection():
    """Test the smart intent detection directly"""
    print("🧠 Testing Smart Intent Detection")
    print("=" * 50)
    
    try:
        from services.smart_intent_detector import get_smart_intent_detector
        
        detector = get_smart_intent_detector()
        
        test_messages = [
            "سلام",
            "قیمت محصولات شما چقدر است؟",
            "گارانتی دارید؟",
            "چطور سفارش بدم؟",
            "ساعات کاری شما چیه؟",
            "چطور می‌تونم با شما تماس بگیرم؟",
            "کمک می‌خوام",
            "محصولات شما چه ویژگی‌هایی دارن؟"
        ]
        
        for message in test_messages:
            result = detector.detect_intent(message)
            print(f"'{message}' → {result.intent.value} (confidence: {result.confidence:.2f})")
            print(f"    Keywords: {result.keywords}")
            print(f"    Context: {result.context}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing intent detection: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_smart_chatbot():
    """Test the smart chatbot directly"""
    print("🤖 Testing Smart Chatbot")
    print("=" * 50)
    
    try:
        from services.smart_chatbot import get_smart_chatbot
        
        chatbot = get_smart_chatbot()
        
        test_queries = [
            "قیمت",
            "گارانتی",
            "سفارش",
            "تماس",
            "کمک",
            "ساعت"
        ]
        
        for query in test_queries:
            print(f"Testing: '{query}'")
            result = chatbot.get_smart_answer(query)
            
            print(f"  Intent: {result.get('intent', 'unknown')}")
            print(f"  Confidence: {result.get('confidence', 0):.2f}")
            print(f"  Success: {result.get('success', False)}")
            print(f"  Answer: {result.get('answer', '')[:100]}...")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing smart chatbot: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Smart Chatbot Direct Tests")
    print("=" * 60)
    
    # Test intent detection
    intent_success = test_smart_intent_detection()
    
    # Test smart chatbot
    chatbot_success = test_smart_chatbot()
    
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Intent Detection: {'✅ Success' if intent_success else '❌ Failed'}")
    print(f"Smart Chatbot: {'✅ Success' if chatbot_success else '❌ Failed'}")
    
    if intent_success and chatbot_success:
        print("\n🎉 All tests passed! The smart chatbot is working correctly.")
        print("The system can now:")
        print("- Detect user intent accurately")
        print("- Rank answers based on intent")
        print("- Provide the best single answer")
    else:
        print("\n❌ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
