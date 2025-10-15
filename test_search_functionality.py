#!/usr/bin/env python3
"""
Test search functionality
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_search_functionality():
    """Test the search functionality"""
    print("🔍 Testing Search Functionality")
    print("=" * 50)
    
    try:
        from services.simple_chatbot import get_simple_chatbot
        
        chatbot = get_simple_chatbot()
        
        # Test loading FAQs
        print("1. Testing FAQ loading...")
        success = chatbot.load_faqs_from_db()
        if success:
            print(f"   ✅ Loaded {len(chatbot.faqs)} FAQs")
        else:
            print("   ❌ Failed to load FAQs")
            return False
        
        # Test search functionality
        test_queries = ["قیمت", "گارانتی", "سفارش", "تماس"]
        
        print("\n2. Testing search functionality...")
        for query in test_queries:
            print(f"\n   Testing: '{query}'")
            results = chatbot.search_faqs(query)
            print(f"   Found {len(results)} results")
            
            if results:
                for i, result in enumerate(results[:3], 1):
                    print(f"     {i}. {result['question'][:50]}... (score: {result['score']:.2f})")
            else:
                print("     No results found")
        
        # Test full answer generation
        print("\n3. Testing full answer generation...")
        for query in test_queries:
            print(f"\n   Testing: '{query}'")
            result = chatbot.get_answer(query)
            print(f"   Success: {result['success']}")
            print(f"   Source: {result['source']}")
            print(f"   Answer: {result['answer'][:50]}...")
            if 'intent' in result:
                print(f"   Intent: {result['intent']}")
                print(f"   Confidence: {result['confidence']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing search: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_search_functionality()
