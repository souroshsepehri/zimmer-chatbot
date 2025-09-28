#!/usr/bin/env python3
"""
Test direct logging to see if the issue is in the chat endpoint
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from core.db import get_db
from models.log import ChatLog
import json

def test_direct_logging():
    print("🔍 Testing Direct Logging")
    print("=" * 50)
    
    try:
        db = next(get_db())
        
        # Create a test log entry
        test_log = ChatLog(
            user_text="تست لاگ جدید",
            ai_text="پاسخ تست جدید",
            intent="test",
            source="test",
            confidence=0.9,
            success=True,
            notes=json.dumps({"test": True})
        )
        
        print("✅ ChatLog object created")
        
        # Add to database
        db.add(test_log)
        db.commit()
        
        print("✅ Log saved to database")
        
        # Check if it was saved
        saved_log = db.query(ChatLog).filter(ChatLog.user_text == "تست لاگ جدید").first()
        if saved_log:
            print(f"✅ Log found with ID: {saved_log.id}")
        else:
            print("❌ Log not found in database")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_logging()
