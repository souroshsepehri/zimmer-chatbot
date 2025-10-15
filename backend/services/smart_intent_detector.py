"""
Smart Intent Detection Service - Understands user intent and provides better answer ranking
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class IntentType(Enum):
    GREETING = "greeting"
    PRICING = "pricing"
    WARRANTY = "warranty"
    ORDER = "order"
    SUPPORT = "support"
    HOURS = "hours"
    CONTACT = "contact"
    PRODUCT_INFO = "product_info"
    COMPLAINT = "complaint"
    GENERAL_QUESTION = "general_question"
    UNKNOWN = "unknown"

@dataclass
class IntentResult:
    intent: IntentType
    confidence: float
    keywords: List[str]
    context: str
    suggested_actions: List[str]

class SmartIntentDetector:
    """
    Advanced intent detection system that understands user requests
    and provides better answer ranking
    """
    
    def __init__(self):
        self.intent_patterns = {
            IntentType.GREETING: {
                'keywords': ['سلام', 'درود', 'صبح بخیر', 'عصر بخیر', 'شب بخیر', 'hi', 'hello', 'hey'],
                'patterns': [r'سلام.*', r'درود.*', r'صبح.*بخیر', r'عصر.*بخیر', r'شب.*بخیر'],
                'weight': 1.0
            },
            IntentType.PRICING: {
                'keywords': ['قیمت', 'هزینه', 'پول', 'چقدر', 'گران', 'ارزان', 'price', 'cost', 'money', 'how much'],
                'patterns': [r'قیمت.*', r'هزینه.*', r'چقدر.*', r'پول.*', r'گران.*', r'ارزان.*'],
                'weight': 1.0
            },
            IntentType.WARRANTY: {
                'keywords': ['گارانتی', 'ضمانت', 'تضمین', 'warranty', 'guarantee'],
                'patterns': [r'گارانتی.*', r'ضمانت.*', r'تضمین.*'],
                'weight': 1.0
            },
            IntentType.ORDER: {
                'keywords': ['سفارش', 'خرید', 'خریدن', 'order', 'buy', 'purchase'],
                'patterns': [r'سفارش.*', r'خرید.*', r'خریدن.*'],
                'weight': 1.0
            },
            IntentType.SUPPORT: {
                'keywords': ['پشتیبانی', 'کمک', 'راهنمایی', 'مشکل', 'خطا', 'support', 'help', 'assistance'],
                'patterns': [r'پشتیبانی.*', r'کمک.*', r'راهنمایی.*', r'مشکل.*', r'خطا.*'],
                'weight': 1.0
            },
            IntentType.HOURS: {
                'keywords': ['ساعت', 'زمان', 'وقت', 'ساعات کاری', 'time', 'hours', 'working hours'],
                'patterns': [r'ساعت.*', r'زمان.*', r'وقت.*', r'ساعات.*کاری.*'],
                'weight': 1.0
            },
            IntentType.CONTACT: {
                'keywords': ['تماس', 'ارتباط', 'تلفن', 'ایمیل', 'contact', 'phone', 'email'],
                'patterns': [r'تماس.*', r'ارتباط.*', r'تلفن.*', r'ایمیل.*'],
                'weight': 1.0
            },
            IntentType.PRODUCT_INFO: {
                'keywords': ['محصول', 'کالا', 'ویژگی', 'مشخصات', 'product', 'item', 'specification'],
                'patterns': [r'محصول.*', r'کالا.*', r'ویژگی.*', r'مشخصات.*'],
                'weight': 0.8
            },
            IntentType.COMPLAINT: {
                'keywords': ['شکایت', 'ناراضی', 'مشکل', 'خراب', 'معیوب', 'complaint', 'problem', 'broken'],
                'patterns': [r'شکایت.*', r'ناراضی.*', r'مشکل.*', r'خراب.*', r'معیوب.*'],
                'weight': 1.0
            }
        }
        
        self.context_boosters = {
            'urgent': ['فوری', 'سریع', 'urgent', 'quick', 'asap'],
            'question_words': ['چطور', 'چگونه', 'کی', 'کجا', 'چرا', 'چه', 'how', 'when', 'where', 'why', 'what'],
            'negative': ['نه', 'نمی', 'نمی‌خواهم', 'no', 'not', 'dont', 'dont want']
        }
    
    def detect_intent(self, message: str) -> IntentResult:
        """
        Detect user intent from message
        """
        message_lower = message.lower().strip()
        
        # Calculate scores for each intent
        intent_scores = {}
        matched_keywords = {}
        
        for intent_type, config in self.intent_patterns.items():
            score = 0.0
            keywords_found = []
            
            # Check keyword matches
            for keyword in config['keywords']:
                if keyword in message_lower:
                    score += 1.0
                    keywords_found.append(keyword)
            
            # Check pattern matches
            for pattern in config['patterns']:
                if re.search(pattern, message_lower):
                    score += 2.0  # Patterns are more specific than keywords
            
            # Apply weight
            score *= config['weight']
            
            # Check for context boosters
            for booster_type, boosters in self.context_boosters.items():
                for booster in boosters:
                    if booster in message_lower:
                        if booster_type == 'urgent':
                            score += 0.5
                        elif booster_type == 'question_words':
                            score += 0.3
                        elif booster_type == 'negative':
                            score += 0.2
            
            intent_scores[intent_type] = score
            matched_keywords[intent_type] = keywords_found
        
        # Find the best intent
        if not intent_scores or max(intent_scores.values()) == 0:
            best_intent = IntentType.UNKNOWN
            confidence = 0.0
        else:
            best_intent = max(intent_scores, key=intent_scores.get)
            max_score = intent_scores[best_intent]
            total_score = sum(intent_scores.values())
            confidence = min(max_score / max(total_score, 1), 1.0)
        
        # Generate context and suggested actions
        context = self._generate_context(best_intent, message)
        suggested_actions = self._get_suggested_actions(best_intent)
        
        return IntentResult(
            intent=best_intent,
            confidence=confidence,
            keywords=matched_keywords.get(best_intent, []),
            context=context,
            suggested_actions=suggested_actions
        )
    
    def _generate_context(self, intent: IntentType, message: str) -> str:
        """Generate context description for the intent"""
        context_map = {
            IntentType.GREETING: "کاربر سلام کرده و احتمالاً می‌خواهد شروع به گفتگو کند",
            IntentType.PRICING: "کاربر در مورد قیمت‌ها و هزینه‌ها سؤال می‌کند",
            IntentType.WARRANTY: "کاربر در مورد گارانتی و ضمانت محصولات سؤال می‌کند",
            IntentType.ORDER: "کاربر می‌خواهد سفارش دهد یا در مورد فرآیند خرید سؤال می‌کند",
            IntentType.SUPPORT: "کاربر نیاز به کمک یا پشتیبانی دارد",
            IntentType.HOURS: "کاربر در مورد ساعات کاری سؤال می‌کند",
            IntentType.CONTACT: "کاربر می‌خواهد با شرکت تماس بگیرد",
            IntentType.PRODUCT_INFO: "کاربر در مورد محصولات و ویژگی‌های آن‌ها سؤال می‌کند",
            IntentType.COMPLAINT: "کاربر شکایت یا مشکلی دارد",
            IntentType.GENERAL_QUESTION: "کاربر سؤال عمومی دارد",
            IntentType.UNKNOWN: "نیت کاربر مشخص نیست"
        }
        return context_map.get(intent, "نیت کاربر مشخص نیست")
    
    def _get_suggested_actions(self, intent: IntentType) -> List[str]:
        """Get suggested actions based on intent"""
        actions_map = {
            IntentType.GREETING: ["ارائه پاسخ دوستانه", "پرسیدن نیاز کاربر"],
            IntentType.PRICING: ["ارائه اطلاعات قیمت", "راهنمایی به بخش قیمت‌گذاری"],
            IntentType.WARRANTY: ["توضیح گارانتی", "ارائه جزئیات ضمانت"],
            IntentType.ORDER: ["راهنمایی فرآیند سفارش", "ارائه اطلاعات خرید"],
            IntentType.SUPPORT: ["ارائه کمک فوری", "راهنمایی به پشتیبانی"],
            IntentType.HOURS: ["ارائه ساعات کاری", "اطلاع‌رسانی زمان‌های تماس"],
            IntentType.CONTACT: ["ارائه اطلاعات تماس", "راهنمایی روش‌های ارتباط"],
            IntentType.PRODUCT_INFO: ["ارائه اطلاعات محصول", "راهنمایی به کاتالوگ"],
            IntentType.COMPLAINT: ["گوش دادن به شکایت", "راهنمایی به بخش شکایات"],
            IntentType.GENERAL_QUESTION: ["پاسخ عمومی", "راهنمایی به FAQ"],
            IntentType.UNKNOWN: ["پرسیدن توضیح بیشتر", "ارائه پاسخ عمومی"]
        }
        return actions_map.get(intent, ["ارائه پاسخ عمومی"])
    
    def rank_answers(self, intent: IntentResult, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank search results based on detected intent
        """
        if not search_results:
            return []
        
        # Score each result based on intent relevance
        scored_results = []
        
        for result in search_results:
            score = result.get('score', 0.0)
            question = result.get('question', '').lower()
            answer = result.get('answer', '').lower()
            category = result.get('category', '').lower()
            
            # Intent-based scoring
            intent_score = 0.0
            
            # Check if question/answer matches intent keywords
            for keyword in intent.keywords:
                if keyword in question:
                    intent_score += 2.0
                if keyword in answer:
                    intent_score += 1.0
                if keyword in category:
                    intent_score += 1.5
            
            # Category-based scoring
            category_boost = self._get_category_boost(intent.intent, category)
            intent_score += category_boost
            
            # Combine original score with intent score
            final_score = (score * 0.6) + (intent_score * 0.4)
            
            result_copy = result.copy()
            result_copy['intent_score'] = intent_score
            result_copy['final_score'] = final_score
            result_copy['intent_match'] = intent_score > 0
            
            scored_results.append(result_copy)
        
        # Sort by final score (descending)
        scored_results.sort(key=lambda x: x['final_score'], reverse=True)
        
        return scored_results
    
    def _get_category_boost(self, intent: IntentType, category: str) -> float:
        """Get category boost based on intent"""
        category_boosts = {
            IntentType.PRICING: {'قیمت‌گذاری': 2.0, 'عمومی': 0.5},
            IntentType.WARRANTY: {'گارانتی': 2.0, 'عمومی': 0.5},
            IntentType.ORDER: {'سفارش': 2.0, 'عمومی': 0.5},
            IntentType.SUPPORT: {'پشتیبانی': 2.0, 'عمومی': 0.5},
            IntentType.CONTACT: {'تماس': 2.0, 'عمومی': 0.5},
            IntentType.HOURS: {'ساعات کاری': 2.0, 'عمومی': 0.5}
        }
        
        boosts = category_boosts.get(intent, {})
        return boosts.get(category, 0.0)

# Global instance
_smart_intent_detector = None

def get_smart_intent_detector() -> SmartIntentDetector:
    """Get smart intent detector instance"""
    global _smart_intent_detector
    if _smart_intent_detector is None:
        _smart_intent_detector = SmartIntentDetector()
    return _smart_intent_detector
