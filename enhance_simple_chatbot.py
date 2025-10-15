#!/usr/bin/env python3
"""
Enhance the existing simple chatbot with smart intent detection
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def enhance_simple_chatbot():
    """Enhance the simple chatbot with intent detection"""
    print("🔧 Enhancing Simple Chatbot with Intent Detection")
    print("=" * 60)
    
    try:
        # Read the current simple chatbot file
        with open('backend/services/simple_chatbot.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add intent detection import at the top
        if 'from services.smart_intent_detector import get_smart_intent_detector' not in content:
            # Find the import section and add our import
            import_section = content.find('import logging')
            if import_section != -1:
                new_import = 'from services.smart_intent_detector import get_smart_intent_detector\n'
                content = content[:import_section] + new_import + content[import_section:]
        
        # Enhance the get_answer method
        old_get_answer = '''def get_answer(self, question: str) -> Dict[str, Any]:
        """Get answer for a question"""
        try:
            # Load FAQs fresh from database
            if not self.load_faqs_from_db():
                return {
                    "answer": "خطا در خواندن پایگاه داده. لطفاً دوباره تلاش کنید.",
                    "source": "error",
                    "success": False
                }
            
            # Search for matching FAQs
            results = self.search_faqs(question)
            
            if results:
                # Use the best match
                best_match = results[0]
                return {
                    "answer": best_match["answer"],
                    "source": "faq",
                    "success": True,
                    "faq_id": best_match["id"],
                    "question": best_match["question"],
                    "category": best_match["category"],
                    "score": best_match["score"],
                    "all_matches": results
                }
            else:
                return {
                    "answer": self.fallback_answer,
                    "source": "fallback",
                    "success": False,
                    "all_matches": []
                }
                
        except Exception as e:
            logger.error(f"Error getting answer: {e}")
            return {
                "answer": f"خطا در پردازش سؤال: {str(e)}",
                "source": "error",
                "success": False
            }'''
        
        new_get_answer = '''def get_answer(self, question: str) -> Dict[str, Any]:
        """Get answer for a question with smart intent detection"""
        try:
            # Load FAQs fresh from database
            if not self.load_faqs_from_db():
                return {
                    "answer": "خطا در خواندن پایگاه داده. لطفاً دوباره تلاش کنید.",
                    "source": "error",
                    "success": False
                }
            
            # Detect user intent
            try:
                intent_detector = get_smart_intent_detector()
                intent_result = intent_detector.detect_intent(question)
                logger.info(f"Detected intent: {intent_result.intent.value} (confidence: {intent_result.confidence:.2f})")
            except Exception as e:
                logger.warning(f"Intent detection failed: {e}")
                intent_result = None
            
            # Search for matching FAQs
            results = self.search_faqs(question)
            
            if results:
                # Smart ranking based on intent
                if intent_result:
                    # Rank results based on intent
                    ranked_results = intent_detector.rank_answers(intent_result, results)
                    best_match = ranked_results[0]
                else:
                    # Use original ranking if intent detection fails
                    best_match = results[0]
                
                return {
                    "answer": best_match["answer"],
                    "source": "faq",
                    "success": True,
                    "faq_id": best_match["id"],
                    "question": best_match["question"],
                    "category": best_match["category"],
                    "score": best_match.get("final_score", best_match.get("score", 0)),
                    "intent": intent_result.intent.value if intent_result else "unknown",
                    "confidence": intent_result.confidence if intent_result else 0.0,
                    "context": intent_result.context if intent_result else None,
                    "intent_match": best_match.get("intent_match", False) if intent_result else None,
                    "all_matches": results
                }
            else:
                return {
                    "answer": self.fallback_answer,
                    "source": "fallback",
                    "success": False,
                    "intent": intent_result.intent.value if intent_result else "unknown",
                    "confidence": intent_result.confidence if intent_result else 0.0,
                    "context": intent_result.context if intent_result else None,
                    "all_matches": []
                }
                
        except Exception as e:
            logger.error(f"Error getting answer: {e}")
            return {
                "answer": f"خطا در پردازش سؤال: {str(e)}",
                "source": "error",
                "success": False
            }'''
        
        # Replace the method
        content = content.replace(old_get_answer, new_get_answer)
        
        # Write the enhanced file
        with open('backend/services/simple_chatbot.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Enhanced simple chatbot with intent detection")
        return True
        
    except Exception as e:
        print(f"❌ Error enhancing chatbot: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enhanced_chatbot():
    """Test the enhanced chatbot"""
    print("\n🧪 Testing Enhanced Chatbot")
    print("=" * 50)
    
    try:
        # Test the enhanced chatbot
        from services.simple_chatbot import get_simple_chatbot
        
        chatbot = get_simple_chatbot()
        
        test_queries = [
            "قیمت",
            "گارانتی",
            "سفارش",
            "تماس",
            "کمک",
            "ساعت"
        ]
        
        for query in test_queries:
            print(f"Testing: '{query}'")
            result = chatbot.get_answer(query)
            
            print(f"  Intent: {result.get('intent', 'unknown')}")
            print(f"  Confidence: {result.get('confidence', 0):.2f}")
            print(f"  Success: {result.get('success', False)}")
            print(f"  Answer: {result.get('answer', '')[:100]}...")
            if result.get('intent_match'):
                print(f"  🎯 Intent Match: ✅")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing enhanced chatbot: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🚀 Enhancing Simple Chatbot")
    print("=" * 60)
    
    # Enhance the chatbot
    enhance_success = enhance_simple_chatbot()
    
    if enhance_success:
        # Test the enhanced chatbot
        test_success = test_enhanced_chatbot()
        
        print("=" * 60)
        print("📊 ENHANCEMENT SUMMARY")
        print("=" * 60)
        print(f"Enhancement: {'✅ Success' if enhance_success else '❌ Failed'}")
        print(f"Testing: {'✅ Success' if test_success else '❌ Failed'}")
        
        if enhance_success and test_success:
            print("\n🎉 Chatbot enhanced successfully!")
            print("The chatbot now includes:")
            print("- Smart intent detection")
            print("- Better answer ranking")
            print("- Single best answer selection")
            print("- Intent-based context understanding")
        else:
            print("\n❌ Enhancement failed. Check the errors above.")
    else:
        print("\n❌ Could not enhance the chatbot.")

if __name__ == "__main__":
    main()
