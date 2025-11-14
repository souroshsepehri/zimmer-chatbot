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
    
    def search_faqs(self, query: str, min_score: float = 20.0) -> List[Dict[str, Any]]:
        """Simple but effective FAQ search with quality threshold"""
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
            matched_words = 0
            total_query_words = 0
            
            # Exact match in question (highest priority)
            if query_lower in question_lower:
                score += 100
            
            # Exact match in answer
            if query_lower in answer_lower:
                score += 50
            
            # Word-by-word matching with better scoring
            query_words = re.findall(r'\b\w+\b', query_lower)
            total_query_words = len([w for w in query_words if len(w) > 2])
            
            for word in query_words:
                if len(word) > 2:  # Only consider words longer than 2 characters
                    # Check if word appears in question (higher weight)
                    if word in question_lower:
                        score += 15  # Increased from 10
                        matched_words += 1
                    # Check if word appears in answer (lower weight)
                    elif word in answer_lower:
                        score += 5
            
            # Bonus for matching multiple words (better relevance)
            if total_query_words > 0:
                match_ratio = matched_words / total_query_words
                if match_ratio >= 0.7:  # 70% or more words matched
                    score += 30  # Increased bonus
                elif match_ratio >= 0.5:  # 50% or more words matched
                    score += 20
                elif match_ratio >= 0.3:  # 30% or more words matched
                    score += 10
            
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
            
            # Only include results that meet minimum score threshold
            if score >= min_score:
                # Normalize score to 0-1 range for consistency
                # Max score can be: 100 (exact question) + 50 (exact answer) + 15*words (word matches) + 30 (bonus) = ~250+
                normalized_score = min(score / 250.0, 1.0)  # Adjusted max score
                results.append({
                    "id": faq["id"],
                    "question": faq["question"],
                    "answer": faq["answer"],
                    "category": faq["category"],
                    "score": normalized_score,
                    "raw_score": score,  # Keep raw score for debugging
                    "match_ratio": matched_words / total_query_words if total_query_words > 0 else 0  # Add match ratio
                })
        
        # Sort by score (highest first)
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Return top 3 results, but only if they have good scores
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
            
            # Search for matching FAQs with quality threshold
            # Higher min_score means stricter matching (only good matches)
            results = self.search_faqs(question, min_score=20.0)
            
            if results:
                # Quality check: Only use result if score is high enough
                best_match = results[0]
                match_score = best_match.get("score", 0)
                raw_score = best_match.get("raw_score", 0)
                
                # Minimum quality threshold: score must be at least 0.3 (30% match) or raw score >= 30
                min_quality_threshold = 0.3
                if match_score < min_quality_threshold and raw_score < 30:
                    logger.info(f"Match score too low ({match_score:.2f}), using fallback")
                    return {
                        "answer": self.fallback_answer,
                        "source": "fallback",
                        "success": False,
                        "intent": intent_result.intent.value if intent_result else "unknown",
                        "confidence": intent_result.confidence if intent_result else 0.0,
                        "context": intent_result.context if intent_result else None,
                        "all_matches": results
                    }
                
                # Smart ranking based on intent
                try:
                    if intent_result:
                        # Rank results based on intent
                        ranked_results = intent_detector.rank_answers(intent_result, results)
                        if ranked_results and len(ranked_results) > 0:
                            # Use ranked result only if it has good score
                            ranked_best = ranked_results[0]
                            if ranked_best.get("score", 0) >= min_quality_threshold:
                                best_match = ranked_best
                            else:
                                # If ranked result is poor, use original best match
                                logger.info("Ranked result score too low, using original best match")
                except Exception as e:
                    logger.warning(f"Error ranking results: {e}, using first result")
                
                # Ensure best_match has required fields with safe defaults
                logger.info(f"Using FAQ match: {best_match.get('question', '')[:50]}... (score: {match_score:.2f})")
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
