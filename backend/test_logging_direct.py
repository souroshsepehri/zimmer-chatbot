#!/usr/bin/env python3
"""
Direct test of chat logging functionality without running the server
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.db import get_db
from models.log import ChatLog
from services.chain import chat_chain
import json

def test_chat_logging():
    """Test chat logging functionality directly"""
    print("Testing chat logging functionality...")
    
    # Get database session
    db = next(get_db())
    
    # Check current log count
    initial_count = db.query(ChatLog).count()
    print(f"Initial log count: {initial_count}")
    
    # Test message
    test_message = "تست لاگ جدید - آیا این پیام لاگ می‌شود؟"
    
    try:
        # Process message through chain
        result = chat_chain.process_message(
            message=test_message,
            db=db,
            debug=False
        )
        
        print(f"Chain result: {result}")
        
        # Create chat log entry (same as in the router)
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
        
        print(f"✅ Chat logged successfully: ID {chat_log.id}")
        
        # Check new log count
        final_count = db.query(ChatLog).count()
        print(f"Final log count: {final_count}")
        print(f"New logs added: {final_count - initial_count}")
        
        # Show the latest log
        latest_log = db.query(ChatLog).order_by(ChatLog.id.desc()).first()
        print(f"\nLatest log details:")
        print(f"  ID: {latest_log.id}")
        print(f"  User: {latest_log.user_text[:50]}...")
        print(f"  AI: {latest_log.ai_text[:50]}...")
        print(f"  Success: {latest_log.success}")
        print(f"  Source: {latest_log.source}")
        print(f"  Intent: {latest_log.intent}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during logging test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        db.close()

if __name__ == "__main__":
    success = test_chat_logging()
    if success:
        print("\n✅ Chat logging test completed successfully!")
    else:
        print("\n❌ Chat logging test failed!")
        sys.exit(1)
