"""
Advanced Smart AI Agent with Multi-Style Response and Web Content Reading
"""

import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
import json
import re
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone
import logging
from urllib.parse import urlparse, urljoin
import time
from dataclasses import dataclass, field
from pydantic import BaseModel

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
try:
    from langchain.memory import ConversationBufferWindowMemory
except ImportError:
    try:
        from langchain_community.memory import ConversationBufferWindowMemory
    except ImportError:
        # Fallback: Create a simple memory class if langchain memory is not available
        class ConversationBufferWindowMemory:
            def __init__(self, k=10):
                self.k = k
                self.messages = []
            def save_context(self, inputs, outputs):
                self.messages.append({"inputs": inputs, "outputs": outputs})
                if len(self.messages) > self.k:
                    self.messages.pop(0)
            def load_memory_variables(self, inputs):
                return {"history": self.messages}
from langchain_core.tools import Tool
from langchain_core.callbacks import StreamingStdOutCallbackHandler

from core.config import settings
from .debugger import debugger
from .api_integration import api_integration
from .simple_chatbot import get_simple_chatbot
from schemas.smart_agent import (
    AVAILABLE_STYLES,
    STYLE_DEFINITIONS,
    STYLE_INSTRUCTIONS,
    ResponseStyle
)
from sqlalchemy.orm import Session
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from schemas.smart_agent import SmartAgentRequest, SmartAgentResponse

logger = logging.getLogger(__name__)


# ============================================================================
# Prompt Orchestrator Models
# ============================================================================

class FAQMatch(BaseModel):
    """Represents a matched FAQ entry with relevance score"""
    question: str
    answer: str
    score: float = 0.0


@dataclass
class AgentContext:
    """
    Context container for the Smart Agent prompt orchestrator.
    
    Contains all information needed to build a comprehensive prompt:
    - User message and chat history
    - Page context from current website page
    - FAQ matches from database
    - Site metadata (brand tone, CTA, etc.)
    """
    user_message: str
    chat_history: List[Dict[str, str]] = field(default_factory=list)  # List of {role: "user"|"assistant", content: "..."}
    page_url: Optional[str] = None
    page_context: Optional[str] = None  # Extracted text content from page
    faq_matches: List[FAQMatch] = field(default_factory=list)
    site_metadata: Dict[str, Any] = field(default_factory=dict)  # site_name, brand_tone, primary_cta

# Import agents with fallback
try:
    from langchain.agents import initialize_agent, AgentType
except ImportError:
    try:
        from langchain.agent import initialize_agent, AgentType
    except ImportError:
        # Fallback for newer langchain versions
        try:
            from langchain.agents.agent_types import AgentType
        except ImportError:
            # Create a dummy AgentType enum
            from enum import Enum
            class AgentType(Enum):
                ZERO_SHOT_REACT_DESCRIPTION = "zero_shot_react_description"
        def initialize_agent(tools, llm, agent, verbose, memory):
            logger.warning("Agent initialization not fully supported in this langchain version")
            return None

