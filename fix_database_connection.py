#!/usr/bin/env python3
"""
Fix database connection issue in API
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def fix_database_connection():
    """Fix the database connection issue"""
    print("🔧 Fixing Database Connection Issue")
    print("=" * 50)
    
    try:
        # Test the simple chatbot with database session
        from services.simple_chatbot import get_simple_chatbot
        from core.db import get_db
        
        print("1. Testing simple chatbot with database session...")
        
        # Get a database session
        db = next(get_db())
        
        # Get the chatbot
        chatbot = get_simple_chatbot()
        
        # Test loading FAQs
        print("2. Testing FAQ loading...")
        success = chatbot.load_faqs_from_db()
        if success:
            print(f"   ✅ Loaded {len(chatbot.faqs)} FAQs")
        else:
            print("   ❌ Failed to load FAQs")
            return False
        
        # Test search with database session
        print("3. Testing search with database session...")
        test_queries = ["قیمت", "گارانتی"]
        
        for query in test_queries:
            print(f"\n   Testing: '{query}'")
            
            # Test direct search
            results = chatbot.search_faqs(query)
            print(f"   Direct search found {len(results)} results")
            
            if results:
                print(f"   Best match: {results[0]['question'][:50]}... (score: {results[0]['score']:.2f})")
            
            # Test full answer generation
            result = chatbot.get_answer(query)
            print(f"   Full answer success: {result['success']}")
            print(f"   Source: {result['source']}")
            print(f"   Intent: {result.get('intent', 'Unknown')}")
            print(f"   Confidence: {result.get('confidence', 0)}")
        
        db.close()
        print("\n✅ Database connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error in database connection test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_with_database_session():
    """Test API with proper database session"""
    print("\n🔧 Testing API with Database Session")
    print("=" * 50)
    
    try:
        from services.simple_chatbot import get_simple_chatbot
        from core.db import get_db
        
        # Get database session
        db = next(get_db())
        
        # Get chatbot
        chatbot = get_simple_chatbot()
        
        # Load FAQs with database session
        success = chatbot.load_faqs_from_db()
        if not success:
            print("❌ Failed to load FAQs")
            return False
        
        print(f"✅ Loaded {len(chatbot.faqs)} FAQs")
        
        # Test queries
        test_queries = ["قیمت", "گارانتی", "سفارش", "تماس"]
        
        for query in test_queries:
            print(f"\nTesting: '{query}'")
            result = chatbot.get_answer(query)
            
            print(f"  Success: {result['success']}")
            print(f"  Source: {result['source']}")
            print(f"  Intent: {result.get('intent', 'Unknown')}")
            print(f"  Confidence: {result.get('confidence', 0)}")
            print(f"  Answer: {result['answer'][:50]}...")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error in API test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Database Connection Fix")
    print("=" * 60)
    
    # Fix database connection
    fix_success = fix_database_connection()
    
    # Test API with database session
    api_success = test_api_with_database_session()
    
    print("\n" + "=" * 60)
    print("📊 FIX SUMMARY")
    print("=" * 60)
    print(f"Database Connection: {'✅ Fixed' if fix_success else '❌ Failed'}")
    print(f"API Test: {'✅ Working' if api_success else '❌ Failed'}")
    
    if fix_success and api_success:
        print("\n🎉 Database connection is working correctly!")
        print("The issue might be in the API request handling.")
    else:
        print("\n❌ There are still issues with the database connection.")
