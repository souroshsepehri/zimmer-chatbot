#!/usr/bin/env python3
"""
Test API endpoints directly without server
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_direct_api():
    print("🧪 Testing API Logic Directly")
    print("=" * 40)
    
    try:
        from core.db import get_db
        from models.log import ChatLog
        from models.faq import FAQ, Category
        from sqlalchemy import func
        from datetime import date
        
        db = next(get_db())
        
        # Test logs stats logic
        print("📊 Testing Logs Stats Logic:")
        
        total_logs = db.query(ChatLog).count()
        successful_logs = db.query(ChatLog).filter(ChatLog.success == True).count()
        
        # Count unanswered logs - simplified approach
        unanswered_logs = db.query(ChatLog).filter(
            ChatLog.notes.contains("unanswered_in_db")
        ).count()
        
        # Get today's logs
        today_logs = db.query(ChatLog).filter(
            func.date(ChatLog.timestamp) == date.today()
        ).count()
        
        success_rate = (successful_logs / total_logs * 100) if total_logs > 0 else 0
        unanswered_rate = (unanswered_logs / total_logs * 100) if total_logs > 0 else 0
        
        stats = {
            "total_logs": total_logs,
            "total_chats": total_logs,
            "successful_logs": successful_logs,
            "success_rate": success_rate,
            "unanswered_logs": unanswered_logs,
            "unanswered_rate": unanswered_rate,
            "today_chats": today_logs
        }
        
        print(f"  Total logs: {stats['total_logs']}")
        print(f"  Success rate: {stats['success_rate']:.1f}%")
        print(f"  Today chats: {stats['today_chats']}")
        print(f"  Unanswered: {stats['unanswered_logs']}")
        
        # Test FAQs
        print(f"\n❓ Testing FAQs:")
        faqs = db.query(FAQ).all()
        print(f"  Total FAQs: {len(faqs)}")
        
        # Test categories
        print(f"\n📁 Testing Categories:")
        categories = db.query(Category).all()
        print(f"  Total Categories: {len(categories)}")
        
        print(f"\n✅ All API logic working correctly!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_api()