class WebContentReader:
    """Advanced web content reader with multiple extraction methods"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    async def read_url_content(self, url: str, max_length: int = 5000) -> Dict[str, Any]:
        """Read and extract content from a URL"""
        try:
            # Validate URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                return {"error": "Invalid URL format"}
            
            # Add protocol if missing
            if not parsed_url.scheme:
                url = "https://" + url
            
            # Fetch content
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract different types of content
            content = {
                "url": url,
                "title": self._extract_title(soup),
                "description": self._extract_description(soup),
                "main_content": self._extract_main_content(soup, max_length),
                "links": self._extract_links(soup, url),
                "images": self._extract_images(soup, url),
                "metadata": self._extract_metadata(soup),
                "timestamp": datetime.now().isoformat()
            }
            
            return content
            
        except Exception as e:
            logger.error(f"Error reading URL {url}: {e}")
            return {"error": f"Failed to read URL: {str(e)}"}
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        # Try meta title
        meta_title = soup.find('meta', property='og:title')
        if meta_title:
            return meta_title.get('content', '').strip()
        
        return "No title found"
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract page description"""
        # Try meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            return meta_desc.get('content', '').strip()
        
        # Try Open Graph description
        og_desc = soup.find('meta', property='og:description')
        if og_desc:
            return og_desc.get('content', '').strip()
        
        return ""
    
    def _extract_main_content(self, soup: BeautifulSoup, max_length: int) -> str:
        """Extract main content from page"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Try to find main content areas
        main_content = ""
        
        # Look for common content containers
        content_selectors = [
            'main', 'article', '.content', '.post', '.entry',
            '.main-content', '.article-content', '.post-content'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                main_content = content_elem.get_text(separator=' ', strip=True)
                break
        
        # If no main content found, get body text
        if not main_content:
            body = soup.find('body')
            if body:
                main_content = body.get_text(separator=' ', strip=True)
        
        # Clean and truncate content
        main_content = re.sub(r'\s+', ' ', main_content).strip()
        if len(main_content) > max_length:
            main_content = main_content[:max_length] + "..."
        
        return main_content
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract relevant links from page"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            text = link.get_text().strip()
            
            if href and text and len(text) > 3:
                # Convert relative URLs to absolute
                absolute_url = urljoin(base_url, href)
                links.append({
                    "url": absolute_url,
                    "text": text[:100]  # Limit text length
                })
        
        return links[:10]  # Limit to 10 links
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract images from page"""
        images = []
        for img in soup.find_all('img', src=True):
            src = img.get('src')
            alt = img.get('alt', '')
            
            if src:
                # Convert relative URLs to absolute
                absolute_url = urljoin(base_url, src)
                images.append({
                    "url": absolute_url,
                    "alt": alt[:100]  # Limit alt text length
                })
        
        return images[:5]  # Limit to 5 images
    
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract metadata from page"""
        metadata = {}
        
        # Extract meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            
            if name and content:
                metadata[name] = content
        
        return metadata

class SmartAIAgent:
    """
    Advanced AI Agent with multi-style response capabilities and web content reading.
    
    Uses a Prompt Orchestrator pattern to combine FAQ, page context, and chat history
    into structured prompts for the LLM.
    """
    
    def __init__(self):
        # In-memory cache for page context (simple dict: url -> (content, timestamp))
        self._page_context_cache: Dict[str, Tuple[str, float]] = {}
        self._cache_ttl = 300  # 5 minutes TTL
        
        # Initialize OpenAI components only if API key is available
        # Check both environment variable and settings (from .env file)
        api_key = os.getenv('OPENAI_API_KEY') or settings.openai_api_key
        self.openai_available = bool(api_key and api_key != "")
        
        if self.openai_available:
            try:
                # Set API key in environment if not already set (for ChatOpenAI)
                if not os.getenv('OPENAI_API_KEY') and settings.openai_api_key:
                    os.environ['OPENAI_API_KEY'] = settings.openai_api_key
                
                self.llm = ChatOpenAI(
                    model=settings.openai_model,
                    temperature=0.7,
                    max_tokens=2000,
                    streaming=True,
                    callbacks=[StreamingStdOutCallbackHandler()]
                )
                self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
            except Exception as e:
                logger.warning(f"OpenAI initialization failed: {e}")
                self.openai_available = False
                self.llm = None
                self.embeddings = None
        else:
            logger.info("OpenAI API key not set. Smart Agent will run in limited mode.")
            self.llm = None
            self.embeddings = None
        
        self.memory = ConversationBufferWindowMemory(k=10)
        self.web_reader = WebContentReader()
        
        # Response styles - use standardized definitions from schema
        # Map style keys to their instructions for easy lookup
        self.response_styles = {
            style.value: STYLE_INSTRUCTIONS.get(style.value, "Provide a helpful response.")
            for style in ResponseStyle
            if style != ResponseStyle.AUTO  # Exclude auto from instruction mapping
        }
        
        # Initialize tools
        self.tools = self._create_tools()
        self.agent = self._create_agent()
    
    def _create_tools(self) -> List[Tool]:
        """Create tools for the AI agent"""
        tools = [
            Tool(
                name="web_reader",
                description="Read content from a website URL. Input should be a valid URL.",
                func=self._web_reader_tool
            ),
            Tool(
                name="url_analyzer",
                description="Analyze a URL and extract key information. Input should be a URL.",
                func=self._url_analyzer_tool
            ),
            Tool(
                name="content_summarizer",
                description="Summarize long content. Input should be the content to summarize.",
                func=self._content_summarizer_tool
            ),
            Tool(
                name="style_selector",
                description="Select appropriate response style based on user query. Input should be the user's message.",
                func=self._style_selector_tool
            ),
            Tool(
                name="api_news",
                description="Get latest news. Input should be a news query or topic.",
                func=self._api_news_tool
            ),
            Tool(
                name="api_weather",
                description="Get weather information. Input should be a city name.",
                func=self._api_weather_tool
            ),
            Tool(
                name="api_translate",
                description="Translate text. Input should be 'text|from_lang|to_lang' format.",
                func=self._api_translate_tool
            ),
            Tool(
                name="api_quote",
                description="Get inspirational quotes. Input should be optional tags separated by commas.",
                func=self._api_quote_tool
            ),
            Tool(
                name="api_wikipedia",
                description="Search Wikipedia for information. Input should be a search query.",
                func=self._api_wikipedia_tool
            )
        ]
        return tools
    
    def _create_agent(self):
        """Create the AI agent with tools"""
        if not self.openai_available:
            return None
        
        return initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.OPENAI_FUNCTIONS,
            verbose=True
        )
    
    def _web_reader_tool(self, url: str) -> str:
        """Tool function for reading web content"""
        try:
            content = asyncio.run(self.web_reader.read_url_content(url))
            if "error" in content:
                return f"Error reading URL: {content['error']}"
            
            result = f"Title: {content['title']}\n"
            result += f"Description: {content['description']}\n"
            result += f"Content: {content['main_content'][:1000]}...\n"
            result += f"Links found: {len(content['links'])}\n"
            result += f"Images found: {len(content['images'])}"
            
            return result
        except Exception as e:
            return f"Error reading URL: {str(e)}"
    
    def _url_analyzer_tool(self, url: str) -> str:
        """Tool function for analyzing URLs"""
        try:
            parsed = urlparse(url)
            analysis = f"Domain: {parsed.netloc}\n"
            analysis += f"Path: {parsed.path}\n"
            analysis += f"Scheme: {parsed.scheme}\n"
            analysis += f"Query: {parsed.query}\n"
            return analysis
        except Exception as e:
            return f"Error analyzing URL: {str(e)}"
    
    def _content_summarizer_tool(self, content: str) -> str:
        """Tool function for summarizing content"""
        try:
            if len(content) < 500:
                return content
            
            # Check if LLM is available
            if not self.llm:
                # Return truncated content if LLM not available
                return content[:500] + "..." if len(content) > 500 else content
            
            # Use AI to summarize
            prompt = f"Summarize the following content in 2-3 sentences:\n\n{content[:2000]}"
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content
        except Exception as e:
            # Return truncated content on error
            return content[:500] + "..." if len(content) > 500 else content
    
    def _style_selector_tool(self, message: str) -> str:
        """Tool function for selecting response style based on message content"""
        try:
            # Analyze message to determine appropriate style
            message_lower = message.lower()
            
            # Check for explicit style requests
            if any(word in message_lower for word in ['formal', 'professional', 'business', 'official', 'رسمی']):
                return ResponseStyle.FORMAL.value
            elif any(word in message_lower for word in ['friendly', 'casual', 'hey', 'hi', 'hello', 'صمیمی', 'محاوره']):
                return ResponseStyle.FRIENDLY.value
            elif any(word in message_lower for word in ['brief', 'short', 'quick', 'summary', 'خلاصه', 'کوتاه']):
                return ResponseStyle.BRIEF.value
            elif any(word in message_lower for word in ['detailed', 'comprehensive', 'thorough', 'complete', 'کامل', 'توضیحی']):
                return ResponseStyle.DETAILED.value
            elif any(word in message_lower for word in ['explain', 'step', 'how to', 'tutorial', 'آموزش', 'مرحله', 'گام']):
                return ResponseStyle.EXPLAINER.value
            elif any(word in message_lower for word in ['marketing', 'promote', 'sell', 'advertise', 'مارکتینگ', 'تبلیغ', 'ترغیب']):
                return ResponseStyle.MARKETING.value
            else:
                # Default to friendly for casual interactions
                return ResponseStyle.FRIENDLY.value
        except Exception as e:
            logger.warning(f"Error in style selection: {e}")
            return ResponseStyle.FRIENDLY.value
    
    def _api_news_tool(self, query: str) -> str:
        """Tool function for getting news"""
        try:
            response = asyncio.run(api_integration.get_news(query))
            if response.success:
                articles = response.data.get('articles', [])
                if articles:
                    result = f"Latest news about '{query}':\n"
                    for i, article in enumerate(articles[:3], 1):
                        result += f"{i}. {article.get('title', 'No title')}\n"
                        result += f"   Source: {article.get('source', {}).get('name', 'Unknown')}\n"
                        result += f"   URL: {article.get('url', 'No URL')}\n\n"
                    return result
                else:
                    return f"No news found for '{query}'"
            else:
                return f"Error getting news: {response.error}"
        except Exception as e:
            return f"Error getting news: {str(e)}"
    
    def _api_weather_tool(self, city: str) -> str:
        """Tool function for getting weather"""
        try:
            response = asyncio.run(api_integration.get_weather(city))
            if response.success:
                data = response.data
                result = f"Weather in {city}:\n"
                result += f"Temperature: {data.get('main', {}).get('temp', 'N/A')}°C\n"
                result += f"Description: {data.get('weather', [{}])[0].get('description', 'N/A')}\n"
                result += f"Humidity: {data.get('main', {}).get('humidity', 'N/A')}%\n"
                result += f"Wind: {data.get('wind', {}).get('speed', 'N/A')} m/s"
                return result
            else:
                return f"Error getting weather: {response.error}"
        except Exception as e:
            return f"Error getting weather: {str(e)}"
    
    def _api_translate_tool(self, input_text: str) -> str:
        """Tool function for translation"""
        try:
            parts = input_text.split('|')
            if len(parts) >= 3:
                text, from_lang, to_lang = parts[0], parts[1], parts[2]
            elif len(parts) == 2:
                text, to_lang = parts[0], parts[1]
                from_lang = 'auto'
            else:
                text = input_text
                from_lang, to_lang = 'auto', 'en'
            
            response = asyncio.run(api_integration.translate_text(text, from_lang, to_lang))
            if response.success:
                translated = response.data.get('responseData', {}).get('translatedText', 'Translation failed')
                return f"Translation: {translated}"
            else:
                return f"Error translating: {response.error}"
        except Exception as e:
            return f"Error translating: {str(e)}"
    
    def _api_quote_tool(self, tags: str) -> str:
        """Tool function for getting quotes"""
        try:
            tag_list = [tag.strip() for tag in tags.split(',')] if tags else None
            response = asyncio.run(api_integration.get_random_quote(tag_list))
            if response.success:
                data = response.data
                quote = data.get('content', 'No quote available')
                author = data.get('author', 'Unknown')
                return f'"{quote}" - {author}'
            else:
                return f"Error getting quote: {response.error}"
        except Exception as e:
            return f"Error getting quote: {str(e)}"
    
    def _api_wikipedia_tool(self, query: str) -> str:
        """Tool function for Wikipedia search"""
        try:
            response = asyncio.run(api_integration.search_wikipedia(query))
            if response.success:
                search_results = response.data.get('query', {}).get('search', [])
                if search_results:
                    result = f"Wikipedia results for '{query}':\n"
                    for i, article in enumerate(search_results[:3], 1):
                        result += f"{i}. {article.get('title', 'No title')}\n"
                        result += f"   Snippet: {article.get('snippet', 'No snippet')[:200]}...\n\n"
                    return result
                else:
                    return f"No Wikipedia results found for '{query}'"
            else:
                return f"Error searching Wikipedia: {response.error}"
        except Exception as e:
            return f"Error searching Wikipedia: {str(e)}"
    
    def get_page_context(self, page_url: str) -> Optional[str]:
        """
        Extract clean text content from a webpage URL.
        
        Responsibilities:
        - Validates URL and domain (only Zimmer domains allowed)
        - Fetches page using requests + BeautifulSoup
        - Strips scripts, styles, nav, footer, header
        - Keeps only main/article/section, headings, paragraphs, lists
        - Normalizes whitespace
        - Truncates to ~4000 characters if needed
        - Uses in-memory caching (5 min TTL)
        
        Args:
            page_url: URL of the page to extract content from
            
        Returns:
            Clean text content string, or None if error/not allowed
        """
        if not page_url or not page_url.strip():
            return None
        
        try:
            parsed_url = urlparse(page_url)
            host = parsed_url.netloc.lower()
            
            # Only allow Zimmer domains for security
            allowed_hosts = ["zimmerai.com", "www.zimmerai.com"]
            if not any(allowed in host for allowed in allowed_hosts):
                logger.warning(f"Page context request for non-allowed domain: {host}")
                return None
            
            # Check cache first
            cache_key = page_url
            if cache_key in self._page_context_cache:
                content, timestamp = self._page_context_cache[cache_key]
                if time.time() - timestamp < self._cache_ttl:
                    logger.debug(f"Using cached page context for {page_url}")
                    return content
                else:
                    # Cache expired, remove it
                    del self._page_context_cache[cache_key]
            
            # Fetch page
            response = requests.get(page_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'noscript']):
                element.decompose()
            
            # Extract main content areas
            content_parts = []
            
            # Try to find main/article/section first
            main_content = soup.find(['main', 'article', 'section'])
            if main_content:
                target = main_content
            else:
                target = soup.find('body') or soup
            
            # Extract text from semantic elements
            for elem in target.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'div']):
                text = elem.get_text(strip=True)
                if text and len(text) > 10:  # Only meaningful text
                    content_parts.append(text)
            
            # Combine and normalize whitespace
            full_text = ' '.join(content_parts)
            full_text = re.sub(r'\s+', ' ', full_text).strip()
            
            # Truncate to ~4000 characters if needed (keep from start)
            if len(full_text) > 4000:
                full_text = full_text[:4000] + "..."
            
            # Cache the result
            self._page_context_cache[cache_key] = (full_text, time.time())
            
            return full_text if full_text else None
            
        except Exception as e:
            logger.warning(f"Error extracting page context from {page_url}: {e}")
            return None
    
    def _get_faq_matches(self, message: str, db: Session) -> List[FAQMatch]:
        """
        Retrieve relevant FAQ entries for the message.
        
        Responsibilities:
        - Uses simple_chatbot to search FAQs
        - Converts results to FAQMatch objects
        - Returns top matches sorted by relevance
        
        Args:
            message: User's message to search against
            db: Database session
            
        Returns:
            List of FAQMatch objects (top 3 most relevant)
        """
        try:
            simple_chatbot = get_simple_chatbot()
            simple_chatbot.db_session = db
            
            # Load FAQs if not already loaded
            if not simple_chatbot.faqs:
                simple_chatbot.load_faqs_from_db()
            
            # Search for relevant FAQs
            faq_results = simple_chatbot.search_faqs(message, min_score=20.0)
            
            # Convert to FAQMatch objects
            matches = []
            for faq in faq_results[:3]:  # Top 3
                matches.append(FAQMatch(
                    question=faq.get('question', ''),
                    answer=faq.get('answer', ''),
                    score=faq.get('score', 0.0)
                ))
            
            return matches
        except Exception as e:
            logger.warning(f"Error retrieving FAQ matches: {e}")
            return []
    
    def build_prompt(self, context: AgentContext) -> str:
        """
        Build a comprehensive prompt from AgentContext.
        
        Responsibilities:
        - Combines system instructions, FAQ matches, page context, and chat history
        - Uses site metadata (brand tone, CTA) in instructions
        - Formats everything in Persian
        - Returns a single prompt string ready for LLM
        
        Args:
            context: AgentContext containing all necessary information
            
        Returns:
            Complete prompt string in Persian
        """
        site_name = context.site_metadata.get('site_name', 'زیمر')
        brand_tone = context.site_metadata.get('brand_tone', 'حرفه‌ای، مینیمال، آرام، فارسی')
        primary_cta = context.site_metadata.get('primary_cta', 'رزرو مشاوره رایگان')
        
        prompt_parts = []
        
        # System role and instructions
        prompt_parts.append(f"[SYSTEM] نقش: دستیار وب‌سایت {site_name}")
        prompt_parts.append("")
        prompt_parts.append("دستورالعمل‌ها:")
        prompt_parts.append(f"- لحن برند: {brand_tone}")
        prompt_parts.append("- اولویت اول: استفاده از اطلاعات FAQ و پایگاه داده")
        prompt_parts.append("- اولویت دوم: استفاده از محتوای صفحه وب‌سایت (در صورت موجود بودن)")
        prompt_parts.append("- اولویت سوم: دانش عمومی (فقط در صورت نیاز)")
        prompt_parts.append("- مهم: هیچ‌وقت اطلاعات جعلی نساز (no hallucinations)")
        prompt_parts.append("- اگر اطلاعات کافی نداری، صادقانه بگو و پیشنهاد کن از فرم تماس استفاده کنند")
        prompt_parts.append(f"- در صورت مناسب بودن، به {primary_cta} اشاره کن")
        prompt_parts.append("- هیچ‌وقت از کاربر نخواه که یک 'سبک' انتخاب کند")
        prompt_parts.append("")
        
        # Website context section
        if context.page_url and context.page_context:
            prompt_parts.append("=== محتوای صفحه وب‌سایت ===")
            prompt_parts.append(f"URL: {context.page_url}")
            prompt_parts.append(f"محتوای صفحه:")
            prompt_parts.append(context.page_context)
            prompt_parts.append("")
        
        # FAQ matches section
        if context.faq_matches:
            prompt_parts.append("=== اطلاعات از پایگاه داده (FAQ) ===")
            for idx, faq in enumerate(context.faq_matches, 1):
                prompt_parts.append(f"\nسوال {idx}: {faq.question}")
                prompt_parts.append(f"پاسخ: {faq.answer}")
            prompt_parts.append("")
        
        # Chat history section
        if context.chat_history:
            prompt_parts.append("=== تاریخچه گفتگو ===")
            for msg in context.chat_history[-5:]:  # Last 5 messages
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                role_label = "کاربر" if role == "user" else "دستیار"
                prompt_parts.append(f"{role_label}: {content}")
            prompt_parts.append("")
        
        # User question
        prompt_parts.append("=== سوال فعلی کاربر ===")
        prompt_parts.append(context.user_message)
        prompt_parts.append("")
        prompt_parts.append("حالا با استفاده از تمام اطلاعات بالا، به سوال کاربر پاسخ بده:")
        
        return "\n".join(prompt_parts)
    
    async def get_smart_response(self, req: 'SmartAgentRequest') -> 'SmartAgentResponse':
        """
        Main entrypoint for the smart-agent chat endpoint.
        
        - Converts SmartAgentRequest into AgentContext
        - Fetches page content if page_url is provided
        - Builds the LLM prompt using build_prompt(context)
        - Calls the LLM and wraps the result into SmartAgentResponse
        """
        # Import here to avoid circular imports
        from schemas.smart_agent import SmartAgentRequest, SmartAgentResponse
        
        start_time = time.monotonic()
        
        try:
            # Extract context dict safely
            raw_ctx = req.context or {}
            session_id = raw_ctx.get("session_id")
            page_url = raw_ctx.get("page_url") or req.page_url
            history = raw_ctx.get("history") or []
            
            # Build base AgentContext
            agent_context = AgentContext(
                user_message=req.message,
                chat_history=history,
                page_url=page_url,
                page_context=None,
                faq_matches=[],  # TODO: wire FAQ retrieval later
                site_metadata={
                    "site_name": "Zimmer",
                    "brand_tone": "حرفه‌ای، مینیمال، آرام، فارسی",
                    "primary_cta": "رزرو مشاوره رایگان",
                },
            )
            
            urls_processed: List[str] = []
            
            # If we have a page_url, try to read page context
            if page_url:
                try:
                    # get_page_context is synchronous, not async
                    page_text = self.get_page_context(page_url)
                    agent_context.page_context = page_text or ""
                    if page_text:
                        urls_processed.append(page_url)
                except Exception as e:
                    # Log but do not kill the whole flow
                    logger.exception(f"Error reading page URL {page_url}: {e}")
            
            # Build the full prompt string using the orchestrator
            prompt = self.build_prompt(agent_context)
            
            # If OpenAI is not available, provide a fallback response
            if not self.openai_available:
                end_time = time.monotonic()
                response_time = end_time - start_time
                
                fallback_response = "متأسفانه در حال حاضر قابلیت‌های پیشرفته AI در دسترس نیست. لطفاً از فرم تماس استفاده کنید."
                
                return SmartAgentResponse(
                    response=fallback_response,
                    style=req.style or "auto",
                    response_time=response_time,
                    web_content_used=bool(agent_context.page_context),
                    urls_processed=urls_processed,
                    context_used=bool(agent_context.page_context or agent_context.faq_matches or agent_context.chat_history),
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    debug_info={
                        "session_id": session_id,
                        "has_page_context": bool(agent_context.page_context),
                        "faq_matches_count": len(agent_context.faq_matches),
                        "history_len": len(agent_context.chat_history),
                        "page_url": page_url,
                        "fallback_mode": True,
                    },
                    error=None,
                )
            
            # Call the LLM (use existing client in this service)
            # The prompt already contains system instructions, so we use it as user message
            # with a minimal system message
            system_message = "تو دستیار هوشمند فارسی برای وب‌سایت زیمر هستی. همیشه به فارسی پاسخ بده."
            
            messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            llm_response_text = response.content
            
            end_time = time.monotonic()
            response_time = end_time - start_time
            
            # Determine if we used any context
            context_used = bool(agent_context.page_context or agent_context.faq_matches or agent_context.chat_history)
            
            # Resolve final style
            # If req.style is not None and not "auto", keep it
            # Otherwise use "auto"
            if req.style and req.style != "auto":
                style = req.style
            else:
                style = "auto"
            
            result = SmartAgentResponse(
                response=llm_response_text,
                style=style,
                response_time=response_time,
                web_content_used=bool(agent_context.page_context),
                urls_processed=urls_processed,
                context_used=context_used,
                timestamp=datetime.now(timezone.utc).isoformat(),
                debug_info={
                    "session_id": session_id,
                    "has_page_context": bool(agent_context.page_context),
                    "faq_matches_count": len(agent_context.faq_matches),
                    "history_len": len(agent_context.chat_history),
                    "page_url": page_url,
                },
                error=None,
            )
            
            # Log to debugger
            debugger.log_request(
                session_id=session_id or "smart_agent",
                user_message=req.message,
                response=llm_response_text,
                response_time=response_time,
                debug_info=result.debug_info or {}
            )
            
            return result
            
        except Exception as e:
            end_time = time.monotonic()
            response_time = end_time - start_time
            error_msg = f"Smart agent error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Log error to debugger
            debugger.log_request(
                session_id=raw_ctx.get("session_id", "smart_agent") if 'raw_ctx' in locals() else "smart_agent",
                user_message=req.message if 'req' in locals() else "",
                response="",
                response_time=response_time,
                error_message=error_msg
            )
            
            # Return SmartAgentResponse with error
            # Short Persian error message in response field
            # Full error details in error field
            return SmartAgentResponse(
                response="متأسفانه خطایی در پردازش درخواست شما رخ داد. لطفاً دوباره تلاش کنید.",
                style=req.style if 'req' in locals() else "auto",
                response_time=response_time,
                web_content_used=False,
                urls_processed=[],
                context_used=False,
                timestamp=datetime.now(timezone.utc).isoformat(),
                debug_info=None,
                error=str(e)  # Store the exception string in error field
            )
    
    def _create_system_prompt(self, style: str, context: Dict[str, Any] = None) -> str:
        """Create system prompt based on style and context (Persian-first)"""
        # Convert style string to ResponseStyle enum
        try:
            style_enum = ResponseStyle(style)
        except ValueError:
            style_enum = ResponseStyle.AUTO
        
        # Get Farsi style instructions
        style_instruction = self._get_style_instructions(style_enum)
        
        # Base prompt in Persian (Persian-first assistant)
        base_prompt = """تو یک دستیار هوش مصنوعی فارسی برای زیمر هستی. قابلیت‌های تو شامل موارد زیر است:
