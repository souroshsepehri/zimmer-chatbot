#!/usr/bin/env python3
"""
Start the chatbot with simple, reliable database reading
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
            
            # Add comprehensive sample FAQs
            sample_faqs = [
                {
                    "question": "سلام، چطوری؟",
                    "answer": "سلام! من خوبم، ممنون. چطور می‌تونم کمکتون کنم؟",
                    "category": "greeting"
                },
                {
                    "question": "ساعت چند است؟",
                    "answer": "متأسفانه من به ساعت دسترسی ندارم. لطفاً از ساعت سیستم خودتون استفاده کنید.",
                    "category": "time"
                },
                {
                    "question": "آیا می‌توانید به من کمک کنید؟",
                    "answer": "البته! من اینجا هستم تا به سؤالات شما پاسخ دهم. چه کمکی از دستم برمی‌آید؟",
                    "category": "help"
                },
                {
                    "question": "چطور می‌تونم با شما صحبت کنم؟",
                    "answer": "شما می‌تونید مستقیماً در این چت با من صحبت کنید. فقط پیام خودتون رو بنویسید و ارسال کنید.",
                    "category": "communication"
                },
                {
                    "question": "ممنون",
                    "answer": "خواهش می‌کنم! خوشحالم که تونستم کمکتون کنم. اگه سوال دیگه‌ای دارید، در خدمتم.",
                    "category": "thanks"
                },
                {
                    "question": "چطور می‌تونم با شما تماس بگیرم؟",
                    "answer": "شما می‌تونید از طریق ایمیل یا تلفن با ما تماس بگیرید. اطلاعات تماس در صفحه تماس با ما موجود است.",
                    "category": "contact"
                },
                {
                    "question": "ساعات کاری شما چیه؟",
                    "answer": "ما از شنبه تا پنج‌شنبه از ساعت 9 تا 17 فعالیت می‌کنیم.",
                    "category": "hours"
                },
                {
                    "question": "چطور می‌تونم سفارش بدم؟",
                    "answer": "شما می‌تونید از طریق وب‌سایت یا تماس تلفنی سفارش خود را ثبت کنید.",
                    "category": "order"
                },
                {
                    "question": "قیمت‌های شما چقدره؟",
                    "answer": "قیمت‌های ما رقابتی و مناسب است. برای جزئیات بیشتر با ما تماس بگیرید.",
                    "category": "price"
                },
                {
                    "question": "آیا گارانتی دارید؟",
                    "answer": "بله، تمام محصولات ما دارای گارانتی معتبر هستند.",
                    "category": "warranty"
                },
                {
                    "question": "چطور می‌تونم محصولات شما رو ببینم؟",
                    "answer": "شما می‌تونید محصولات ما را در بخش محصولات وب‌سایت مشاهده کنید.",
                    "category": "products"
                },
                {
                    "question": "آیا ارسال رایگان دارید؟",
                    "answer": "بله، برای سفارشات بالای 500 هزار تومان ارسال رایگان داریم.",
                    "category": "shipping"
                }
            ]
            
            for faq_data in sample_faqs:
                faq = FAQ(
                    question=faq_data["question"],
                    answer=faq_data["answer"],
                    category=faq_data["category"]
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
        import traceback
        traceback.print_exc()
        return False

def test_simple_chatbot():
    """Test the simple chatbot functionality"""
    print("🧪 Testing simple chatbot...")
    
    try:
        from services.simple_chatbot import get_simple_chatbot
        
        chatbot = get_simple_chatbot()
        
        # Test loading FAQs
        if chatbot.load_faqs_from_db():
            print(f"✅ Simple chatbot loaded {len(chatbot.faqs)} FAQs")
            
            # Test a simple search
            results = chatbot.search_faqs("سلام")
            print(f"✅ Search test successful - found {len(results)} results")
            
            # Test getting an answer
            answer_result = chatbot.get_answer("چطور می‌تونم با شما تماس بگیرم؟")
            print(f"✅ Answer test successful - source: {answer_result['source']}")
            
            return True
        else:
            print("❌ Failed to load FAQs in simple chatbot")
            return False
            
    except Exception as e:
        print(f"❌ Simple chatbot test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Start the server with simple, reliable chatbot"""
    print("🚀 Starting Simple Reliable Chatbot...")
    print("📊 Focus: Reliable database reading and FAQ responses")
    print()
    
    # Initialize database first
    if not initialize_database():
        print("❌ Failed to initialize database. Please check your setup.")
        return
    
    # Test simple chatbot
    if not test_simple_chatbot():
        print("❌ Simple chatbot test failed. Please check the implementation.")
        return
    
    print("🌐 Simple test interface: http://localhost:8002")
    print("🔧 API documentation: http://localhost:8002/docs")
    print("📊 Database test endpoint: http://localhost:8002/api/test-database")
    print("💬 Simple chat endpoint: http://localhost:8002/api/simple-chat")
    print()
    
    print("✅ All tests passed! The chatbot should work reliably now.")
    print()
    
    # Start the server
    port = int(os.environ.get("PORT", 8002))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
