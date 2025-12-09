import os
import time
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from core.config import settings

# Load .env file to ensure OPENAI_API_KEY is available
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=True)


class AnswerGenerator:
    def __init__(self):
        # Get API key from environment variable ONLY
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key or api_key == "":
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
        
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            api_key=api_key,
            temperature=0.3
        )
        
        self.system_prompt = """تو دستیار فارسی زیمر هستی. لحن: محترمانه و کوتاه. 
اگر پاسخ دقیق در دانش موجود هست عیناً استفاده کن. 
در غیر این صورت کوتاه پاسخ بده و اگر مطمئن نیستی بگو پاسخ در دسترس نیست.

راهنمایی:
- همیشه به فارسی پاسخ بده
- کوتاه و مفید باش
- اگر اطلاعات کافی نداری، صادقانه بگو
- لحن محترمانه و دوستانه داشته باش"""

    def generate_answer(
        self, 
        user_message: str, 
        context_faqs: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate answer using LLM with optional FAQ context"""
        start_time = time.time()
        
        # Prepare context from FAQs
        context_text = ""
        if context_faqs:
            context_text = "\n\nاطلاعات مرتبط:\n"
            for i, faq in enumerate(context_faqs, 1):
                context_text += f"{i}. سؤال: {faq['question']}\n"
                context_text += f"   پاسخ: {faq['answer']}\n\n"
        
        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "سؤال کاربر: {user_message}\n\n{context}")
        ])
        
        formatted_prompt = prompt.format_messages(
            user_message=user_message,
            context=context_text
        )
        
        try:
            response = self.llm.invoke(formatted_prompt)
            
            # Calculate latency
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Get token usage (if available)
            tokens_in = getattr(response, 'usage_metadata', {}).get('input_tokens', 0)
            tokens_out = getattr(response, 'usage_metadata', {}).get('output_tokens', 0)
            
            answer = response.content.strip()
            
            # Quality check
            is_quality_good = self._check_answer_quality(answer)
            
            return {
                "answer": answer,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "latency_ms": latency_ms,
                "is_quality_good": is_quality_good
            }
            
        except Exception as e:
            print(f"Answer generation error: {e}")
            return {
                "answer": "متأسفانه خطایی رخ داده است. لطفاً دوباره تلاش کنید.",
                "tokens_in": 0,
                "tokens_out": 0,
                "latency_ms": int((time.time() - start_time) * 1000),
                "is_quality_good": False
            }
    
    def _check_answer_quality(self, answer: str) -> bool:
        """Check if the answer is of good quality"""
        if not answer or len(answer.strip()) < 10:
            return False
        
        # Check for hedging words in Persian
        hedging_words = [
            "فکر می‌کنم", "احتمالاً", "شاید", "ممکن است", 
            "نمی‌دانم", "مطمئن نیستم", "فکر نمی‌کنم"
        ]
        
        answer_lower = answer.lower()
        for word in hedging_words:
            if word in answer_lower:
                return False
        
        # Check if answer is too long (might be rambling)
        if len(answer) > 500:
            return False
        
        return True


# Global instance - lazy initialization
_answer_generator = None

def get_answer_generator():
    """Get the answer generator instance with lazy initialization"""
    global _answer_generator
    if _answer_generator is None:
        _answer_generator = AnswerGenerator()
    return _answer_generator

# Create a proxy object that initializes lazily
class LazyAnswerGenerator:
    def __getattr__(self, name):
        return getattr(get_answer_generator(), name)

answer_generator = LazyAnswerGenerator()
