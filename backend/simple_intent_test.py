#!/usr/bin/env python3
"""
Simple test for the enhanced intent detection system
"""

try:
    from services.intent import intent_detector
    print("✅ Import successful")
    
    # Test a simple message
    result = intent_detector.detect("سلام")
    print(f"✅ Test result: {result}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
