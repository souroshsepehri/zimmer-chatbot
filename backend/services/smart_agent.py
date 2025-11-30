import os
import logging
import asyncio
from typing import List, Dict, Any, Optional

import requests
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage

logger = logging.getLogger("smart_agent")


class SmartAIAgent:
    """
    Simple smart agent that calls OpenAI Chat Completion API directly via requests,
    avoiding the new openai client + httpx unicode header issues.
    """

    def __init__(self) -> None:
        self.enabled: bool = False
        self.model: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.api_key: str | None = os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            logger.warning(
                "SmartAIAgent: OPENAI_API_KEY not set. Smart agent is DISABLED and system will use baseline engine only."
            )
            return

        # فقط برای لاگ
        logger.info("SmartAIAgent initialized with model %s", self.model)
        self.enabled = True

    def _convert_messages(self, messages: List[BaseMessage]) -> List[Dict[str, str]]:
        """Convert LangChain-style messages to OpenAI chat format."""
        converted: List[Dict[str, str]] = []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                role = "system"
            elif isinstance(msg, HumanMessage):
                role = "user"
            else:
                # برای سادگی هر چیز ناشناخته را user حساب می‌کنیم
                role = "user"
            converted.append({"role": role, "content": str(msg.content)})
        return converted

    async def run(
        self,
        message: str | None = None,
        *,
        baseline_result: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        page_url: Optional[str] = None,
        history: Optional[List[Dict[str, Any]]] = None,
        context: Optional[Dict[str, Any]] = None,
        debug: bool = False,
        question: str | None = None,
        **kwargs,
    ) -> dict:
        """
        Main entry point for SmartAIAgent.

        Args:
            message: The user's message/query (primary parameter)
            baseline_result: Optional baseline result from answering_agent
            session_id: Optional session identifier
            page_url: Optional page URL for context
            history: Optional chat history
            context: Optional context dictionary for additional information
            debug: Optional debug flag
            question: Deprecated parameter for backwards compatibility. If message is None and question is provided, message will be set to question.
            **kwargs: Additional keyword arguments

        Returns:
            Dict with keys: answer, success, reason, error
        """
        # Handle backwards compatibility: if message is None and question is not None, set message = question
        if message is None and question is not None:
            message = question

        # Validate that message is provided
        if message is None:
            raise ValueError("SmartAIAgent.run: `message` is required")

        if not self.enabled:
            return {
                "answer": None,
                "success": False,
                "reason": "disabled",
                "error": "SmartAIAgent is disabled (no OPENAI_API_KEY)",
            }

        # Strict system prompt - only use DB/site context
        system_prompt = (
            "تو فقط دستیار هوشمند همین وب‌سایت و همین سیستم هستی.\n"
            "منابع تو فقط این‌ها هستند:\n"
            "- پاسخ اولیه‌ای که از موتور اصلی بات (دیتابیس، FAQ، جستجو) گرفته شده است.\n"
            "- متن‌های زمینه و اطلاعاتی که به‌عنوان کانتکست از صفحات سایت و پایگاه داده به تو داده می‌شود.\n\n"
            "قوانین مهم:\n"
            "1) فقط بر اساس همین اطلاعات پاسخ بده. از هیچ دانش عمومی دیگری استفاده نکن.\n"
            "2) اگر سؤال کاربر ربطی به این سایت، خدمات آن یا داده‌های موجود ندارد، صریحاً بگو که من فقط به سوالات مرتبط با همین سایت و اطلاعات ثبت‌شده جواب می‌دهم.\n"
            "3) اگر اطلاعات موجود ناقص است یا مطمئن نیستی، حدس نزن؛ شفاف بگو که اطلاعات کافی ندارم.\n"
            "4) همیشه به زبان فارسی روان، کوتاه و شفاف جواب بده."
        )

        # Build messages list
        messages_list = []
        messages_list.append({"role": "system", "content": system_prompt})

        # Add baseline result as context if available
        if baseline_result and isinstance(baseline_result.get("answer"), str):
            messages_list.append({
                "role": "system",
                "content": f"پاسخ اولیه بر اساس دیتابیس/FAQ:\n{baseline_result['answer']}"
            })

        # Extract context_text from context or kwargs
        context_text = None
        if context and isinstance(context.get("text"), str):
            context_text = context["text"]
        elif "context_text" in kwargs and isinstance(kwargs["context_text"], str):
            context_text = kwargs["context_text"]

        # Add site/DB context if available
        if context_text:
            messages_list.append({
                "role": "system",
                "content": "این متن‌ها از سایت/دیتابیس به‌عنوان زمینه اضافه شده‌اند:\n" + context_text
            })

        # Add chat history if available
        if history:
            for hist_item in history:
                if isinstance(hist_item, dict):
                    role = hist_item.get("role", "user")
                    content = hist_item.get("content") or hist_item.get("text", "")
                    if content:
                        messages_list.append({"role": role, "content": content})

        # Add final user message
        messages_list.append({"role": "user", "content": message})

        payload_messages = messages_list

        async def _async_call() -> Dict[str, Any]:
            loop = asyncio.get_running_loop()

            def _call_openai_sync() -> Dict[str, Any]:
                url = "https://api.openai.com/v1/chat/completions"
                headers = {
                    # هدرها ۱۰۰٪ ASCII هستند تا مشکل encoding نداشته باشیم
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
                data = {
                    "model": self.model,
                    "messages": payload_messages,
                    "temperature": 0.2,
                }

                try:
                    resp = requests.post(url, headers=headers, json=data, timeout=30)
                    resp.raise_for_status()
                except Exception as e:  # network / HTTP error
                    logger.error("SmartAIAgent HTTP error: %s", e, exc_info=True)
                    return {
                        "answer": None,
                        "success": False,
                        "reason": "http_error",
                        "error": str(e),
                    }

                try:
                    j = resp.json()
                    answer = j["choices"][0]["message"]["content"]
                except Exception as e:
                    logger.error("SmartAIAgent parse error: %s", e, exc_info=True)
                    return {
                        "answer": None,
                        "success": False,
                        "reason": "parse_error",
                        "error": str(e),
                    }

                return {
                    "answer": answer,
                    "success": True,
                    "reason": "ok",
                    "error": None,
                }

            return await loop.run_in_executor(None, _call_openai_sync)

        try:
            return await _async_call()
        except Exception as e:
            logger.error("SmartAIAgent: unexpected error: %s", e, exc_info=True)
            return {
                "answer": None,
                "success": False,
                "reason": "llm_error",
                "error": str(e),
            }


# singleton instance used elsewhere in the app
smart_agent = SmartAIAgent()
