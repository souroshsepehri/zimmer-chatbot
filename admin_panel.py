#!/usr/bin/env python3
"""
Simple Admin Panel for Chatbot Database
Direct database access without needing the server to be running
"""

import sqlite3
import json
from datetime import datetime
import os

# Database path
DB_PATH = "backend/app.db"

def connect_db():
    """Connect to the SQLite database"""
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        print("Make sure the backend has been run at least once to create the database.")
        return None
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return None

def show_stats():
    """Show database statistics"""
    conn = connect_db()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get total chat logs
        cursor.execute("SELECT COUNT(*) as total FROM chat_logs")
        total_logs = cursor.fetchone()['total']
        
        # Get successful logs
        cursor.execute("SELECT COUNT(*) as successful FROM chat_logs WHERE success = 1")
        successful_logs = cursor.fetchone()['successful']
        
        # Get failed logs
        cursor.execute("SELECT COUNT(*) as failed FROM chat_logs WHERE success = 0")
        failed_logs = cursor.fetchone()['failed']
        
        # Get FAQs count
        cursor.execute("SELECT COUNT(*) as faqs FROM faqs")
        faqs_count = cursor.fetchone()['faqs']
        
        print("📊 DATABASE STATISTICS")
        print("=" * 50)
        print(f"Total Chat Logs: {total_logs}")
        print(f"Successful Chats: {successful_logs}")
        print(f"Failed Chats: {failed_logs}")
        print(f"Total FAQs: {faqs_count}")
        print(f"Success Rate: {(successful_logs/total_logs*100):.1f}%" if total_logs > 0 else "No data")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
    finally:
        conn.close()

def show_recent_logs(limit=10):
    """Show recent chat logs"""
    conn = connect_db()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, user_text, ai_text, success, intent, source, confidence
            FROM chat_logs 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        
        logs = cursor.fetchall()
        
        if not logs:
            print("📝 No chat logs found")
            return
        
        print(f"📝 RECENT CHAT LOGS (Last {len(logs)})")
        print("=" * 80)
        
        for log in logs:
            status = "✅" if log['success'] else "❌"
            print(f"\n{status} ID: {log['id']} | {log['timestamp']}")
            print(f"User: {log['user_text'][:50]}{'...' if len(log['user_text']) > 50 else ''}")
            print(f"AI: {log['ai_text'][:50]}{'...' if len(log['ai_text']) > 50 else ''}")
            print(f"Intent: {log['intent'] or 'N/A'} | Source: {log['source'] or 'N/A'} | Confidence: {log['confidence'] or 'N/A'}")
            print("-" * 80)
        
    except Exception as e:
        print(f"❌ Error getting logs: {e}")
    finally:
        conn.close()

def show_faqs():
    """Show all FAQs"""
    conn = connect_db()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, question, answer, is_active FROM faqs ORDER BY id")
        
        faqs = cursor.fetchall()
        
        if not faqs:
            print("❓ No FAQs found")
            return
        
        print(f"❓ FAQS ({len(faqs)} total)")
        print("=" * 80)
        
        for faq in faqs:
            status = "✅ Active" if faq['is_active'] else "❌ Inactive"
            print(f"\n{status} ID: {faq['id']}")
            print(f"Q: {faq['question']}")
            print(f"A: {faq['answer'][:100]}{'...' if len(faq['answer']) > 100 else ''}")
            print("-" * 80)
        
    except Exception as e:
        print(f"❌ Error getting FAQs: {e}")
    finally:
        conn.close()

def search_logs(query):
    """Search chat logs by user text"""
    conn = connect_db()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, user_text, ai_text, success, intent, source
            FROM chat_logs 
            WHERE user_text LIKE ? OR ai_text LIKE ?
            ORDER BY timestamp DESC
        """, (f"%{query}%", f"%{query}%"))
        
        logs = cursor.fetchall()
        
        if not logs:
            print(f"🔍 No logs found containing '{query}'")
            return
        
        print(f"🔍 SEARCH RESULTS for '{query}' ({len(logs)} found)")
        print("=" * 80)
        
        for log in logs:
            status = "✅" if log['success'] else "❌"
            print(f"\n{status} ID: {log['id']} | {log['timestamp']}")
            print(f"User: {log['user_text']}")
            print(f"AI: {log['ai_text'][:100]}{'...' if len(log['ai_text']) > 100 else ''}")
            print(f"Intent: {log['intent'] or 'N/A'} | Source: {log['source'] or 'N/A'}")
            print("-" * 80)
        
    except Exception as e:
        print(f"❌ Error searching logs: {e}")
    finally:
        conn.close()

def export_logs():
    """Export logs to JSON file"""
    conn = connect_db()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, user_text, ai_text, success, intent, source, confidence, notes
            FROM chat_logs 
            ORDER BY timestamp DESC
        """)
        
        logs = cursor.fetchall()
        
        # Convert to list of dictionaries
        logs_data = []
        for log in logs:
            logs_data.append({
                'id': log['id'],
                'timestamp': log['timestamp'],
                'user_text': log['user_text'],
                'ai_text': log['ai_text'],
                'success': bool(log['success']),
                'intent': log['intent'],
                'source': log['source'],
                'confidence': log['confidence'],
                'notes': log['notes']
            })
        
        # Save to JSON file
        filename = f"chat_logs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(logs_data, f, ensure_ascii=False, indent=2)
        
        print(f"📁 Exported {len(logs_data)} logs to {filename}")
        
    except Exception as e:
        print(f"❌ Error exporting logs: {e}")
    finally:
        conn.close()

def main():
    """Main admin panel interface"""
    print("🤖 CHATBOT ADMIN PANEL")
    print("=" * 50)
    
    while True:
        print("\nChoose an option:")
        print("1. Show Statistics")
        print("2. Show Recent Logs")
        print("3. Show All FAQs")
        print("4. Search Logs")
        print("5. Export Logs")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            show_stats()
        elif choice == '2':
            limit = input("How many recent logs? (default 10): ").strip()
            limit = int(limit) if limit.isdigit() else 10
            show_recent_logs(limit)
        elif choice == '3':
            show_faqs()
        elif choice == '4':
            query = input("Enter search term: ").strip()
            if query:
                search_logs(query)
        elif choice == '5':
            export_logs()
        elif choice == '6':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
