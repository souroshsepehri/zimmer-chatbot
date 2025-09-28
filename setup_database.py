#!/usr/bin/env python3
"""
Setup Database Tables
Creates all necessary database tables for the chatbot
"""

import os
import sys

def setup_database():
    """Setup database tables"""
    print("🗄️ SETTING UP DATABASE")
    print("=" * 40)
    
    # Set API key
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "your_openai_api_key_here")
    
    try:
        # Add backend to path
        sys.path.append('backend')
        
        print("1. Importing database modules...")
        from core.db import engine, Base
        from models.log import ChatLog
        from models.faq import FAQ
        print("✅ Database modules imported")
        
        print("2. Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created")
        
        print("3. Testing database connection...")
        from core.db import get_db
        db = next(get_db())
        
        # Test if tables exist
        from sqlalchemy import text
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
        tables = [row[0] for row in result.fetchall()]
        print(f"✅ Tables created: {tables}")
        
        print("4. Adding sample data...")
        # Add sample FAQ
        sample_faq = FAQ(
            question="سلام",
            answer="سلام وقت بخیر\nربات هوش مصنوعی زیمر هستم چگونه میتونم کمکتون کنم",
            category_id=1,
            is_active=True
        )
        db.add(sample_faq)
        db.commit()
        print("✅ Sample FAQ added")
        
        print("\n🎉 DATABASE SETUP COMPLETED!")
        print("=" * 40)
        print("✅ All tables created")
        print("✅ Sample data added")
        print("✅ Database ready for use")
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup error: {e}")
        return False

if __name__ == "__main__":
    setup_database()
