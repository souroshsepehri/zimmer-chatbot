"""
Ultra-simple chatbot that focuses on reliable database reading
"""

import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from models.faq import FAQ
from core.db import get_db
from .smart_intent_detector import get_smart_intent_detector
import logging

logger = logging.getLogger(__name__)

class SimpleChatbot:
    """
    Ultra-simple chatbot that reliably reads from database
    """
    
    def __init__(self):
        self.faqs = []
        self.fallback_answer = "متأسفانه پاسخ مناسبی برای این سؤال پیدا نکردم. لطفاً سؤال خود را به شکل دیگری مطرح کنید."
    
    def load_faqs_from_db(self) -> bool:
        """Load FAQs directly from database with error handling"""
        try:
            # Use provided database session or create a new one
            if hasattr(self, 'db_session') and self.db_session:
                db = self.db_session
            else:
                db = next(get_db())
            
            # Get all active FAQs
            faqs = db.query(FAQ).filter(FAQ.is_active == True).all()
            
            self.faqs = []
            for faq in faqs:
                # Handle category safely
                category_name = None
                try:
                    if faq.category:
                        category_name = faq.category.name
                except:
                    category_name = "عمومی"
                
                self.faqs.append({
                    "id": faq.id,
                    "question": faq.question,
                    "answer": faq.answer,
                    "category": category_name
                })
            
            # Only close the database session if we created it
            if not (hasattr(self, 'db_session') and self.db_session):
                db.close()
            logger.info(f"Loaded {len(self.faqs)} FAQs from database")
            return True
            
        except Exception as e:
            logger.error(f"Error loading FAQs: {e}")
            self.faqs = []
            return False
    
    def search_faqs(self, query: str) -> List[Dict[str, Any]]:
        """Simple but effective FAQ search"""
        if not self.faqs:
            logger.warning("No FAQs loaded")
            return []
        
        query_lower = query.lower().strip()
        if not query_lower:
            return []
        
        results = []
        
        for faq in self.faqs:
            score = 0
            question_lower = faq["question"].lower()
            answer_lower = faq["answer"].lower()
            
            # Exact match in question (highest priority)
            if query_lower in question_lower:
                score += 100
            
            # Exact match in answer
            if query_lower in answer_lower:
                score += 50
            
            # Word-by-word matching
            query_words = re.findall(r'\b\w+\b', query_lower)
            for word in query_words:
                if len(word) > 2:  # Only consider words longer than 2 characters
                    if word in question_lower:
                        score += 10
                    if word in answer_lower:
                        score += 5
            
            # Persian keyword matching
            persian_matches = {
                'سفارش': ['سفارش', 'خرید', 'خریدن', 'order'],
                'پشتیبانی': ['پشتیبانی', 'کمک', 'راهنمایی', 'support', 'help'],
                'ساعت': ['ساعت', 'زمان', 'وقت', 'time'],
                'قیمت': ['قیمت', 'هزینه', 'پول', 'price', 'cost'],
                'ارسال': ['ارسال', 'ارسال', 'پست', 'shipping', 'delivery'],
                'بازگشت': ['بازگشت', 'مرجوع', 'برگشت', 'return'],
                'تماس': ['تماس', 'ارتباط', 'contact'],
                'سوال': ['سوال', 'سؤال', 'question'],
                'پاسخ': ['پاسخ', 'answer', 'reply']
            }
            
            for category, keywords in persian_matches.items():
                if any(keyword in query_lower for keyword in keywords):
                    if any(keyword in question_lower for keyword in keywords):
                        score += 15
                    if any(keyword in answer_lower for keyword in keywords):
                        score += 8
            
            if score > 0:
                results.append({
                    "id": faq["id"],
                    "question": faq["question"],
                    "answer": faq["answer"],
                    "category": faq["category"],
                    "score": score
                })
        
        # Sort by score (highest first)
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Return top 3 results
        return results[:3]
    
    def get_answer(self, question: str) -> Dict[str, Any]:
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
                try:
                    if intent_result:
                        # Rank results based on intent
                        ranked_results = intent_detector.rank_answers(intent_result, results)
                        if ranked_results and len(ranked_results) > 0:
                            best_match = ranked_results[0]
                        else:
                            best_match = results[0]
                    else:
                        # Use original ranking if intent detection fails
                        best_match = results[0]
                except Exception as e:
                    logger.warning(f"Error ranking results: {e}, using first result")
                    best_match = results[0]
                
                # Ensure best_match has required fields with safe defaults
                return {
                    "answer": best_match.get("answer", self.fallback_answer),
                    "source": "faq",
                    "success": True,
                    "faq_id": best_match.get("id") or best_match.get("faq_id"),
                    "question": best_match.get("question", ""),
                    "category": best_match.get("category"),
                    "score": best_match.get("final_score") or best_match.get("score", 0),
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
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get chatbot statistics"""
        try:
            if self.load_faqs_from_db():
                return {
                    "status": "healthy",
                    "faq_count": len(self.faqs),
                    "faqs": [
                        {
                            "id": faq["id"],
                            "question": faq["question"][:50] + "..." if len(faq["question"]) > 50 else faq["question"],
                            "category": faq["category"]
                        }
                        for faq in self.faqs[:5]  # Show first 5 FAQs
                    ]
                }
            else:
                return {
                    "status": "error",
                    "faq_count": 0,
                    "error": "Could not load FAQs from database"
                }
        except Exception as e:
            return {
                "status": "error",
                "faq_count": 0,
                "error": str(e)
            }

# Global instance
_simple_chatbot = None

def get_simple_chatbot():
    """Get simple chatbot instance"""
    global _simple_chatbot
    if _simple_chatbot is None:
        _simple_chatbot = SimpleChatbot()
    return _simple_chatbot
