from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from services.intent import intent_detector
from services.retriever import faq_retriever
from services.simple_retriever import simple_faq_retriever
from services.answer import answer_generator
from schemas.chat import DebugInfo, IntentResult, RetrievalResult
from core.config import settings


class ChatChain:
    def __init__(self):
        self.fallback_answer = "فعلاً پاسخ مناسبی برای این سؤال ندارم. لطفاً سؤال خود را به شکل دیگری مطرح کنید یا با پشتیبانی تماس بگیرید."
    
    def process_message(
        self, 
        message: str, 
        db: Session, 
        debug: bool = False,
        category_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process user message through the complete chain"""
        
        # 1. Intent Detection (skip if no API key)
        try:
            intent_result = intent_detector.detect(message)
            intent = IntentResult(**intent_result)
        except Exception as e:
            print(f"Intent detection failed: {e}")
            intent = IntentResult(label="unknown", confidence=0.5)
        
        # 2. FAQ Retrieval - Always check database first with simple search
        retrieval_results = []
        print(f"DEBUG: Processing message: {message}")
        
        # Always try simple search first (more reliable for Persian text)
        try:
            simple_faq_retriever.load_faqs(db)
            retrieval_results = simple_faq_retriever.search(
                query=message,
                top_k=settings.retrieval_top_k,
                threshold=0.2  # Very low threshold to catch even distant matches
            )
            print(f"DEBUG: Simple search found {len(retrieval_results)} results")
            for i, result in enumerate(retrieval_results[:3]):
                print(f"  {i+1}. {result['question'][:50]}... (score: {result['score']:.3f})")
        except Exception as e:
            print(f"DEBUG: Simple search failed: {e}")
            retrieval_results = []
        
        # If simple search finds no results, try semantic search as backup
        if len(retrieval_results) == 0:
            try:
                retrieval_results = faq_retriever.semantic_search(
                    query=message,
                    top_k=settings.retrieval_top_k,
                    threshold=0.5  # Lower threshold for semantic search
                )
                print(f"DEBUG: Semantic search found {len(retrieval_results)} results")
            except Exception as e:
                print(f"DEBUG: Semantic search also failed: {e}")
                retrieval_results = []
        
        # 3. Determine source and generate answer
        source = "fallback"
        answer = self.fallback_answer
        success = False
        matched_faq_id = None
        unanswered_in_db = True
        
        if retrieval_results:
            # Always use the best database match, even if score is low
            best_match = retrieval_results[0]
            source = "faq"
            answer = best_match["answer"]
            success = True
            matched_faq_id = best_match["faq_id"]
            unanswered_in_db = False
            print(f"DEBUG: Using database answer with score: {best_match['score']:.3f}")
        else:
            # No relevant FAQs found, use fallback
            source = "fallback"
            answer = self.fallback_answer
            success = False
            print("DEBUG: No database matches found, using fallback")
        
        # 4. Final quality check
        if not success and source in ["rag", "llm"]:
            # Check for low confidence or poor quality
            if intent.confidence < 0.6 or intent.label == "out_of_scope":
                source = "fallback"
                answer = self.fallback_answer
                success = False
        
        # 5. Prepare debug info
        debug_info = None
        if debug:
            retrieval_results_formatted = [
                RetrievalResult(
                    faq_id=r["faq_id"],
                    question=r["question"],
                    answer=r["answer"],
                    score=r["score"],
                    category=r["category"]
                ) for r in retrieval_results
            ]
            
            debug_info = DebugInfo(
                intent=intent,
                source=source,
                retrieval_results=retrieval_results_formatted,
                success=success,
                unanswered_in_db=unanswered_in_db
            )
        
        return {
            "answer": answer,
            "debug_info": debug_info.dict() if debug_info else None,
            "intent": intent.dict(),
            "source": source,
            "success": success,
            "matched_faq_id": matched_faq_id,
            "unanswered_in_db": unanswered_in_db,
            "retrieval_results": retrieval_results
        }


# Global instance - lazy initialization
_chat_chain = None

def get_chat_chain():
    """Get the chat chain instance with lazy initialization"""
    global _chat_chain
    if _chat_chain is None:
        _chat_chain = ChatChain()
    return _chat_chain

# Create a proxy object that initializes lazily
class LazyChatChain:
    def __getattr__(self, name):
        return getattr(get_chat_chain(), name)

chat_chain = LazyChatChain()
