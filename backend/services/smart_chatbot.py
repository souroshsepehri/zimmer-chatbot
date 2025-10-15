"""
Smart Chatbot Service - Uses intent detection to provide the best single answer
"""

import logging
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from services.smart_intent_detector import get_smart_intent_detector, IntentResult
from services.simple_chatbot import SimpleChatbot
from models.faq import FAQ
from core.db import get_db

logger = logging.getLogger(__name__)

class SmartChatbot:
    """
    Smart chatbot that uses intent detection to provide the best single answer
    """
    
    def __init__(self):
        self.intent_detector = get_smart_intent_detector()
        self.simple_chatbot = SimpleChatbot()
        self.fallback_answer = "متأسفانه پاسخ مناسبی برای این سؤال پیدا نکردم. لطفاً سؤال خود را به شکل دیگری مطرح کنید یا با پشتیبانی تماس بگیرید."
    
    def get_smart_answer(self, question: str) -> Dict[str, Any]:
        """
        Get the best single answer using intent detection and smart ranking
        """
        try:
            # 1. Detect user intent
            intent_result = self.intent_detector.detect_intent(question)
            logger.info(f"Detected intent: {intent_result.intent.value} (confidence: {intent_result.confidence:.2f})")
            
            # 2. Load FAQs from database
            if not self.simple_chatbot.load_faqs_from_db():
                return {
                    "answer": "خطا در خواندن پایگاه داده. لطفاً دوباره تلاش کنید.",
                    "source": "error",
                    "success": False,
                    "intent": intent_result.intent.value,
                    "confidence": intent_result.confidence
                }
            
            # 3. Search for relevant FAQs
            search_results = self.simple_chatbot.search_faqs(question)
            
            if not search_results:
                return {
                    "answer": self.fallback_answer,
                    "source": "fallback",
                    "success": False,
                    "intent": intent_result.intent.value,
                    "confidence": intent_result.confidence,
                    "context": intent_result.context
                }
            
            # 4. Rank results based on intent
            ranked_results = self.intent_detector.rank_answers(intent_result, search_results)
            
            # 5. Select the best answer
            best_result = ranked_results[0]
            
            # 6. Quality check - if confidence is too low, use fallback
            if intent_result.confidence < 0.3 and best_result['final_score'] < 1.0:
                return {
                    "answer": self.fallback_answer,
                    "source": "fallback",
                    "success": False,
                    "intent": intent_result.intent.value,
                    "confidence": intent_result.confidence,
                    "context": intent_result.context,
                    "reason": "Low confidence and poor match"
                }
            
            # 7. Prepare response
            response = {
                "answer": best_result["answer"],
                "source": "faq",
                "success": True,
                "faq_id": best_result["id"],
                "question": best_result["question"],
                "category": best_result["category"],
                "score": best_result["final_score"],
                "intent": intent_result.intent.value,
                "confidence": intent_result.confidence,
                "context": intent_result.context,
                "intent_match": best_result.get('intent_match', False),
                "suggested_actions": intent_result.suggested_actions
            }
            
            # 8. Add debug info if needed
            if len(ranked_results) > 1:
                response["alternative_answers"] = [
                    {
                        "question": r["question"],
                        "answer": r["answer"][:100] + "...",
                        "score": r["final_score"]
                    } for r in ranked_results[1:3]  # Show top 2 alternatives
                ]
            
            logger.info(f"Selected answer: {best_result['question'][:50]}... (score: {best_result['final_score']:.3f})")
            return response
            
        except Exception as e:
            logger.error(f"Error in smart chatbot: {e}")
            return {
                "answer": f"خطا در پردازش سؤال: {str(e)}",
                "source": "error",
                "success": False,
                "intent": "unknown",
                "confidence": 0.0
            }
    
    def get_answer_with_explanation(self, question: str) -> Dict[str, Any]:
        """
        Get answer with detailed explanation of the decision process
        """
        try:
            # Get the smart answer
            result = self.get_smart_answer(question)
            
            # Add explanation
            if result["success"]:
                explanation = f"بر اساس تشخیص نیت شما ({result['intent']}) و جستجو در پایگاه داده، بهترین پاسخ انتخاب شد."
                if result.get('intent_match'):
                    explanation += " این پاسخ با نیت شما مطابقت دارد."
                else:
                    explanation += " این پاسخ نزدیک‌ترین پاسخ موجود است."
            else:
                explanation = f"نیت شما ({result.get('intent', 'نامشخص')}) تشخیص داده شد، اما پاسخ مناسبی در پایگاه داده پیدا نشد."
            
            result["explanation"] = explanation
            return result
            
        except Exception as e:
            logger.error(f"Error in explanation: {e}")
            return {
                "answer": f"خطا در پردازش سؤال: {str(e)}",
                "source": "error",
                "success": False,
                "explanation": "خطا در پردازش درخواست"
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get chatbot statistics"""
        return {
            "type": "smart_chatbot",
            "intent_detection": True,
            "smart_ranking": True,
            "fallback_answer": self.fallback_answer
        }

# Global instance
_smart_chatbot = None

def get_smart_chatbot() -> SmartChatbot:
    """Get smart chatbot instance"""
    global _smart_chatbot
    if _smart_chatbot is None:
        _smart_chatbot = SmartChatbot()
    return _smart_chatbot
