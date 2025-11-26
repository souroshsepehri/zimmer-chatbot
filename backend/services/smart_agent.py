"""
Smart AI Agent Service

Clean implementation using modern LangChain APIs (no AgentType).
Acts as an intelligent enhancer that refines baseline answers using GPT.
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime

# LangChain imports (modern API)
# Try to import ChatOpenAI - this should NOT crash the module if import fails
try:
    # LangChain جدید
    from langchain_openai import ChatOpenAI
except ImportError:
    # fallback برای نسخه‌های قدیمی‌تر
    try:
        from langchain.chat_models import ChatOpenAI
    except ImportError:
        # Both imports failed - this is OK, SmartAIAgent will be disabled
        ChatOpenAI = None


def get_env_bool(name: str, default: bool = False) -> bool:
    """Helper function to get boolean value from environment variable.
    
    Args:
        name: Environment variable name
        default: Default value if env var is not set
        
    Returns:
        bool: True if env var is one of ("1", "true", "yes", "y", "on"), False otherwise
    """
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "y", "on")

# System prompt for Zimmer AI automation agency
SYSTEM_PROMPT = """You are Zimmer, an AI automation agency specializing in building intelligent automation solutions for Iranian small and medium enterprises (SMEs).

## About Zimmer

Zimmer is a leading AI automation agency in Iran that helps businesses automate their customer service, sales, and operations using advanced AI technologies. We specialize in creating custom AI-powered assistants and bots tailored to each business's unique needs.

## What We Build

Zimmer creates various types of AI-powered automations:

1. **Travel Agency Assistant**: Helps customers with flight bookings, hotel reservations, visa inquiries, and travel planning
2. **Online Shop Assistant**: Handles product inquiries, order tracking, payment assistance, and customer support for e-commerce
3. **Debt Collector Bot**: Manages payment reminders, payment plans, and debt collection communications professionally
4. **Clinic Receptionist**: Handles appointment scheduling, patient inquiries, medical information, and clinic services
5. **SEO Agent**: Provides SEO consultation, keyword research, content optimization advice, and digital marketing guidance
6. **Custom Business Assistants**: Tailored AI solutions for any industry or business need

## Integration Channels

Our AI assistants can connect to multiple platforms:
- **Telegram**: Telegram bots and channels
- **WhatsApp**: WhatsApp Business API integration
- **Instagram DM**: Direct messaging automation
- **Website Widgets**: Embedded chat widgets for websites
- **Other platforms**: Custom integrations as needed

## Our Services

Zimmer offers comprehensive services:

1. **Consultation**: Free initial consultation to understand your business needs and automation opportunities
2. **Design**: Custom design of AI assistant workflows, conversation flows, and user experience
3. **Implementation**: Full development and deployment of AI automation solutions
4. **Support**: Ongoing maintenance, updates, and optimization support

## Communication Guidelines

**Language**: 
- Default language is Persian (Farsi)
- Respond in Farsi unless the user explicitly asks in another language
- Use friendly but professional tone (صمیمی اما حرفه‌ای)
- Be helpful, clear, and concise

**Tone**:
- Friendly and approachable (like talking to a helpful colleague)
- Professional and trustworthy
- Patient and understanding
- Enthusiastic about helping businesses grow

## Pricing Policy

When users ask about pricing:
- Provide general pricing information and logic
- Explain that pricing depends on:
  * Complexity of the automation
  * Number of integrations needed
  * Custom features required
  * Support level needed
- Always suggest booking a **free consultation** for exact pricing tailored to their needs
- Emphasize that the consultation is free and helps understand their specific requirements

Example response structure:
"قیمت‌گذاری بستگی به پیچیدگی پروژه، تعداد پلتفرم‌هایی که می‌خواهید به آن‌ها متصل شوید، و ویژگی‌های سفارشی دارد. برای دریافت قیمت دقیق و مناسب با نیازهای شما، پیشنهاد می‌کنم یک جلسه مشاوره رایگان رزرو کنید. در این جلسه می‌توانیم نیازهای شما را بررسی کنیم و قیمت دقیق را ارائه دهیم."

## Handling Baseline Answers

When a baseline answer from FAQ/DB is provided:

1. **If the baseline answer is relevant and accurate**:
   - Use it as the foundation
   - Enhance it by:
     * Making the language more natural and conversational
     * Fixing any unclear or awkward phrasing
     * Adding helpful context or examples if appropriate
     * Making it more human and friendly
   - Preserve all factual information - do not add or remove facts
   - Keep the same meaning and accuracy

2. **If the baseline answer is unclear or too technical**:
   - Simplify the language
   - Break down complex concepts into simpler terms
   - Add examples or analogies to help understanding
   - Make it more accessible to non-technical users

