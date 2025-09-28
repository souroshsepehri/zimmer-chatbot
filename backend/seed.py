from sqlalchemy.orm import Session
from core.db import SessionLocal, engine, Base
from models.faq import Category, FAQ
from services.retriever import faq_retriever

# Create tables
Base.metadata.create_all(bind=engine)

def create_sample_data():
    """Create sample categories and FAQs"""
    db = SessionLocal()
    
    try:
        # Create categories
        categories_data = [
            {"name": "عمومی", "slug": "general"},
            {"name": "سفارش‌ها", "slug": "orders"}
        ]
        
        categories = []
        for cat_data in categories_data:
            existing = db.query(Category).filter(Category.slug == cat_data["slug"]).first()
            if not existing:
                category = Category(**cat_data)
                db.add(category)
                categories.append(category)
            else:
                categories.append(existing)
        
        db.commit()
        
        # Create FAQs
        faqs_data = [
            {
                "question": "چطور می‌تونم سفارش بدم؟",
                "answer": "برای سفارش دادن می‌تونید از طریق وب‌سایت ما، اپلیکیشن موبایل یا تماس تلفنی اقدام کنید. ابتدا محصولات مورد نظر خود را انتخاب کرده و به سبد خرید اضافه کنید.",
                "category_id": categories[1].id if len(categories) > 1 else None
            },
            {
                "question": "زمان تحویل سفارش چقدر است؟",
                "answer": "زمان تحویل سفارش‌ها معمولاً ۲ تا ۵ روز کاری است. برای سفارش‌های فوری امکان تحویل در همان روز نیز وجود دارد.",
                "category_id": categories[1].id if len(categories) > 1 else None
            },
            {
                "question": "آیا امکان بازگشت کالا وجود دارد؟",
                "answer": "بله، شما تا ۷ روز پس از دریافت کالا می‌تونید درخواست بازگشت دهید. کالا باید در شرایط اولیه و با بسته‌بندی اصلی باشد.",
                "category_id": categories[1].id if len(categories) > 1 else None
            },
            {
                "question": "چطور می‌تونم با پشتیبانی تماس بگیرم؟",
                "answer": "شما می‌تونید از طریق شماره تلفن ۰۲۱-۱۲۳۴۵۶۷۸، ایمیل support@zimer.com یا چت آنلاین در وب‌سایت با ما در ارتباط باشید.",
                "category_id": categories[0].id if len(categories) > 0 else None
            },
            {
                "question": "ساعات کاری شما چه موقع است؟",
                "answer": "ما از شنبه تا پنج‌شنبه از ساعت ۹ صبح تا ۶ عصر و جمعه‌ها از ساعت ۹ صبح تا ۲ ظهر در خدمت شما هستیم.",
                "category_id": categories[0].id if len(categories) > 0 else None
            }
        ]
        
        for faq_data in faqs_data:
            existing = db.query(FAQ).filter(FAQ.question == faq_data["question"]).first()
            if not existing:
                faq = FAQ(**faq_data)
                db.add(faq)
        
        db.commit()
        print("Sample data created successfully!")
        
        # Reindex FAQs
        print("Rebuilding FAQ index...")
        faq_retriever.reindex(db)
        print("FAQ index rebuilt successfully!")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_sample_data()
