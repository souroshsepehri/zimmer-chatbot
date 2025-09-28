import json
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from core.config import settings


class IntentDetector:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
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
خروجی: {{"label": "sales", "confidence": 0.9}}

کاربر: "چطور هستید؟"
خروجی: {{"label": "smalltalk", "confidence": 0.95}}

کاربر: "مشکل دارم با سفارشم"
خروجی: {{"label": "complaint", "confidence": 0.85}}"""

    def detect(self, message: str) -> Dict[str, Any]:
        """Detect intent from user message"""
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("human", "کاربر: {message}")
            ])
            
            formatted_prompt = prompt.format_messages(message=message)
            response = self.llm.invoke(formatted_prompt)
            
            # Parse JSON response
            result = json.loads(response.content.strip())
            
            return {
                "label": result.get("label", "out_of_scope"),
                "confidence": float(result.get("confidence", 0.5))
            }
            
        except Exception as e:
            print(f"Intent detection error: {e}")
            return {
                "label": "out_of_scope",
                "confidence": 0.0
            }


# Global instance
intent_detector = IntentDetector()
