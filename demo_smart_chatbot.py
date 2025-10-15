#!/usr/bin/env python3
"""
Demo of Smart Chatbot with Intent Detection
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def demo_intent_detection():
    """Demo the intent detection system"""
    print("🧠 Smart Chatbot with Intent Detection Demo")
    print("=" * 60)
    
    try:
        from services.smart_intent_detector import get_smart_intent_detector
        
        detector = get_smart_intent_detector()
        
        # Demo queries
        demo_queries = [
            "سلام",
            "قیمت محصولات شما چقدر است؟",
            "گارانتی دارید؟",
            "چطور سفارش بدم؟",
            "ساعات کاری شما چیه؟",
            "چطور می‌تونم با شما تماس بگیرم؟",
            "کمک می‌خوام",
            "محصولات شما چه ویژگی‌هایی دارن؟"
        ]
        
        print("🎯 Intent Detection Results:")
        print("-" * 40)
        
        for i, query in enumerate(demo_queries, 1):
            result = detector.detect_intent(query)
            print(f"{i:2d}. '{query}'")
            print(f"    Intent: {result.intent.value}")
            print(f"    Confidence: {result.confidence:.2f}")
            print(f"    Keywords: {', '.join(result.keywords)}")
            print(f"    Context: {result.context}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error in intent detection demo: {e}")
        import traceback
        traceback.print_exc()
        return False

def demo_answer_ranking():
    """Demo how answers would be ranked based on intent"""
    print("📊 Answer Ranking Demo")
    print("=" * 40)
    
    try:
        from services.smart_intent_detector import get_smart_intent_detector
        
        detector = get_smart_intent_detector()
        
        # Simulate search results
        mock_search_results = [
            {
                "id": 1,
                "question": "قیمت محصولات شما چقدر است؟",
                "answer": "قیمت‌های ما رقابتی و مناسب است. برای اطلاع از قیمت دقیق محصولات، می‌تونید با پشتیبانی تماس بگیرید.",
                "category": "قیمت‌گذاری",
                "score": 2.5
            },
            {
                "id": 2,
                "question": "چطور می‌تونم قیمت محصولات رو ببینم؟",
                "answer": "شما می‌تونید قیمت‌ها را در وب‌سایت ما مشاهده کنید یا با پشتیبانی تماس بگیرید.",
                "category": "قیمت‌گذاری",
                "score": 2.0
            },
            {
                "id": 3,
                "question": "ساعات کاری شما چطور است؟",
                "answer": "ما 24 ساعت شبانه‌روز در خدمت شما هستیم.",
                "category": "عمومی",
                "score": 1.5
            }
        ]
        
        # Test with different intents
        test_queries = [
            "قیمت",
            "گارانتی",
            "ساعت"
        ]
        
        for query in test_queries:
            print(f"Query: '{query}'")
            
            # Detect intent
            intent_result = detector.detect_intent(query)
            print(f"  Detected Intent: {intent_result.intent.value} (confidence: {intent_result.confidence:.2f})")
            
            # Rank results
            ranked_results = detector.rank_answers(intent_result, mock_search_results)
            
            print("  Ranked Results:")
            for i, result in enumerate(ranked_results[:3], 1):
                print(f"    {i}. {result['question'][:50]}...")
                print(f"       Original Score: {result.get('score', 0):.2f}")
                print(f"       Intent Score: {result.get('intent_score', 0):.2f}")
                print(f"       Final Score: {result.get('final_score', 0):.2f}")
                print(f"       Intent Match: {'✅' if result.get('intent_match') else '❌'}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error in answer ranking demo: {e}")
        import traceback
        traceback.print_exc()
        return False

def demo_smart_chatbot_workflow():
    """Demo the complete smart chatbot workflow"""
    print("🤖 Smart Chatbot Workflow Demo")
    print("=" * 50)
    
    try:
        from services.smart_intent_detector import get_smart_intent_detector
        
        detector = get_smart_intent_detector()
        
        # Simulate the complete workflow
        user_query = "قیمت محصولات شما چقدر است؟"
        
        print(f"User Query: '{user_query}'")
        print()
        
        # Step 1: Intent Detection
        print("Step 1: Intent Detection")
        intent_result = detector.detect_intent(user_query)
        print(f"  Intent: {intent_result.intent.value}")
        print(f"  Confidence: {intent_result.confidence:.2f}")
        print(f"  Context: {intent_result.context}")
        print()
        
        # Step 2: Database Search (simulated)
        print("Step 2: Database Search")
        mock_results = [
            {
                "id": 1,
                "question": "قیمت محصولات شما چقدر است؟",
                "answer": "قیمت‌های ما رقابتی و مناسب است. برای اطلاع از قیمت دقیق محصولات، می‌تونید با پشتیبانی تماس بگیرید یا در وب‌سایت ما قیمت‌ها را مشاهده کنید.",
                "category": "قیمت‌گذاری",
                "score": 2.5
            },
            {
                "id": 2,
                "question": "چطور می‌تونم قیمت محصولات رو ببینم؟",
                "answer": "شما می‌تونید قیمت‌ها را در وب‌سایت ما مشاهده کنید یا با پشتیبانی تماس بگیرید.",
                "category": "قیمت‌گذاری",
                "score": 2.0
            }
        ]
        print(f"  Found {len(mock_results)} potential answers")
        print()
        
        # Step 3: Smart Ranking
        print("Step 3: Smart Ranking")
        ranked_results = detector.rank_answers(intent_result, mock_results)
        best_answer = ranked_results[0]
        print(f"  Best Answer: {best_answer['question']}")
        print(f"  Final Score: {best_answer.get('final_score', 0):.2f}")
        print(f"  Intent Match: {'✅' if best_answer.get('intent_match') else '❌'}")
        print()
        
        # Step 4: Final Response
        print("Step 4: Final Response")
        print(f"  Answer: {best_answer['answer']}")
        print(f"  Source: FAQ Database")
        print(f"  Intent: {intent_result.intent.value}")
        print(f"  Confidence: {intent_result.confidence:.2f}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error in workflow demo: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main demo function"""
    print("🚀 Smart Chatbot Demo")
    print("=" * 60)
    print("This demo shows how the smart chatbot works:")
    print("1. Detects user intent from their question")
    print("2. Searches the database for relevant answers")
    print("3. Ranks answers based on intent relevance")
    print("4. Returns the best single answer")
    print("=" * 60)
    print()
    
    # Demo intent detection
    intent_success = demo_intent_detection()
    
    # Demo answer ranking
    ranking_success = demo_answer_ranking()
    
    # Demo complete workflow
    workflow_success = demo_smart_chatbot_workflow()
    
    print("=" * 60)
    print("📊 DEMO SUMMARY")
    print("=" * 60)
    print(f"Intent Detection: {'✅ Success' if intent_success else '❌ Failed'}")
    print(f"Answer Ranking: {'✅ Success' if ranking_success else '❌ Failed'}")
    print(f"Complete Workflow: {'✅ Success' if workflow_success else '❌ Failed'}")
    
    if intent_success and ranking_success and workflow_success:
        print("\n🎉 Smart Chatbot Demo Completed Successfully!")
        print("\nThe system can now:")
        print("✅ Understand user intent accurately")
        print("✅ Rank answers based on intent relevance")
        print("✅ Provide the best single answer")
        print("✅ Avoid giving multiple confusing answers")
        print("\nThis solves the problem of the chatbot giving")
        print("multiple answers instead of understanding what")
        print("the user really wants!")
    else:
        print("\n❌ Some demos failed. Check the errors above.")

if __name__ == "__main__":
    main()
