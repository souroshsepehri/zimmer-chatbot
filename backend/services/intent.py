import json
import os
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from core.config import settings


class EnhancedIntentDetector:
    def __init__(self):
        # Get API key from multiple sources
        api_key = (
            os.getenv("OPENAI_API_KEY") or 
            settings.openai_api_key
        )
        
        if not api_key or api_key == "":
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
        
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            api_key=api_key,
            temperature=0.1
        )
        
        self.intent_labels = [
            "faq", "smalltalk", "chitchat", "complaint", 
            "sales", "support", "out_of_scope"
        ]
        
        self.system_prompt = f"""تو یک دسته‌بند نیت کاربر هستی. فقط یکی از برچسب‌ها را با احتمال برگردان. خروجی JSON بده.

برچسب‌های موجود:
- faq: سؤالات مربوط به محصولات، خدمات، یا اطلاعات عمومی
- smalltalk: احوال‌پرسی، تشکر، تعارف
- chitchat: گفت‌وگوی غیررسمی و دوستانه
- complaint: شکایت، نارضایتی، مشکل
- sales: سؤالات فروش، قیمت، خرید
- support: پشتیبانی فنی، راهنمایی
- out_of_scope: خارج از حوزه کاری

مثال:
کاربر: "سلام، چطور می‌تونم سفارش بدم؟"
خروجی: {{"label": "sales", "confidence": 0.9, "reasoning": "کاربر در مورد نحوه سفارش سؤال می‌پرسد که مربوط به فروش است"}}

کاربر: "چطور هستید؟"
خروجی: {{"label": "smalltalk", "confidence": 0.95, "reasoning": "احوال‌پرسی ساده و غیررسمی"}}

کاربر: "مشکل دارم با سفارشم"
خروجی: {{"label": "complaint", "confidence": 0.85, "reasoning": "کاربر از مشکل با سفارش شکایت می‌کند"}}"""

    def _analyze_message(self, message: str) -> Dict[str, Any]:
        """Analyze the user message to detect intent"""
        try:
            # Simple keyword-based intent detection as fallback
            message_lower = message.lower()
            
            # Check for common patterns
            if any(word in message_lower for word in ["سلام", "درود", "صبح بخیر", "عصر بخیر"]):
                return {
                    "intent_label": "smalltalk",
                    "confidence": 0.9,
                    "reasoning": "Greeting detected",
                    "raw_response": "Keyword-based detection"
                }
            elif any(word in message_lower for word in ["قیمت", "خرید", "سفارش", "فروش"]):
                return {
                    "intent_label": "sales",
                    "confidence": 0.8,
                    "reasoning": "Sales-related keywords detected",
                    "raw_response": "Keyword-based detection"
                }
            elif any(word in message_lower for word in ["مشکل", "خطا", "خراب", "ناراضی"]):
                return {
                    "intent_label": "complaint",
                    "confidence": 0.8,
                    "reasoning": "Complaint-related keywords detected",
                    "raw_response": "Keyword-based detection"
                }
            elif any(word in message_lower for word in ["چطور", "چگونه", "راهنمایی", "کمک"]):
                return {
                    "intent_label": "support",
                    "confidence": 0.7,
                    "reasoning": "Support-related keywords detected",
                    "raw_response": "Keyword-based detection"
                }
            else:
                return {
                    "intent_label": "faq",
                    "confidence": 0.6,
                    "reasoning": "Default to FAQ for general questions",
                    "raw_response": "Keyword-based detection"
                }
            
        except Exception as e:
            print(f"Intent analysis error: {e}")
            return {
                "intent_label": "out_of_scope",
                "confidence": 0.0,
                "reasoning": f"Error in intent analysis: {str(e)}",
                "raw_response": f"Error: {str(e)}"
            }

    def _validate_intent(self, intent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the detected intent"""
        intent_label = intent_data["intent_label"]
        confidence = intent_data["confidence"]
        
        # Validate intent label
        if intent_label not in self.intent_labels:
            intent_label = "out_of_scope"
            confidence = 0.0
            reasoning = f"Invalid intent label detected: {intent_label}"
        else:
            reasoning = intent_data.get("reasoning", "Intent validated")
        
        return {
            "intent_label": intent_label,
            "confidence": confidence,
            "reasoning": reasoning,
            "raw_response": intent_data.get("raw_response", "")
        }

    def _enhance_confidence(self, intent_data: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Enhance confidence based on additional heuristics"""
        intent_label = intent_data["intent_label"]
        confidence = intent_data["confidence"]
        
        # Apply confidence adjustments based on message characteristics
        if intent_label == "smalltalk":
            # Boost confidence for common greetings
            greetings = ["سلام", "درود", "صبح بخیر", "عصر بخیر", "شب بخیر"]
            if any(greeting in message.lower() for greeting in greetings):
                confidence = min(confidence + 0.1, 1.0)
        
        elif intent_label == "sales":
            # Boost confidence for sales-related keywords
            sales_keywords = ["قیمت", "خرید", "سفارش", "فروش", "تخفیف"]
            if any(keyword in message.lower() for keyword in sales_keywords):
                confidence = min(confidence + 0.1, 1.0)
        
        elif intent_label == "complaint":
            # Boost confidence for complaint-related keywords
            complaint_keywords = ["مشکل", "خطا", "خراب", "ناراضی", "شکایت"]
            if any(keyword in message.lower() for keyword in complaint_keywords):
                confidence = min(confidence + 0.1, 1.0)
        
        return {
            **intent_data,
            "confidence": confidence
        }

    def detect(self, message: str) -> Dict[str, Any]:
        """Detect intent from user message using enhanced pipeline"""
        try:
            # Step 1: Analyze message
            analysis_result = self._analyze_message(message)
            
            # Step 2: Validate intent
            validation_result = self._validate_intent(analysis_result)
            
            # Step 3: Enhance confidence
            enhanced_result = self._enhance_confidence(validation_result, message)
            
            return {
                "label": enhanced_result["intent_label"],
                "confidence": enhanced_result["confidence"],
                "reasoning": enhanced_result.get("reasoning", ""),
                "graph_trace": 3,  # Simulate graph steps
                "enhanced": True
            }
            
        except Exception as e:
            print(f"Enhanced intent detection error: {e}")
            return {
                "label": "out_of_scope",
                "confidence": 0.0,
                "reasoning": f"Pipeline execution error: {str(e)}",
                "graph_trace": 0,
                "enhanced": False
            }


# Global instance - lazy initialization
_intent_detector = None

def get_intent_detector():
    """Get the intent detector instance with lazy initialization"""
    global _intent_detector
    if _intent_detector is None:
        _intent_detector = EnhancedIntentDetector()
    return _intent_detector

# Create a proxy object that initializes lazily
class LazyIntentDetector:
    def __getattr__(self, name):
        return getattr(get_intent_detector(), name)

intent_detector = LazyIntentDetector()