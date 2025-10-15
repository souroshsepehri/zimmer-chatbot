#!/usr/bin/env python3
"""
Check database content
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def check_database():
    """Check what's in the database"""
    try:
        from core.db import get_db
        from models.faq import FAQ
        
        db = next(get_db())
        faqs = db.query(FAQ).all()
        
        print(f"Total FAQs: {len(faqs)}")
        print("=" * 50)
        
        for i, faq in enumerate(faqs, 1):
            category_name = faq.category.name if faq.category else "None"
            print(f"{i}. Q: {faq.question}")
            print(f"   A: {faq.answer[:50]}...")
            print(f"   Category: {category_name}")
            print()
        
        db.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database()
