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

        # ۲) اگر SmartAIAgent فعال است، سعی کن LLM را هم اجرا کنی
        if getattr(smart_agent, "enabled", False):
            mode = "auto"

            # context برای سیستم
            context_dict = {
                "baseline_answer": baseline_result.get("answer"),
                "intent": baseline_result.get("intent"),
                "confidence": baseline_result.get("confidence"),
                "source": baseline_result.get("source"),
                "success": baseline_result.get("success"),
                "matched_ids": baseline_result.get("matched_ids", []),
                "metadata": baseline_result.get("metadata", {}),
                "session_id": session_id or "default_session",
                "page_url": page_url,
                "history": [],
            }

            system_prompt = (
                "You are the intelligent website assistant for Zimmer AI Automation (Zimmerman). "
                "You always answer in fluent Persian (Farsi). Explain clearly what Zimmer does: "
                "building custom AI automations for businesses, multi-channel chatbots (Telegram, WhatsApp, Instagram), "
                "travel agency AI, online shop agents, debt collector automation, SEO content agent, etc. "
                "If user asks about Zimmer's services, be specific and helpful even if the FAQ DB is empty. "
                "If context about FAQ / DB results is provided, you MAY use it but you are not limited to it.\n\n"
                f"Additional context for you (may be from DB or previous logic): {context_dict}"
            )

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=message),
            ]

            try:
                smart_result = await smart_agent.run(messages)
                # smart_result باید ساختاری شبیه این داشته باشد:
                # { "answer": str | None, "success": bool, "reason": str, "error": str | None }

                if smart_result.get("success") and smart_result.get("answer"):
                    final_answer = smart_result["answer"]
                    final_source = f"smart:{baseline_result.get('source', 'baseline')}"
                    final_success = True
                else:
                    # LLM جواب نداده → fallback به baseline
                    mode = "baseline_exception"
            except Exception as e:
                logger.exception("ChatOrchestrator: error when calling SmartAIAgent: %s", e)
                smart_result = {
                    "answer": None,
                    "success": False,
                    "reason": "llm_error",
                    "error": str(e),
                }
                mode = "baseline_exception"
        else:
            mode = "baseline_only"

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





