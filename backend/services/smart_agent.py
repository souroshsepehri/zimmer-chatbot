"""
Smart AI Agent Service

Minimal but working SmartAIAgent wrapper around ChatOpenAI.
Uses modern LangChain APIs (no AgentType).
"""

import os
import logging
from typing import Any, Dict, Optional

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not available, rely on system environment
    pass

try:
    # Newer LangChain style
    from langchain_openai import ChatOpenAI
except ImportError:  # fallback for older LangChain installations
    # type: ignore
    from langchain.chat_models import ChatOpenAI


logger = logging.getLogger("smart_agent")


def get_env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "y", "on")


class SmartAIAgent:
    """
    Minimal but working SmartAIAgent wrapper around ChatOpenAI.

    - Uses OPENAI_API_KEY and OPENAI_MODEL from environment.
    - Controlled by SMART_AGENT_ENABLED (true/false).
    - Exposes:
      - self.enabled (bool)
      - self.llm (ChatOpenAI or None)
      - async run(...) returning a dict used as smart_agent_raw.
    """

    def __init__(self) -> None:
        self.enabled: bool = False
        self.llm: Optional[ChatOpenAI] = None
        self.model_name: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

        api_key = os.getenv("OPENAI_API_KEY")
        enabled_flag = get_env_bool("SMART_AGENT_ENABLED", default=True)

        logger.info(
            "SmartAIAgent init: api_key_present=%s, SMART_AGENT_ENABLED=%s, model=%s",
            bool(api_key),
            os.getenv("SMART_AGENT_ENABLED"),
            self.model_name,
        )

        if not api_key:
            logger.warning(
                "SmartAIAgent: OPENAI_API_KEY not set. Smart agent is DISABLED, baseline will be used."
            )
            return

        if not enabled_flag:
            logger.info(
                "SmartAIAgent: SMART_AGENT_ENABLED is false. Smart agent disabled by configuration."
            )
            return

        try:
            self.llm = ChatOpenAI(
                model=self.model_name,
                temperature=0.2,
                openai_api_key=api_key,
            )
            self.enabled = True
            logger.info(
                "SmartAIAgent initialized successfully with model %s", self.model_name
            )
        except Exception as e:
            logger.exception(
                "SmartAIAgent: failed to initialize ChatOpenAI. Smart agent DISABLED. Error: %s",
                e,
            )
            self.enabled = False
            self.llm = None

    async def run(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        High-level entrypoint used by chat_orchestrator.

        Returns a dict that will be stored under debug_info['smart_agent_raw'].
        """
        if not self.enabled or self.llm is None:
            return {
                "answer": None,
                "success": False,
                "reason": "smart_agent_disabled",
            }

        system_prompt = (
            "You are the intelligent website assistant for Zimmer AI Automation (Zimmerman). "
            "You always answer in fluent Persian (Farsi). "
            "Explain clearly what Zimmer does: building custom AI automations for businesses, "
            "multi-channel chatbots (Telegram, WhatsApp, Instagram), travel agency AI, "
            "online shop agents, debt collector automation, SEO content agent, etc. "
            "If user asks about Zimmer's services, be specific and helpful even if the FAQ DB is empty. "
            "If context about FAQ / DB results is provided, you MAY use it but you are not limited to it."
        )

        # Build messages for LangChain ChatOpenAI
        try:
            from langchain_core.messages import SystemMessage, HumanMessage
        except ImportError:
            # Fallback for older LangChain versions
            try:
                from langchain.schema import SystemMessage, HumanMessage
            except ImportError:
                logger.error("Could not import SystemMessage/HumanMessage from langchain_core or langchain.schema")
                return {
                    "answer": None,
                    "success": False,
                    "reason": "import_error",
                }

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=message),
        ]

        # Optional: incorporate context into the system message
        if context:
            # Keep it simple to avoid crashes
            try:
                extra = f"\n\nAdditional context for you (may be from DB or previous logic): {context}"
                messages[0].content += extra
            except Exception:
                # don't let bad context crash the agent
                pass

        try:
            # Support both async and sync interface depending on installed version
            if hasattr(self.llm, "ainvoke"):
                resp = await self.llm.ainvoke(messages)  # type: ignore[arg-type]
            else:
                # Synchronous fallback - run in thread to avoid blocking
                import asyncio
                resp = await asyncio.to_thread(self.llm.invoke, messages)  # type: ignore[arg-type]

            content = getattr(resp, "content", None) or str(resp)

            return {
                "answer": content,
                "success": True,
                "model": self.model_name,
            }
        except Exception as e:
            logger.exception("SmartAIAgent: error during LLM call: %s", e)
            return {
                "answer": None,
                "success": False,
                "reason": "llm_error",
                "error": str(e),
            }

    # Backwards compatible alias if older code calls generate_answer or similar
    async def generate_answer(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return await self.run(message, context)

    # Minimal compatibility method for router
    async def get_smart_response(
        self,
        message: str = None,
        style: str = "auto",
        context: Optional[Dict[str, Any]] = None,
        request: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Minimal compatibility wrapper for router endpoints"""
        from datetime import datetime, timezone
        
        if request:
            message = getattr(request, "message", message)
            context = getattr(request, "context", context) or context
        
        if not message:
            return {
                "response": "لطفاً پیام خود را وارد کنید.",
                "style": style,
                "response_time": 0.0,
                "web_content_used": False,
                "urls_processed": [],
                "context_used": False,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": "No message provided",
                "debug_info": {},
            }
        
        result = await self.run(message, context=context)
        
        if result and result.get("success"):
            return {
                "response": result.get("answer", ""),
                "style": style,
                "response_time": 0.0,
                "web_content_used": False,
                "urls_processed": [],
                "context_used": bool(context),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": None,
                "debug_info": result,
            }
        else:
            return {
                "response": "متأسفانه در حال حاضر سرویس هوشمند در دسترس نیست.",
                "style": style,
                "response_time": 0.0,
                "web_content_used": False,
                "urls_processed": [],
                "context_used": False,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": result.get("reason", "SmartAIAgent disabled") if result else "SmartAIAgent disabled",
                "debug_info": {},
            }

    # Minimal compatibility method for URL reading
    async def read_url_content(self, url: str, max_length: int = 5000) -> Dict[str, Any]:
        """Minimal compatibility wrapper for URL reading"""
        from datetime import datetime, timezone
        try:
            from services.web_context_reader import read_url_content as read_url
            content = await read_url(url, max_length)
            
            if content.error:
                return {
                    "url": url,
                    "title": "",
                    "description": "",
                    "main_content": "",
                    "links": [],
                    "images": [],
                    "metadata": {},
                    "timestamp": content.timestamp,
                    "error": content.error,
                }
            
            return {
                "url": content.url,
                "title": content.title,
                "description": content.description,
                "main_content": content.main_content,
                "links": content.links,
                "images": content.images,
                "metadata": content.metadata,
                "timestamp": content.timestamp,
                "error": None,
            }
        except Exception as e:
            logger.exception(f"Error reading URL {url}: {e}")
            return {
                "url": url,
                "title": "",
                "description": "",
                "main_content": "",
                "links": [],
                "images": [],
                "metadata": {},
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": str(e),
            }


# Global instance used by the rest of the app
smart_agent = SmartAIAgent()
