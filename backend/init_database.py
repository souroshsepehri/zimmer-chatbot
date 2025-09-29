#!/usr/bin/env python3
"""
Initialize database for Render deployment
"""
import os
import sys
from pathlib import Path

def init_database():
    """Initialize database and create tables"""
    print("Initializing database...")
    
    try:
        # Import database components
        from core.db import engine, Base
        from models.log import ChatLog
        from models.faq import FAQ
        
        # Create database directory if it doesn't exist
        db_dir = Path(".")
        db_dir.mkdir(exist_ok=True)
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
        # Test database connection
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("✅ Database connection test successful")
        
        print("✅ Database initialization completed")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    init_database()
