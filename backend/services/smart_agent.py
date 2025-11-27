"""
Smart AI Agent Service

Minimal but working SmartAIAgent wrapper around ChatOpenAI.
Uses modern LangChain APIs (no AgentType).
"""

import os
import json
import logging
from typing import Any, Dict, Optional

# Note: .env file is loaded in app.py at the very top, before this module is imported
# Do NOT call load_dotenv here

from langchain_openai import ChatOpenAI

logger = logging.getLogger("smart_agent")


class SmartAIAgent:
    """
    SmartAIAgent wrapper around ChatOpenAI for Zimmer AI Automation chatbot.
    
    - Uses OPENAI_API_KEY and OPENAI_MODEL from environment.
    - Controlled by SMART_AGENT_ENABLED (true/false).
    - Exposes:
      - self.enabled (bool)
      - self.llm (ChatOpenAI or None)
      - async run(...) returning a dict used as smart_agent_raw.
    """

    def __init__(self) -> None:
        """Initialize SmartAIAgent with minimal ASCII-only configuration."""
        api_key = os.getenv("OPENAI_API_KEY")
        model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        enabled_str = os.getenv("SMART_AGENT_ENABLED", "false").lower().strip()
        
        self.enabled = bool(api_key) and enabled_str in ("1", "true", "yes")
        
        if self.enabled:
            # Initialize ChatOpenAI with minimal ASCII-only config
            # IMPORTANT: No default_headers, extra_headers, or any custom headers
            # Farsi text is only allowed in message content (JSON body), not in HTTP headers
            try:
                self.llm = ChatOpenAI(
                    api_key=api_key,
                    model=model_name,
                    temperature=0.2,
                )
                logger.info(f"SmartAIAgent initialized with model={model_name}")
            except Exception as e:
                logger.exception(f"SmartAIAgent: failed to initialize LLM: {e}")
                self.enabled = False
                self.llm = None
        else:
            self.llm = None
            if not api_key:
                logger.warning("SmartAIAgent: OPENAI_API_KEY not set. Disabling smart agent.")
            elif enabled_str not in ("1", "true", "yes"):
                logger.info(f"SmartAIAgent: disabled by SMART_AGENT_ENABLED='{enabled_str}'")

    async def answer(
        self,
        message: str,
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Main entrypoint for SmartAIAgent that returns a standardized response dict.
        This method wraps run() and converts the result to the expected format.

        Args:
            message: User's message/question
            source: Optional source identifier (not used in headers)
            metadata: Optional metadata dict (converted to baseline_result)

        Returns:
            Dictionary with answer, intent, confidence, source, success, metadata.
        """
        # Convert metadata to baseline_result format for run()
        baseline_result = metadata if isinstance(metadata, dict) else None
        
        # Call run() which handles everything safely
        result = await self.run(message=message, baseline_result=baseline_result)
        
        # Convert run() result format to answer() format
        if not result.get("success"):
            return {
                "answer": None,
                "intent": None,
                "confidence": None,
                "source": "smart_agent_disabled" if result.get("reason") == "disabled" else "smart_agent",
                "success": False,
                "metadata": {
                    "reason": result.get("reason", "unknown_error"),
                    "error": result.get("error"),
                },
            }
        
        return {
            "answer": result.get("answer"),
            "intent": None,  # Smart agent doesn't detect intent separately
            "confidence": 0.85,  # Default confidence for LLM-generated answers
            "source": "smart_agent",
            "success": True,
            "metadata": {
                "reasoning": "LLM-generated answer",
            },
        }

    async def run(
        self,
        *,
        message: str,
        baseline_result: dict | None = None,
        session_id: str | None = None,
        page_url: str | None = None,
        history: list | None = None,
    ) -> dict:
        """
        Run the smart agent. Returns a dict:
        {
          "answer": str | None,
          "success": bool,
          "reason": str,
          "error": str | None
        }
        
        Args:
            message: User's message/question
            baseline_result: Optional baseline result dict (from FAQ/DB lookup)
            session_id: Optional session identifier
            page_url: Optional page URL for context
            history: Optional conversation history
        
        Note: Farsi text in system_prompt and user_message is fine (goes in JSON body).
        No custom HTTP headers are used - only ASCII headers set by the SDK.
        """
        if not self.enabled or self.llm is None:
            return {
                "answer": None,
                "success": False,
                "reason": "disabled",
                "error": None,
            }
        
        # Build system prompt - Farsi is OK here (goes in message content, not headers)
        system_prompt = (
            "You are the intelligent website assistant for Zimmer AI Automation (Zimmerman). "
            "You always answer in fluent Persian (Farsi). Explain clearly what Zimmer does: "
            "building custom AI automations for businesses, multi-channel chatbots (Telegram, WhatsApp, Instagram), "
            "travel agency AI, online shop agents, debt collector automation, SEO content agent, etc. "
            "If user asks about Zimmer's services, be specific and helpful even if the FAQ DB is empty. "
            "If context about FAQ / DB results is provided, you MAY use it but you are not limited to it."
        )
        
        # Add baseline_result and other context if provided
        # Safely format as JSON-like string (avoid non-ASCII in string formatting that might leak to headers)
        context_parts = []
        if baseline_result:
            try:
                context_parts.append(f"baseline_result: {json.dumps(baseline_result, ensure_ascii=False)}")
            except Exception:
                # Fallback to string representation if JSON serialization fails
                try:
                    context_parts.append(f"baseline_result: {str(baseline_result)}")
                except Exception:
                    pass  # Don't let bad context crash the agent
        
        if session_id:
            context_parts.append(f"session_id: {session_id}")
        
        if page_url:
            context_parts.append(f"page_url: {page_url}")
        
        if history:
            try:
                context_parts.append(f"history: {json.dumps(history, ensure_ascii=False)}")
            except Exception:
                try:
                    context_parts.append(f"history: {str(history)}")
                except Exception:
                    pass
        
        if context_parts:
            system_prompt += "\n\nAdditional context: " + " | ".join(context_parts)
        
        # Build messages - Farsi is fine in message content
        try:
            from langchain_core.messages import SystemMessage, HumanMessage
        except ImportError:
            try:
                from langchain.schema import SystemMessage, HumanMessage
            except ImportError:
                logger.error("Could not import SystemMessage/HumanMessage from langchain_core or langchain.schema")
                return {
                    "answer": None,
                    "success": False,
                    "reason": "import_error",
                    "error": "Could not import LangChain message classes",
                }
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=message),
        ]
        
        try:
            # Call LLM - no custom headers, only SDK default headers (ASCII-only)
            resp = await self.llm.ainvoke(messages)  # type: ignore[arg-type]
            answer_text = resp.content if hasattr(resp, "content") else str(resp)
            
            return {
                "answer": answer_text,
                "success": True,
                "reason": "ok",
                "error": None,
            }
        except Exception as e:
            logger.error(f"SmartAIAgent: error during LLM call: {e}", exc_info=True)
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
        baseline_result = context if isinstance(context, dict) else None
        return await self.run(message=message, baseline_result=baseline_result)

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
        
        baseline_result = context if isinstance(context, dict) else None
        result = await self.run(message=message, baseline_result=baseline_result)
        
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


# FastAPI router for debugging
from fastapi import APIRouter

router = APIRouter()


@router.get("/smart-agent/status")
async def smart_agent_status():
    import os
    return {
        "enabled": smart_agent.enabled,
        "has_llm": bool(smart_agent.llm),
        "env": {
            "SMART_AGENT_ENABLED": os.getenv("SMART_AGENT_ENABLED"),
            "OPENAI_API_KEY_PRESENT": bool(os.getenv("OPENAI_API_KEY")),
            "OPENAI_MODEL": os.getenv("OPENAI_MODEL"),
        },
    }
