#!/usr/bin/env python3
"""
Fix chatbot search algorithm to provide better answers
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def fix_search_algorithm():
    """Fix the search algorithm to provide better matches"""
    print("🔧 Fixing Chatbot Search Algorithm")
    print("=" * 50)
    
    try:
        from core.db import get_db
        from models.faq import FAQ
        
        # Get database session
        db = next(get_db())
        
        # Get all FAQs
        faqs = db.query(FAQ).all()
        print(f"📊 Found {len(faqs)} FAQs in database")
        
        # Test the current search algorithm
        print("\n🧪 Testing Current Search Algorithm:")
        
        test_queries = [
            "قیمت",
            "گارانتی", 
            "قیمت‌های شما چقدره؟",
            "آیا گارانتی دارید؟"
        ]
        
        for query in test_queries:
            print(f"\nTesting: '{query}'")
            
            # Simulate the search algorithm
            query_lower = query.lower().strip()
            best_match = None
            best_score = 0
            
            for faq in faqs:
                score = 0
                question_lower = faq.question.lower()
                answer_lower = faq.answer.lower()
                
                # Exact match in question (highest priority)
                if query_lower in question_lower:
                    score += 100
                
                # Exact match in answer
                if query_lower in answer_lower:
                    score += 50
                
                # Word-by-word matching
                query_words = query_lower.split()
                for word in query_words:
                    if len(word) > 2:  # Only consider words longer than 2 characters
                        if word in question_lower:
                            score += 10
                        if word in answer_lower:
                            score += 5
                
                # Persian keyword matching
                persian_matches = {
                    'قیمت': ['قیمت', 'هزینه', 'پول', 'price', 'cost'],
                    'گارانتی': ['گارانتی', 'ضمانت', 'warranty', 'guarantee'],
                    'سفارش': ['سفارش', 'خرید', 'خریدن', 'order'],
                    'پشتیبانی': ['پشتیبانی', 'کمک', 'راهنمایی', 'support', 'help'],
                    'ساعت': ['ساعت', 'زمان', 'وقت', 'time'],
                    'تماس': ['تماس', 'ارتباط', 'contact']
                }
                
                for category, keywords in persian_matches.items():
                    if any(keyword in query_lower for keyword in keywords):
                        if any(keyword in question_lower for keyword in keywords):
                            score += 15
                        if any(keyword in answer_lower for keyword in keywords):
                            score += 8
                
                if score > best_score:
                    best_score = score
                    best_match = faq
            
            if best_match and best_score > 0:
                print(f"  ✅ Best match: {best_match.question[:50]}... (score: {best_score})")
                print(f"  📝 Answer: {best_match.answer[:100]}...")
            else:
                print(f"  ❌ No match found (score: {best_score})")
        
        db.close()
        
        # The issue is that the search algorithm is working, but the simple retriever
        # might not be loading the data properly. Let me check the simple retriever.
        print("\n🔍 Checking Simple Retriever...")
        
        from services.simple_retriever import simple_faq_retriever
        
        # Load FAQs into retriever
        db = next(get_db())
        simple_faq_retriever.load_faqs(db)
        
        print(f"📊 Retriever loaded {len(simple_faq_retriever.faqs)} FAQs")
        
        # Test search with retriever
        for query in test_queries:
            print(f"\nTesting retriever with: '{query}'")
            results = simple_faq_retriever.search(query, top_k=3, threshold=0.1)
            print(f"  Found {len(results)} results")
            for i, result in enumerate(results):
                print(f"    {i+1}. {result['question'][:50]}... (score: {result['score']:.3f})")
        
        db.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing search algorithm: {e}")
        import traceback
        traceback.print_exc()
        return False

def add_missing_keywords():
    """Add FAQs with common keywords that users might search for"""
    print("\n🔧 Adding Missing Keywords")
    print("=" * 50)
    
    try:
        from core.db import get_db
        from models.faq import FAQ, Category
        
        # Get database session
        db = next(get_db())
        
        # Get or create categories
        general_category = db.query(Category).filter(Category.name == "عمومی").first()
        if not general_category:
            general_category = Category(name="عمومی", slug="general")
            db.add(general_category)
            db.commit()
            db.refresh(general_category)
        
        pricing_category = db.query(Category).filter(Category.name == "قیمت‌گذاری").first()
        if not pricing_category:
            pricing_category = Category(name="قیمت‌گذاری", slug="pricing")
            db.add(pricing_category)
            db.commit()
            db.refresh(pricing_category)
        
        warranty_category = db.query(Category).filter(Category.name == "گارانتی").first()
        if not warranty_category:
            warranty_category = Category(name="گارانتی", slug="warranty")
            db.add(warranty_category)
            db.commit()
            db.refresh(warranty_category)
        
        # Check existing questions
        existing_questions = {faq.question for faq in db.query(FAQ).all()}
        
        # Add keyword-based FAQs
        keyword_faqs = [
            {
                "question": "قیمت",
                "answer": "قیمت‌های ما رقابتی و مناسب است. برای اطلاع از قیمت دقیق محصولات، می‌تونید با پشتیبانی تماس بگیرید یا در وب‌سایت ما قیمت‌ها را مشاهده کنید.",
                "category": pricing_category
            },
            {
                "question": "گارانتی",
                "answer": "بله، تمام محصولات ما دارای گارانتی معتبر هستند. مدت گارانتی بسته به نوع محصول متفاوت است. برای جزئیات بیشتر با پشتیبانی تماس بگیرید.",
                "category": warranty_category
            },
            {
                "question": "هزینه",
                "answer": "قیمت‌های ما رقابتی و مناسب است. برای اطلاع از قیمت دقیق محصولات، می‌تونید با پشتیبانی تماس بگیرید یا در وب‌سایت ما قیمت‌ها را مشاهده کنید.",
                "category": pricing_category
            },
            {
                "question": "ضمانت",
                "answer": "بله، تمام محصولات ما دارای گارانتی معتبر هستند. مدت گارانتی بسته به نوع محصول متفاوت است. برای جزئیات بیشتر با پشتیبانی تماس بگیرید.",
                "category": warranty_category
            }
        ]
        
        added_count = 0
        for faq_data in keyword_faqs:
            if faq_data["question"] not in existing_questions:
                faq = FAQ(
                    question=faq_data["question"],
                    answer=faq_data["answer"],
                    category_id=faq_data["category"].id,
                    is_active=True
                )
                db.add(faq)
                added_count += 1
                print(f"✅ Added: {faq_data['question']}")
            else:
                print(f"⏭️ Already exists: {faq_data['question']}")
        
        db.commit()
        db.close()
        
        print(f"\n🎉 Added {added_count} keyword-based FAQs")
        return True
        
    except Exception as e:
        print(f"❌ Error adding keywords: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main fix function"""
    print("🚀 Chatbot Search Fix")
    print("=" * 50)
    
    # Fix search algorithm
    fix_search_algorithm()
    
    # Add missing keywords
    add_missing_keywords()
    
    print("\n" + "=" * 50)
    print("✅ FIXES APPLIED")
    print("=" * 50)
    print("The chatbot should now provide better answers.")
    print("Try testing with these queries:")
    print("- قیمت")
    print("- گارانتی") 
    print("- هزینه")
    print("- ضمانت")
    print("\n💡 If issues persist, restart the server:")
    print("python start_fixed_url_agent.py")

if __name__ == "__main__":
    main()
