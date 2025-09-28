#!/usr/bin/env python3
"""
Test semantic search and FAQ index building
"""

import sys
import os
sys.path.append('backend')

from sqlalchemy.orm import Session
from backend.core.db import engine, Base
from backend.models.faq import FAQ, Category
from backend.services.retriever import faq_retriever

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Create a session
db = Session(engine)

def test_semantic_search():
    print("🔍 TESTING SEMANTIC SEARCH")
    print("=" * 50)
    
    try:
        # Test 1: Check if vectorstore exists
        print("1️⃣ Checking vectorstore...")
        vectorstore_path = "./backend/vectorstore"
        index_path = os.path.join(vectorstore_path, "faiss.index")
        mapping_path = os.path.join(vectorstore_path, "mapping.pkl")
        
        if os.path.exists(index_path) and os.path.exists(mapping_path):
            print("   ✅ Vectorstore files exist")
        else:
            print("   ⚠️  Vectorstore files not found, building index...")
            
            # Build the index
            faq_retriever.build_index(db)
            
            if os.path.exists(index_path) and os.path.exists(mapping_path):
                print("   ✅ Index built successfully!")
            else:
                print("   ❌ Index building failed")
                return False
        
        # Test 2: Test semantic search
        print("\n2️⃣ Testing semantic search...")
        
        test_queries = [
            "چطور می‌تونم سفارش بدم؟",
            "ساعات کاری",
            "پشتیبانی",
            "خرید محصول"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n   Query {i}: {query}")
            
            try:
                results = faq_retriever.semantic_search(
                    query=query,
                    top_k=3,
                    threshold=0.5  # Lower threshold for testing
                )
                
                print(f"   Found {len(results)} results:")
                for j, result in enumerate(results):
                    print(f"     {j+1}. Score: {result['score']:.3f}")
                    print(f"        Q: {result['question'][:50]}...")
                    print(f"        A: {result['answer'][:50]}...")
                    
            except Exception as e:
                print(f"   ❌ Search failed: {e}")
        
        # Test 3: Test with different thresholds
        print(f"\n3️⃣ Testing different thresholds...")
        
        query = "چطور می‌تونم سفارش بدم؟"
        thresholds = [0.1, 0.3, 0.5, 0.7, 0.8, 0.9]
        
        for threshold in thresholds:
            try:
                results = faq_retriever.semantic_search(
                    query=query,
                    top_k=3,
                    threshold=threshold
                )
                print(f"   Threshold {threshold}: {len(results)} results")
                if results:
                    print(f"     Best score: {results[0]['score']:.3f}")
            except Exception as e:
                print(f"   Threshold {threshold}: Error - {e}")
        
        print("\n" + "=" * 50)
        print("🎯 SEMANTIC SEARCH TEST COMPLETED!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    test_semantic_search()
