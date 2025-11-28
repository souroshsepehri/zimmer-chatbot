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

    async def run(self, messages: List[BaseMessage]) -> Dict[str, Any]:
        """
        Main entry point used by chat_orchestrator.

        Returns a dict with keys: answer, success, reason, error
        """
        if not self.enabled:
            return {
                "answer": None,
                "success": False,
                "reason": "disabled",
                "error": "SmartAIAgent is disabled (no OPENAI_API_KEY)",
            }

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
