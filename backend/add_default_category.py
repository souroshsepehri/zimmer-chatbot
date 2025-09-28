#!/usr/bin/env python3
"""
Script to add a default category to the database
"""

from sqlalchemy.orm import Session
from core.db import engine, Base
from models.faq import Category

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Create a session
db = Session(engine)

try:
    # Check if any categories exist
    existing_categories = db.query(Category).count()
    
    if existing_categories == 0:
        # Add a default category
        default_category = Category(
            name="عمومی",
            slug="general"
        )
        db.add(default_category)
        db.commit()
        print("✅ Default category 'عمومی' added successfully!")
    else:
        print(f"✅ Database already has {existing_categories} categories")
        
    # List all categories
    categories = db.query(Category).all()
    print("\n📋 Current categories:")
    for cat in categories:
        print(f"  - {cat.name} (slug: {cat.slug})")
        
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
