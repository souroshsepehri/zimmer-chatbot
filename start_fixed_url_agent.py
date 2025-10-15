#!/usr/bin/env python3
"""
Start the chatbot with URL agent functionality - Fixed version
"""

import uvicorn
import os
import sys
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def initialize_database():
    """Initialize database and add sample data if needed"""
    print("🔧 Initializing database...")
    
    try:
        from core.db import get_db, engine, Base
        from models.faq import FAQ
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created/verified")
        
        # Check if we have data
        db = next(get_db())
        faq_count = db.query(FAQ).count()
        
        if faq_count == 0:
            print("📝 Adding sample data...")
            
            # Add basic sample FAQs
            sample_faqs = [
                {
                    "question": "چطور می‌تونم با شما تماس بگیرم؟",
                    "answer": "شما می‌تونید از طریق ایمیل یا تلفن با ما تماس بگیرید.",
                    "category": "تماس",
                    "tags": "تماس, ارتباط"
                },
                {
                    "question": "ساعات کاری شما چیه؟",
                    "answer": "ما از شنبه تا پنج‌شنبه از ساعت 9 تا 17 فعالیت می‌کنیم.",
                    "category": "ساعات کاری",
                    "tags": "ساعات, زمان"
                },
                {
                    "question": "چطور می‌تونم سفارش بدم؟",
                    "answer": "شما می‌تونید از طریق وب‌سایت یا تماس تلفنی سفارش خود را ثبت کنید.",
                    "category": "سفارش",
                    "tags": "سفارش, خرید"
                },
                {
                    "question": "قیمت‌های شما چقدره؟",
                    "answer": "قیمت‌های ما رقابتی و مناسب است. برای جزئیات بیشتر با ما تماس بگیرید.",
                    "category": "قیمت",
                    "tags": "قیمت, هزینه"
                },
                {
                    "question": "آیا گارانتی دارید؟",
                    "answer": "بله، تمام محصولات ما دارای گارانتی معتبر هستند.",
                    "category": "گارانتی",
                    "tags": "گارانتی, ضمانت"
                }
            ]
            
            for faq_data in sample_faqs:
                faq = FAQ(
                    question=faq_data["question"],
                    answer=faq_data["answer"],
                    category=faq_data["category"],
                    tags=faq_data["tags"]
                )
                db.add(faq)
            
            db.commit()
            print(f"✅ Added {len(sample_faqs)} sample FAQs")
        else:
            print(f"✅ Database already has {faq_count} FAQs")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def main():
    """Start the server with URL agent support"""
    print("🚀 Starting Persian Chatbot with Fixed URL Agent...")
    print("📡 URL Agent can read websites and use them as a second database")
    print()
    
    # Initialize database first
    if not initialize_database():
        print("❌ Failed to initialize database. Please check your setup.")
        return
    
    print("🌐 Enhanced interface available at: http://localhost:8002")
    print("📚 Simple interface available at: http://localhost:8002/simple")
    print("🔧 API documentation at: http://localhost:8002/docs")
    print()
    
    # Set environment variables if not already set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set. Please set it for full functionality.")
        print("   You can set it with: set OPENAI_API_KEY=your_key_here")
        print("   Without it, only basic FAQ search will work.")
        print()
    
    # Start the server
    port = int(os.environ.get("PORT", 8002))
    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
