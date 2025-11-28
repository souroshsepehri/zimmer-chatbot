import os
import logging
import asyncio
from typing import List, Dict, Any

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
        context: dict | None = None,
        debug: bool = False,
        question: str | None = None,
    ) -> dict:
        """
        Main entry point for SmartAIAgent.

        Args:
            message: The user's message/query (primary parameter)
            context: Optional context dictionary for additional information
            debug: Optional debug flag
            question: Deprecated parameter for backwards compatibility. If message is None and question is provided, message will be set to question.

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

        # Build system prompt from context if provided
        system_prompt = (
            "You are the intelligent website assistant for Zimmer AI Automation (Zimmerman). "
            "You always answer in fluent Persian (Farsi). Explain clearly what Zimmer does: "
            "building custom AI automations for businesses, multi-channel chatbots (Telegram, WhatsApp, Instagram), "
            "travel agency AI, online shop agents, debt collector automation, SEO content agent, etc. "
            "If user asks about Zimmer's services, be specific and helpful even if the FAQ DB is empty. "
            "If context about FAQ / DB results is provided, you MAY use it but you are not limited to it."
        )
        
        if context:
            context_str = str(context)
            system_prompt += f"\n\nAdditional context for you (may be from DB or previous logic): {context_str}"

        # Convert string message to message format
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=message),
        ]

        payload_messages = self._convert_messages(messages)

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
