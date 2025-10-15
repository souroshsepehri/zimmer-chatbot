#!/usr/bin/env python3
"""
Add missing FAQs to improve chatbot coverage
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def add_missing_faqs():
    """Add missing FAQs to improve chatbot coverage"""
    print("🔄 Adding missing FAQs...")
    
    try:
        from core.db import get_db, engine, Base
        from models.faq import FAQ, Category
        
        # Get database session
        db = next(get_db())
        
        # Get or create categories
        general_category = db.query(Category).filter(Category.name == "عمومی").first()
        if not general_category:
            general_category = Category(name="عمومی", slug="general")
            db.add(general_category)
            db.commit()
            db.refresh(general_category)
        
        pricing_category = db.query(Category).filter(Category.name == "قیمت‌گذاری").first()
        if not pricing_category:
            pricing_category = Category(name="قیمت‌گذاری", slug="pricing")
            db.add(pricing_category)
            db.commit()
            db.refresh(pricing_category)
        
        warranty_category = db.query(Category).filter(Category.name == "گارانتی").first()
        if not warranty_category:
            warranty_category = Category(name="گارانتی", slug="warranty")
            db.add(warranty_category)
            db.commit()
            db.refresh(warranty_category)
        
        # Additional FAQs to add
        additional_faqs = [
            {
                "question": "قیمت محصولات شما چقدر است؟",
                "answer": "قیمت‌های ما رقابتی و مناسب است. برای اطلاع از قیمت دقیق محصولات، می‌تونید با پشتیبانی تماس بگیرید یا در وب‌سایت ما قیمت‌ها را مشاهده کنید.",
                "category": pricing_category
            },
            {
                "question": "آیا گارانتی دارید؟",
                "answer": "بله، تمام محصولات ما دارای گارانتی معتبر هستند. مدت گارانتی بسته به نوع محصول متفاوت است. برای جزئیات بیشتر با پشتیبانی تماس بگیرید.",
                "category": warranty_category
            },
            {
                "question": "ساعات کاری شما چطور است؟",
                "answer": "ما 24 ساعت شبانه‌روز در خدمت شما هستیم. تیم پشتیبانی ما همیشه آماده پاسخگویی به سؤالات شما است.",
                "category": general_category
            },
            {
                "question": "چطور می‌تونم قیمت محصولات رو ببینم؟",
                "answer": "شما می‌تونید قیمت محصولات را در وب‌سایت ما مشاهده کنید یا با پشتیبانی تماس بگیرید تا قیمت دقیق را دریافت کنید.",
                "category": pricing_category
            },
            {
                "question": "گارانتی محصولات چقدر طول می‌کشه؟",
                "answer": "مدت گارانتی بسته به نوع محصول متفاوت است. معمولاً بین 6 ماه تا 2 سال گارانتی داریم. برای اطلاعات دقیق با پشتیبانی تماس بگیرید.",
                "category": warranty_category
            }
        ]
        
        # Check which FAQs already exist
        existing_questions = {faq.question for faq in db.query(FAQ).all()}
        
        added_count = 0
        for faq_data in additional_faqs:
            if faq_data["question"] not in existing_questions:
                faq = FAQ(
                    question=faq_data["question"],
                    answer=faq_data["answer"],
                    category_id=faq_data["category"].id,
                    is_active=True
                )
                db.add(faq)
                added_count += 1
                print(f"✅ Added: {faq_data['question'][:50]}...")
            else:
                print(f"⏭️  Skipped (already exists): {faq_data['question'][:50]}...")
        
        db.commit()
        db.close()
        
        print(f"\n🎉 Successfully added {added_count} new FAQs")
        
        # Show final stats
        db = next(get_db())
        total_faqs = db.query(FAQ).count()
        total_categories = db.query(Category).count()
        print(f"📊 Total FAQs in database: {total_faqs}")
        print(f"📊 Total categories: {total_categories}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error adding FAQs: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = add_missing_faqs()
    if success:
        print("\n🎉 FAQ addition completed successfully!")
        print("🚀 The chatbot should now have better coverage.")
    else:
        print("\n💥 FAQ addition failed. Please check the errors above.")
