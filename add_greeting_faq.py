#!/usr/bin/env python3
"""
Add greeting FAQ to handle common greetings
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def add_greeting_faq():
    """Add greeting FAQ"""
    print("🔄 Adding greeting FAQ...")
    
    try:
        from core.db import get_db, engine, Base
        from models.faq import FAQ, Category
        
        # Get database session
        db = next(get_db())
        
        # Get or create general category
        general_category = db.query(Category).filter(Category.name == "عمومی").first()
        if not general_category:
            general_category = Category(name="عمومی", slug="general")
            db.add(general_category)
            db.commit()
            db.refresh(general_category)
        
        # Check if greeting FAQ already exists
        existing_greeting = db.query(FAQ).filter(FAQ.question == "سلام").first()
        if existing_greeting:
            print("⏭️  Greeting FAQ already exists")
            db.close()
            return True
        
        # Add greeting FAQ
        greeting_faq = FAQ(
            question="سلام",
            answer="سلام وقت بخیر! ربات هوشمند زیمر هستم. چطور می‌تونم کمکتون کنم؟",
            category_id=general_category.id,
            is_active=True
        )
        
        db.add(greeting_faq)
        db.commit()
        db.close()
        
        print("✅ Successfully added greeting FAQ")
        return True
        
    except Exception as e:
        print(f"❌ Error adding greeting FAQ: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = add_greeting_faq()
    if success:
        print("🎉 Greeting FAQ added successfully!")
    else:
        print("💥 Failed to add greeting FAQ.")
