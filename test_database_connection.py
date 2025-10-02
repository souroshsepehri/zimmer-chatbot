#!/usr/bin/env python3
"""
Test database connection and setup
"""
import sys
import os
sys.path.append('backend')

def test_database():
    """Test database connection and setup"""
    print("🧪 Testing database connection...")
    
    try:
        # Import database components
        from backend.core.db import engine, Base, get_db
        from backend.core.config import settings
        from backend.models.log import ChatLog
        from backend.models.faq import FAQ
        
        print(f"✅ Database URL: {settings.database_url}")
        
        # Test engine connection
        with engine.connect() as conn:
            print("✅ Database engine connection successful")
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
        # Test database session
        db = next(get_db())
        print("✅ Database session created successfully")
        
        # Test inserting a record
        test_log = ChatLog(
            user_text="Test message",
            ai_text="Test response",
            intent="test",
            source="test",
            confidence=0.9,
            success=True
        )
        
        db.add(test_log)
        db.commit()
        print("✅ Test record inserted successfully")
        
        # Test querying
        logs = db.query(ChatLog).all()
        print(f"✅ Found {len(logs)} chat logs in database")
        
        db.close()
        print("✅ Database test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_database()
