#!/usr/bin/env python3
"""
Diagnostic script for chatbot issues
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def check_imports():
    """Check if all required modules can be imported"""
    print("🔍 Checking imports...")
    
    try:
        from core.db import get_db, engine, Base
        print("✅ Database modules imported")
    except Exception as e:
        print(f"❌ Database import failed: {e}")
        return False
    
    try:
        from models.faq import FAQ
        print("✅ FAQ model imported")
    except Exception as e:
        print(f"❌ FAQ model import failed: {e}")
        return False
    
    try:
        from services.retriever import get_faq_retriever
        print("✅ FAQ retriever imported")
    except Exception as e:
        print(f"❌ FAQ retriever import failed: {e}")
        return False
    
    try:
        from services.simple_retriever import simple_faq_retriever
        print("✅ Simple retriever imported")
    except Exception as e:
        print(f"❌ Simple retriever import failed: {e}")
        return False
    
    try:
        from services.url_agent import get_url_agent
        print("✅ URL agent imported")
    except Exception as e:
        print(f"❌ URL agent import failed: {e}")
        return False
    
    return True

def check_database():
    """Check database connection and data"""
    print("\n🔍 Checking database...")
    
    try:
        from core.db import get_db, engine, Base
        from models.faq import FAQ
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created/verified")
        
        # Test connection
        db = next(get_db())
        faq_count = db.query(FAQ).count()
        print(f"✅ Database connection successful - {faq_count} FAQs found")
        
        if faq_count > 0:
            # Show sample FAQ
            sample_faq = db.query(FAQ).first()
            print(f"✅ Sample FAQ: {sample_faq.question[:50]}...")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_retrievers():
    """Check retriever functionality"""
    print("\n🔍 Checking retrievers...")
    
    try:
        from services.simple_retriever import simple_faq_retriever
        from core.db import get_db
        
        db = next(get_db())
        simple_faq_retriever.load_faqs(db)
        
        # Test search
        results = simple_faq_retriever.search("test", top_k=3, threshold=0.1)
        print(f"✅ Simple retriever working - found {len(results)} results")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Simple retriever failed: {e}")
        return False

def check_config():
    """Check configuration"""
    print("\n🔍 Checking configuration...")
    
    try:
        from core.config import settings
        
        print(f"✅ Database URL: {settings.database_url}")
        print(f"✅ OpenAI Model: {settings.openai_model}")
        print(f"✅ Embedding Model: {settings.embedding_model}")
        print(f"✅ Retrieval Top K: {settings.retrieval_top_k}")
        print(f"✅ Retrieval Threshold: {settings.retrieval_threshold}")
        
        # Check API key
        if settings.openai_api_key:
            print("✅ OpenAI API key is set")
        else:
            print("⚠️ OpenAI API key is not set")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration check failed: {e}")
        return False

def main():
    """Run all diagnostic checks"""
    print("🚀 Chatbot Diagnostic Tool\n")
    
    all_good = True
    
    # Check imports
    if not check_imports():
        all_good = False
    
    # Check configuration
    if not check_config():
        all_good = False
    
    # Check database
    if not check_database():
        all_good = False
    
    # Check retrievers
    if not check_retrievers():
        all_good = False
    
    print("\n" + "="*50)
    if all_good:
        print("✅ All diagnostic checks passed!")
        print("\n📋 Your chatbot should work properly now.")
        print("🚀 Start the server with: python start_fixed_url_agent.py")
    else:
        print("❌ Some diagnostic checks failed.")
        print("\n🔧 Please fix the issues above before starting the server.")
        print("💡 You can also run: python test_database_fix.py")

if __name__ == "__main__":
    main()
