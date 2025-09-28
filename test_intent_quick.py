#!/usr/bin/env python3
"""
Quick test for intent system
"""

def test_intent():
    try:
        from services.intent import intent_detector
        print("✅ Intent system loaded")
        
        result = intent_detector.detect("سلام")
        print(f"✅ Test result: {result['label']} (confidence: {result['confidence']:.2f})")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_intent()
