#!/usr/bin/env python3
"""
Test script for the new Enhanced Intent Detection System
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.intent import intent_detector
import json


def test_intent_detection():
    """Test the Enhanced intent detection system"""
    
    test_messages = [
        "سلام، چطور می‌تونم سفارش بدم؟",
        "چطور هستید؟",
        "مشکل دارم با سفارشم",
        "قیمت محصولات چقدر است؟",
        "چطور می‌تونم پشتیبانی بگیرم؟",
        "هوا چطوره؟",
        "ساعت چند است؟",
        "چطور می‌تونم حساب کاربری بسازم؟"
    ]
    
    print("🧪 Testing Enhanced Intent Detection System")
    print("=" * 50)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. Testing: '{message}'")
        print("-" * 30)
        
        try:
            result = intent_detector.detect(message)
            
            print(f"   Label: {result['label']}")
            print(f"   Confidence: {result['confidence']:.2f}")
            print(f"   Reasoning: {result.get('reasoning', 'N/A')}")
            print(f"   Graph Trace: {result.get('graph_trace', 'N/A')}")
            print(f"   Enhanced: {result.get('enhanced', 'N/A')}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Enhanced Intent Detection Test Complete")


def test_pipeline_structure():
    """Test the pipeline structure and components"""
    print("\n🔍 Testing Pipeline Structure")
    print("-" * 30)
    
    try:
        # Test if the detector is properly initialized
        detector = intent_detector
        print(f"   Detector initialized: ✅")
        print(f"   Detector type: {type(detector)}")
        
        # Test intent labels
        print(f"   Intent labels: {detector.intent_labels}")
        
        # Test a simple message through the pipeline
        test_message = "سلام"
        result = detector.detect(test_message)
        print(f"   Pipeline execution: ✅")
        print(f"   Result keys: {list(result.keys())}")
        
        # Test individual pipeline steps
        analysis_result = detector._analyze_message(test_message)
        print(f"   Analysis step: ✅")
        
        validation_result = detector._validate_intent(analysis_result)
        print(f"   Validation step: ✅")
        
        enhanced_result = detector._enhance_confidence(validation_result, test_message)
        print(f"   Enhancement step: ✅")
        
    except Exception as e:
        print(f"   ❌ Pipeline structure error: {e}")


if __name__ == "__main__":
    try:
        test_intent_detection()
        test_pipeline_structure()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
