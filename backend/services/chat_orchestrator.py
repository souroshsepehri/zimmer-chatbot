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

        # Step 2: Try to use SmartAIAgent (unless mode is "baseline")
        smart_result = None
        if mode != "baseline" and smart_agent.enabled:
            # Use SmartAIAgent.run() - the high-level entrypoint
            try:
                smart_result = await smart_agent.run(
                    message=message,
                    context={
                        "baseline_answer": baseline_answer,
                        **baseline_debug,
                    },
                )
                logger.debug(f"SmartAIAgent.run() returned: success={smart_result.get('success')}")
            except Exception as e:
                # Log error but don't crash - continue with baseline answer
                logger.error(f"SmartAIAgent.run() failed: {e}. Continuing with baseline answer.")
                smart_result = None
        elif mode != "baseline":
            logger.debug("SmartAIAgent is disabled (missing API key or SMART_AGENT_ENABLED=false). Using baseline answer only.")

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
            smart_answer = smart_result.get("answer")
            if smart_answer and smart_answer.strip():
                # Use SmartAgent's answer as the final answer
                answer = smart_answer
                source = "smart_agent"
                success = True
                logger.info("Using SmartAIAgent answer (success=True)")
            else:
                # SmartAgent returned success but no answer - fallback to baseline
                answer = baseline_answer
                source = baseline.get("source", "fallback")
                logger.warning("SmartAIAgent returned success=True but empty answer. Using baseline.")
        else:
            # SmartAgent not available or failed - use baseline
            answer = baseline_answer
            source = baseline.get("source", "fallback")
            if smart_result is not None:
                logger.info(f"SmartAIAgent failed: reason={smart_result.get('reason')}. Using baseline answer.")
            else:
                logger.info("Using baseline answer (SmartAIAgent not available or disabled)")
        
        # Always store smart_result in debug_info (even if None or failed)
        debug_info["smart_agent_raw"] = smart_result

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





