#!/usr/bin/env python3
"""
Check database contents
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_database():
    print("📊 Checking Database Contents")
    print("=" * 40)
    
    try:
        from core.db import get_db
        from models.log import ChatLog
        from models.faq import FAQ, Category
        
        db = next(get_db())
        
        # Check logs
        from sqlalchemy import func
        from datetime import date
        
        total_logs = db.query(ChatLog).count()
        successful_logs = db.query(ChatLog).filter(ChatLog.success == True).count()
        today_logs = db.query(ChatLog).filter(
            func.date(ChatLog.timestamp) == date.today()
        ).count()
        
        print(f"📝 Chat Logs:")
        print(f"  Total: {total_logs}")
        print(f"  Successful: {successful_logs}")
        print(f"  Today: {today_logs}")
        print(f"  Success Rate: {(successful_logs/total_logs*100):.1f}%" if total_logs > 0 else "  Success Rate: 0%")
        
        # Check FAQs
        total_faqs = db.query(FAQ).count()
        active_faqs = db.query(FAQ).filter(FAQ.is_active == True).count()
        
        print(f"\n❓ FAQs:")
        print(f"  Total: {total_faqs}")
        print(f"  Active: {active_faqs}")
        
        # Check categories
        total_categories = db.query(Category).count()
        
        print(f"\n📁 Categories:")
        print(f"  Total: {total_categories}")
        
        # Show recent logs
        recent_logs = db.query(ChatLog).order_by(ChatLog.timestamp.desc()).limit(3).all()
        print(f"\n🕒 Recent Logs:")
        for log in recent_logs:
            print(f"  {log.timestamp}: {log.user_text[:30]}... -> {log.intent} ({log.success})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database()
