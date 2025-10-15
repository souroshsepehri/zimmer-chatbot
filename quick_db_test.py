#!/usr/bin/env python3
"""
Quick database test
"""

import sqlite3
import os

def test_database():
    """Test database directly with sqlite3"""
    print("🔍 Testing Database with SQLite3")
    print("=" * 40)
    
    db_path = "app.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"✅ Found tables: {[table[0] for table in tables]}")
        
        # Check FAQs table
        if ('faqs',) in tables:
            cursor.execute("SELECT COUNT(*) FROM faqs")
            count = cursor.fetchone()[0]
            print(f"✅ Found {count} FAQs in database")
            
            # Get sample FAQs
            cursor.execute("SELECT question, answer FROM faqs LIMIT 3")
            faqs = cursor.fetchall()
            
            print("\n📝 Sample FAQs:")
            for i, (question, answer) in enumerate(faqs, 1):
                print(f"  {i}. {question[:50]}...")
                print(f"     {answer[:50]}...")
                print()
        
        # Check categories table
        if ('categories',) in tables:
            cursor.execute("SELECT COUNT(*) FROM categories")
            count = cursor.fetchone()[0]
            print(f"✅ Found {count} categories in database")
        
        conn.close()
        print("🎉 Database test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == "__main__":
    test_database()
