#!/usr/bin/env python3
"""
Debug intent detection in the enhanced chatbot
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def debug_intent_detection():
    """Debug the intent detection system"""
    print("🔍 Debugging Intent Detection")
    print("=" * 50)
    
    try:
        # Test 1: Direct intent detection
        print("1. Testing direct intent detection...")
        from services.smart_intent_detector import get_smart_intent_detector
        
        detector = get_smart_intent_detector()
        result = detector.detect_intent("قیمت")
        print(f"   Direct result: {result.intent.value} (confidence: {result.confidence:.2f})")
        print("   ✅ Direct intent detection works!")
        
        # Test 2: Simple chatbot
        print("\n2. Testing simple chatbot...")
        from services.simple_chatbot import get_simple_chatbot
        
        chatbot = get_simple_chatbot()
        result = chatbot.get_answer("قیمت")
        print(f"   Chatbot result keys: {list(result.keys())}")
        print(f"   Intent: {result.get('intent', 'NOT_FOUND')}")
        print(f"   Confidence: {result.get('confidence', 'NOT_FOUND')}")
        print(f"   Success: {result.get('success', 'NOT_FOUND')}")
        
        if result.get('intent') != 'unknown':
            print("   ✅ Simple chatbot intent detection works!")
        else:
            print("   ❌ Simple chatbot intent detection failed!")
        
        # Test 3: Check if the import is working
        print("\n3. Testing import...")
        try:
            from services.simple_chatbot import get_smart_intent_detector
            print("   ✅ Import works!")
        except Exception as e:
            print(f"   ❌ Import failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in debugging: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_chatbot_directly():
    """Test the simple chatbot directly"""
    print("\n🧪 Testing Simple Chatbot Directly")
    print("=" * 50)
    
    try:
        from services.simple_chatbot import get_simple_chatbot
        
        chatbot = get_simple_chatbot()
        
        test_queries = ["قیمت", "گارانتی", "سفارش"]
        
        for query in test_queries:
            print(f"\nTesting: '{query}'")
            result = chatbot.get_answer(query)
            
            print(f"  Answer: {result.get('answer', '')[:50]}...")
            print(f"  Intent: {result.get('intent', 'NOT_FOUND')}")
            print(f"  Confidence: {result.get('confidence', 'NOT_FOUND')}")
            print(f"  Success: {result.get('success', 'NOT_FOUND')}")
            print(f"  Source: {result.get('source', 'NOT_FOUND')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing simple chatbot: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Debugging Intent Detection")
    print("=" * 60)
    
    # Debug intent detection
    debug_success = debug_intent_detection()
    
    # Test simple chatbot directly
    test_success = test_simple_chatbot_directly()
    
    print("\n" + "=" * 60)
    print("📊 DEBUG SUMMARY")
    print("=" * 60)
    print(f"Intent Detection Debug: {'✅ Success' if debug_success else '❌ Failed'}")
    print(f"Simple Chatbot Test: {'✅ Success' if test_success else '❌ Failed'}")
    
    if debug_success and test_success:
        print("\n🎉 All debugging tests passed!")
    else:
        print("\n❌ Some debugging tests failed. Check the errors above.")
