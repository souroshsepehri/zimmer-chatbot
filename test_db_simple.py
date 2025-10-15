#!/usr/bin/env python3
"""
Simple database test
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def test_database():
    """Test database connection"""
    print("🔍 Testing Database Connection")
    print("=" * 40)
    
    try:
        print("1. Testing imports...")
        from core.db import get_db
        from models.faq import FAQ
        print("   ✅ Imports successful")
        
        print("2. Testing database connection...")
        db = next(get_db())
        print("   ✅ Database connection successful")
        
        print("3. Testing FAQ query...")
        faqs = db.query(FAQ).all()
        print(f"   ✅ Found {len(faqs)} FAQs")
        
        if faqs:
            print("4. Sample FAQs:")
            for i, faq in enumerate(faqs[:3], 1):
                print(f"   {i}. {faq.question[:50]}...")
        
        db.close()
        print("   ✅ Database test completed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_chatbot():
    """Test chatbot functionality"""
    print("\n🤖 Testing Chatbot")
    print("=" * 40)
    
    try:
        print("1. Testing chatbot import...")
        from services.simple_chatbot import get_simple_chatbot
        print("   ✅ Chatbot import successful")
        
        print("2. Testing chatbot initialization...")
        chatbot = get_simple_chatbot()
        print("   ✅ Chatbot initialized")
        
        print("3. Testing FAQ loading...")
        success = chatbot.load_faqs_from_db()
        if success:
            print(f"   ✅ Loaded {len(chatbot.faqs)} FAQs")
        else:
            print("   ❌ Failed to load FAQs")
            return False
        
        print("4. Testing search...")
        results = chatbot.search_faqs("قیمت")
        print(f"   ✅ Search found {len(results)} results")
        
        if results:
            print(f"   Best match: {results[0]['question'][:50]}...")
        
        print("5. Testing answer generation...")
        result = chatbot.get_answer("قیمت")
        print(f"   ✅ Generated answer: {result['answer'][:50]}...")
        print(f"   Success: {result['success']}")
        print(f"   Source: {result['source']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Database and Chatbot Test")
    print("=" * 60)
    
    # Test database
    db_success = test_database()
    
    # Test chatbot
    chatbot_success = test_chatbot()
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Database: {'✅ Working' if db_success else '❌ Failed'}")
    print(f"Chatbot: {'✅ Working' if chatbot_success else '❌ Failed'}")
    
    if db_success and chatbot_success:
        print("\n🎉 Everything is working! The chatbot can read the database.")
        print("The issue might be with the server startup.")
    else:
        print("\n❌ There are issues with database or chatbot functionality.")
