#!/usr/bin/env python3
"""
Start the chatbot with dual database system (FAQ + Website)
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

async def test_dual_database_system():
    """Test the dual database system"""
    print("🧪 Testing dual database system...")
    
    try:
        from services.dual_database_agent import get_dual_database_agent
        
        agent = get_dual_database_agent()
        
        # Test primary database
        primary_result = agent.search_primary_database("سلام")
        print(f"✅ Primary database test - Success: {primary_result['success']}")
        
        # Test secondary database (might be empty initially)
        secondary_result = await agent.search_secondary_database("test")
        print(f"✅ Secondary database test - Success: {secondary_result['success']}")
        
        # Test combined search
        combined_result = await agent.search_dual_database("چطور می‌تونم با شما تماس بگیرم؟")
        print(f"✅ Combined search test - Sources used: {combined_result.get('sources_used', [])}")
        
        # Test answer generation
        answer_result = await agent.answer_question("چطور می‌تونم با شما تماس بگیرم؟")
        print(f"✅ Answer generation test - Sources: {answer_result.get('sources_used', [])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Dual database system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Start the server with dual database system"""
    print("🚀 Starting Dual Database Chatbot...")
    print("📊 Primary Database: FAQ (Reliable)")
    print("🌐 Secondary Database: Website Content (URL Agent)")
    print()
    
    # Initialize database first
    if not initialize_database():
        print("❌ Failed to initialize database. Please check your setup.")
        return
    
    # Test dual database system
    import asyncio
    if not asyncio.run(test_dual_database_system()):
        print("❌ Dual database system test failed. Please check the implementation.")
        return
    
    print("🌐 Dual database interface: http://localhost:8002")
    print("🎛️ Website management dashboard: http://localhost:8002/dashboard")
    print("🔒 Admin panel (restricted): http://localhost:8002/admin")
    print("🌐 Example website with chatbot: http://localhost:8002/example")
    print("🔧 API documentation: http://localhost:8002/docs")
    print("📊 Simple test interface: http://localhost:8002/simple")
    print()
    
    print("✅ All tests passed! The dual database system is ready.")
    print()
    print("📋 Features:")
    print("  • Primary Database: Reliable FAQ system")
    print("  • Secondary Database: Website content via URL agent")
    print("  • Combined search across both databases")
    print("  • Individual database testing")
    print("  • Website management dashboard")
    print("  • Admin panel (restricted access)")
    print("  • Chatbot widget for external websites")
    print("  • Example website with embedded chatbot")
    print()
    
    # Set environment variables if not already set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set.")
        print("   Primary database (FAQ) will work without it.")
        print("   Secondary database (website content) needs it for semantic search.")
        print("   You can set it with: set OPENAI_API_KEY=your_key_here")
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
