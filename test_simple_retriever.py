#!/usr/bin/env python3
"""
Test simple retriever directly
"""

from sqlalchemy.orm import Session
from core.db import engine, Base
from models.faq import FAQ, Category
from services.simple_retriever import simple_faq_retriever

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Create a session
db = Session(engine)

try:
    # Load FAQs
    simple_faq_retriever.load_faqs(db)
    
    # Test searches
    test_queries = [
        "چطور می‌تونم سفارش بدم؟",
        "ساعات کاری",
        "پشتیبانی",
        "سلام"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        results = simple_faq_retriever.search(query, top_k=3, threshold=0.1)
        print(f"Found {len(results)} results:")
        
        for i, result in enumerate(results):
            print(f"  {i+1}. Score: {result['score']:.3f}")
            print(f"     Q: {result['question'][:50]}...")
            print(f"     A: {result['answer'][:50]}...")
            print(f"     Category: {result['category']}")
            
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
