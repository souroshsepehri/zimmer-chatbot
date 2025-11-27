"""
Chat Orchestrator Service

Orchestrates between SmartAIAgent and baseline answering_agent,
providing intelligent routing and fallback mechanisms.
"""

import logging
from typing import Any, Dict, Optional

from services.smart_agent import smart_agent
from services.answering_agent import answer_user_query

logger = logging.getLogger("chat_orchestrator")


class ChatOrchestrator:
    """
    Orchestrate between:
    - SmartAIAgent (web + FAQ + LLM)
    - Baseline answering_agent (FAQ-based / DB-based)
    """

    async def route_message(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        mode: str = "auto",
        user_id: Optional[str] = None,
        db: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Route a message: first try SmartAIAgent, then fall back to baseline if needed.

        Flow:
        1. Try SmartAIAgent first (unless mode is "baseline")
        2. Run baseline engine
        3. Decision: Use smart agent if it succeeded AND (baseline has no match OR smart agent has higher confidence)
        4. Otherwise use baseline answer

        Args:
            message: User's message
            context: Optional context dict (session_id, page_url, history, ip, user_agent, etc.)
            mode: Routing mode - "auto", "smart_agent", or "baseline"
            user_id: Optional user identifier
            db: Optional database session

        Returns:
            Dictionary matching ChatResponse schema with:
            - answer: Final answer text
            - source: "smart_agent" or "baseline" or "baseline:baseline_exception"
            - debug_info.smart_agent_raw: Smart agent result (or None)
            - debug_info.baseline_raw: Baseline result
            - debug_info.mode: "smart_agent", "baseline", or "baseline_exception"
        """
        context = context or {}
        session_id = context.get("session_id")
        source = context.get("source") or "unknown"

        # Step 1: Run baseline engine first (FAQ/DB lookup)
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

        # Extract baseline answer
        baseline_answer = baseline_result.get("answer", "")

        # Initialize debug_info with baseline data
        debug_info: Dict[str, Any] = {
            "baseline_raw": baseline_result,
            "mode": None,
            "matched_ids": baseline_result.get("matched_ids", []),
            "metadata": baseline_result.get("metadata", {}),
            "smart_agent_raw": None,
        }

        # Start with baseline answer and source
        final_answer = baseline_answer
        final_source = baseline_result.get("source", "baseline")

        # -------------------------------
        # Try SmartAIAgent if available
        # -------------------------------
        smart_used = False

        if smart_agent.enabled and smart_agent.llm:
            logger.debug("ChatOrchestrator: Attempting to use SmartAIAgent for message: %s", message[:50])
            smart_raw = await smart_agent.run(
                message=message,
                source=source,
                baseline_result=baseline_result,
            )
            debug_info["smart_agent_raw"] = smart_raw

            if smart_raw.get("success") and smart_raw.get("answer"):
                final_answer = smart_raw["answer"]
                final_source = "smart_agent"
                debug_info["mode"] = "smart_only"
                smart_used = True
                logger.info("ChatOrchestrator: Using SmartAIAgent answer (mode=smart_only)")
            else:
                debug_info["mode"] = "smart_error"
                logger.info(
                    "ChatOrchestrator: SmartAIAgent failed or returned empty answer. reason=%s error=%s, falling back to baseline",
                    smart_raw.get("reason"),
                    smart_raw.get("error"),
                )
        else:
            debug_info["mode"] = "baseline_only"
            debug_info["smart_agent_raw"] = None
            if not smart_agent.enabled:
                logger.debug("ChatOrchestrator: SmartAIAgent is disabled, using baseline only")
            elif not smart_agent.llm:
                logger.debug("ChatOrchestrator: SmartAIAgent.llm is None, using baseline only")

        # If smart agent didn't handle it, we already have baseline answer
        if not smart_used and not final_answer:
            # If baseline also had no answer, keep the previous fallback behavior
            final_answer = baseline_answer or "متأسفانه پاسخ مناسبی برای این سؤال پیدا نکردم. لطفاً سؤال خود را به شکل دیگری مطرح کنید یا با پشتیبانی تماس بگیرید."

        # Build the response using final_answer and debug_info
        # (keep the same response structure as before)
        return {
            "answer": final_answer,
            "debug_info": debug_info,
            "intent": baseline_result.get("intent"),
            "confidence": baseline_result.get("confidence", 0.0),
            "context": str(baseline_result.get("metadata", {})) if baseline_result.get("metadata") else "{}",
            "intent_match": baseline_result.get("success", False),
            "source": final_source,
            "success": True,
            "matched_faq_id": baseline_result.get("matched_faq_id"),
            "question": message,
            "category": baseline_result.get("category"),
            "score": baseline_result.get("score", 0.0),
        }


# Global instance
chat_orchestrator = ChatOrchestrator()





