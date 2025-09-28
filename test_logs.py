#!/usr/bin/env python3
"""
Quick test to check if chat logs are being saved
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from core.db import get_db
from models.log import ChatLog

def check_logs():
    try:
        db = next(get_db())
        logs = db.query(ChatLog).order_by(ChatLog.timestamp.desc()).limit(5).all()
        
        print("📊 Recent Chat Logs:")
        print("=" * 50)
        
        if not logs:
            print("❌ No chat logs found in database")
            return
            
        for log in logs:
            print(f"ID: {log.id}")
            print(f"Time: {log.timestamp}")
            print(f"User: {log.user_text[:50]}...")
            print(f"AI: {log.ai_text[:50]}...")
            print(f"Intent: {log.intent}")
            print(f"Source: {log.source}")
            print(f"Success: {log.success}")
            print("-" * 30)
            
        print(f"✅ Found {len(logs)} recent logs")
        
    except Exception as e:
        print(f"❌ Error checking logs: {e}")

if __name__ == "__main__":
    check_logs()
