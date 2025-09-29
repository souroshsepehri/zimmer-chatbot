#!/usr/bin/env python3
"""
Add sample data to the database
"""
import os
import sys
from pathlib import Path

def add_sample_data():
    """Add sample FAQ data to the database"""
    print("Adding sample data...")
    
    try:
        # Import database components
        from core.db import get_db, engine, Base
        from models.faq import FAQ
        from models.log import ChatLog
        
        # Create tables first
        Base.metadata.create_all(bind=engine)
        
        # Get database session
        db = next(get_db())
        
        # Check if data already exists
        existing_faqs = db.query(FAQ).count()
        if existing_faqs > 0:
            print(f"✅ Database already has {existing_faqs} FAQs")
            db.close()
            return True
        
        # Add sample FAQs
        sample_faqs = [
            {
                "question": "سلام، چطوری؟",
                "answer": "سلام! من خوبم، ممنون. چطور می‌تونم کمکتون کنم؟",
                "category": "greeting",
                "tags": "سلام, چطوری, احوالپرسی"
            },
            {
                "question": "ساعت چند است؟",
                "answer": "متأسفانه من به ساعت دسترسی ندارم. لطفاً از ساعت سیستم خودتون استفاده کنید.",
                "category": "time",
                "tags": "ساعت, زمان, وقت"
            },
            {
                "question": "آیا می‌توانید به من کمک کنید؟",
                "answer": "البته! من اینجا هستم تا به سؤالات شما پاسخ دهم. چه کمکی از دستم برمی‌آید؟",
                "category": "help",
                "tags": "کمک, سوال, پشتیبانی"
            },
            {
                "question": "چطور می‌تونم با شما صحبت کنم؟",
                "answer": "شما می‌تونید مستقیماً در این چت با من صحبت کنید. فقط پیام خودتون رو بنویسید و ارسال کنید.",
                "category": "communication",
                "tags": "صحبت, چت, ارتباط"
            },
            {
                "question": "ممنون",
                "answer": "خواهش می‌کنم! خوشحالم که تونستم کمکتون کنم. اگه سوال دیگه‌ای دارید، در خدمتم.",
                "category": "thanks",
                "tags": "ممنون, تشکر, قدردانی"
            }
        ]
        
        # Insert sample FAQs
        for faq_data in sample_faqs:
            faq = FAQ(
                question=faq_data["question"],
                answer=faq_data["answer"],
                category=faq_data["category"],
                tags=faq_data["tags"]
            )
            db.add(faq)
        
        db.commit()
        print(f"✅ Added {len(sample_faqs)} sample FAQs to database")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to add sample data: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    add_sample_data()
