#!/usr/bin/env python3
"""
Test if database has data
"""
import sys
import os

def test_database_data():
    """Test if database has FAQ data"""
    print("Testing database data...")
    
    try:
        from core.db import get_db, engine, Base
        from models.faq import FAQ
        from models.log import ChatLog
        
        # Create tables first
        Base.metadata.create_all(bind=engine)
        
        # Get database session
        db = next(get_db())
        
        # Check FAQs
        faq_count = db.query(FAQ).count()
        print(f"FAQ count: {faq_count}")
        
        if faq_count > 0:
            faqs = db.query(FAQ).limit(3).all()
            for faq in faqs:
                print(f"FAQ: {faq.question[:50]}... -> {faq.answer[:50]}...")
        else:
            print("No FAQs found in database")
        
        # Check logs
        log_count = db.query(ChatLog).count()
        print(f"Chat log count: {log_count}")
        
        db.close()
        return faq_count > 0
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_database_data()
