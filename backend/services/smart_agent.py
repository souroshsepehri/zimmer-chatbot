import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger("services.smart_agent")


class SmartAIAgent:
    """
    Temporary stub implementation of the 'smart agent'.

    هدف این کلاس فقط این است که:
    - backend موقع import کردن smart_agent کرش نکند
    - chat_orchestrator بتواند در صورت خطا روی baseline سوییچ کند

    وقتی خواستیم نسخه نهایی SmartAIAgent را با LangChain پیاده‌سازی کنیم،
    این فایل را دوباره بازنویسی می‌کنیم.
    """

    def __init__(self) -> None:
        # در نسخه stub فعلی عملاً agent غیر فعال است
        self.enabled = False

        api_key = (
            os.getenv("OPENAI_API_KEY")
            or os.getenv("OPENAI_API_KEY_ZIMMER")
        )

        if not api_key:
            logger.warning(
                "SmartAIAgent: OPENAI_API_KEY not set. "
                "Smart agent will be disabled and the system will fall back to the baseline engine."
            )
        else:
            # اگر بعداً خواستیم مستقیم به OpenAI وصل شویم، همین‌جا client را می‌سازیم.
            logger.info(
                "SmartAIAgent initialized with API key, "
                "but LangChain-based agent is DISABLED (stub implementation)."
            )

    def _create_agent(self) -> None:
        """
        Placeholder for the real LangChain agent construction.

        در این نسخه‌ی موقت، هیچ agent واقعی ساخته نمی‌شود تا وابستگی به
        langchain.agents.AgentType نداشته باشیم.
        """
        return None

    async def arun(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Async entrypoint.

        در نسخه‌ی موقت، همیشه خطا می‌دهد تا orchestrator برود روی baseline.
        """
        raise RuntimeError(
            "SmartAIAgent stub: smart agent is currently disabled; "
            "fallback to baseline engine."
        )

    def run(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Sync entrypoint (اگر جایی قبلاً از نسخه sync استفاده شده باشد).
        """
        raise RuntimeError(
            "SmartAIAgent stub: smart agent is currently disabled; "
            "fallback to baseline engine."
        )


# global instance used by chat_orchestrator
smart_agent = SmartAIAgent()
