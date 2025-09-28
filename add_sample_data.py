#!/usr/bin/env python3
"""
Add sample data to test dashboard statistics
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from core.db import get_db, engine
from models.faq import FAQ, Category
from models.log import ChatLog
from datetime import datetime, timedelta
import random

def add_sample_data():
    print("📊 Adding sample data for dashboard testing...")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Add sample category
        category = Category(
            name="عمومی",
            slug="general",
            created_at=datetime.now()
        )
        db.add(category)
        db.commit()
        db.refresh(category)
        print(f"✅ Added category: {category.name}")
        
        # Add sample FAQs
        sample_faqs = [
            {
                "question": "چطور می‌تونم سفارش بدم؟",
                "answer": "برای سفارش می‌تونید از طریق سایت یا تماس تلفنی اقدام کنید.",
                "category_id": category.id
            },
            {
                "question": "قیمت محصولات چقدر است؟",
                "answer": "قیمت‌ها در سایت به‌روزرسانی می‌شوند. برای اطلاع از آخرین قیمت‌ها، سایت را بررسی کنید.",
                "category_id": category.id
            },
            {
                "question": "چطور می‌تونم پشتیبانی بگیرم؟",
                "answer": "از طریق چت آنلاین، ایمیل یا تماس تلفنی می‌تونید با پشتیبانی در ارتباط باشید.",
                "category_id": category.id
            }
        ]
        
        for faq_data in sample_faqs:
            faq = FAQ(
                question=faq_data["question"],
                answer=faq_data["answer"],
                category_id=faq_data["category_id"],
                is_active=True,
                created_at=datetime.now()
            )
            db.add(faq)
        
        db.commit()
        print(f"✅ Added {len(sample_faqs)} FAQs")
        
        # Add sample chat logs
        sample_logs = [
            {
                "user_text": "سلام",
                "ai_text": "سلام! چطور می‌تونم کمکتون کنم؟",
                "intent": "smalltalk",
                "source": "faq",
                "success": True,
                "confidence": 0.9
            },
            {
                "user_text": "قیمت محصولات چقدر است؟",
                "ai_text": "قیمت‌ها در سایت به‌روزرسانی می‌شوند...",
                "intent": "sales",
                "source": "faq",
                "success": True,
                "confidence": 0.8
            },
            {
                "user_text": "مشکل دارم با سفارشم",
                "ai_text": "متأسفم که مشکل دارید. لطفاً با پشتیبانی تماس بگیرید.",
                "intent": "complaint",
                "source": "fallback",
                "success": False,
                "confidence": 0.7
            }
        ]
        
        # Add logs for today and yesterday
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        
        for i, log_data in enumerate(sample_logs):
            # Add some for today
            log = ChatLog(
                user_text=log_data["user_text"],
                ai_text=log_data["ai_text"],
                intent=log_data["intent"],
                source=log_data["source"],
                confidence=log_data["confidence"],
                success=log_data["success"],
                timestamp=today - timedelta(hours=i),
                notes='{"unanswered_in_db": false}' if log_data["success"] else '{"unanswered_in_db": true}'
            )
            db.add(log)
            
            # Add some for yesterday
            log_yesterday = ChatLog(
                user_text=log_data["user_text"] + " (دیروز)",
                ai_text=log_data["ai_text"],
                intent=log_data["intent"],
                source=log_data["source"],
                confidence=log_data["confidence"],
                success=log_data["success"],
                timestamp=yesterday - timedelta(hours=i),
                notes='{"unanswered_in_db": false}' if log_data["success"] else '{"unanswered_in_db": true}'
            )
            db.add(log_yesterday)
        
        db.commit()
        print(f"✅ Added {len(sample_logs) * 2} chat logs")
        
        # Show statistics
        total_faqs = db.query(FAQ).count()
        total_categories = db.query(Category).count()
        total_logs = db.query(ChatLog).count()
        successful_logs = db.query(ChatLog).filter(ChatLog.success == True).count()
        
        print("\n📈 Current Statistics:")
        print(f"  Total FAQs: {total_faqs}")
        print(f"  Total Categories: {total_categories}")
        print(f"  Total Chat Logs: {total_logs}")
        print(f"  Successful Logs: {successful_logs}")
        print(f"  Success Rate: {(successful_logs/total_logs*100):.1f}%" if total_logs > 0 else "  Success Rate: 0%")
        
    except Exception as e:
        print(f"❌ Error adding sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_sample_data()
