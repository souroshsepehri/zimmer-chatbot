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
        page_url = context.get("page_url")
        session_id = context.get("session_id")
        history = context.get("history") or []

        # Initialize smart_result to None (will be set later if smart agent runs)
        smart_result = None

        # Step 1: Run baseline engine first (FAQ/DB lookup)
        baseline = None
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
                    "mode": "baseline_only",  # Baseline failed, smart agent not attempted
                    "smart_agent_raw": None,
                    "baseline_error": str(e),
                },
            }

        # Extract baseline data
        baseline_answer = baseline.get("answer", "")
        baseline_success = baseline.get("success", False)
        baseline_confidence = baseline.get("confidence", 0.0)
        baseline_matched_ids = baseline.get("matched_ids", [])
        baseline_has_match = baseline_success and len(baseline_matched_ids) > 0

        # Step 2: Try SmartAIAgent if enabled (unless mode is "baseline" or "baseline_only")
        if mode != "baseline" and mode != "baseline_only" and smart_agent.enabled:
            try:
                # Build baseline_result dict to pass to smart_agent.run()
                baseline_result_dict = {
                    "answer": baseline_answer,
                    "intent": baseline.get("intent", "unknown"),
                    "confidence": baseline_confidence,
                    "source": baseline.get("source", "unknown"),
                    "success": baseline_success,
                    "matched_ids": baseline_matched_ids,
                    "metadata": baseline.get("metadata", {}),
                }
                
                # Call smart_agent.run() with all parameters
                smart_result = await smart_agent.run(
                    message=message,
                    baseline_result=baseline_result_dict,
                    session_id=session_id,
                    page_url=page_url,
                    history=history,
                )
                logger.debug(f"SmartAIAgent.run() returned: success={smart_result.get('success')}")
            except Exception as e:
                # Log the exception but don't crash
                logger.exception("Smart agent error", exc_info=e)
                # Set smart_result to indicate error
                smart_result = {
                    "answer": None,
                    "success": False,
                    "reason": "exception",
                    "error": str(e),
                }
        elif mode != "baseline" and mode != "baseline_only":
            logger.debug("SmartAIAgent is disabled (missing API key or SMART_AGENT_ENABLED=false). Will use baseline answer.")
            # smart_result remains None to indicate smart agent was not attempted

        # Step 3: Decision logic - choose between smart agent and baseline
        # Use smart agent if:
        #   - smart_result is not None AND success is True AND has a valid non-empty answer
        use_smart_agent = (
            smart_result is not None
            and smart_result.get("success") is True
            and smart_result.get("answer")
            and isinstance(smart_result.get("answer"), str)
            and smart_result.get("answer", "").strip()
        )

        # Determine final mode and final answer
        if use_smart_agent:
            # Smart agent succeeded - use its answer
            final_answer = smart_result.get("answer", "").strip()
            final_mode = "auto" if mode == "auto" else "smart_only"
            logger.info(
                "Smart agent used",
                extra={
                    "mode": final_mode,
                    "message": message[:100],  # First 100 chars for context
                }
            )
        else:
            # Use baseline answer
            final_answer = baseline_answer
            # Determine mode based on whether smart agent was attempted
            if smart_result is not None:
                # Smart agent was attempted but failed
                final_mode = "smart_error"
                reason = smart_result.get("reason", "unknown")
                logger.warning(
                    "SmartAIAgent failed, using baseline fallback",
                    extra={
                        "reason": reason,
                        "smart_agent_success": smart_result.get("success"),
                        "error": smart_result.get("error"),
                    }
                )
            else:
                # Smart agent was not attempted (disabled or mode is baseline)
                final_mode = "baseline_only"
                logger.debug("Using baseline answer (SmartAIAgent not available or disabled)")

        # Build smart_agent_raw with proper structure
        # Ensure it always has: { answer, success, reason, error? } or null
        if smart_result is not None:
            smart_agent_raw = {
                "answer": smart_result.get("answer"),
                "success": smart_result.get("success", False),
                "reason": smart_result.get("reason", "unknown"),
            }
            if smart_result.get("error"):
                smart_agent_raw["error"] = smart_result.get("error")
        else:
            smart_agent_raw = None

        # Build debug_info with required structure
        debug_info = {
            "mode": final_mode,  # "auto", "baseline_only", "smart_only", or "smart_error"
            "baseline_raw": baseline,
            "smart_agent_raw": smart_agent_raw,  # None if smart agent didn't run, dict if it did
            "matched_ids": baseline.get("matched_ids", []),
            "metadata": baseline.get("metadata", {}),
        }

        # Return final response with exact structure as specified
        return {
            "answer": final_answer,
            "debug_info": debug_info,
            "intent": baseline.get("intent"),
            "confidence": baseline.get("confidence", 0.0),
            "context": str(baseline.get("metadata", {})) if baseline.get("metadata") else "{}",
            "intent_match": baseline.get("success", False),
            "source": final_mode,
            "success": True,
            "matched_faq_id": baseline.get("matched_faq_id"),
            "question": message,
            "category": baseline.get("category"),
            "score": baseline.get("score", 0.0),
        }


# Global instance
chat_orchestrator = ChatOrchestrator()