3. **If the baseline answer is incomplete**:
   - Extend it with relevant additional helpful information
   - But only if you're confident the information is accurate
   - Do not make up information

4. **If the baseline answer is not relevant**:
   - Acknowledge that the FAQ answer may not fully address the question
   - Provide a helpful response based on your knowledge of Zimmer's services
   - Suggest contacting human support for more specific information

## When You Don't Know

If you don't know the answer or are uncertain:
- Be honest and transparent: "متأسفانه اطلاعات دقیقی در این مورد ندارم"
- Don't make up information or guess
- Suggest contacting human support:
  * "برای دریافت اطلاعات دقیق‌تر، پیشنهاد می‌کنم با تیم پشتیبانی ما تماس بگیرید"
  * "می‌توانید از طریق [contact method] با ما در ارتباط باشید"
- Offer alternative ways to help: "اما می‌توانم در مورد [related topic] کمک کنم"

## General Behavior

- Always be helpful and solution-oriented
- Focus on how Zimmer can help solve the user's business challenges
- Ask clarifying questions if needed to better understand their needs
- Provide examples and use cases when relevant
- Be enthusiastic about the potential of AI automation for their business
- Maintain a positive, can-do attitude

## Important Rules

1. **Accuracy First**: Never provide incorrect information. If unsure, say so.
2. **Preserve Facts**: When enhancing baseline answers, keep all factual information intact.
3. **Be Honest**: Admit when you don't know something rather than guessing.
4. **Stay On Brand**: Always represent Zimmer professionally and accurately.
5. **Language**: Default to Farsi, but adapt if user uses another language.
6. **Tone**: Friendly but professional - like a helpful business consultant.
"""


class SmartAIAgent:
    """
    Smart AI Agent that enhances baseline answers using GPT.
    
    This agent:
    - Takes the baseline answer from FAQ/DB engine
    - Refines it using GPT-3.5-turbo for better clarity, tone, and completeness
    - Returns enhanced answer or None if disabled/failed
    """

    def __init__(self) -> None:
        """Initialize SmartAIAgent with configuration"""
        self.enabled: bool = False
        self.llm: Optional[ChatOpenAI] = None
        self.model_name: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
        self.logger = logging.getLogger("smart_agent")
        
        api_key = os.getenv("OPENAI_API_KEY")
        enabled_flag = get_env_bool("SMART_AGENT_ENABLED", default=True)
        
        if not api_key:
            self.logger.warning(
                "SmartAIAgent: OPENAI_API_KEY not set. Smart agent will be disabled and baseline will be used."
            )
            return
        
        if not enabled_flag:
            self.logger.info(
                "SmartAIAgent: SMART_AGENT_ENABLED is false. Smart agent is disabled by configuration."
            )
            return
        
        # Check if ChatOpenAI is available
        if ChatOpenAI is None:
            self.logger.warning(
                "SmartAIAgent: LangChain ChatOpenAI not available (langchain-openai or langchain not installed). "
                "Smart agent will be disabled. Install with: pip install langchain-openai"
            )
            return
        
        try:
            self.llm = ChatOpenAI(
                model=self.model_name,
                temperature=0.2,
                openai_api_key=api_key,
            )
            self.enabled = True
            self.logger.info(
                "SmartAIAgent initialized successfully with model %s", self.model_name
            )
        except Exception as e:
            self.logger.exception(
                "SmartAIAgent: failed to initialize ChatOpenAI. Smart agent disabled. Error: %s",
                e,
            )
            self.enabled = False
            self.llm = None

    async def run(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        High-level entrypoint used by chat_orchestrator.
        
        Returns a dict that will be stored under debug_info['smart_agent_raw'].
        
        Args:
            message: User's message
            context: Optional context dict (can include baseline_answer, intent, etc.)
            
        Returns:
            dict with keys: {"answer": str or None, "success": bool, "model": str, "reason": str (optional), "error": str (optional)}
        """
        if not self.enabled or self.llm is None:
            return {
                "answer": None,
                "success": False,
                "reason": "smart_agent_disabled",
            }

        system_prompt = (
            "You are Zimmerman (Zimmer AI Automation) website assistant. "
            "You answer in fluent Persian. "
            "Explain clearly what Zimmerman does: building custom AI automations, chatbots, "
            "travel agency AI, online shop agents, debt collector bot, etc. "
            "If user asks general or business questions about Zimmerman, answer helpfully, "
            "even if it's not in the FAQ database."
        )

        # Build messages for LangChain ChatOpenAI (using modern API)
        try:
            from langchain_core.messages import SystemMessage, HumanMessage
        except ImportError:
            # Fallback for older LangChain versions
            try:
                from langchain.schema import SystemMessage, HumanMessage
            except ImportError:
                self.logger.error("Could not import SystemMessage/HumanMessage from langchain_core or langchain.schema")
                return {
                    "answer": None,
                    "success": False,
                    "reason": "import_error",
                }

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=message),
        ]

        # If context has baseline_answer, add it as context
        if context and context.get("baseline_answer"):
            baseline_msg = (
                "این یک پاسخ اولیه از سیستم داخلی است. "
                "اگر مفید است از آن استفاده کن، اگر ناقص است آن را کامل و بهتر کن:\n"
                f"{context['baseline_answer']}"
            )
            messages.insert(1, SystemMessage(content=baseline_msg))

        try:
            resp = await self.llm.ainvoke(messages)
            answer_text = resp.content if hasattr(resp, "content") else str(resp)
            
            if not answer_text or not answer_text.strip():
                return {
                    "answer": None,
                    "success": False,
                    "reason": "empty_response",
                }
            
            return {
                "answer": answer_text.strip(),
                "success": True,
                "model": self.model_name,
            }
        except Exception as e:
            self.logger.exception("SmartAIAgent: error during LLM call: %s", e)
            return {
                "answer": None,
                "success": False,
                "reason": "llm_error",
                "error": str(e),
            }

    async def generate_smart_answer(
        self,
        user_message: str,
        baseline_answer: Optional[str] = None,
        debug_context: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Generate a smart answer using LangChain ChatOpenAI model.

        This method uses GPT to enhance baseline answers or generate new responses.
        It requires:
        - OPENAI_API_KEY to be set
        - SMART_AGENT_ENABLED to be "true"
        - LangChain ChatOpenAI to be available

        Args:
            user_message: The user's original question/message
            baseline_answer: Optional answer from baseline engine (FAQ/DB) to enhance
            debug_context: Optional debug context (intent, confidence, source, etc.)

        Returns:
            dict with keys: {"answer": str, "model": str, "usage": dict, "success": bool, "raw": Any}
            or None if disabled, llm is None, or any error occurs.
            
        Note:
            This method will NOT crash the app. If any error occurs, it logs the error
            and returns None, allowing the baseline logic to handle the request.
        """
        # Validate agent is enabled and llm is available
        if not self.enabled:
            self.logger.debug("SmartAIAgent.generate_smart_answer called but agent is disabled. Returning None to use baseline logic.")
            return None
        
        if self.llm is None:
            self.logger.warning("SmartAIAgent.generate_smart_answer called but self.llm is None (should not happen if enabled=True). Returning None.")
            return None

        try:
            # Build messages list compatible with the ChatOpenAI invoke/ainvoke API.
            messages = []

            # System message (using modern LangChain API)
            try:
                from langchain_core.messages import SystemMessage, HumanMessage
            except ImportError:
                # Fallback for older LangChain versions
                try:
                    from langchain.schema import SystemMessage, HumanMessage
                except ImportError:
                    self.logger.error("Could not import SystemMessage/HumanMessage from langchain_core or langchain.schema")
                    return None

            messages.append(SystemMessage(content=SYSTEM_PROMPT))

            # Optionally include baseline answer as context
            if baseline_answer:
                baseline_msg = (
                    "این یک پاسخ اولیه است که از سیستم داخلی (FAQ / دیتابیس) به دست آمده. "
                    "اگر مفید است از آن استفاده کن، اگر ناقص است آن را کامل و بهتر کن:\n"
                    f"{baseline_answer}"
                )
                messages.append(SystemMessage(content=baseline_msg))

            # Optionally include debug context in a compact form
            if debug_context:
                short_ctx = str({k: debug_context.get(k) for k in list(debug_context.keys())[:5]})
                messages.append(
                    SystemMessage(
                        content=(
                            "این اطلاعات زمینه‌ای برای درک بهتر وضعیت سیستم است. "
                            "فقط در صورت مفید بودن از آن استفاده کن و در متن جواب مستقیم نشان نده:\n"
                            f"{short_ctx}"
                        )
                    )
                )

            # User message
            messages.append(HumanMessage(content=user_message))

            # Asynchronous call via LangChain
            result = await self.llm.ainvoke(messages)

            # Extract answer text from result
            # For ChatOpenAI, result should have a 'content' attribute
            answer_text = None
            if hasattr(result, "content"):
                answer_text = result.content
            elif isinstance(result, str):
                answer_text = result
            elif hasattr(result, "text"):
                answer_text = result.text
            else:
                # Try to get content from message object
                self.logger.warning("SmartAIAgent: unexpected result type, trying to extract content. result=%r", type(result))
                answer_text = str(result) if result else None
            
            if not answer_text or not answer_text.strip():
                self.logger.warning("SmartAIAgent: empty or whitespace-only content from LLM. result=%r", result)
                return None

            # Extract usage info if available
            usage = {}
            if hasattr(result, "response_metadata") and result.response_metadata:
                usage = result.response_metadata
            elif hasattr(result, "usage"):
                usage = result.usage

            self.logger.debug("SmartAIAgent: Successfully generated answer using model %s", self.model_name)
            
            return {
                "answer": answer_text.strip(),
                "model": self.model_name,
                "usage": usage,
                "success": True,
                "raw": result,
            }

        except Exception as e:
            # Log error but don't crash - return None so baseline logic can be used
            self.logger.error(f"SmartAIAgent: error while generating smart answer: {e}. Returning None to use baseline logic.")
            return None

    async def get_smart_response(
        self,
        message: str = None,
        style: str = "auto",
        context: Optional[Dict[str, Any]] = None,
        request: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Compatibility method for existing router endpoints.
        
        This method provides a simple response without baseline enhancement.
        For the orchestrator flow, use generate_smart_answer() instead.
        
        Args:
            message: User's message
            style: Response style (ignored in new implementation)
            context: Optional context
            request: Optional SmartAgentRequest object
            
        Returns:
            Dictionary matching SmartAgentResponse format
        """
        from datetime import timezone
        
        if request:
            message = request.message
            context = request.context or context
            if hasattr(request, 'page_url') and request.page_url and context:
                context["page_url"] = request.page_url
        
        if not message:
            return {
                "response": "لطفاً پیام خود را وارد کنید.",
                "style": style,
                "response_time": 0.0,
                "web_content_used": False,
                "urls_processed": [],
                "context_used": False,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": "No message provided",
                "debug_info": {},
            }
        
        if not self.enabled:
            return {
                "response": "متأسفانه در حال حاضر سرویس هوشمند در دسترس نیست. لطفاً از پاسخ پایه استفاده کنید.",
                "style": style,
                "response_time": 0.0,
                "web_content_used": False,
                "urls_processed": [],
                "context_used": False,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": "SmartAIAgent disabled",
                "debug_info": {},
            }
        
        # Generate a simple answer (without baseline)
        result = await self.generate_smart_answer(
            user_message=message,
            baseline_answer=None,
            debug_context=context,
        )
        
        if result:
            return {
                "response": result.get("answer", ""),
                "style": style,
                "response_time": result.get("processing_time", 0.0),
                "web_content_used": False,
                "urls_processed": [],
                "context_used": bool(context),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": None,
                "debug_info": result.get("metadata", {}),
            }
        else:
            return {
                "response": "متأسفانه در حال حاضر سرویس هوشمند در دسترس نیست.",
                "style": style,
                "response_time": 0.0,
                "web_content_used": False,
                "urls_processed": [],
                "context_used": False,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": "SmartAIAgent returned None",
                "debug_info": {},
            }

    async def read_url_content(self, url: str, max_length: int = 5000) -> Dict[str, Any]:
        """
        Read URL content (used by router).
        
        Args:
            url: URL to read
            max_length: Maximum content length
            
        Returns:
            Dictionary with URL content information
        """
        from services.web_context_reader import read_url_content as read_url
        from datetime import timezone
        
        try:
            content = await read_url(url, max_length)
            
            if content.error:
                return {
                    "url": url,
                    "title": "",
                    "description": "",
                    "main_content": "",
                    "links": [],
                    "images": [],
                    "metadata": {},
                    "timestamp": content.timestamp,
                    "error": content.error,
                }
            
            return {
                "url": content.url,
                "title": content.title,
                "description": content.description,
                "main_content": content.main_content,
                "links": content.links,
                "images": content.images,
                "metadata": content.metadata,
                "timestamp": content.timestamp,
                "error": None,
            }
        except Exception as e:
            self.logger.exception(f"Error reading URL {url}: {e}")
            return {
                "url": url,
                "title": "",
                "description": "",
                "main_content": "",
                "links": [],
                "images": [],
                "metadata": {},
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": str(e),
            }

    def get_available_styles(self) -> list:
        """Get list of available response styles (compatibility method)"""
        from schemas.smart_agent import AVAILABLE_STYLES
        return [
            {
                "key": style.value,
                "label": info["label"],
                "description": info["description"],
            }
            for style, info in AVAILABLE_STYLES.items()
        ]

    @property
    def openai_available(self) -> bool:
        """Check if OpenAI is available (compatibility property)"""
        return self.enabled



# Global instance used by chat_orchestrator
smart_agent = SmartAIAgent()
