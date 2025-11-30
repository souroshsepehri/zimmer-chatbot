"""
Enhanced Answering Agent - Centralized agent for answering user questions

This agent is the main entry point for processing user queries. It:
1. Normalizes and understands questions (handles different phrasings and tones)
2. Detects intent using smart intent detection
3. Retrieves relevant data from database and existing services
4. Composes accurate, helpful responses using LLM when available
5. Logs all operations for observability

Main entry point: answer_user_query(user_id, message, context=None, db=None)

Architecture:
- Uses existing services: smart_intent_detector, answer_generator, retrievers
- Extensible intent handlers
- Comprehensive logging to database and application logs
- Handles errors gracefully with fallbacks
"""

import re
import logging
import json
from typing import Dict, Any, List, Optional, Tuple, Callable
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from models.faq import FAQ, Category
from models.log import ChatLog
from core.db import get_db
from core.config import settings

# Import existing services for reuse
try:
    from services.smart_intent_detector import get_smart_intent_detector, IntentType
except ImportError:
    get_smart_intent_detector = None
    IntentType = None

try:
    from services.answer import get_answer_generator
except ImportError:
    get_answer_generator = None

try:
    from services.simple_retriever import simple_faq_retriever
except ImportError:
    simple_faq_retriever = None

try:
    from services.retriever import faq_retriever
except ImportError:
    faq_retriever = None

logger = logging.getLogger(__name__)


