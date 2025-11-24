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
        Route a message to the appropriate agent based on mode and context.

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

        # Determine which agent to use
        use_smart_agent = False

        if mode == "smart_agent":
            use_smart_agent = True
            logger.info(f"Mode 'smart_agent': forcing SmartAIAgent")
        elif mode == "baseline":
            use_smart_agent = False
            logger.info(f"Mode 'baseline': using answering_agent")
        else:
            # auto mode: decide based on context
            if page_url:
                use_smart_agent = True
                logger.info(f"Auto mode: page_url present, using SmartAIAgent")
            else:
                # For now, default to SmartAIAgent in auto mode
                # Can be adjusted based on performance/requirements
                use_smart_agent = True
                logger.info(f"Auto mode: no page_url, defaulting to SmartAIAgent")

        if use_smart_agent:
            try:
                sa_result = await smart_agent.get_smart_response(
                    message=message,
                    style="auto",
                    context={
                        "session_id": session_id,
                        "page_url": page_url,
                        "history": history,
                    },
                )

                # Check for errors or fallback usage
                error = sa_result.get("error")
                debug_info = sa_result.get("debug_info") or {}
                fallback_used = debug_info.get("fallback_used", False)

                if error or fallback_used:
                    logger.warning(
                        "SmartAIAgent fallback or error detected (error=%s, fallback=%s). Using baseline.",
                        error,
                        fallback_used,
                    )
                    # Fallback to baseline
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
                    return self._normalize_baseline_response(
                        message=message,
                        smart_agent_result=sa_result,
                        baseline=baseline,
                        mode="baseline_fallback",
                    )

                # SmartAIAgent succeeded
                logger.info("SmartAIAgent succeeded, returning response")
                return self._normalize_smart_agent_response(
                    message=message,
                    smart_agent_result=sa_result,
                    mode="smart_agent",
                )

            except Exception as e:
                logger.exception("SmartAIAgent failed, falling back to baseline: %s", e)
                # Fallback to baseline on exception
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
                    return self._normalize_baseline_response(
                        message=message,
                        smart_agent_result=None,
                        baseline=baseline,
                        mode="baseline_exception",
                    )
                except Exception as baseline_error:
                    logger.exception("Baseline also failed: %s", baseline_error)
                    # Last resort: return error response
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
                            "error": str(baseline_error),
                            "mode": "error",
                        },
                    }

        # Use baseline directly (mode == "baseline" or explicit choice)
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
            return self._normalize_baseline_response(
                message=message,
                smart_agent_result=None,
                baseline=baseline,
                mode="baseline",
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

    def _normalize_smart_agent_response(
        self,
        message: str,
        smart_agent_result: Dict[str, Any],
        mode: str,
    ) -> Dict[str, Any]:
        """
        Map SmartAgentResponse to ChatResponse format.

        Args:
            message: Original user message
            smart_agent_result: Result from SmartAIAgent.get_smart_response
            mode: Mode used ("smart_agent")

        Returns:
            Dictionary matching ChatResponse schema
        """
        debug_info = smart_agent_result.get("debug_info") or {}
        
        return {
            "answer": smart_agent_result.get("response", ""),
            "source": f"smart_agent:{mode}",
            "success": smart_agent_result.get("error") is None,
            "intent": debug_info.get("intent"),
            "confidence": debug_info.get("confidence"),
            "context": None,  # Can be populated from debug_info if needed
            "intent_match": debug_info.get("intent") is not None,
            "matched_faq_id": None,  # SmartAIAgent doesn't expose this directly
            "question": message,
            "category": None,
            "score": debug_info.get("confidence"),
            "debug_info": {
                "smart_agent_raw": smart_agent_result,
                "mode": mode,
                "main_source_hint": debug_info.get("main_source_hint"),
                "user_intent_hint": debug_info.get("user_intent_hint"),
                "has_page_content": debug_info.get("has_page_content"),
                "faq_count": debug_info.get("faq_count"),
            },
        }

    def _normalize_baseline_response(
        self,
        message: str,
        smart_agent_result: Optional[Dict[str, Any]],
        baseline: Dict[str, Any],
        mode: str,
    ) -> Dict[str, Any]:
        """
        Map baseline (answering_agent) response to ChatResponse format.

        Args:
            message: Original user message
            smart_agent_result: Optional SmartAIAgent result (if fallback was used)
            baseline: Result from answer_user_query
            mode: Mode used ("baseline", "baseline_fallback", "baseline_exception")

        Returns:
            Dictionary matching ChatResponse schema
        """
        answer = baseline.get("answer") or ""
        intent = baseline.get("intent", "unknown")
        confidence = baseline.get("confidence", 0.0)
        source = baseline.get("source", "fallback")
        success = baseline.get("success", False)
        matched_ids = baseline.get("matched_ids", [])
        metadata = baseline.get("metadata", {})

        return {
            "answer": answer,
            "source": f"baseline:{mode}",
            "success": success,
            "intent": intent,
            "confidence": confidence,
            "context": str(metadata) if metadata else None,
            "intent_match": success,
            "matched_faq_id": matched_ids[0] if matched_ids else None,
            "question": message,
            "category": None,  # Can be extracted from metadata if available
            "score": confidence,
            "debug_info": {
                "smart_agent_raw": smart_agent_result,
                "baseline_raw": baseline,
                "mode": mode,
                "matched_ids": matched_ids,
                "metadata": metadata,
            },
        }


# Global instance
chat_orchestrator = ChatOrchestrator()