1. می‌توانی محتوای وب‌سایت‌ها و URL ها را بخوانی و تحلیل کنی
2. می‌توانی به سبک‌ها و زبان‌های مختلف پاسخ دهی
3. به محتوای وب دسترسی داری و می‌توانی اطلاعات به‌روز ارائه دهی
4. می‌توانی زمینه را درک کنی و پاسخ‌های مرتبط بدهی

راهنمایی‌های کلی:
- همیشه مفید و دقیق باش
- اگر به محتوای وب اشاره می‌کنی، منبع را ذکر کن
- اگر چیزی را نمی‌دانی، صادقانه بگو
- از مثال‌ها و تشبیهات استفاده کن وقتی مفید است
"""
        
        # Add style instruction if provided
        if style_instruction:
            base_prompt += f"\n\nلحن پاسخ:\n{style_instruction}\n"
        
        # Add context if provided
        if context:
            base_prompt += f"\n\nزمینه اضافی: {json.dumps(context, ensure_ascii=False)}"
        
        return base_prompt
    
    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        return urls
    
    def _enhance_message_with_context(self, message: str, web_content: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """Enhance message with web content and context"""
        enhanced = message
        
        if web_content:
            enhanced += "\n\nWeb content context:\n"
            for url, content in web_content.items():
                if "error" not in content:
                    enhanced += f"From {url}:\n"
                    enhanced += f"Title: {content.get('title', 'N/A')}\n"
                    enhanced += f"Content: {content.get('main_content', 'N/A')[:500]}...\n\n"
        
        if context:
            enhanced += f"\nAdditional context: {json.dumps(context, ensure_ascii=False)}"
        
        return enhanced
    
    async def read_url_content(self, url: str) -> Dict[str, Any]:
        """Read content from a URL"""
        return await self.web_reader.read_url_content(url)
    
    def get_available_styles(self) -> Dict[str, Dict[str, str]]:
        """Get available response styles with full metadata (backward compatible format)"""
        return STYLE_DEFINITIONS
    
    def get_available_styles_dict(self) -> Dict[ResponseStyle, Dict[str, str]]:
        """Get available response styles in the new TypedDict format"""
        return AVAILABLE_STYLES
    
    def get_style_instruction(self, style: str) -> str:
        """Get the instruction prompt for a specific style (English, for backward compatibility)"""
        if style == "auto":
            return STYLE_INSTRUCTIONS.get("auto", "Analyze the user's message and choose the most appropriate response style automatically.")
        # Get instruction from STYLE_INSTRUCTIONS
        return STYLE_INSTRUCTIONS.get(style, STYLE_INSTRUCTIONS.get("friendly", "Provide a helpful response."))
    
    def _normalize_and_validate_style(self, style: Optional[str]) -> str:
        """Normalize and validate style, defaulting to AUTO if invalid"""
        if style is None:
            return ResponseStyle.AUTO.value
        
        style_lower = style.lower().strip()
        
        # Check if style is a valid ResponseStyle enum value
        try:
            style_enum = ResponseStyle(style_lower)
            return style_enum.value
        except ValueError:
            # Invalid style, fallback to AUTO
            logger.warning(f"Invalid style '{style}' provided, defaulting to 'auto'")
            return ResponseStyle.AUTO.value
    
    def _get_style_instructions(self, style: ResponseStyle) -> str:
        """
        Get Farsi instructions for the LLM based on the response style.
        Returns empty string for AUTO style.
        """
        style_instructions_map = {
            ResponseStyle.AUTO: "بسته به سوال و زمینه کاربر، مناسب‌ترین لحن را انتخاب کن.",
            ResponseStyle.FORMAL: "پاسخ را با لحن رسمی، محترمانه و حرفه‌ای بنویس. از جملات کامل و معیار استفاده کن.",
            ResponseStyle.FRIENDLY: "پاسخ را با لحن صمیمی، شبیه چت اینستاگرامی اما مؤدب و حرفه‌ای بنویس. از عبارت‌های محاوره‌ای ملایم استفاده کن.",
            ResponseStyle.BRIEF: "پاسخ را خیلی خلاصه و مستقیم بنویس. حداکثر ۲–۳ جمله، بدون حاشیه.",
            ResponseStyle.DETAILED: "پاسخ را کامل و توضیحی بنویس، با مثال‌ها و جزئیات لازم، اما منظم و قابل‌خواندن.",
            ResponseStyle.EXPLAINER: "پاسخ را به صورت مرحله‌به‌مرحله و آموزشی بنویس. از شماره‌گذاری مراحل استفاده کن.",
            ResponseStyle.MARKETING: "پاسخ را با لحن مارکتینگی و ترغیب‌کننده بنویس، اما صادق و بدون اغراق. تمرکز روی مزایا برای کاربر.",
        }
        
        return style_instructions_map.get(style, "")
    
    def set_response_style(self, style: str) -> bool:
        """Set default response style"""
        # Check if style is a valid ResponseStyle enum value
        try:
            style_enum = ResponseStyle(style)
            if style_enum in AVAILABLE_STYLES:
                self.default_style = style
                return True
        except ValueError:
            pass
        return False
    
    def _create_fallback_response(self, message: str, style: str, web_content: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """Create a fallback response when OpenAI is not available"""
        message_lower = message.lower()
        
        # Extract URLs from message
        urls = self._extract_urls(message)
        
        # Check for common patterns and provide appropriate responses
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'سلام']):
            # Use friendly style for greetings
            if style == ResponseStyle.FRIENDLY.value:
                return "سلام! من یک دستیار هوشمند هستم. متأسفانه در حال حاضر قابلیت‌های پیشرفته AI در دسترس نیست، اما می‌توانم به شما در خواندن محتوای وب و استفاده از API های مختلف کمک کنم."
            elif style == ResponseStyle.FORMAL.value:
                return "سلام. من یک دستیار هوشمند هستم. در حال حاضر در حالت محدود عمل می‌کنم (کلید API OpenAI تنظیم نشده است)، اما می‌توانم در خواندن محتوای وب و استفاده از API های مختلف به شما کمک کنم."
            else:
                return f"Hello! I'm your Smart AI Agent. I'm currently running in limited mode (OpenAI API key not set), but I can still help you with web content reading and API integrations. How can I assist you today?"
        
        elif any(word in message_lower for word in ['weather', 'هوا', 'آب و هوا']):
            return "I can help you get weather information! Please provide a city name and I'll fetch the current weather data for you using our weather API."
        
        elif any(word in message_lower for word in ['news', 'اخبار', 'خبر']):
            return "I can help you get the latest news! Please specify a topic or query and I'll search for relevant news articles."
        
        elif any(word in message_lower for word in ['translate', 'ترجمه', 'ترجمه کن']):
            return "I can help you translate text! Please provide the text you want to translate and specify the target language."
        
        elif any(word in message_lower for word in ['quote', 'نقل قول', 'جمله']):
            return "I can provide you with inspirational quotes! Would you like a random quote or quotes on a specific topic?"
        
        elif any(word in message_lower for word in ['wikipedia', 'ویکی‌پدیا', 'اطلاعات']):
            return "I can search Wikipedia for information! Please provide a search query and I'll find relevant articles for you."
        
        elif urls:
            # If URLs are provided, analyze them
            url_info = []
            for url, content in web_content.items():
                if "error" not in content:
                    url_info.append(f"URL: {url}\nTitle: {content.get('title', 'N/A')}\nContent: {content.get('main_content', 'N/A')[:200]}...")
                else:
                    url_info.append(f"URL: {url}\nError: {content['error']}")
            
            if url_info:
                return f"I've analyzed the provided URL(s):\n\n" + "\n\n".join(url_info)
            else:
                return "I found URLs in your message but couldn't read their content. Please check if the URLs are accessible."
        
        else:
            # Generic fallback response - adapt based on style
            if style == ResponseStyle.BRIEF.value:
                return "در حال حاضر در حالت محدود هستم. لطفاً API key OpenAI را تنظیم کنید. می‌توانم در خواندن وب و API ها کمک کنم."
            elif style == ResponseStyle.DETAILED.value:
                return "متأسفانه در حال حاضر قابلیت‌های پیشرفته AI در دسترس نیست. لطفاً API key مربوط به OpenAI را تنظیم کنید تا بتوانم پاسخ‌های هوشمندانه‌تری ارائه دهم. در عین حال، می‌توانم در خواندن محتوای وب و استفاده از API های مختلف به شما کمک کنم:\n\n• خواندن و تحلیل محتوای وب\n• اطلاعات اخبار و آب و هوا\n• خدمات ترجمه\n• جستجو در ویکی‌پدیا\n• نقل قول‌های الهام‌بخش\n• و بیشتر!\n\nچه کاری می‌خواهید امتحان کنید؟"
            elif style == ResponseStyle.FRIENDLY.value:
                return "سلام! متأسفانه الان در حالت محدود کار می‌کنم چون API key OpenAI تنظیم نشده. برای پاسخ‌های کامل‌تر لطفاً API key رو تنظیم کن. ولی هنوز می‌تونم در خواندن وب و استفاده از API ها کمکت کنم!"
            else:
                return "I'm currently running in limited mode because the OpenAI API key is not set. To get full AI-powered responses, please set up your OpenAI API key. However, I can still help you with:\n\n• Web content reading and analysis\n• News and weather information\n• Translation services\n• Wikipedia searches\n• Inspirational quotes\n• And more!\n\nWhat would you like to try?"

# Global smart agent instance
smart_agent = SmartAIAgent()
