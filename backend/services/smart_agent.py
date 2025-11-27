import os
import logging
import asyncio
from typing import List, Dict, Any

from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
import openai
from fastapi import APIRouter

logger = logging.getLogger("smart_agent")


class SmartAIAgent:
    def __init__(self) -> None:
        self.enabled: bool = False
        self.model: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            logger.warning("SmartAIAgent: OPENAI_API_KEY not set. Smart agent is DISABLED and system will use baseline engine only.")
            return

        # استفاده از SDK legacy (v0.x)
        try:
            openai.api_key = api_key
            self._use_legacy = True
        except (AttributeError, TypeError):
            # اگر SDK جدید باشد، از client استفاده می‌کنیم
            try:
                self._openai_client = openai.OpenAI(api_key=api_key)
                self._use_legacy = False
            except Exception as e:
                logger.error("SmartAIAgent: failed to initialize OpenAI client: %s", e)
                return

        self.api_key = api_key
        self.enabled = True
        logger.info("SmartAIAgent initialized with model %s", self.model)

    def _convert_messages(self, messages: List[BaseMessage]) -> List[Dict[str, str]]:
        converted = []
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

        try:
            payload_messages = self._convert_messages(messages)

            # چون openai.ChatCompletion.create سینک است، در async از loop.run_in_executor استفاده کن
            loop = asyncio.get_running_loop()

            def _call_openai():
                if self._use_legacy:
                    # SDK legacy (v0.x)
                    return openai.ChatCompletion.create(
                        model=self.model,
                        messages=payload_messages,
                        temperature=0.2,
                    )
                else:
                    # SDK جدید (v1.x)
                    return self._openai_client.chat.completions.create(
                        model=self.model,
                        messages=payload_messages,
                        temperature=0.2,
                    )

            resp = await loop.run_in_executor(None, _call_openai)

            try:
                # سازگاری با هر دو SDK
                if self._use_legacy:
                    answer = resp["choices"][0]["message"]["content"]
                else:
                    # SDK جدید
                    answer = resp.choices[0].message.content
            except Exception as e:
                logger.exception("SmartAIAgent: unexpected OpenAI response format: %s", e)
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
            logger.error("SmartAIAgent: error during LLM call: %s", e, exc_info=True)
            return {
                "answer": None,
                "success": False,
                "reason": "llm_error",
                "error": str(e),
            }


# Global agent instance
# This will be initialized when the module is imported
logger.info("SmartAIAgent: Creating global instance...")
smart_agent = SmartAIAgent()
if smart_agent.enabled:
    logger.info("SmartAIAgent: Global instance created and enabled")
else:
    logger.warning("SmartAIAgent: Global instance created but disabled")

# ---------------------------------------------------------
# FastAPI router for health / status
# ---------------------------------------------------------
router = APIRouter()


@router.get("/smart-agent/status")
async def smart_agent_status():
    """
    Lightweight status endpoint for SmartAIAgent.
    Used for debugging / health checks.
    """
    env_info = {
        "SMART_AGENT_ENABLED": os.getenv("SMART_AGENT_ENABLED"),
        "OPENAI_API_KEY_PRESENT": bool(os.getenv("OPENAI_API_KEY")),
        "OPENAI_MODEL": os.getenv("OPENAI_MODEL"),
    }
    return {
        "enabled": getattr(smart_agent, "enabled", False),
        "model": getattr(smart_agent, "model", None),
        "env": env_info,
    }


# Public exports
__all__ = ["SmartAIAgent", "smart_agent", "router"]
