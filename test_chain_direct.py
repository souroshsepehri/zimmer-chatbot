#!/usr/bin/env python3
"""
Test chain directly to debug the issue
"""

import sys
import os
sys.path.append('backend')

from sqlalchemy.orm import Session
from backend.core.db import engine, Base
from backend.models.faq import FAQ, Category
from backend.services.chain import chat_chain

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Create a session
db = Session(engine)

try:
    print("🧪 Testing chat chain directly...")
    
    test_message = "چطور می‌تونم سفارش بدم؟"
    print(f"📝 Test message: {test_message}")
    
    result = chat_chain.process_message(
        message=test_message,
        db=db,
        debug=True
    )
    
    print(f"🤖 Answer: {result['answer']}")
    print(f"📊 Source: {result['source']}")
    print(f"✅ Success: {result['success']}")
    print(f"🔍 Matched FAQ ID: {result['matched_faq_id']}")
    print(f"❓ Unanswered in DB: {result['unanswered_in_db']}")
    
    if result.get('debug_info'):
        debug = result['debug_info']
        print(f"🔧 Debug Info:")
        print(f"   Intent: {debug.get('intent', {}).get('label', 'unknown')}")
        print(f"   Confidence: {debug.get('intent', {}).get('confidence', 0)}")
        print(f"   Retrieval Results: {len(debug.get('retrieval_results', []))}")
        
        for i, ret in enumerate(debug.get('retrieval_results', [])[:3]):
            print(f"     {i+1}. {ret.get('question', '')[:50]}... (score: {ret.get('score', 0):.3f})")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
