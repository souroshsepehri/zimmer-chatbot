#!/usr/bin/env python3
"""
Test chat logging functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_chat_logging():
    print("🧪 Testing Chat Logging System")
    print("=" * 40)
    
    try:
        # Test database connection
        from core.db import get_db
        from models.log import ChatLog
        
        db = next(get_db())
        initial_count = db.query(ChatLog).count()
        print(f"✅ Database connected. Initial log count: {initial_count}")
        
        # Test chat chain
        from services.chain import chat_chain
        
        test_message = "سلام، چطور می‌تونم سفارش بدم؟"
        print(f"Testing message: {test_message}")
        
        result = chat_chain.process_message(
            message=test_message,
            db=db,
            debug=False
        )
        
        print(f"✅ Chat chain processed. Result: {result.get('answer', 'No answer')[:50]}...")
        print(f"   Intent: {result.get('intent', {}).get('label', 'Unknown')}")
        print(f"   Success: {result.get('success', False)}")
        
        # Test logging
        import json
        
        notes_data = {
            "intent": result.get("intent", {}),
            "source": result.get("source", "unknown"),
            "unanswered_in_db": result.get("unanswered_in_db", False),
            "retrieval_count": len(result.get("retrieval_results", []))
        }
        
        chat_log = ChatLog(
            user_text=test_message,
            ai_text=result["answer"],
            intent=result.get("intent", {}).get("label"),
            source=result.get("source", "unknown"),
            confidence=result.get("intent", {}).get("confidence"),
            success=result.get("success", False),
            matched_faq_id=result.get("matched_faq_id"),
            notes=json.dumps(notes_data, ensure_ascii=False)
        )
        
        db.add(chat_log)
        db.commit()
        
        final_count = db.query(ChatLog).count()
        print(f"✅ Log saved successfully! Final count: {final_count}")
        print(f"   Log ID: {chat_log.id}")
        print(f"   Timestamp: {chat_log.timestamp}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chat_logging()