class AnsweringAgent:
    """
    Enhanced Centralized Answering Agent that handles all user queries.
    
    This agent replaces the previous ad-hoc answering logic with a
    structured, extensible approach that:
    - Handles different phrasings and tones
    - Uses smart intent detection
    - Leverages LLM for answer composition when available
    - Provides comprehensive logging
    """
    
    def __init__(self):
        """Initialize the answering agent"""
        self.fallback_answer = (
            "متأسفانه پاسخ مناسبی برای این سؤال پیدا نکردم. "
            "لطفاً سؤال خود را به شکل دیگری مطرح کنید یا با پشتیبانی تماس بگیرید."
        )
        
        # Initialize services (lazy loading)
        self._intent_detector = None
        self._answer_generator = None
        
        # Intent handlers mapping - easily extensible
        self.intent_handlers: Dict[str, Callable] = {
            "greeting": self._handle_greeting_intent,
            "pricing": self._handle_faq_intent,  # Pricing questions go to FAQ
            "warranty": self._handle_faq_intent,
            "order": self._handle_faq_intent,
            "support": self._handle_faq_intent,
            "hours": self._handle_faq_intent,
            "contact": self._handle_faq_intent,
            "product_info": self._handle_faq_intent,
            "complaint": self._handle_faq_intent,
            "general_question": self._handle_faq_intent,
            "category": self._handle_category_intent,
            "unknown": self._handle_unknown_intent,
        }
    
    @property
    def intent_detector(self):
        """Lazy load intent detector"""
        if self._intent_detector is None and get_smart_intent_detector:
            try:
                self._intent_detector = get_smart_intent_detector()
            except Exception as e:
                logger.warning(f"Could not load intent detector: {e}")
        return self._intent_detector
    
    @property
    def answer_generator(self):
        """Lazy load answer generator"""
        if self._answer_generator is None and get_answer_generator:
            try:
                self._answer_generator = get_answer_generator()
            except Exception as e:
                logger.warning(f"Could not load answer generator: {e}")
        return self._answer_generator
    
    def answer_user_query(
        self,
        user_id: Optional[str],
        message: str,
        context: Optional[Dict[str, Any]] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Main entry point for answering user queries.
        
        This function handles the complete flow:
        1. Normalize question (handle different phrasings)
        2. Detect intent
        3. Retrieve relevant data
        4. Compose answer
        5. Log everything
        
        Args:
            user_id: Optional user identifier
            message: User's question/message
            context: Optional context (e.g., session data, previous messages, category_filter)
            db: Optional database session (will create one if not provided)
        
        Returns:
            Dictionary with:
            - answer: The final answer text
            - intent: Detected intent
            - confidence: Confidence score (0-1)
            - source: Data source used (faq, database, llm, fallback)
            - success: Whether a good answer was found
            - matched_ids: IDs of records used in the answer
            - metadata: Additional metadata about the query
        """
        start_time = datetime.now()
        
        # Create DB session if not provided
        should_close_db = False
        if db is None:
            db = next(get_db())
            should_close_db = True
        
        try:
            # Initialize response structure
            response = {
                "answer": self.fallback_answer,
                "intent": "unknown",
                "confidence": 0.0,
                "source": "fallback",
                "success": False,
                "matched_ids": [],
                "metadata": {
                    "original_message": message,
                    "normalized_message": "",
                    "canonical_question": "",
                    "tables_queried": [],
                    "retrieval_method": None,
                    "processing_time_ms": 0,
                    "llm_used": False,
                }
            }
            
            # 1. Normalize and understand the question
            normalized_message = self._normalize_question(message)
            response["metadata"]["normalized_message"] = normalized_message
            
            # Validate input
            if not normalized_message or len(normalized_message.strip()) < 2:
                response["answer"] = "لطفاً سؤال خود را به صورت واضح مطرح کنید."
                response["source"] = "validation_error"
                response["metadata"]["processing_time_ms"] = (
                    (datetime.now() - start_time).total_seconds() * 1000
                )
                self._log_query(user_id, message, normalized_message, "validation_error", 
                              0.0, response["answer"], "validation_error", False, [], 
                              [], response["metadata"]["processing_time_ms"], db)
                return response
            
            # Handle very long messages
            if len(normalized_message) > 1000:
                normalized_message = normalized_message[:1000]
                response["metadata"]["truncated"] = True
            
            # Create canonical question (for better matching across phrasings)
            canonical_question = self._create_canonical_question(normalized_message)
            response["metadata"]["canonical_question"] = canonical_question
            
            # 2. Detect intent using smart intent detector
            intent, intent_confidence, intent_metadata = self._detect_intent_enhanced(
                normalized_message, canonical_question
            )
            response["intent"] = intent
            response["confidence"] = intent_confidence
            response["metadata"].update(intent_metadata)
            
            logger.info(
                f"Detected intent: {intent} (confidence: {intent_confidence:.2f}) "
                f"for message: {normalized_message[:50]}"
            )
            
            # 3. Decide what data is needed and retrieve it
            handler = self.intent_handlers.get(intent, self.intent_handlers["unknown"])
            result = handler(normalized_message, canonical_question, db, context)
            
            # 4. Compose final answer (use LLM if available and needed)
            if result.get("success") and result.get("answer"):
                # If we have FAQ data, optionally enhance with LLM
                if self.answer_generator and result.get("source") == "faq":
                    enhanced_answer = self._enhance_answer_with_llm(
                        user_message=normalized_message,
                        faq_data=result.get("faq_data"),
                        original_answer=result.get("answer")
                    )
                    if enhanced_answer:
                        result["answer"] = enhanced_answer
                        result["metadata"]["llm_used"] = True
                        response["metadata"]["llm_used"] = True
            
            # 5. Update response with result
            response.update(result)
            response["metadata"]["tables_queried"] = result.get("tables_queried", [])
            response["matched_ids"] = result.get("matched_ids", [])
            response["metadata"]["retrieval_method"] = result.get("metadata", {}).get("retrieval_method")
            
            # 6. Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            response["metadata"]["processing_time_ms"] = round(processing_time, 2)
            
            # 7. Log the query
            self._log_query(
                user_id=user_id,
                original_message=message,
                normalized_message=normalized_message,
                intent=intent,
                confidence=intent_confidence,
                answer=response["answer"],
                source=response["source"],
                success=response["success"],
                matched_ids=response["matched_ids"],
                tables_queried=response["metadata"]["tables_queried"],
                processing_time_ms=processing_time,
                db=db,
                metadata=response["metadata"]
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in answer_user_query: {e}", exc_info=True)
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            return {
                "answer": "خطایی در پردازش سؤال شما رخ داد. لطفاً دوباره تلاش کنید.",
                "intent": "error",
                "confidence": 0.0,
                "source": "error",
                "success": False,
                "matched_ids": [],
                "metadata": {
                    "error": str(e),
                    "original_message": message,
                    "processing_time_ms": round(processing_time, 2),
                }
            }
        finally:
            if should_close_db:
                db.close()
    
    def _normalize_question(self, question: str) -> str:
        """
        Normalize the user's question to handle different phrasings and tones.
        
        This function ensures that:
        - "قیمت محصولات چقدر است؟"
        - "چقدر محصولات قیمت دارند؟"
        - "هزینه محصولات چقدره؟"
        all get normalized to similar forms for better matching.
        
        Args:
            question: Original user question
        
        Returns:
            Normalized question string
        """
        if not question:
            return ""
        
        # Trim whitespace
        normalized = question.strip()
        
        # Remove excessive punctuation (keep single punctuation)
        # Fix: Include Persian question mark (؟) in the regex
        # Persian question mark: ؟ (U+061F)
        normalized = re.sub(r'[!?؟]+', '؟', normalized)  # Replace multiple !, ?, or ؟ with single Persian ?
        normalized = re.sub(r'[.]+', '.', normalized)  # Replace multiple . with single .
        
        # Remove leading/trailing punctuation but keep meaningful punctuation at end
        # First, check what punctuation exists at the end
        has_question_mark = normalized.endswith('؟') or normalized.endswith('?')
        has_exclamation = normalized.endswith('!')
        has_period = normalized.endswith('.')
        
        # Strip punctuation (include both Persian and English question marks)
        normalized = normalized.strip('.,!?؟;:')
        
        # Restore punctuation if it was there (priority: ? > ! > .)
        if has_question_mark:
            normalized = normalized.rstrip('؟?') + '؟'
        elif has_exclamation and not has_question_mark:
            normalized = normalized.rstrip('!') + '!'
        elif has_period and not has_question_mark and not has_exclamation:
            normalized = normalized.rstrip('.') + '.'
        
        # Normalize Persian characters (optional - can be extended)
        # Normalize common variations
        persian_normalizations = {
            'ي': 'ی',  # Arabic yeh to Persian yeh
            'ك': 'ک',  # Arabic kaf to Persian kaf
            'ة': 'ه',  # Arabic teh marbuta to heh
            'أ': 'ا',  # Arabic alef with hamza to alef
            'إ': 'ا',  # Arabic alef with hamza below to alef
            'آ': 'ا',  # Arabic alef with madda to alef
        }
        for old, new in persian_normalizations.items():
            normalized = normalized.replace(old, new)
        
        # Normalize spacing
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Remove common filler words that don't affect meaning
        # Only remove if there are enough words
        filler_words = ['که', 'را', 'هم', 'همین', 'همان']
        words = normalized.split()
        if len(words) > 3:
            normalized = ' '.join([w for w in words if w not in filler_words])
        
        return normalized
    
    def _create_canonical_question(self, question: str) -> str:
        """
        Create a canonical form of the question for better matching.
        
        This helps ensure different phrasings of the same question
        lead to the same core logic and data retrieval.
        
        Example:
        - "قیمت اتاق A برای فردا چقدر است؟"
        - "چقدر اتاق A برای فردا قیمت دارد؟"
        - "هزینه اتاق A برای فردا چقدره؟"
        
        All should map to similar canonical forms.
        
        Args:
            question: Normalized question
        
        Returns:
            Canonical question form
        """
        canonical = question.lower()
        
        # Map question patterns to canonical forms
        # Price questions
        price_patterns = [
            (r'چقدر.*قیمت', 'قیمت'),
            (r'هزینه.*چقدر', 'قیمت'),
            (r'قیمت.*چقدر', 'قیمت'),
            (r'چقدر.*هزینه', 'قیمت'),
        ]
        
        for pattern, replacement in price_patterns:
            if re.search(pattern, canonical):
                canonical = re.sub(pattern, replacement, canonical)
                break
        
        # How questions
        how_patterns = [
            (r'چطور.*', 'چطور'),
            (r'چگونه.*', 'چطور'),
            (r'راه.*', 'چطور'),
        ]
        
        for pattern, replacement in how_patterns:
            if re.search(pattern, canonical):
                canonical = re.sub(pattern, replacement, canonical)
                break
        
        return canonical
    
    def _detect_intent_enhanced(
        self, 
        message: str, 
        canonical_question: str
    ) -> Tuple[str, float, Dict[str, Any]]:
        """
        Enhanced intent detection using smart intent detector if available.
        
        Args:
            message: Normalized message
            canonical_question: Canonical form of question
        
        Returns:
            Tuple of (intent_name, confidence_score, metadata)
        """
        metadata = {}
        message_lower = message.lower()
        
        # First, check for question indicators (high priority)
        # This ensures questions are detected even if smart detector misclassifies
        question_indicators = ["؟", "?", "چی", "چطور", "چگونه", "کجا", "کی", "چرا", "چه", "کار می‌کند", "چطور می‌شود"]
        if any(indicator in message_lower for indicator in question_indicators):
            # If it's clearly a question, prioritize that
            # But still check smart detector for more specific intent
            is_question = True
        else:
            is_question = False
        
        # Try smart intent detector
        if self.intent_detector:
            try:
                intent_result = self.intent_detector.detect_intent(message)
                if intent_result and hasattr(intent_result, 'intent'):
                    intent_name = intent_result.intent.value if hasattr(intent_result.intent, 'value') else str(intent_result.intent)
                    confidence = intent_result.confidence
                    metadata = {
                        "intent_keywords": getattr(intent_result, 'keywords', []),
                        "intent_context": getattr(intent_result, 'context', ''),
                        "suggested_actions": getattr(intent_result, 'suggested_actions', []),
                    }
                    
                    # If smart detector says greeting but message has question indicators, override
                    if is_question and intent_name == "greeting" and confidence < 0.5:
                        return ("general_question", 0.7, metadata)
                    
                    # If smart detector has high confidence, use it
                    if confidence > 0.5:
                        return (intent_name, confidence, metadata)
                    
                    # If it's a question but smart detector gave low confidence, use question intent
                    if is_question:
                        return ("general_question", 0.7, metadata)
                    
                    # Otherwise use smart detector result
                    return (intent_name, confidence, metadata)
            except Exception as e:
                logger.warning(f"Smart intent detection failed: {e}, using fallback")
        
        # Fallback to simple keyword-based detection
        # Check for explicit intent keywords
        intent_keywords = {
            "greeting": ["سلام", "درود", "صبح بخیر", "عصر بخیر", "hi", "hello"],
            "pricing": ["قیمت", "هزینه", "پول", "چقدر", "price", "cost"],
            "support": ["پشتیبانی", "کمک", "راهنمایی", "support", "help"],
            "contact": ["تماس", "ارتباط", "تلفن", "contact", "phone"],
            "category": ["دسته", "دسته‌بندی", "گروه", "category"],
        }
        
        for intent, keywords in intent_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    # Don't override question intent with greeting if it's clearly a question
                    if intent == "greeting" and is_question:
                        continue
                    return (intent, 0.8, metadata)
        
        # Default: assume FAQ intent for most questions
        if is_question:
            return ("general_question", 0.7, metadata)
        
        # Default to FAQ intent with lower confidence
        return ("general_question", 0.5, metadata)
    
    def _handle_faq_intent(
        self,
        message: str,
        canonical_question: str,
        db: Session,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle FAQ-related queries.
        
        Retrieves relevant FAQs from the database using both
        simple keyword matching and semantic search.
        Supports different phrasings through canonical question matching.
        Filters by tracked_site_id if provided in context.
        """
        tables_queried = ["faqs", "categories"]
        matched_ids = []
        category_filter = context.get("category_filter") if context else None
        tracked_site_id = context.get("tracked_site_id") if context else None
        
        # Log site filtering
        if tracked_site_id:
            logger.info(f"Filtering FAQs by tracked_site_id: {tracked_site_id}")
        
        try:
            # Try using simple_chatbot's search_faqs which has better scoring
            from services.simple_chatbot import get_simple_chatbot
            
            simple_chatbot = get_simple_chatbot()
            simple_chatbot.db_session = db
            
            # Use simple_chatbot's improved search with site filtering
            simple_results = []
            try:
                if simple_chatbot.load_faqs_from_db(tracked_site_id=tracked_site_id):
                    simple_results = simple_chatbot.search_faqs(
                        query=message,
                        min_score=10.0  # Lower threshold for better matching
                    )
                    # Filter results by site_id if provided (double-check)
                    if tracked_site_id and simple_results:
                        simple_results = [
                            r for r in simple_results
                            if r.get("tracked_site_id") is None or r.get("tracked_site_id") == tracked_site_id
                        ]
                    logger.info(f"Simple chatbot search found {len(simple_results)} results (site_id: {tracked_site_id})")
            except Exception as e:
                logger.warning(f"Simple chatbot search failed: {e}, trying simple retriever")
                # Fallback to simple retriever
                if simple_faq_retriever:
                    try:
                        simple_faq_retriever.load_faqs(db, tracked_site_id=tracked_site_id)
                        simple_results = simple_faq_retriever.search(
                            query=message,
                            top_k=5,
                            threshold=0.1  # Lower threshold
                        )
                        # Filter results by site_id if provided (double-check)
                        if tracked_site_id and simple_results:
                            simple_results = [
                                r for r in simple_results
                                if r.get("tracked_site_id") is None or r.get("tracked_site_id") == tracked_site_id
                            ]
                    except Exception as e2:
                        logger.warning(f"Simple retriever also failed: {e2}")
            
            # Apply category filter if provided
            if category_filter and simple_results:
                simple_results = [
                    r for r in simple_results 
                    if r.get("category", "").lower() == category_filter.lower()
                ]
            
            # Process results with improved quality checks
            if simple_results and len(simple_results) > 0:
                best_match = simple_results[0]
                score = best_match.get("score", 0)
                raw_score = best_match.get("raw_score", 0)
                
                # Quality thresholds - higher for better answers
                # For good matches: raw_score >= 30 (or normalized >= 0.15)
                # For acceptable matches: raw_score >= 20 (or normalized >= 0.1)
                # Below that, check if it's significantly better than alternatives
                good_match_threshold = 0.15
                good_raw_threshold = 30.0
                acceptable_match_threshold = 0.1
                acceptable_raw_threshold = 20.0
                
                # Check if this is a good match
                is_good_match = score >= good_match_threshold or raw_score >= good_raw_threshold
                
                # If not a good match, check if it's significantly better than alternatives
                is_significantly_better = False
                if len(simple_results) > 1:
                    second_best = simple_results[1]
                    second_score = second_best.get("score", 0)
                    second_raw = second_best.get("raw_score", 0)
                    
                    # Best match should be at least 1.5x better than second best
                    score_ratio = (raw_score / second_raw) if second_raw > 0 else 2.0
                    is_significantly_better = score_ratio >= 1.5 and raw_score >= acceptable_raw_threshold
                
                # Only use match if it meets quality criteria
                if is_good_match or is_significantly_better:
                    matched_ids.append(best_match.get("id") or best_match.get("faq_id"))
                    
                    # Calculate confidence based on quality
                    if is_good_match:
                        confidence = min(max(score, raw_score / 200.0), 1.0)
                    else:
                        # Lower confidence for acceptable matches
                        confidence = min(max(score, raw_score / 200.0), 0.7)
                    
                    logger.info(f"Using FAQ match: {best_match.get('question', '')[:50]}... (score: {score:.3f}, raw: {raw_score}, confidence: {confidence:.3f})")
                    
                    return {
                        "answer": best_match.get("answer", self.fallback_answer),
                        "source": "faq",
                        "success": True,
                        "confidence": confidence,
                        "matched_ids": matched_ids,
                        "tables_queried": tables_queried,
                        "faq_data": [best_match],  # For LLM enhancement
                        "metadata": {
                            "matched_question": best_match.get("question"),
                            "match_score": score,
                            "raw_score": raw_score,
                            "retrieval_method": "simple_search",
                            "all_matches": simple_results[:3],  # Top 3 for context
                            "match_quality": "good" if is_good_match else "acceptable"
                        }
                    }
                else:
                    # Match quality is too low, don't use it
                    logger.info(f"Match quality too low: score={score:.3f}, raw={raw_score}, using fallback")
            
            # If simple search didn't find good results, try semantic search
            # Only try semantic if simple search found nothing or very poor matches
            should_try_semantic = False
            if not simple_results or len(simple_results) == 0:
                should_try_semantic = True
            elif simple_results:
                best_score = simple_results[0].get("score", 0)
                best_raw = simple_results[0].get("raw_score", 0)
                # Only try semantic if simple search score is very low
                if best_score < 0.1 and best_raw < 20:
                    should_try_semantic = True
            
            if should_try_semantic:
                try:
                    if faq_retriever:
                        semantic_results = faq_retriever.semantic_search(
                            query=message,
                            top_k=3,
                            threshold=0.4,  # Higher threshold for semantic to ensure quality
                            category_filter=category_filter
                        )
                    else:
                        semantic_results = []
                    
                    if semantic_results and len(semantic_results) > 0:
                        best_match = semantic_results[0]
                        score = best_match.get("score", 0)
                        
                        # Use higher threshold for semantic search to ensure quality
                        if score >= 0.4:
                            matched_ids.append(best_match.get("faq_id"))
                            
                            logger.info(f"Using semantic search match: {best_match.get('question', '')[:50]}... (score: {score:.3f})")
                            
                            return {
                                "answer": best_match.get("answer", self.fallback_answer),
                                "source": "faq",
                                "success": True,
                                "confidence": min(score, 1.0),
                                "matched_ids": matched_ids,
                                "tables_queried": tables_queried,
                                "faq_data": [best_match],
                                "metadata": {
                                    "matched_question": best_match.get("question"),
                                    "match_score": score,
                                    "retrieval_method": "semantic_search",
                                    "all_matches": semantic_results,
                                    "match_quality": "good" if score >= 0.6 else "acceptable"
                                }
                            }
                        else:
                            logger.info(f"Semantic search match score too low: {score:.3f} < 0.4")
                except Exception as e:
                    logger.warning(f"Semantic search failed: {e}")
            
            # Don't use low-quality matches - better to return fallback
            # This prevents bad answers from being returned
            
            # Last resort: Try direct database query with LIKE search
            if not simple_results or len(simple_results) == 0:
                try:
                    logger.info("Trying direct database query as fallback")
                    # Search in question and answer fields
                    query_words = message.split()[:3]  # Use first 3 words
                    search_terms = [f"%{word}%" for word in query_words if len(word) > 2]
                    
                    if search_terms:
                        # Build filter conditions
                        filter_conditions = [
                            FAQ.is_active == True,
                            or_(
                                *[FAQ.question.like(term) for term in search_terms],
                                *[FAQ.answer.like(term) for term in search_terms]
                            )
                        ]
                        
                        # Add site filtering if tracked_site_id is provided
                        if tracked_site_id:
                            filter_conditions.append(
                                or_(
                                    FAQ.tracked_site_id == tracked_site_id,
                                    FAQ.tracked_site_id.is_(None)  # Also include global FAQs (no site_id)
                                )
                            )
                        
                        db_faqs = db.query(FAQ).filter(
                            and_(*filter_conditions)
                        ).limit(3).all()
                        
                        if db_faqs:
                            best_faq = db_faqs[0]
                            matched_ids.append(best_faq.id)
                            
                            logger.info(f"Found FAQ via direct DB query: {best_faq.question[:50]}")
                            
                            return {
                                "answer": best_faq.answer,
                                "source": "faq",
                                "success": True,
                                "confidence": 0.5,  # Lower confidence for direct DB match
                                "matched_ids": matched_ids,
                                "tables_queried": tables_queried,
                                "faq_data": [{
                                    "id": best_faq.id,
                                    "question": best_faq.question,
                                    "answer": best_faq.answer,
                                    "category": best_faq.category.name if best_faq.category else None
                                }],
                                "metadata": {
                                    "matched_question": best_faq.question,
                                    "retrieval_method": "direct_db_query",
                                    "warning": "direct_db_fallback"
                                }
                            }
                except Exception as e:
                    logger.warning(f"Direct DB query also failed: {e}")
            
            # No matches found at all
            logger.warning(f"No FAQ matches found for query: {message[:50]}")
            return {
                "answer": self.fallback_answer,
                "source": "fallback",
                "success": False,
                "confidence": 0.0,
                "matched_ids": [],
                "tables_queried": tables_queried,
                "metadata": {
                    "retrieval_method": "none",
                    "reason": "no_matches_found",
                    "simple_results_count": len(simple_results) if simple_results else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error in _handle_faq_intent: {e}", exc_info=True)
            return {
                "answer": "خطا در جستجوی پایگاه داده. لطفاً دوباره تلاش کنید.",
                "source": "error",
                "success": False,
                "confidence": 0.0,
                "matched_ids": [],
                "tables_queried": tables_queried,
                "metadata": {"error": str(e)}
            }
    
    def _handle_category_intent(
        self,
        message: str,
        canonical_question: str,
        db: Session,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle category-related queries.
        
        Returns list of categories or FAQs in a specific category.
        """
        tables_queried = ["categories", "faqs"]
        matched_ids = []
        
        try:
            # Check if asking for list of categories
            list_keywords = ["لیست", "همه", "تمام", "list", "all"]
            if any(keyword in message.lower() for keyword in list_keywords):
                categories = db.query(Category).all()
                if categories:
                    category_names = [cat.name for cat in categories]
                    answer = f"دسته‌بندی‌های موجود:\n" + "\n".join(f"- {name}" for name in category_names)
                    matched_ids = [cat.id for cat in categories]
                    
                    return {
                        "answer": answer,
                        "source": "database",
                        "success": True,
                        "confidence": 0.9,
                        "matched_ids": matched_ids,
                        "tables_queried": tables_queried,
                        "metadata": {"retrieval_method": "category_list"}
                    }
            
            # Try to find specific category
            categories = db.query(Category).filter(
                or_(
                    Category.name.contains(message),
                    Category.slug.contains(message.lower().replace(" ", "-"))
                )
            ).all()
            
            if categories:
                category = categories[0]
                # Build filter conditions
                filter_conditions = [
                    FAQ.category_id == category.id,
                    FAQ.is_active == True
                ]
                
                # Add site filtering if tracked_site_id is provided
                if tracked_site_id:
                    from sqlalchemy import or_
                    filter_conditions.append(
                        or_(
                            FAQ.tracked_site_id == tracked_site_id,
                            FAQ.tracked_site_id.is_(None)  # Also include global FAQs
                        )
                    )
                
                faqs = db.query(FAQ).filter(
                    and_(*filter_conditions)
                ).limit(5).all()
                
                if faqs:
                    answer = f"سوالات در دسته‌بندی '{category.name}':\n\n"
                    for faq in faqs:
                        answer += f"• {faq.question}\n"
                    matched_ids = [category.id] + [faq.id for faq in faqs]
                else:
                    answer = f"دسته‌بندی '{category.name}' پیدا شد اما سوالی در آن وجود ندارد."
                    matched_ids = [category.id]
                
                return {
                    "answer": answer,
                    "source": "database",
                    "success": True,
                    "confidence": 0.8,
                    "matched_ids": matched_ids,
                    "tables_queried": tables_queried,
                    "metadata": {"retrieval_method": "category_search"}
                }
            
            return {
                "answer": "دسته‌بندی مورد نظر پیدا نشد.",
                "source": "fallback",
                "success": False,
                "confidence": 0.0,
                "matched_ids": [],
                "tables_queried": tables_queried,
                "metadata": {"retrieval_method": "none"}
            }
            
        except Exception as e:
            logger.error(f"Error in _handle_category_intent: {e}", exc_info=True)
            return {
                "answer": "خطا در جستجوی دسته‌بندی‌ها.",
                "source": "error",
                "success": False,
                "confidence": 0.0,
                "matched_ids": [],
                "tables_queried": tables_queried,
                "metadata": {"error": str(e)}
            }
    
    def _handle_greeting_intent(
        self,
        message: str,
        canonical_question: str,
        db: Session,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle greeting messages."""
        message_lower = message.lower()
        
        if "سلام" in message_lower or "hi" in message_lower or "hello" in message_lower:
            return {
                "answer": "سلام! خوش آمدید. چطور می‌تونم کمکتون کنم؟",
                "source": "static",
                "success": True,
                "confidence": 1.0,
                "matched_ids": [],
                "tables_queried": [],
                "metadata": {"retrieval_method": "greeting"}
            }
        
        if "خداحافظ" in message_lower or "بای" in message_lower or "bye" in message_lower:
            return {
                "answer": "خداحافظ! موفق باشید.",
                "source": "static",
                "success": True,
                "confidence": 1.0,
                "matched_ids": [],
                "tables_queried": [],
                "metadata": {"retrieval_method": "greeting"}
            }
        
        if "ممنون" in message_lower or "تشکر" in message_lower or "thanks" in message_lower:
            return {
                "answer": "خواهش می‌کنم! اگر سوال دیگری دارید، بپرسید.",
                "source": "static",
                "success": True,
                "confidence": 1.0,
                "matched_ids": [],
                "tables_queried": [],
                "metadata": {"retrieval_method": "greeting"}
            }
        
        # Default greeting response
        return {
            "answer": "سلام! چطور می‌تونم کمکتون کنم؟",
            "source": "static",
            "success": True,
            "confidence": 0.7,
            "matched_ids": [],
            "tables_queried": [],
            "metadata": {"retrieval_method": "greeting"}
        }
    
    def _handle_unknown_intent(
        self,
        message: str,
        canonical_question: str,
        db: Session,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle unknown intents - try FAQ search as fallback.
        """
        # Try FAQ search anyway
        return self._handle_faq_intent(message, canonical_question, db, context)
    
    def _enhance_answer_with_llm(
        self,
        user_message: str,
        faq_data: List[Dict[str, Any]],
        original_answer: str
    ) -> Optional[str]:
        """
        Optionally enhance the answer using LLM for better phrasing.
        
        This helps make answers more conversational and natural
        while maintaining accuracy.
        """
        if not self.answer_generator or not faq_data:
            return None
        
        try:
            # Use LLM to enhance the answer
            result = self.answer_generator.generate_answer(
                user_message=user_message,
                context_faqs=faq_data
            )
            
            if result.get("is_quality_good") and result.get("answer"):
                return result["answer"]
            else:
                # LLM answer not good quality, use original
                return None
        except Exception as e:
            logger.warning(f"LLM enhancement failed: {e}")
            return None
    
    def _log_query(
        self,
        user_id: Optional[str],
        original_message: str,
        normalized_message: str,
        intent: str,
        confidence: float,
        answer: str,
        source: str,
        success: bool,
        matched_ids: List[int],
        tables_queried: List[str],
        processing_time_ms: float,
        db: Session,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Comprehensive logging for observability.
        
        Logs to both application logger and database (ChatLog model).
        This makes it easy to see why the agent answered something in a certain way.
        """
        log_data = {
            "user_id": user_id,
            "original_message": original_message,
            "normalized_message": normalized_message,
            "intent": intent,
            "confidence": confidence,
            "answer": answer[:500],  # Truncate very long answers
            "source": source,
            "success": success,
            "matched_ids": matched_ids,
            "tables_queried": tables_queried,
            "processing_time_ms": processing_time_ms,
            "metadata": metadata or {},
        }
        
        # Log to application logger
        logger.info(f"Query processed: {json.dumps(log_data, ensure_ascii=False, default=str)}")
        
        # Log to database (ChatLog model)
        try:
            chat_log = ChatLog(
                user_text=original_message,
                ai_text=answer,
                intent=intent,
                source=source,
                confidence=confidence,
                success=success,
                matched_faq_id=matched_ids[0] if matched_ids else None,
                latency_ms=int(processing_time_ms),
                notes=json.dumps({
                    "normalized_message": normalized_message,
                    "tables_queried": tables_queried,
                    "matched_ids": matched_ids,
                    "user_id": user_id,
                    "metadata": metadata or {},
                }, ensure_ascii=False)
            )
            db.add(chat_log)
            db.commit()
        except Exception as e:
            logger.warning(f"Failed to log to database: {e}")


# Global instance
_answering_agent = None


def get_answering_agent() -> AnsweringAgent:
    """Get the global answering agent instance"""
    global _answering_agent
    if _answering_agent is None:
        _answering_agent = AnsweringAgent()
    return _answering_agent


def answer_user_query(
    user_id: Optional[str],
    message: str,
    context: Optional[Dict[str, Any]] = None,
    db: Optional[Session] = None
) -> Dict[str, Any]:
    """
    Main entry point for answering user queries.
    
    This is the function that other parts of the system should call.
    
    Example:
        from services.answering_agent import answer_user_query
        
        result = answer_user_query(
            user_id="user123",
            message="قیمت محصولات چقدر است؟",
            context={"session_id": "abc123", "category_filter": "pricing"}
        )
        print(result["answer"])
        print(f"Intent: {result['intent']}, Confidence: {result['confidence']}")
    
    Args:
        user_id: Optional user identifier
        message: User's question/message
        context: Optional context dictionary (can include session_id, category_filter, debug, etc.)
        db: Optional database session (will be created if not provided)
    
    Returns:
        Dictionary with:
        - answer: The final answer text
        - intent: Detected intent (e.g., "pricing", "support", "greeting")
        - confidence: Confidence score (0-1)
        - source: Data source used ("faq", "database", "llm", "static", "fallback", "error")
        - success: Whether a good answer was found (boolean)
        - matched_ids: List of IDs of records used in the answer (e.g., FAQ IDs)
        - metadata: Additional metadata including:
            - original_message: Original user message
            - normalized_message: Normalized version
            - canonical_question: Canonical form for matching
            - tables_queried: List of database tables queried
            - retrieval_method: Method used ("simple_search", "semantic_search", etc.)
            - processing_time_ms: Processing time in milliseconds
            - llm_used: Whether LLM was used for answer enhancement
    
    Notes:
        - The agent handles different phrasings automatically through normalization
        - Questions with the same meaning but different wording will get the same answer
        - All queries are logged to both application logs and database
        - The agent gracefully handles errors and always returns a response
    """
    agent = get_answering_agent()
    return agent.answer_user_query(user_id, message, context, db)
