#!/usr/bin/env python3
"""
Debug logging issue
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from core.db import get_db
from models.log import ChatLog
import json

def test_logging():
    try:
        print("🔍 Testing logging functionality...")
        
        # Get database session
        db = next(get_db())
        print("✅ Database connection successful")
        
        # Create a test log entry
        test_log = ChatLog(
            user_text="تست لاگ",
            ai_text="پاسخ تست",
            intent="test",
            source="test",
            confidence=0.9,
            success=True,
            notes=json.dumps({"test": True})
        )
        
        print("✅ ChatLog object created")
        
        # Add to database
        db.add(test_log)
        print("✅ Added to session")
        
        # Commit
        db.commit()
        print("✅ Committed to database")
        
        # Check if it was saved
        saved_log = db.query(ChatLog).filter(ChatLog.user_text == "تست لاگ").first()
        if saved_log:
            print(f"✅ Log saved successfully with ID: {saved_log.id}")
        else:
            print("❌ Log not found in database")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_logging()
