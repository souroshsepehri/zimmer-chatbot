"""
Chat Orchestrator Service

Orchestrates between SmartAIAgent and baseline answering_agent,
providing intelligent routing and fallback mechanisms.
"""

import logging
from typing import Any, Dict, Optional

from services.smart_agent import smart_agent
from langchain_core.messages import SystemMessage, HumanMessage
from services.answering_agent import answer_user_query
from core.config import settings

logger = logging.getLogger("services.chat_orchestrator")


class ChatOrchestrator:
    """
    Orchestrate between:
    - SmartAIAgent (web + FAQ + LLM)
    - Baseline answering_agent (FAQ-based / DB-based)
    """

    async def handle_chat(
        self,
        message: str,
        source: Optional[str] = None,
        page_url: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        db: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Handle chat message with deterministic flow:
        1. Run baseline (FAQ/simple chatbot)
        2. If smart_agent enabled, try LLM with baseline context
        3. Return final answer with debug_info
        """
        context = context or {}
        session_id = context.get("session_id")
        source = source or context.get("source") or "unknown"
        page_url = page_url or context.get("page_url")

        # ۱) اجرای baseline / FAQ / simple chatbot
        baseline_result = None
        try:
            baseline_result = answer_user_query(
                user_id=user_id,
                message=message,
                context={
                    "session_id": session_id,
                    "category_filter": context.get("category_filter"),
                    "debug": context.get("debug", False),
                },
                db=db,
            )
        except Exception as e:
            logger.exception("Baseline answering_agent failed: %s", e)
            # Baseline failed - return error with proper debug_info
            return {
                "answer": "متأسفانه در حال حاضر سیستم با مشکل مواجه شده است. لطفاً چند دقیقه دیگر دوباره تلاش کنید.",
                "source": "error",
                "success": False,
                "intent": "error",
                "confidence": 0.0,
                "context": None,
                "intent_match": False,
                "matched_faq_id": None,
                "question": message,
                "category": None,
                "score": 0.0,
                "debug_info": {
                    "mode": "baseline_only",
                    "baseline_raw": None,
                    "smart_agent_raw": None,
                    "matched_ids": [],
                    "metadata": {},
                    "baseline_error": str(e),
                },
            }

        # baseline_result باید حداقل این فیلدها را داشته باشد:
        # answer, intent, confidence, source, success, matched_ids, metadata, tables_queried

        final_answer = baseline_result.get("answer")
        final_source = baseline_result.get("source", "baseline")
        final_success = baseline_result.get("success", True)

        smart_result: Optional[Dict[str, Any]] = None
        mode: Optional[str] = None

        # ۲) Gate SmartAIAgent: only call if baseline result is based on real data, not fallback
        # Extract intent and source from baseline result
        intent = baseline_result.get("intent")
        source = baseline_result.get("source")

        # Define disallowed intents and sources for smart agent
        DISALLOWED_INTENTS_FOR_SMART = {"unknown"}
        DISALLOWED_SOURCES_FOR_SMART = {"fallback", "static_greeting"}

        # Determine if SmartAIAgent should be called
        smart_agent_allowed = (
            settings.smart_agent_enabled
            and getattr(smart_agent, "enabled", False)
            and baseline_result is not None
            and baseline_result.get("success") is True
            and source not in DISALLOWED_SOURCES_FOR_SMART
            and intent not in DISALLOWED_INTENTS_FOR_SMART
        )

        if not smart_agent_allowed:
            logger.info(
                "SmartAIAgent skipped: intent=%s, source=%s, enabled=%s",
                intent,
                source,
                getattr(smart_agent, "enabled", False),
            )
            mode = "baseline_only"
        else:
            mode = "auto"
            
            # Extract history from context if available
            history = context.get("history", []) if context else []
            
            # Extract context_text for smart agent
            context_text = None
            if context and isinstance(context.get("text"), str):
                context_text = context["text"]
            
            try:
                smart_result = await smart_agent.run(
                    message=message,
                    baseline_result=baseline_result,
                    session_id=session_id,
                    page_url=page_url,
                    history=history,
                    context={"text": context_text} if context_text else context,
                )
                logger.debug(
                    "SmartAIAgent.run() returned: success=%s reason=%s",
                    smart_result.get("success"),
                    smart_result.get("reason"),
                )

                if smart_result.get("success"):
                    final_answer = smart_result["answer"]
                    final_source = "smart_agent"
                else:
                    logger.info("SmartAIAgent failed or returned unsuccessfully. Using baseline answer.")
                    final_answer = baseline_result["answer"]
                    final_source = baseline_result.get("source", "baseline")
            except Exception as e:
                logger.exception("ChatOrchestrator: error when calling SmartAIAgent: %s", e)
                smart_result = {
                    "answer": None,
                    "success": False,
                    "reason": "llm_error",
                    "error": str(e),
                }
                logger.info("SmartAIAgent exception. Using baseline answer.")
                final_answer = baseline_result["answer"]
                final_source = baseline_result.get("source", "baseline")
                mode = "baseline_exception"

        debug_info = {
            "baseline_raw": baseline_result,
            "smart_agent_raw": smart_result,
            "mode": mode,
            "matched_ids": baseline_result.get("matched_ids", []),
            "metadata": baseline_result.get("metadata", {}),
        }

        # خروجی نهایی سازگار با ساختار فعلی /api/chat
        return {
            "answer": final_answer,
            "debug_info": debug_info,
            "intent": baseline_result.get("intent"),
            "confidence": baseline_result.get("confidence", 0.0),
            "context": str(baseline_result.get("metadata", {})),
            "intent_match": baseline_result.get("success", False),
            "source": final_source,
            "success": final_success,
            "matched_faq_id": baseline_result.get("matched_faq_id"),
            "question": message,
            "category": baseline_result.get("category"),
            "score": baseline_result.get("score", 0.0),
        }

    async def route_message(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        mode: str = "auto",
        user_id: Optional[str] = None,
        db: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Route a message (wrapper for handle_chat to maintain backward compatibility).
        """
        context = context or {}
        source = context.get("source")
        page_url = context.get("page_url")
        
        return await self.handle_chat(
            message=message,
            source=source,
            page_url=page_url,
            context=context,
            user_id=user_id,
            db=db,
        )


# Global instance
chat_orchestrator = ChatOrchestrator()





