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

# Feature flag: DB-only mode - no OpenAI calls in main chat flow
USE_SMART_AGENT = False  # DB-only mode: no OpenAI calls


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

        # Extract baseline answer safely
        baseline_answer = None
        if isinstance(baseline_result, dict):
            baseline_answer = baseline_result.get("answer") or baseline_result.get("response")

        smart_result: Optional[Dict[str, Any]] = None
        mode = "baseline_only"  # DB-only mode: never call SmartAIAgent

        # DB-only mode: never call SmartAIAgent here
        if baseline_answer:
            final_answer = baseline_answer
            final_source = baseline_result.get("source", "baseline") if isinstance(baseline_result, dict) else "baseline"
            final_success = baseline_result.get("success", True) if isinstance(baseline_result, dict) else True
        else:
            # No data in DB - return fixed Farsi message
            final_answer = (
                "برای این سؤال در حال حاضر هیچ پاسخی در داده‌های ثبت‌شده ندارم. "
                "لطفاً سؤال را به شکل دیگری مطرح کنید یا با پشتیبانی تماس بگیرید."
            )
            final_source = "fallback"
            final_success = False

        logger.info(
            "DB-only mode: using baseline answer. source=%s, has_answer=%s",
            final_source,
            bool(baseline_answer),
        )

        debug_info = {
            "baseline_raw": baseline_result,
            "smart_agent_raw": None,  # Never called in DB-only mode
            "mode": mode,
            "matched_ids": baseline_result.get("matched_ids", []) if isinstance(baseline_result, dict) else [],
            "metadata": baseline_result.get("metadata", {}) if isinstance(baseline_result, dict) else {},
        }

        # خروجی نهایی سازگار با ساختار فعلی /api/chat
        return {
            "answer": final_answer,
            "debug_info": debug_info,
            "intent": baseline_result.get("intent") if isinstance(baseline_result, dict) else None,
            "confidence": baseline_result.get("confidence", 0.0) if isinstance(baseline_result, dict) else 0.0,
            "context": str(baseline_result.get("metadata", {})) if isinstance(baseline_result, dict) else "{}",
            "intent_match": baseline_result.get("success", False) if isinstance(baseline_result, dict) else False,
            "source": final_source,
            "success": final_success,
            "matched_faq_id": baseline_result.get("matched_faq_id") if isinstance(baseline_result, dict) else None,
            "question": message,
            "category": baseline_result.get("category") if isinstance(baseline_result, dict) else None,
            "score": baseline_result.get("score", 0.0) if isinstance(baseline_result, dict) else 0.0,
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





