"""
Chat Orchestrator Service

Orchestrates between SmartAIAgent and baseline answering_agent,
providing intelligent routing and fallback mechanisms.
"""

import logging
from typing import Any, Dict, Optional

from services.smart_agent import smart_agent
from services.answering_agent import answer_user_query

logger = logging.getLogger(__name__)


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
        Route a message: first run baseline engine, then enhance with SmartAIAgent if enabled.

        Args:
            message: User's message
            context: Optional context dict (session_id, page_url, history, etc.)
            mode: Routing mode - "auto", "smart_agent", or "baseline"
            user_id: Optional user identifier
            db: Optional database session

        Returns:
            Dictionary matching ChatResponse schema
        """
        context = context or {}
        page_url = context.get("page_url")
        session_id = context.get("session_id")
        history = context.get("history") or []

        # Step 1: Always run baseline engine first
        try:
            baseline = answer_user_query(
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
                    "error": str(e),
                    "mode": "error",
                },
            }

        # Extract baseline data
        baseline_answer = baseline.get("answer", "")
        baseline_debug = {
            "intent": baseline.get("intent", "unknown"),
            "confidence": baseline.get("confidence", 0.0),
            "source": baseline.get("source", "unknown"),
            "success": baseline.get("success", False),
            "matched_ids": baseline.get("matched_ids", []),
            "metadata": baseline.get("metadata", {}),
            "session_id": session_id,
            "page_url": page_url,
            "history": history,
        }

        # Step 2: Try to enhance with SmartAIAgent (unless mode is "baseline")
        smart_result = None
        if mode != "baseline" and smart_agent.enabled:
            try:
                smart_result = await smart_agent.generate_smart_answer(
                    user_message=message,
                    baseline_answer=baseline_answer,
                    debug_context=baseline_debug,
                )
            except Exception as e:
                logger.exception("SmartAIAgent failed during enhancement: %s", e)
                # Continue with baseline answer

        # Step 3: Build final response
        # Start with baseline response structure
        answer = baseline_answer
        intent = baseline.get("intent", "unknown")
        confidence = baseline.get("confidence", 0.0)
        source = baseline.get("source", "fallback")
        success = baseline.get("success", False)
        matched_ids = baseline.get("matched_ids", [])
        metadata = baseline.get("metadata", {})
        
        # Build debug_info with baseline data
        debug_info = {
            "baseline_raw": baseline,
            "mode": mode,
            "matched_ids": matched_ids,
            "metadata": metadata,
        }

        # If SmartAIAgent succeeded, use its answer
        if smart_result is not None and smart_result.get("success") is True:
            answer = smart_result.get("answer", baseline_answer)
            source = "smart+baseline"
            debug_info["smart_agent_raw"] = smart_result
            logger.info("Using SmartAIAgent enhanced answer")
        else:
            # Keep baseline behavior
            debug_info["smart_agent_raw"] = None
            logger.info("Using baseline answer (SmartAIAgent not available or failed)")

        # Return final response (preserving existing structure)
        return {
            "answer": answer,
            "source": source,
            "success": success,
            "intent": intent,
            "confidence": confidence,
            "context": str(metadata) if metadata else None,
            "intent_match": success,
            "matched_faq_id": matched_ids[0] if matched_ids else None,
            "question": message,
            "category": None,
            "score": confidence,
            "debug_info": debug_info,
        }


# Global instance
chat_orchestrator = ChatOrchestrator()





