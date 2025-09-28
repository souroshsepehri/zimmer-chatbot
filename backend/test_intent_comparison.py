#!/usr/bin/env python3
"""
Comparison test between old and new intent detection systems
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.intent import intent_detector as new_detector
from services.intent_old import intent_detector as old_detector
import json


def compare_intent_systems():
    """Compare old vs new intent detection systems"""
    
    test_messages = [
        "سلام، چطور می‌تونم سفارش بدم؟",
        "چطور هستید؟",
        "مشکل دارم با سفارشم",
        "قیمت محصولات چقدر است؟"
    ]
    
    print("🔄 Comparing Old vs New Intent Detection Systems")
    print("=" * 60)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. Testing: '{message}'")
        print("-" * 40)
        
        # Test old system
        try:
            old_result = old_detector.detect(message)
            print(f"   OLD System:")
            print(f"     Label: {old_result['label']}")
            print(f"     Confidence: {old_result['confidence']:.2f}")
        except Exception as e:
            print(f"   OLD System: ❌ Error: {e}")
        
        # Test new system
        try:
            new_result = new_detector.detect(message)
            print(f"   NEW System (LangGraph):")
            print(f"     Label: {new_result['label']}")
            print(f"     Confidence: {new_result['confidence']:.2f}")
            print(f"     Reasoning: {new_result.get('reasoning', 'N/A')}")
            print(f"     Graph Trace: {new_result.get('graph_trace', 'N/A')}")
        except Exception as e:
            print(f"   NEW System: ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Intent System Comparison Complete")


if __name__ == "__main__":
    try:
        compare_intent_systems()
    except Exception as e:
        print(f"❌ Comparison test failed: {e}")
        sys.exit(1)
