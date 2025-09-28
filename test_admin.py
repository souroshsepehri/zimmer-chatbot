#!/usr/bin/env python3
"""
Test script to demonstrate admin panel functionality
"""

import sqlite3
import json
from datetime import datetime
import os

# Database path
DB_PATH = "backend/app.db"

def test_admin_panel():
    """Test admin panel functionality"""
    print("🤖 TESTING ADMIN PANEL DATABASE ACCESS")
    print("=" * 50)
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Test 1: Get statistics
        print("\n📊 DATABASE STATISTICS:")
        print("-" * 30)
        
        cursor.execute("SELECT COUNT(*) as total FROM chat_logs")
        total_logs = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as successful FROM chat_logs WHERE success = 1")
        successful_logs = cursor.fetchone()['successful']
        
        cursor.execute("SELECT COUNT(*) as failed FROM chat_logs WHERE success = 0")
        failed_logs = cursor.fetchone()['failed']
        
        cursor.execute("SELECT COUNT(*) as faqs FROM faqs")
        faqs_count = cursor.fetchone()['faqs']
        
        print(f"Total Chat Logs: {total_logs}")
        print(f"Successful Chats: {successful_logs}")
        print(f"Failed Chats: {failed_logs}")
        print(f"Total FAQs: {faqs_count}")
        print(f"Success Rate: {(successful_logs/total_logs*100):.1f}%" if total_logs > 0 else "No data")
        
        # Test 2: Show recent logs
        print(f"\n📝 RECENT CHAT LOGS (Last 3):")
        print("-" * 50)
        
        cursor.execute("""
            SELECT id, timestamp, user_text, ai_text, success, intent, source
            FROM chat_logs 
            ORDER BY timestamp DESC 
            LIMIT 3
        """)
        
        logs = cursor.fetchall()
        
        for log in logs:
            status = "✅" if log['success'] else "❌"
            print(f"\n{status} ID: {log['id']} | {log['timestamp']}")
            print(f"User: {log['user_text'][:50]}{'...' if len(log['user_text']) > 50 else ''}")
            print(f"AI: {log['ai_text'][:50]}{'...' if len(log['ai_text']) > 50 else ''}")
            print(f"Intent: {log['intent'] or 'N/A'} | Source: {log['source'] or 'N/A'}")
        
        # Test 3: Show FAQs
        print(f"\n❓ FAQS:")
        print("-" * 30)
        
        cursor.execute("SELECT id, question, answer, is_active FROM faqs ORDER BY id")
        faqs = cursor.fetchall()
        
        for faq in faqs:
            status = "✅ Active" if faq['is_active'] else "❌ Inactive"
            print(f"\n{status} ID: {faq['id']}")
            print(f"Q: {faq['question']}")
            print(f"A: {faq['answer'][:60]}{'...' if len(faq['answer']) > 60 else ''}")
        
        print(f"\n✅ ADMIN PANEL DATABASE ACCESS IS WORKING PERFECTLY!")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    test_admin_panel()
