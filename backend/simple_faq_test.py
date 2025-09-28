#!/usr/bin/env python3
"""
Simple FAQ test without OpenAI API key
"""

from sqlalchemy.orm import Session
from core.db import engine, Base
from models.faq import FAQ, Category

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Create a session
db = Session(engine)

try:
    # Check if there are any FAQs in the database
    faq_count = db.query(FAQ).filter(FAQ.is_active == True).count()
    print(f"📊 Found {faq_count} active FAQs in database")
    
    if faq_count == 0:
        print("❌ No active FAQs found. Please add some FAQs through the admin panel first.")
    else:
        # List all FAQs
        faqs = db.query(FAQ).filter(FAQ.is_active == True).all()
        print("\n📋 Active FAQs:")
        for faq in faqs:
            category_name = faq.category.name if faq.category else "بدون دسته"
            print(f"  - {faq.question[:50]}... (دسته: {category_name})")
            print(f"    پاسخ: {faq.answer[:100]}...")
            print()
        
        print("✅ Database has FAQ data ready for chatbot!")
        print("💡 To enable semantic search, you need to:")
        print("   1. Set your OpenAI API key in backend/.env file")
        print("   2. Run: python build_faq_index.py")
            
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
