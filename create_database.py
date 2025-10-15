#!/usr/bin/env python3
"""
Create and populate the database
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def create_database():
    """Create and populate the database"""
    print("🔧 Creating and Populating Database")
    print("=" * 50)
    
    try:
        from core.db import engine, Base
        from models.faq import FAQ, Category
        from sqlalchemy.orm import sessionmaker
        
        print("1. Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("   ✅ Database tables created")
        
        print("2. Creating database session...")
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        print("3. Creating categories...")
        categories = {
            "عمومی": Category(name="عمومی", slug="general"),
            "قیمت‌گذاری": Category(name="قیمت‌گذاری", slug="pricing"),
            "گارانتی": Category(name="گارانتی", slug="warranty"),
            "سفارشات": Category(name="سفارشات", slug="orders"),
            "پشتیبانی": Category(name="پشتیبانی", slug="support"),
            "بازگشت کالا": Category(name="بازگشت کالا", slug="returns")
        }
        
        for category in categories.values():
            db.add(category)
        db.commit()
        print("   ✅ Categories created")
        
        print("4. Adding FAQs...")
        faqs_data = [
            {
                "question": "چطور می‌تونم سفارش بدم؟",
                "answer": "برای سفارش دادن می‌تونید از طریق وب‌سایت ما اقدام کنید. ابتدا محصول مورد نظرتون رو انتخاب کنید، سپس به سبد خرید اضافه کنید و مراحل پرداخت رو تکمیل کنید.",
                "category": "سفارشات"
            },
            {
                "question": "چرا سفارشم هنوز ارسال نشده؟",
                "answer": "زمان ارسال سفارشات معمولاً 1-3 روز کاری طول می‌کشه. اگر بیشتر از این زمان گذشته، با پشتیبانی تماس بگیرید.",
                "category": "سفارشات"
            },
            {
                "question": "آیا امکان بازگشت کالا وجود داره؟",
                "answer": "بله، شما 7 روز فرصت دارید تا کالای خریداری شده رو برگردونید. کالا باید در شرایط اولیه باشه.",
                "category": "بازگشت کالا"
            },
            {
                "question": "اگر محصول معیوب باشه چی کار کنم؟",
                "answer": "اگر محصول معیوب باشه، بلافاصله با پشتیبانی تماس بگیرید. ما محصول معیوب رو تعویض می‌کنیم.",
                "category": "پشتیبانی"
            },
            {
                "question": "چطور می‌تونم با پشتیبانی تماس بگیرم؟",
                "answer": "شما می‌تونید از طریق تلفن 021-12345678، ایمیل support@example.com یا چت آنلاین در وب‌سایت با ما تماس بگیرید.",
                "category": "پشتیبانی"
            },
            {
                "question": "قیمت محصولات شما چقدر است؟",
                "answer": "قیمت‌های ما رقابتی و مناسب است. برای اطلاع از قیمت دقیق محصولات، می‌تونید با پشتیبانی تماس بگیرید یا در وب‌سایت ما قیمت‌ها را مشاهده کنید.",
                "category": "قیمت‌گذاری"
            },
            {
                "question": "آیا گارانتی دارید؟",
                "answer": "بله، تمام محصولات ما دارای گارانتی معتبر هستند. مدت گارانتی بسته به نوع محصول متفاوت است. برای جزئیات بیشتر با پشتیبانی تماس بگیرید.",
                "category": "گارانتی"
            },
            {
                "question": "ساعات کاری شما چطور است؟",
                "answer": "ما 24 ساعت شبانه‌روز در خدمت شما هستیم. تیم پشتیبانی ما همیشه آماده پاسخگویی به سؤالات شما است.",
                "category": "عمومی"
            },
            {
                "question": "چطور می‌تونم قیمت محصولات رو ببینم؟",
                "answer": "شما می‌تونید قیمت محصولات را در وب‌سایت ما مشاهده کنید یا با پشتیبانی تماس بگیرید.",
                "category": "قیمت‌گذاری"
            },
            {
                "question": "گارانتی محصولات چقدر طول می‌کشه؟",
                "answer": "مدت گارانتی بسته به نوع محصول متفاوت است. معمولاً بین 1 تا 3 سال گارانتی داریم.",
                "category": "گارانتی"
            },
            {
                "question": "سلام",
                "answer": "سلام وقت بخیر! ربات هوشمند زیمر هستم. چطور می‌تونم کمکتون کنم؟",
                "category": "عمومی"
            },
            {
                "question": "قیمت",
                "answer": "قیمت‌های ما رقابتی و مناسب است. برای اطلاع از قیمت دقیق محصولات، می‌تونید با پشتیبانی تماس بگیرید یا در وب‌سایت ما قیمت‌ها را مشاهده کنید.",
                "category": "قیمت‌گذاری"
            },
            {
                "question": "گارانتی",
                "answer": "بله، تمام محصولات ما دارای گارانتی معتبر هستند. مدت گارانتی بسته به نوع محصول متفاوت است. برای جزئیات بیشتر با پشتیبانی تماس بگیرید.",
                "category": "گارانتی"
            },
            {
                "question": "هزینه",
                "answer": "قیمت‌های ما رقابتی و مناسب است. برای اطلاع از قیمت دقیق محصولات، می‌تونید با پشتیبانی تماس بگیرید یا در وب‌سایت ما قیمت‌ها را مشاهده کنید.",
                "category": "قیمت‌گذاری"
            },
            {
                "question": "ضمانت",
                "answer": "بله، تمام محصولات ما دارای گارانتی معتبر هستند. مدت گارانتی بسته به نوع محصول متفاوت است. برای جزئیات بیشتر با پشتیبانی تماس بگیرید.",
                "category": "گارانتی"
            }
        ]
        
        for faq_data in faqs_data:
            category = categories.get(faq_data["category"])
            faq = FAQ(
                question=faq_data["question"],
                answer=faq_data["answer"],
                category_id=category.id if category else None,
                is_active=True
            )
            db.add(faq)
        
        db.commit()
        print(f"   ✅ Added {len(faqs_data)} FAQs")
        
        print("5. Verifying database...")
        faq_count = db.query(FAQ).count()
        category_count = db.query(Category).count()
        print(f"   ✅ Database has {faq_count} FAQs and {category_count} categories")
        
        db.close()
        print("\n🎉 Database created and populated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    create_database()
