"""
Simple FAQ retriever that works without OpenAI API key
Uses basic text matching instead of semantic search
"""

import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from models.faq import FAQ


class SimpleFAQRetriever:
    def __init__(self):
        self.faqs = []
        self.faq_mapping = {}
    
    def load_faqs(self, db: Session):
        """Load FAQs from database"""
        faqs = db.query(FAQ).filter(FAQ.is_active == True).all()
        self.faqs = []
        self.faq_mapping = {}
        
        for i, faq in enumerate(faqs):
            self.faqs.append({
                "faq_id": faq.id,
                "question": faq.question,
                "answer": faq.answer,
                "category": faq.category.name if faq.category else None
            })
            self.faq_mapping[i] = faq.id
        
        print(f"Loaded {len(self.faqs)} FAQs for simple matching")
    
    def simple_search(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """Simple text-based search using keyword matching"""
        if not self.faqs:
            return []
        
        query_lower = query.lower()
        query_words = re.findall(r'\b\w+\b', query_lower)
        
        results = []
        
        for faq in self.faqs:
            score = 0
            question_lower = faq["question"].lower()
            answer_lower = faq["answer"].lower()
            
            # Check for exact phrase matches
            if query_lower in question_lower:
                score += 10
            if query_lower in answer_lower:
                score += 5
            
            # Check for word matches
            for word in query_words:
                if word in question_lower:
                    score += 2
                if word in answer_lower:
                    score += 1
            
            # Check for common Persian keywords
            persian_keywords = {
                'سفارش': ['سفارش', 'خرید', 'خریدن'],
                'پشتیبانی': ['پشتیبانی', 'کمک', 'راهنمایی'],
                'ساعت': ['ساعت', 'زمان', 'وقت'],
                'قیمت': ['قیمت', 'هزینه', 'پول'],
                'ارسال': ['ارسال', 'ارسال', 'پست'],
                'بازگشت': ['بازگشت', 'مرجوع', 'برگشت']
            }
            
            for category, keywords in persian_keywords.items():
                if any(keyword in query_lower for keyword in keywords):
                    if any(keyword in question_lower for keyword in keywords):
                        score += 3
                    if any(keyword in answer_lower for keyword in keywords):
                        score += 2
            
            if score > 0:
                results.append({
                    "faq_id": faq["faq_id"],
                    "question": faq["question"],
                    "answer": faq["answer"],
                    "score": score / 10.0,  # Normalize to 0-1 range
                    "category": faq["category"]
                })
        
        # Sort by score and return top results
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def search(self, query: str, top_k: int = 4, threshold: float = 0.1) -> List[Dict[str, Any]]:
        """Main search method with very low threshold to catch more matches"""
        results = self.simple_search(query, top_k)
        
        # Use very low threshold to catch even distant matches
        filtered_results = [r for r in results if r["score"] >= threshold]
        
        return filtered_results


# Global instance - lazy initialization
_simple_faq_retriever = None

def get_simple_faq_retriever():
    """Get the simple FAQ retriever instance with lazy initialization"""
    global _simple_faq_retriever
    if _simple_faq_retriever is None:
        _simple_faq_retriever = SimpleFAQRetriever()
    return _simple_faq_retriever

# Create a proxy object that initializes lazily
class LazySimpleFAQRetriever:
    def __getattr__(self, name):
        return getattr(get_simple_faq_retriever(), name)

simple_faq_retriever = LazySimpleFAQRetriever()
