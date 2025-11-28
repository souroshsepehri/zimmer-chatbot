import os
import logging
from typing import List, Dict, Any

from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
import openai

logger = logging.getLogger("smart_agent")


class SmartAIAgent:
    def __init__(self) -> None:
        self.enabled: bool = False
        self.model: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            logger.warning(
                "SmartAIAgent: OPENAI_API_KEY not set. Smart agent is DISABLED and system will use baseline engine only."
            )
            return

        openai.api_key = api_key

        self.enabled = True
        logger.info("SmartAIAgent initialized with model %s", self.model)

    def _convert_messages(self, messages: List[BaseMessage]) -> List[Dict[str, str]]:
        converted: List[Dict[str, str]] = []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                role = "system"
            elif isinstance(msg, HumanMessage):
                role = "user"
            else:
                role = "user"
            converted.append({"role": role, "content": str(msg.content)})
        return converted

    async def run(self, messages: List[BaseMessage]) -> Dict[str, Any]:
        if not self.enabled:
            return {
                "answer": None,
                "success": False,
                "reason": "disabled",
                "error": "SmartAIAgent is disabled (no OPENAI_API_KEY)",
            }

        import asyncio

        try:
            payload_messages = self._convert_messages(messages)

            loop = asyncio.get_running_loop()

            def _call_openai():
                # استفاده از API legacy تا وارد مسیر httpx جدید نشویم
                return openai.ChatCompletion.create(
                    model=self.model,
                    messages=payload_messages,
                    temperature=0.2,
                )

            resp = await loop.run_in_executor(None, _call_openai)

            try:
                answer = resp["choices"][0]["message"]["content"]
            except Exception as e:
                logger.exception(
                    "SmartAIAgent: unexpected OpenAI response format: %s", e
                )
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

        except Exception as e:
            logger.error(
                "SmartAIAgent: error during LLM call: %s", e, exc_info=True
            )
            return {
                "answer": None,
                "success": False,
                "reason": "llm_error",
                "error": str(e),
            }


smart_agent = SmartAIAgent()
