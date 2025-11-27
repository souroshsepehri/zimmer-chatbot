import os
import logging
from langchain_openai import ChatOpenAI
from fastapi import APIRouter

logger = logging.getLogger("smart_agent")

class SmartAIAgent:
    def __init__(self) -> None:
        self.enabled = os.getenv("SMART_AGENT_ENABLED", "false").lower() == "true"

        if not self.enabled:
            logger.info("SmartAIAgent: disabled via SMART_AGENT_ENABLED env")
            self.llm = None
            return

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("SmartAIAgent: OPENAI_API_KEY not set. Smart agent disabled.")
            self.enabled = False
            self.llm = None
            return

        model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

        try:
            # ✅ فقط پارامترهای استاندارد، بدون هدر فارسی / سفارشی
            self.llm = ChatOpenAI(
                model=model,
                temperature=0.2,
                openai_api_key=api_key,
            )

            logger.info("SmartAIAgent: initialized with model %s", model)
        except Exception as e:
            logger.exception("SmartAIAgent: failed to initialize LLM: %s", e)
            self.enabled = False
            self.llm = None

    async def run(self, messages):
        """
        messages: list[BaseMessage] (System / Human / AI)
        """
        if not self.enabled or self.llm is None:
            return {
                "answer": None,
                "success": False,
                "reason": "disabled",
                "error": "Smart agent disabled",
            }

        try:
            resp = await self.llm.ainvoke(messages)
            content = resp.content if hasattr(resp, "content") else str(resp)
            return {
                "answer": content,
                "success": True,
                "reason": "ok",
                "error": None,
            }
        except Exception as e:
            logger.exception("SmartAIAgent: error during LLM call: %s", e)
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
        "has_llm": bool(getattr(smart_agent, "llm", None)),
        "env": env_info,
    }


# Public exports
__all__ = ["SmartAIAgent", "smart_agent", "router"]
