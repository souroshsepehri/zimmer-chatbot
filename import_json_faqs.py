#!/usr/bin/env python3
"""
Import JSON FAQs into the database
"""

import sys
import os
import json
from pathlib import Path

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def import_json_faqs():
    """Import FAQs from sample_json_faqs.json into the database"""
    print("🔄 Importing JSON FAQs into database...")
    
    try:
        from core.db import get_db, engine, Base
        from models.faq import FAQ, Category
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        
        # Load JSON data
        json_file = Path("backend/sample_json_faqs.json")
        if not json_file.exists():
            print(f"❌ JSON file not found: {json_file}")
            return False
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        faqs_data = data.get('faqs', [])
        print(f"📄 Found {len(faqs_data)} FAQs in JSON file")
        
        # Get database session
        db = next(get_db())
        
        # Clear existing FAQs
        print("🗑️  Clearing existing FAQs...")
        db.query(FAQ).delete()
        db.query(Category).delete()
        db.commit()
        
        # Create categories
        categories = {}
        for faq_data in faqs_data:
            category_name = faq_data.get('category', 'عمومی')
            if category_name not in categories:
                category = Category(
                    name=category_name,
                    slug=category_name.lower().replace(' ', '-').replace('‌', '-')
                )
                db.add(category)
                db.commit()
                db.refresh(category)
                categories[category_name] = category
        
        # Import FAQs
        imported_count = 0
        for faq_data in faqs_data:
            try:
                category_name = faq_data.get('category', 'عمومی')
                category = categories.get(category_name)
                
                faq = FAQ(
                    question=faq_data['question'],
                    answer=faq_data['answer'],
                    category_id=category.id if category else None,
                    is_active=faq_data.get('is_active', True)
                )
                
                db.add(faq)
                imported_count += 1
                
            except Exception as e:
                print(f"⚠️  Error importing FAQ '{faq_data.get('question', 'Unknown')}': {e}")
        
        db.commit()
        db.close()
        
        print(f"✅ Successfully imported {imported_count} FAQs")
        print(f"📊 Categories created: {len(categories)}")
        
        # Verify import
        db = next(get_db())
        total_faqs = db.query(FAQ).count()
        print(f"🔍 Total FAQs in database: {total_faqs}")
        
        # Show sample FAQs
        sample_faqs = db.query(FAQ).limit(3).all()
        print("\n📋 Sample FAQs:")
        for i, faq in enumerate(sample_faqs, 1):
            print(f"  {i}. Q: {faq.question[:50]}...")
            print(f"     A: {faq.answer[:50]}...")
            print(f"     Category: {faq.category.name if faq.category else 'None'}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error importing FAQs: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = import_json_faqs()
    if success:
        print("\n🎉 FAQ import completed successfully!")
        print("🚀 You can now test the chatbot with proper data.")
    else:
        print("\n💥 FAQ import failed. Please check the errors above.")
