#!/usr/bin/env python3
"""
Test if the chatbot can read the database directly
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_database_reading():
    """Test if the chatbot can read the database"""
    print("🔍 Testing Database Reading")
    print("=" * 50)
    
    try:
        # Test 1: Direct database access
        print("1. Testing direct database access...")
        from core.db import get_db
        from models.faq import FAQ
        
        db = next(get_db())
        faqs = db.query(FAQ).all()
        print(f"   ✅ Found {len(faqs)} FAQs in database")
        
        if faqs:
            print(f"   Sample FAQ: {faqs[0].question[:50]}...")
        
        db.close()
        
        # Test 2: Simple chatbot database reading
        print("\n2. Testing simple chatbot database reading...")
        from services.simple_chatbot import get_simple_chatbot
        
        chatbot = get_simple_chatbot()
        success = chatbot.load_faqs_from_db()
        
        if success:
            print(f"   ✅ Chatbot loaded {len(chatbot.faqs)} FAQs")
            if chatbot.faqs:
                print(f"   Sample FAQ: {chatbot.faqs[0]['question'][:50]}...")
        else:
            print("   ❌ Chatbot failed to load FAQs")
        
        # Test 3: Test search functionality
        print("\n3. Testing search functionality...")
        if chatbot.faqs:
            results = chatbot.search_faqs("قیمت")
            print(f"   ✅ Search found {len(results)} results for 'قیمت'")
            if results:
                print(f"   Best match: {results[0]['question'][:50]}...")
                print(f"   Score: {results[0]['score']:.2f}")
        else:
            print("   ❌ No FAQs loaded, cannot test search")
        
        # Test 4: Test full answer generation
        print("\n4. Testing full answer generation...")
        if chatbot.faqs:
            result = chatbot.get_answer("قیمت")
            print(f"   ✅ Generated answer: {result['answer'][:50]}...")
            print(f"   Success: {result['success']}")
            print(f"   Source: {result['source']}")
            if 'intent' in result:
                print(f"   Intent: {result['intent']}")
                print(f"   Confidence: {result['confidence']}")
        else:
            print("   ❌ No FAQs loaded, cannot test answer generation")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing database reading: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_retriever():
    """Test the simple retriever"""
    print("\n🔍 Testing Simple Retriever")
    print("=" * 50)
    
    try:
        from services.simple_retriever import simple_faq_retriever
        from core.db import get_db
        
        db = next(get_db())
        
        # Load FAQs into retriever
        simple_faq_retriever.load_faqs(db)
        print(f"✅ Retriever loaded {len(simple_faq_retriever.faqs)} FAQs")
        
        # Test search
        results = simple_faq_retriever.search("قیمت", top_k=3, threshold=0.1)
        print(f"✅ Search found {len(results)} results")
        
        for i, result in enumerate(results[:3], 1):
            print(f"   {i}. {result['question'][:50]}... (score: {result['score']:.3f})")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error testing simple retriever: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Testing Database Reading")
    print("=" * 60)
    
    # Test database reading
    db_success = test_database_reading()
    
    # Test simple retriever
    retriever_success = test_simple_retriever()
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Database Reading: {'✅ Success' if db_success else '❌ Failed'}")
    print(f"Simple Retriever: {'✅ Success' if retriever_success else '❌ Failed'}")
    
    if db_success and retriever_success:
        print("\n🎉 Database reading is working correctly!")
        print("The issue might be with the server startup, not the database.")
    else:
        print("\n❌ Database reading has issues. Check the errors above.")
