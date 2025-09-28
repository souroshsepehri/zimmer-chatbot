#!/usr/bin/env python3
"""
Script to build FAQ index from database
"""

from sqlalchemy.orm import Session
from core.db import engine, Base
from models.faq import FAQ, Category
from services.retriever import faq_retriever

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Create a session
db = Session(engine)

try:
    # Check if there are any FAQs in the database
    faq_count = db.query(FAQ).filter(FAQ.is_active == True).count()
    print(f"📊 Found {faq_count} active FAQs in database")
    
    if faq_count == 0:
        print("❌ No active FAQs found. Please add some FAQs through the admin panel first.")
    else:
        # List all FAQs
        faqs = db.query(FAQ).filter(FAQ.is_active == True).all()
        print("\n📋 Active FAQs:")
        for faq in faqs:
            category_name = faq.category.name if faq.category else "بدون دسته"
            print(f"  - {faq.question[:50]}... (دسته: {category_name})")
        
        # Build the index
        print("\n🔨 Building FAQ index...")
        faq_retriever.build_index(db)
        print("✅ FAQ index built successfully!")
        
        # Test the index
        print("\n🧪 Testing index...")
        test_results = faq_retriever.semantic_search("سفارش", top_k=3)
        print(f"Test search returned {len(test_results)} results")
        for i, result in enumerate(test_results):
            print(f"  {i+1}. {result['question'][:50]}... (score: {result['score']:.3f})")
            
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
