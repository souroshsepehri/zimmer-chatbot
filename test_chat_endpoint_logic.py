#!/usr/bin/env python3
"""
Test the exact chat endpoint logic to find the logging issue
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from core.db import get_db
from models.log import ChatLog
from services.chain import chat_chain
import json

def test_chat_endpoint_logic():
    print("🔍 Testing Chat Endpoint Logic")
    print("=" * 50)
    
    try:
        # Get database session
        db = next(get_db())
        print("✅ Database connection successful")
        
        # Simulate the chat endpoint logic
        message = "تست لاگ از طریق چت"
        
        # Process message through chain
        result = chat_chain.process_message(
            message=message,
            db=db,
            debug=True,
            category_filter=None
        )
        
        print(f"✅ Chat chain result: {result}")
        
        # Log the chat interaction (exact same code as in chat endpoint)
        try:
            # Prepare notes with additional metadata
            notes_data = {
                "intent": result.get("intent", {}),
                "source": result.get("source", "unknown"),
                "unanswered_in_db": result.get("unanswered_in_db", False),
                "retrieval_count": len(result.get("retrieval_results", []))
            }
            
            # Create chat log entry
            chat_log = ChatLog(
                user_text=message,
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
            
        except Exception as log_error:
            print(f"❌ Logging error: {log_error}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chat_endpoint_logic()
