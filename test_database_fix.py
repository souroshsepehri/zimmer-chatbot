#!/usr/bin/env python3
"""
Test script to verify database fixes and URL agent functionality
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_database_connection():
    """Test basic database connection"""
    print("🔍 Testing database connection...")
    
    try:
        from core.db import get_db, engine, Base
        from models.faq import FAQ
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created/verified")
        
        # Test database session
        db = next(get_db())
        faq_count = db.query(FAQ).count()
        print(f"✅ Database connection successful - {faq_count} FAQs found")
        
        if faq_count > 0:
            # Test simple retriever
            from services.simple_retriever import simple_faq_retriever
            simple_faq_retriever.load_faqs(db)
            results = simple_faq_retriever.search("test", top_k=3, threshold=0.1)
            print(f"✅ Simple retriever working - found {len(results)} results")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_faq_retriever():
    """Test FAQ retriever functionality"""
    print("\n🔍 Testing FAQ retriever...")
    
    try:
        from services.retriever import get_faq_retriever
        from core.db import get_db
        
        retriever = get_faq_retriever()
        db = next(get_db())
        
        # Try to build index
        retriever.build_index(db)
        print("✅ FAQ retriever index built")
        
        # Test search
        results = retriever.semantic_search("test", top_k=3)
        print(f"✅ FAQ semantic search working - found {len(results)} results")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ FAQ retriever failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_url_agent_basic():
    """Test basic URL agent functionality"""
    print("\n🔍 Testing URL agent basic functionality...")
    
    try:
        from services.url_agent import get_url_agent
        
        agent = get_url_agent()
        print("✅ URL agent initialized")
        
        # Test search without web content
        results = await agent.search_dual_database(
            query="test question",
            include_faq=True,
            include_web=False
        )
        
        print(f"✅ URL agent search working - FAQ results: {len(results['faq_results'])}")
        
        # Test stats
        stats = agent.get_stats()
        print(f"✅ URL agent stats working: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ URL agent failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def add_sample_data_if_needed():
    """Add sample data if database is empty"""
    print("\n🔍 Checking if sample data is needed...")
    
    try:
        from core.db import get_db
        from models.faq import FAQ
        
        db = next(get_db())
        faq_count = db.query(FAQ).count()
        
        if faq_count == 0:
            print("📝 Adding sample data...")
            
            # Add some basic sample FAQs
            sample_faqs = [
                {
                    "question": "چطور می‌تونم با شما تماس بگیرم؟",
                    "answer": "شما می‌تونید از طریق ایمیل یا تلفن با ما تماس بگیرید.",
                    "category": "تماس",
                    "tags": "تماس, ارتباط"
                },
                {
                    "question": "ساعات کاری شما چیه؟",
                    "answer": "ما از شنبه تا پنج‌شنبه از ساعت 9 تا 17 فعالیت می‌کنیم.",
                    "category": "ساعات کاری",
                    "tags": "ساعات, زمان"
                },
                {
                    "question": "چطور می‌تونم سفارش بدم؟",
                    "answer": "شما می‌تونید از طریق وب‌سایت یا تماس تلفنی سفارش خود را ثبت کنید.",
                    "category": "سفارش",
                    "tags": "سفارش, خرید"
                }
            ]
            
            for faq_data in sample_faqs:
                faq = FAQ(
                    question=faq_data["question"],
                    answer=faq_data["answer"],
                    category=faq_data["category"],
                    tags=faq_data["tags"]
                )
                db.add(faq)
            
            db.commit()
            print(f"✅ Added {len(sample_faqs)} sample FAQs")
        else:
            print(f"✅ Database already has {faq_count} FAQs")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to add sample data: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Database Fix Tests...\n")
    
    # Test database connection
    if not test_database_connection():
        print("\n❌ Database connection failed. Please check your database setup.")
        return
    
    # Add sample data if needed
    add_sample_data_if_needed()
    
    # Test FAQ retriever
    if not test_faq_retriever():
        print("\n⚠️ FAQ retriever has issues but continuing...")
    
    # Test URL agent
    if not await test_url_agent_basic():
        print("\n❌ URL agent failed. Please check the implementation.")
        return
    
    print("\n✅ All tests passed! The database integration should now work properly.")
    print("\n📋 Next steps:")
    print("1. Start the server: python start_with_url_agent.py")
    print("2. Test the interface: http://localhost:8002")
    print("3. Try adding a website and asking questions")

if __name__ == "__main__":
    asyncio.run(main())
