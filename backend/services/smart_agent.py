import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from fastapi import APIRouter
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

logger = logging.getLogger("smart_agent")
logger.setLevel(logging.INFO)

# ---------------------------------------------------------
# Load environment from explicit .env paths
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

POSSIBLE_ENV_PATHS = [
    BASE_DIR / ".env",          # backend/.env
    BASE_DIR.parent / ".env",   # project_root/.env
]

for env_path in POSSIBLE_ENV_PATHS:
    if env_path.exists():
        try:
            load_dotenv(env_path, override=False)
            logger.info("SmartAIAgent: Loaded env from %s", env_path)
        except Exception as e:
            logger.error("SmartAIAgent: Failed to load %s: %s", env_path, e)

# ---------------------------------------------------------
# SmartAIAgent implementation
# ---------------------------------------------------------
class SmartAIAgent:
    """
    LangChain-based smart assistant for Zimmer website.

    - Uses ChatOpenAI via langchain_openai
    - Always answers in Persian (Farsi)
    - Acts as a general intelligent assistant for Zimmer,
      not limited to FAQ DB.
    """

    def __init__(self) -> None:
        # Read env
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        enabled_flag = os.getenv("SMART_AGENT_ENABLED", "false").lower() in {"1", "true", "yes"}

        self.api_key: Optional[str] = api_key
        self.model: str = model
        self.enabled: bool = False
        self.llm: Optional[ChatOpenAI] = None

        if not enabled_flag:
            logger.warning(
                "SmartAIAgent: SMART_AGENT_ENABLED is not true (value: '%s'). Smart agent will be disabled.",
                os.getenv("SMART_AGENT_ENABLED", "not set")
            )
            return

        if not api_key:
            logger.warning("SmartAIAgent: OPENAI_API_KEY not set. Smart agent will be disabled.")
            return

        try:
            # No custom non-ASCII headers; let langchain_openai handle the client
            logger.info("SmartAIAgent: Initializing ChatOpenAI with model=%s", self.model)
            self.llm = ChatOpenAI(
                model=self.model,
                api_key=self.api_key,
                temperature=0.2,
                streaming=False,
            )
            self.enabled = True
            logger.info("SmartAIAgent: Successfully initialized with model=%s, enabled=True", self.model)
        except Exception as e:
            logger.exception("SmartAIAgent: Failed to initialize LLM: %s", e)
            self.enabled = False
            self.llm = None

    async def run(
        self,
        *,
        message: str,
        source: Optional[str],
        baseline_result: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Run the smart agent.

        Inputs:
        - message: user question (string)
        - source: source string from /api/chat (e.g. widget, public-smart-test)
        - baseline_result: the dict produced by the baseline FAQ engine
          (can be None).

        Returns a dict that will be stored in debug_info.smart_agent_raw:
        {
          "answer": str | None,
          "success": bool,
          "reason": str,
          "error": str | None
        }
        """
        if not self.enabled or not self.llm:
            return {
                "answer": None,
                "success": False,
                "reason": "disabled",
                "error": None,
            }

        # Safe JSON-serializable context
        context_payload: Dict[str, Any] = baseline_result or {}
        try:
            context_json = json.dumps(context_payload, ensure_ascii=False)
        except Exception:
            context_json = "{}"

        system_text = (
            "You are the intelligent website assistant for Zimmer AI Automation (Zimmerman).\n"
            "You ALWAYS answer in fluent Persian (Farsi).\n"
            "Explain clearly what Zimmer does: building custom AI automations for businesses, "
            "multi-channel chatbots (Telegram, WhatsApp, Instagram), travel agency AI, "
            "online shop agents, debt collector automation, SEO content agent, etc.\n"
            "If the user asks about Zimmer's services, be specific, structured and helpful "
            "even if the FAQ database is empty.\n"
            "If context about FAQ / DB results is provided, you MAY use it but you are NOT limited to it.\n\n"
            f"Additional context (may be from DB or previous logic) as JSON: {context_json}"
        )

        messages = [
            SystemMessage(content=system_text),
            HumanMessage(content=message),
        ]

        try:
            resp = await self.llm.ainvoke(messages)  # type: ignore[arg-type]
        except Exception as e:
            logger.exception("SmartAIAgent: error during LLM call: %s", e)
            return {
                "answer": None,
                "success": False,
                "reason": "llm_error",
                "error": str(e),
            }

        if isinstance(resp, AIMessage):
            answer_text = resp.content
        else:
            answer_text = str(resp)

        # Basic sanity check
        if not isinstance(answer_text, str) or not answer_text.strip():
            return {
                "answer": None,
                "success": False,
                "reason": "empty_answer",
                "error": None,
            }

        return {
            "answer": answer_text,
            "success": True,
            "reason": "ok",
            "error": None,
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
