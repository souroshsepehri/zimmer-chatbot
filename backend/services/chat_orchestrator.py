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
        site_host: Optional[str] = None,  # NEW: explicit site_host parameter
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
        tracked_site = context.get("tracked_site")
        tracked_site_id = context.get("tracked_site_id")
        
        # Use explicit site_host parameter if provided, otherwise fall back to context
        effective_site_host = site_host or context.get("site_host")

        # If site_host was provided but no active site found, return site-specific fallback
        if effective_site_host and not tracked_site:
            logger.info(f"No active tracked site found for host: {effective_site_host}")
            return {
                "answer": "برای این سؤال در حال حاضر هیچ پاسخی در داده‌های ثبت‌شده ندارم. لطفاً سؤال را به شکل دیگری مطرح کنید یا با پشتیبانی تماس بگیرید.",
                "source": "fallback",
                "success": False,
                "intent": "unknown",
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
                    "metadata": {
                        "site_host": effective_site_host,
                        "site_resolved": False,
                        "tracked_site_id": None,
                    },
                },
            }

        # ۱) اجرای baseline / FAQ / simple chatbot
        baseline_result = None
        try:
            # Pass tracked_site_id and site_host in context for potential site-scoped queries
            query_context = {
                "session_id": session_id,
                "category_filter": context.get("category_filter"),
                "debug": context.get("debug", False),
                "tracked_site_id": tracked_site_id,
                "site_host": effective_site_host,  # Pass site_host to answering_agent
            }
            
            # Log site information
            if tracked_site:
                logger.info(
                    f"Processing chat for site: {tracked_site.name} (id: {tracked_site_id}, domain: {tracked_site.domain})"
                )
            elif effective_site_host:
                logger.info(f"Processing chat for unknown site_host: {effective_site_host}")
            
            baseline_result = answer_user_query(
                user_id=user_id,
                message=message,
                context=query_context,
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
        baseline_source = None
        baseline_success = False
        baseline_intent = None
        if isinstance(baseline_result, dict):
            baseline_answer = baseline_result.get("answer") or baseline_result.get("response")
            baseline_source = baseline_result.get("source")
            baseline_success = baseline_result.get("success", False)
            baseline_intent = baseline_result.get("intent")

        smart_result: Optional[Dict[str, Any]] = None
        mode = "baseline_only"

        # Define allowed sources for SmartAIAgent (only real data, not fallback)
        ALLOWED_SOURCES_FOR_SMART = {"faq", "db", "kb", "database"}
        
        # Determine if SmartAIAgent should be called (even if USE_SMART_AGENT is False, we enforce the logic)
        smart_agent_enabled = getattr(settings, "SMART_AGENT_ENABLED", False) or getattr(settings, "smart_agent_enabled", False)
        smart_agent_allowed = (
            USE_SMART_AGENT
            and smart_agent_enabled
            and getattr(smart_agent, "enabled", False)
            and baseline_success is True
            and baseline_source in ALLOWED_SOURCES_FOR_SMART
            and baseline_source not in ("fallback", "unknown", None)
            and baseline_answer is not None
        )

        # ===================================================================
        # FINAL ANSWER SELECTION LOGIC
        # ===================================================================
        # This section determines the final answer based on baseline results.
        # Priority order:
        # 1. Smart Agent (if enabled) - uses baseline as context
        # 2. Greeting Intent - ALWAYS preserve successful greeting responses
        #    - When intent="greeting" AND baseline_success=True AND baseline_answer exists
        #    - Return baseline_answer directly, do NOT replace with fallback
        #    - This ensures greeting messages like "سلام" get proper responses
        # 3. FAQ/DB Match - baseline has real data from FAQ or database
        #    - When baseline_success=True AND source in ALLOWED_SOURCES_FOR_SMART
        #    - Return baseline_answer (FAQ match, database query result, etc.)
        # 4. No Match (Fallback) - no FAQ match and no baseline answer
        #    - Return generic fallback message
        #    - Only applies to non-greeting messages (greetings handled in #2)
        # ===================================================================
        
        # DB-only mode: never call SmartAIAgent (USE_SMART_AGENT = False)
        # But if it were enabled, we would only call it when baseline has real data
        if smart_agent_allowed:
            # This block would call SmartAIAgent, but it's disabled by USE_SMART_AGENT = False
            mode = "auto"
            logger.warning("SmartAIAgent would be called but is disabled by USE_SMART_AGENT flag")
            # Fall through to use baseline answer
            final_answer = baseline_answer
            final_source = baseline_source
            final_success = baseline_success
        elif baseline_intent == "greeting" and baseline_success and baseline_answer:
            # SPECIAL CASE: Greeting messages with successful baseline should always be returned
            # Do NOT replace with generic fallback message
            # This ensures that greeting responses like "سلام! خوش آمدید..." are preserved
            final_answer = baseline_answer
            final_source = baseline_source or "greeting"  # Use "greeting" as source if baseline_source is None
            final_success = True
            logger.info(f"Preserving greeting response: intent={baseline_intent}, source={final_source}, success={baseline_success}")
        elif baseline_answer and baseline_success and baseline_source in ALLOWED_SOURCES_FOR_SMART:
            # Baseline has real data from FAQ or database - use it
            final_answer = baseline_answer
            final_source = baseline_source
            final_success = baseline_success
        else:
            # No data in DB or fallback - return site-specific fallback message
            # BUT: Only for non-greeting messages (greeting messages are handled above)
            if tracked_site:
                final_answer = (
                    "در حال حاضر فقط می‌توانم به سوالات مربوط به اطلاعات ثبت‌شده برای این سایت پاسخ بدهم. "
                    "لطفاً سوالتان را دقیق‌تر و مرتبط‌تر با خدمات سایت مطرح کنید."
                )
            else:
                final_answer = (
                    "برای این سؤال در حال حاضر هیچ پاسخی در داده‌های ثبت‌شده ندارم. "
                    "لطفاً سؤال را به شکل دیگری مطرح کنید یا با پشتیبانی تماس بگیرید."
                )
            final_source = "fallback"
            final_success = False

        logger.info(
            "DB-only mode: using baseline answer. source=%s, has_answer=%s, site_id=%s, site_host=%s",
            final_source,
            bool(baseline_answer),
            tracked_site_id,
            effective_site_host,
        )

        # Build metadata with site information
        metadata = baseline_result.get("metadata", {}) if isinstance(baseline_result, dict) else {}
        if tracked_site:
            metadata["tracked_site_id"] = tracked_site_id
            metadata["tracked_site_name"] = tracked_site.name
            metadata["tracked_site_domain"] = tracked_site.domain
        if effective_site_host:
            metadata["site_host"] = effective_site_host

        debug_info = {
            "baseline_raw": baseline_result,
            "smart_agent_raw": None,  # Never called in DB-only mode
            "mode": mode,
            "matched_ids": baseline_result.get("matched_ids", []) if isinstance(baseline_result, dict) else [],
            "metadata": metadata,
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
        site_host: Optional[str] = None,  # NEW: explicit site_host parameter
        db: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Route a message (wrapper for handle_chat to maintain backward compatibility).
        """
        context = context or {}
        source = context.get("source")
        page_url = context.get("page_url")
        
        # Use explicit site_host parameter if provided, otherwise get from context
        effective_site_host = site_host or context.get("site_host")
        
        return await self.handle_chat(
            message=message,
            source=source,
            page_url=page_url,
            context=context,
            user_id=user_id,
            site_host=effective_site_host,  # Pass site_host explicitly
            db=db,
        )


# Global instance
chat_orchestrator = ChatOrchestrator()





