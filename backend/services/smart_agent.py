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
    Internal AgentContext for SmartAIAgent v1 pipeline.
    
    Contains all runtime context for a single request:
    - User message (normalized and original)
    - Session and history
    - Page content from page_url
    - FAQ answer from answering_agent
    - Site metadata
    """
    user_message: str
    normalized_message: str = ""
    session_id: Optional[str] = None
    history: List[Dict[str, Any]] = field(default_factory=list)
    style: str = "auto"
    page_url: Optional[str] = None
    page_title: Optional[str] = None
    page_description: Optional[str] = None
    page_content: Optional[str] = None
    site_metadata: Dict[str, Any] = field(default_factory=dict)
    faq_answer: Optional[str] = None
    faq_source: Optional[str] = None  # e.g. "faq_db", "smart_chat"
    faq_intent: Optional[str] = None
    faq_confidence: Optional[float] = None
    faq_debug: Dict[str, Any] = field(default_factory=dict)
    
    # Backward compatibility: support old field names
    @property
    def chat_history(self) -> List[Dict[str, Any]]:
        """Backward compatibility: alias for history"""
        return self.history
    
    @chat_history.setter
    def chat_history(self, value: List[Dict[str, Any]]) -> None:
        """Backward compatibility: alias for history"""
        self.history = value
    
    @property
    def faq_snippets(self) -> List[Dict[str, Any]]:
        """Backward compatibility: convert faq_answer to snippets format"""
        if self.faq_answer:
            return [{
                "question": self.user_message,
                "answer": self.faq_answer,
                "score": self.faq_confidence or 0.0,
                "id": None,
                "category": None,
            }]
        return []
    
    @property
    def main_source_hint(self) -> Optional[str]:
        """Backward compatibility: infer from available sources"""
        if self.faq_answer and self.page_content:
            return "mixed"
        elif self.faq_answer:
            return "faq"
        elif self.page_content:
            return "page"
        return "none"
    
    @property
    def user_intent_hint(self) -> Optional[str]:
        """Backward compatibility: return faq_intent"""
        return self.faq_intent

# Import agents with fallback
try:
    from langchain.agents import initialize_agent
except ImportError:
    try:
        from langchain.agent import initialize_agent
    except ImportError:
        def initialize_agent(tools, llm, agent, verbose, handle_parsing_errors):
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
        self.enabled = self.openai_available  # Alias for compatibility
        
        if self.openai_available:
            try:
                # Set API key in environment if not already set (for ChatOpenAI)
                if not os.getenv('OPENAI_API_KEY') and settings.openai_api_key:
                    os.environ['OPENAI_API_KEY'] = settings.openai_api_key
                
                self.model_name = settings.openai_model
                self.llm = ChatOpenAI(
                    model=self.model_name,
                    temperature=0.4,  # Use 0.3-0.5 range as specified
                    max_tokens=2000,
                    streaming=True,
                    callbacks=[StreamingStdOutCallbackHandler()]
                )
                self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
            except Exception as e:
                logger.warning(f"OpenAI initialization failed: {e}")
                self.openai_available = False
                self.enabled = False
                self.llm = None
                self.embeddings = None
                self.model_name = None
        else:
            logger.info("OpenAI API key not set. Smart Agent will run in limited mode.")
            self.llm = None
            self.embeddings = None
            self.model_name = None
        
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
        """Create the LangChain agent that powers SmartAIAgent.

        NOTE:
            We avoid using AgentType enum because newer LangChain versions
            removed or changed it. We instead pass the agent type as a string.
        """
        if not self.openai_available:
            return None

        agent_type = "chat-conversational-react-description"

        agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=agent_type,
            handle_parsing_errors=True,
            verbose=True,
        )
        return agent
    
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
    
    def _build_agent_context(
        self,
        message: str,
        style: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> AgentContext:
        """
        Build AgentContext from message, style, and context dict.
        
        Uses the same normalization utilities as answering_agent.
        Extracts session_id, page_url, history from context.
        
        Args:
            message: User's message
            style: Optional style string (defaults to "auto")
            context: Optional context dict with session_id, page_url, history
            
        Returns:
            AgentContext instance with initialized fields
        """
        # Extract from context
        raw_ctx = context or {}
        session_id = raw_ctx.get("session_id")
        page_url = raw_ctx.get("page_url")
        history = raw_ctx.get("history") or []
        
        # Also check if page_url is in the top-level context (for backward compatibility)
        if not page_url and "page_url" in raw_ctx:
            page_url = raw_ctx["page_url"]
        
        # Truncate history to last 10 items to avoid huge prompts
        if len(history) > 10:
            history = history[-10:]
        
        # Normalize message using the same logic as answering_agent
        try:
            from services.answering_agent import AnsweringAgent
            answering_agent = AnsweringAgent()
            normalized_message = answering_agent._normalize_question(message)
        except Exception as e:
            logger.warning(f"Error normalizing message, using original: {e}")
            normalized_message = message.strip()
        
        # Initialize AgentContext with default values
        return AgentContext(
            user_message=message,
            normalized_message=normalized_message,
            session_id=session_id,
            history=history,
            style=style or "auto",
            page_url=page_url,
            page_title=None,
            page_description=None,
            page_content=None,
            site_metadata={},  # Will be populated by _enrich_with_page_content
            faq_answer=None,
            faq_source=None,
            faq_intent=None,
            faq_confidence=None,
            faq_debug={},
        )
    
    async def _enrich_with_page_content(self, agent_ctx: AgentContext) -> None:
        """
        Enrich AgentContext with page content from page_url.
        
        Uses services.web_context_reader.read_url_content.
        Never raises exceptions; logs errors and sets agent_ctx.site_metadata["error"].
        
        Args:
            agent_ctx: AgentContext to enrich (modified in place)
        """
        if not agent_ctx.page_url:
            return
        
        try:
            # Import and use the web_context_reader service
            from services.web_context_reader import read_url_content
            
            # Call read_url_content with max_length=5000 as specified
            web_content = await read_url_content(agent_ctx.page_url, max_length=5000)
            
            if web_content.error:
                logger.warning(f"Error reading page {agent_ctx.page_url}: {web_content.error}")
                agent_ctx.site_metadata["error"] = web_content.error
                agent_ctx.site_metadata["status_code"] = None
                agent_ctx.site_metadata["text_length"] = 0
                return
            
            # Extract and set page metadata
            agent_ctx.page_title = web_content.title
            agent_ctx.page_description = web_content.description
            agent_ctx.page_content = web_content.main_content
            
            # Set site_metadata from web_content.metadata
            agent_ctx.site_metadata.update({
                "status_code": web_content.metadata.get("status_code", 200),
                "text_length": web_content.metadata.get("text_length", len(web_content.main_content)),
                "url": web_content.url,
                "final_url": web_content.metadata.get("final_url", web_content.url),
                "timestamp": web_content.timestamp,
                "links_count": web_content.metadata.get("links_count", 0),
                "images_count": web_content.metadata.get("images_count", 0),
            })
            
        except Exception as e:
            logger.exception(f"Error enriching page content for {agent_ctx.page_url}: {e}")
            agent_ctx.site_metadata["error"] = str(e)
            agent_ctx.site_metadata["status_code"] = None
            agent_ctx.site_metadata["text_length"] = 0
            # Leave page_content as None on error
    
    async def _enrich_with_faq_answer(self, agent_ctx: AgentContext) -> None:
        """
        Enrich AgentContext with FAQ answer using existing FAQ/intent logic.
        
        Reuses the same internal function(s) that /api/smart-chat uses.
        Does NOT call HTTP endpoints; calls Python service layer directly.
        
        Populates:
        - agent_ctx.faq_answer
        - agent_ctx.faq_source
        - agent_ctx.faq_intent
        - agent_ctx.faq_confidence
        - agent_ctx.faq_debug (full debug dict)
        
        Args:
            agent_ctx: AgentContext to enrich (modified in place)
        """
        try:
            from services.answering_agent import answer_user_query
            from core.db import get_db
            
            # Get database session
            db_gen = get_db()
            db = next(db_gen)
            
            try:
                # Use the same answering_agent logic that /api/smart-chat uses
                result = answer_user_query(
                    user_id=agent_ctx.session_id,
                    message=agent_ctx.normalized_message or agent_ctx.user_message,
                    context={},
                    db=db
                )
                
                # Extract FAQ answer and metadata
                if result.get("success") and result.get("answer"):
                    agent_ctx.faq_answer = result.get("answer", "")
                    agent_ctx.faq_source = result.get("source", "faq_db")
                    agent_ctx.faq_intent = result.get("intent")
                    agent_ctx.faq_confidence = result.get("confidence", 0.0)
                    
                    # Store full debug info
                    agent_ctx.faq_debug = {
                        "matched_ids": result.get("matched_ids", []),
                        "metadata": result.get("metadata", {}),
                        "source": result.get("source"),
                        "success": result.get("success", False),
                    }
                else:
                    # No good FAQ match found
                    agent_ctx.faq_answer = None
                    agent_ctx.faq_source = None
                    agent_ctx.faq_intent = result.get("intent", "unknown")
                    agent_ctx.faq_confidence = result.get("confidence", 0.0)
                    agent_ctx.faq_debug = {
                        "success": False,
                        "source": result.get("source", "fallback"),
                    }
                    
            finally:
                # Complete the generator to trigger cleanup
                try:
                    next(db_gen, None)
                except StopIteration:
                    pass
                    
        except Exception as e:
            logger.warning(f"Error enriching FAQ answer for message: {e}")
            # Leave FAQ fields as None on error
            agent_ctx.faq_answer = None
            agent_ctx.faq_source = None
            agent_ctx.faq_intent = None
            agent_ctx.faq_confidence = None
            agent_ctx.faq_debug = {"error": str(e)}
    
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
    
    async def _generate_response(self, message: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a fallback response using the existing answering agent system.
        
        This is the stub behavior used when LLM is not available or fails.
        Uses the existing answering_agent to get a response.
        
        Args:
            message: User's message
            user_id: Optional user/session identifier
            
        Returns:
            Dict with keys: answer, intent, confidence, metadata
        """
        try:
            from services.answering_agent import AnsweringAgent
            from core.db import get_db
            
            # Get database session
            db_gen = get_db()
            db = next(db_gen)
            
            try:
                # Use the existing answering agent
                answering_agent = AnsweringAgent()
                result = answering_agent.answer_user_query(
                    user_id=user_id,
                    message=message,
                    context={},
                    db=db
                )
                
                return {
                    "answer": result.get("answer", "متأسفانه پاسخ مناسبی پیدا نشد."),
                    "intent": result.get("intent"),
                    "confidence": result.get("confidence"),
                    "metadata": {
                        "agent_type": result.get("source", "answering_agent"),
                        "success": result.get("success", False),
                    }
                }
            finally:
                # Complete the generator to trigger cleanup
                try:
                    next(db_gen, None)
                except StopIteration:
                    pass
                    
        except Exception as e:
            logger.exception(f"Error in _generate_response: {e}")
            # Return a safe fallback
            return {
                "answer": "متأسفانه در پردازش درخواست شما خطایی رخ داد. لطفاً دوباره تلاش کنید.",
                "intent": None,
                "confidence": None,
                "metadata": {
                    "agent_type": "stub",
                    "success": False,
                    "error": str(e)
                }
            }
    
    async def _call_llm(self, message: str, style: Optional[str] = None) -> Optional[str]:
        """
        Call the LLM with a simple Persian prompt and return the assistant text.
        
        If anything fails, return None. This is a minimal implementation that ensures
        the LLM is actually called when OPENAI_API_KEY is set.
        
        Args:
            message: User's message
            style: Optional style hint (auto/formal/casual, etc.)
            
        Returns:
            Assistant's message text, or None if unavailable/failed
        """
        if not self.enabled or not self.llm:
            return None
        
        try:
            # Build a simple Persian prompt
            # Keep it minimal for now; we will add page_url/FAQ context later
            base_instructions = (
                "تو دستیار هوشمند وب‌سایت Zimmer هستی. "
                "به زبان فارسی، کوتاه، واضح و حرفه‌ای جواب بده. "
                "از حاشیه‌گویی و جملات انگیزشی خودداری کن."
            )
            
            # Optionally adjust tone by style (very light)
            if style and style not in ("auto", "", None):
                # e.g. if style == "casual" or "formal", just note it in system hint
                style_hint = f" لحن کلی جواب کمی {style} باشد."
            else:
                style_hint = ""
            
            prompt_text = f"{base_instructions}{style_hint}\n\nپیام کاربر:\n{message}"
            
            # Use the existing LangChain LLM client
            system_message = "تو دستیار هوشمند فارسی برای وب‌سایت زیمر هستی. همیشه به فارسی پاسخ بده."
            
            messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=prompt_text)
            ]
            
            # Call the LLM (this is already async-compatible via LangChain)
            response = self.llm.invoke(messages)
            answer = response.content.strip()
            
            return answer if answer else None
            
        except Exception as e:
            logger.exception(f"SmartAIAgent LLM call failed: {e}")
            return None
    
    async def _build_and_call_llm(self, agent_ctx: AgentContext) -> str:
        """
        Build a comprehensive prompt and call the LLM.
        
        Builds OpenAI chat messages list with:
        - System message in Persian (as specified)
        - Second system/developer message describing available context
        - One assistant-style context message summarizing history, FAQ, and page content
        - Final user message
        
        Calls OpenAI API using the existing client/configuration pattern.
        Uses model from environment/config, defaulting to project's current default.
        
        Args:
            agent_ctx: AgentContext with all enriched information
            
        Returns:
            Final natural language answer (in Persian) as string
        """
        if not self.enabled or not self.llm:
            raise RuntimeError("LLM not available")
        
        try:
            # System message (Persian) - exact text as specified
            system_message = (
                "شما دستیار رسمی وب‌سایت زیمر هستید. همیشه به زبان فارسی و شفاف پاسخ بده. "
                "از محتوای صفحه‌ی وب، سوال کاربر، سابقه گفتگو و دانش پایه (FAQ) استفاده کن تا دقیق‌ترین و مختصرترین جواب را بدهی. "
                "اگر اطلاعات کافی نداری، صریح بگو و حدس الکی نزن."
            )
            
            # Second system / developer message describing available context
            context_parts = []
            if agent_ctx.page_content:
                context_parts.append("has page_content")
            if agent_ctx.faq_answer:
                context_parts.append("has faq_answer")
            if agent_ctx.history:
                context_parts.append(f"history length: {len(agent_ctx.history)}")
            
            if context_parts:
                developer_message = f"[Context available: {', '.join(context_parts)}]"
            else:
                developer_message = "[Context available: none]"
            
            # One assistant-style context message that summarizes:
            context_summary_parts = []
            
            # If history not empty → 1-3 line summary of previous turns
            if agent_ctx.history:
                recent_history = agent_ctx.history[-3:]  # Last 3 turns
                history_lines = []
                for msg in recent_history:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if len(content) > 150:
                        content = content[:150] + "..."
                    role_label = "User" if role == "user" else "Assistant"
                    history_lines.append(f"{role_label}: {content}")
                
                if len(history_lines) <= 3:
                    context_summary_parts.append(f"Previous conversation: {' | '.join(history_lines)}")
                else:
                    context_summary_parts.append(f"Previous conversation: {' | '.join(history_lines[:2])} ...")
            
            # If faq_answer exists → short note that "knowledge base suggests: ..."
            if agent_ctx.faq_answer:
                faq_note = agent_ctx.faq_answer
                if len(faq_note) > 400:
                    faq_note = faq_note[:400] + "..."
                context_summary_parts.append(f"Knowledge base suggests: {faq_note}")
            
            # If page_content exists → short abstract of the page (truncate to 800-1000 chars)
            if agent_ctx.page_content:
                page_abstract = agent_ctx.page_content
                if len(page_abstract) > 1000:
                    page_abstract = page_abstract[:1000] + "..."
                context_summary_parts.append(f"Current page content: {page_abstract}")
            
            # Combine context summary
            context_summary = "\n".join(context_summary_parts) if context_summary_parts else "No additional context available."
            
            # Final user message
            user_message_content = agent_ctx.user_message
            
            # Build messages list
            messages = [
                SystemMessage(content=system_message),
                SystemMessage(content=developer_message),
                HumanMessage(content=f"Context:\n{context_summary}\n\nUser question: {user_message_content}")
            ]
            
            # Call LLM using the existing client pattern
            response = self.llm.invoke(messages)
            answer = response.content.strip()
            
            if not answer:
                raise ValueError("LLM returned empty response")
            
            return answer
            
        except Exception as e:
            logger.exception(f"Error in _build_and_call_llm: {e}")
            raise
    
    def _build_prompt(self, agent_ctx: AgentContext, style: Optional[str] = None) -> str:
        """
        Build a comprehensive prompt from AgentContext with clear answer policy.
        
        Builds a SINGLE text prompt in Persian with:
        - Role and tone definition
        - Clear answer policy (FAQ first, page second, LLM for glue)
        - Intent-aware CTA
        - Source usage hints
        - Context pack (page content, FAQ, history)
        - User message
        
        Args:
            agent_ctx: AgentContext containing all necessary information
            style: Optional style hint (auto/formal/casual, etc.)
            
        Returns:
            Complete prompt string in Persian
        """
        prompt_parts = []
        
        # 1) Role and tone
        prompt_parts.append("تو دستیار هوشمند وب‌سایت Zimmer هستی.")
        prompt_parts.append("زیمر یک سرویس اتوماسیون هوش مصنوعی برای کسب‌وکارها است.")
        prompt_parts.append("")
        prompt_parts.append("لحن: حرفه‌ای، مینیمال، کوتاه، شفاف و بدون هیجان‌زدگی.")
        prompt_parts.append("از جملات انگیزشی، شعارهای کلی و تعارف‌های طولانی خودداری کن.")
        prompt_parts.append("")
        
        # Style adaptation (subtle, not exposed to user)
        if style and style not in ("auto", "", None):
            if style == "formal":
                prompt_parts.append("(لحن: رسمی و محترمانه)")
            elif style == "casual":
                prompt_parts.append("(لحن: صمیمی‌تر اما همچنان حرفه‌ای)")
            prompt_parts.append("")
        
        # 2) Answer policy (explicit, in Persian)
        prompt_parts.append("=== سیاست پاسخ‌دهی ===")
        prompt_parts.append("اگر اطلاعات دقیق و مرتبط در «سوالات متداول (FAQ)» وجود دارد، اولویت با آن‌ها است.")
        prompt_parts.append("اگر متن صفحه‌ی فعلی سایت (page_content) مرتبط است، آن را برای توضیح و مثال استفاده کن.")
        prompt_parts.append("اگر هیچ‌کدام کافی نیستند، حدس نزن و سرویس یا قابلیتی را اختراع نکن.")
        prompt_parts.append("اگر مطمئن نیستی، صادقانه بگو «بر اساس اطلاعات فعلی مطمئن نیستم» و پیشنهاد بده کاربر از فرم مشاوره یا راه‌های تماس استفاده کند.")
        prompt_parts.append("")
        
        # 3) Source usage hint based on main_source_hint
        main_source = agent_ctx.main_source_hint or "none"
        if main_source == "faq":
            prompt_parts.append("=== راهنمای استفاده از منابع ===")
            prompt_parts.append("اگر پاسخ در FAQها آمده است، آن را به شکل خلاصه و بدون ذکر ساختار دیتابیس بازگو کن.")
            prompt_parts.append("")
        elif main_source == "page":
            prompt_parts.append("=== راهنمای استفاده از منابع ===")
            prompt_parts.append("اگر متن صفحه‌ی فعلی مرتبط است، از آن برای توضیح استفاده کن و مراقب باش اطلاعات قدیمی یا ناقص اضافه نکنی.")
            prompt_parts.append("")
        elif main_source == "mixed":
            prompt_parts.append("=== راهنمای استفاده از منابع ===")
            prompt_parts.append("ابتدا از FAQ برای هسته‌ی جواب استفاده کن و اگر لازم بود، متن صفحه را برای توضیحات تکمیلی به‌کار ببر.")
            prompt_parts.append("")
        elif main_source == "none":
            prompt_parts.append("=== راهنمای استفاده از منابع ===")
            prompt_parts.append("فقط از دانش عمومی مدل استفاده کن، اما درباره‌ی سرویس‌های Zimmer اگر مطمئن نیستی چیزی را قطعی نگوی.")
            prompt_parts.append("")
        
        # 4) Context pack
        # Page content
        if agent_ctx.page_content:
            prompt_parts.append("=== خلاصه‌ای از صفحه فعلی ===")
            prompt_parts.append(f"عنوان: {agent_ctx.page_title or 'نامشخص'}")
            prompt_parts.append(f"توضیح کوتاه: {agent_ctx.page_description or 'نامشخص'}")
            prompt_parts.append("")
            prompt_parts.append("متن صفحه (خلاصه‌شده):")
            content_preview = agent_ctx.page_content[:500] if len(agent_ctx.page_content) > 500 else agent_ctx.page_content
            prompt_parts.append(content_preview)
            prompt_parts.append("")
        
        # FAQ snippets
        if agent_ctx.faq_snippets:
            prompt_parts.append("=== نمونه‌هایی از سوالات متداول مرتبط ===")
            for faq in agent_ctx.faq_snippets:
                prompt_parts.append(f"- سوال: {faq.get('question', '')}")
                prompt_parts.append(f"  پاسخ: {faq.get('answer', '')}")
            prompt_parts.append("")
        
        # Chat history
        if agent_ctx.chat_history:
            prompt_parts.append("=== خلاصه تاریخچه گفتگو ===")
            recent_history = agent_ctx.chat_history[-5:]  # Last 5 messages
            history_summary = []
            for msg in recent_history:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                if len(content) > 100:
                    content = content[:100] + "..."
                role_label = "کاربر" if role == "user" else "دستیار"
                history_summary.append(f"{role_label}: {content}")
            if len(history_summary) <= 3:
                prompt_parts.append(" | ".join(history_summary))
            else:
                prompt_parts.append(" | ".join(history_summary[:3]) + " ...")
            prompt_parts.append("")
        
        # 5) User message
        prompt_parts.append("=== پیام فعلی کاربر ===")
        prompt_parts.append(agent_ctx.user_message)
        prompt_parts.append("")
        
        # 6) Intent-aware CTA instruction
        user_intent = agent_ctx.user_intent_hint or "general_info"
        if user_intent == "pricing":
            prompt_parts.append("بعد از پاسخ، به‌صورت کوتاه پیشنهاد بده:")
            prompt_parts.append("«برای دریافت جزئیات قیمت و پیشنهاد متناسب با کسب‌وکار خودت، بهتر است فرم مشاوره را در سایت پر کنی یا از طریق واتساپ با ما در تماس باشی.»")
            prompt_parts.append("")
        elif user_intent == "sales":
            prompt_parts.append("بعد از پاسخ، به‌صورت کوتاه پیشنهاد بده:")
            prompt_parts.append("«برای رزرو مشاوره و بررسی پروژه‌ی خودت، می‌توانی فرم مشاوره را در سایت پر کنی.»")
            prompt_parts.append("")
        elif user_intent == "support":
            prompt_parts.append("بعد از پاسخ، به‌صورت کوتاه پیشنهاد بده:")
            prompt_parts.append("«اگر مشکل حل نشد، لطفاً جزئیات مشکل را از طریق فرم تماس یا واتساپ برای پشتیبانی ارسال کن.»")
            prompt_parts.append("")
        
        # Final instruction
        prompt_parts.append("لطفاً یک پاسخ کوتاه، دقیق، کاربردی و صادقانه به زبان فارسی بده.")
        prompt_parts.append("اگر پاسخ مطمئن نیست، این را شفاف بگو و یک راه ارتباط یا مشاوره پیشنهاد کن.")
        
        return "\n".join(prompt_parts)
    
    def build_prompt(self, context: AgentContext) -> str:
        """
        Backward compatibility wrapper for build_prompt.
        Calls _build_prompt with style="auto".
        """
        return self._build_prompt(context, style="auto")
    
    async def get_smart_response(
        self,
        message_or_req: Any,
        style: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Main entrypoint for SmartAIAgent v1 pipeline.
        
        Accepts either:
        - SmartAgentRequest object (used by router)
        - (message: str, style: Optional[str], context: Optional[Dict]) - direct call
        
        Returns:
        - SmartAgentResponse object (if called with SmartAgentRequest)
        - Dict matching SmartAgentResponse schema (if called with message string)
        """
        from schemas.smart_agent import SmartAgentRequest, SmartAgentResponse
        
        # Handle SmartAgentRequest object (from router)
        if isinstance(message_or_req, SmartAgentRequest) or (
            hasattr(message_or_req, 'message') and hasattr(message_or_req, 'style')
        ):
            req = message_or_req
            message = req.message
            style = req.style or "auto"
            # Merge page_url from request into context if provided
            if req.page_url:
                if context is None:
                    context = {}
                context["page_url"] = req.page_url
            # Use context from request if provided
            if req.context:
                if context is None:
                    context = {}
                context.update(req.context)
            
            # Call internal implementation
            result_dict = await self._get_smart_response_internal(message, style, context)
            
            # Convert dict to SmartAgentResponse
            return SmartAgentResponse(**result_dict)
        
        # Handle direct call with message string
        else:
            message = message_or_req
            return await self._get_smart_response_internal(message, style, context)
    
    async def _get_smart_response_internal(
        self,
        message: str,
        style: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main entrypoint for SmartAIAgent v1 pipeline.
        
        Implements the full site assistant pipeline:
        1. Builds AgentContext from message, style, context
        2. Enriches with page content (_enrich_with_page_content)
        3. Enriches with FAQ answer (_enrich_with_faq_answer)
        4. Builds prompt and calls LLM (_build_and_call_llm)
        5. Falls back to safe answer if LLM unavailable/fails
        6. Returns SmartAgentResponse-compatible dict
        
        Args:
            message: User's message
            style: Optional style string (defaults to "auto")
            context: Optional context dict with session_id, page_url, history
            
        Returns:
            Dict matching SmartAgentResponse schema
        """
        start_time = datetime.now(timezone.utc)
        raw_ctx = context or {}
        
        try:
            # STEP 1: Build AgentContext
            agent_ctx = self._build_agent_context(message, style or "auto", raw_ctx)
            
            # STEP 2: Enrich with page content
            await self._enrich_with_page_content(agent_ctx)
            
            # STEP 3: Enrich with FAQ answer
            await self._enrich_with_faq_answer(agent_ctx)
            
            # STEP 4: Decide whether to call LLM
            answer_text: str
            fallback_used = False
            
            # Check if there is no OpenAI API key or LLM client cannot be used
            if not self.enabled or not self.llm:
                # No LLM available - use fallback logic
                if agent_ctx.faq_answer:
                    # Use FAQ answer as main answer, with small note
                    answer_text = agent_ctx.faq_answer
                    answer_text += "\n\nاین جواب از پایگاه دانش داخلی آمده است."
                elif agent_ctx.page_content:
                    # Produce short summary of page content manually (no LLM, simple slicing)
                    page_summary = agent_ctx.page_content[:300] + "..." if len(agent_ctx.page_content) > 300 else agent_ctx.page_content
                    answer_text = f"بر اساس محتوای صفحه فعلی:\n\n{page_summary}\n\nلطفاً سوال خود را دقیق‌تر مطرح کنید."
                else:
                    # Safe fallback similar to current stub
                    core = await self._generate_response(message, user_id=agent_ctx.session_id)
                    answer_text = core.get("answer", "متأسفانه در حال حاضر پاسخ مناسبی پیدا نشد. لطفاً دوباره تلاش کنید.")
            else:
                # LLM is available - call it
                try:
                    answer_text = await self._build_and_call_llm(agent_ctx)
                except Exception as e:
                    logger.warning(f"LLM call failed, using fallback: {e}")
                    fallback_used = True
                    # Fallback to FAQ or page content
                    if agent_ctx.faq_answer:
                        answer_text = agent_ctx.faq_answer
                        answer_text += "\n\nاین جواب از پایگاه دانش داخلی آمده است."
                    elif agent_ctx.page_content:
                        page_summary = agent_ctx.page_content[:300] + "..." if len(agent_ctx.page_content) > 300 else agent_ctx.page_content
                        answer_text = f"بر اساس محتوای صفحه فعلی:\n\n{page_summary}\n\nلطفاً سوال خود را دقیق‌تر مطرح کنید."
                    else:
                        core = await self._generate_response(message, user_id=agent_ctx.session_id)
                        answer_text = core.get("answer", "متأسفانه در حال حاضر پاسخ مناسبی پیدا نشد. لطفاً دوباره تلاش کنید.")
            
            end_time = datetime.now(timezone.utc)
            response_time = (end_time - start_time).total_seconds()
            
            # Build response dict matching SmartAgentResponse
            web_content_used = bool(agent_ctx.page_content)
            urls_processed = [agent_ctx.page_url] if agent_ctx.page_url and web_content_used else []
            context_used = bool(agent_ctx.page_content or agent_ctx.faq_answer or agent_ctx.history)
            
            # Build debug_info as specified
            api_key_available = bool(self.enabled and self.llm)
            debug_info = {
                "mode": "hybrid_web_faq_llm",
                "has_openai_key": api_key_available,
                "session_id": agent_ctx.session_id,
                "history_len": len(agent_ctx.history),
                "faq_debug": agent_ctx.faq_debug,
                "site_metadata": agent_ctx.site_metadata,
            }
            
            result = {
                "response": answer_text,
                "style": agent_ctx.style,
                "response_time": response_time,
                "web_content_used": web_content_used,
                "urls_processed": urls_processed,
                "context_used": context_used,
                "timestamp": end_time.isoformat(),
                "debug_info": debug_info,
                "error": None,
            }
            
            # Log to debugger
            debugger.log_request(
                session_id=agent_ctx.session_id or "smart_agent",
                user_message=message,
                response=answer_text,
                response_time=response_time,
                debug_info=debug_info
            )
            
            return result
            
        except Exception as e:
            logger.exception(f"Error in get_smart_response: {e}")
            end_time = datetime.now(timezone.utc)
            response_time = (end_time - start_time).total_seconds()
            
            # Return safe error response (as specified)
            return {
                "response": "متأسفانه خطایی در پردازش درخواست شما رخ داد. لطفاً دوباره تلاش کنید.",
                "style": style or "auto",
                "response_time": response_time,
                "web_content_used": False,
                "urls_processed": [],
                "context_used": False,
                "timestamp": end_time.isoformat(),
                "debug_info": {
                    "mode": "error",
                    "error": str(e),
                },
                "error": str(e),
            }
    
    async def _self_test_smart_agent(self) -> Dict[str, Any]:
        """
        Internal self-test helper for debugging.
        
        Constructs a dummy context with a Zimmer page URL and calls get_smart_response.
        Returns the raw dict for debugging via debug router or REPL.
        
        Returns:
            Dict with test result
        """
        test_context = {
            "session_id": "test-session",
            "page_url": "https://zimmerai.com/services",
            "history": [],
        }
        
        result = await self._get_smart_response_internal(
            message="این صفحه دقیقا درباره چی توضیح میده؟",
            style="auto",
            context=test_context
        )
        
        return result
    
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
        """
        Read content from a URL.
        
        This method is used by the /api/smart-agent/read-url endpoint.
        It uses the web_context_reader service for consistency.
        
        Args:
            url: URL to read
            
        Returns:
            Dict with content information (compatible with URLReadResponse)
        """
        from services.web_context_reader import read_url_content
        
        web_content = await read_url_content(url, max_length=5000)
        
        # Convert WebPageContent to dict format for backward compatibility
        if web_content.error:
            return {
                "error": web_content.error,
                "url": web_content.url,
                "title": "",
                "description": "",
                "main_content": "",
                "links": [],
                "images": [],
                "metadata": {},
                "timestamp": web_content.timestamp,
            }
        
        return {
            "url": web_content.url,
            "title": web_content.title,
            "description": web_content.description,
            "main_content": web_content.main_content,
            "links": web_content.links,
            "images": web_content.images,
            "metadata": web_content.metadata,
            "timestamp": web_content.timestamp,
        }
    
    async def _get_faq_matches(self, message: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant FAQ entries for a message.
        
        Uses the existing simple_chatbot service to search for FAQs.
        Returns a list of dicts with FAQ information for debug_info.
        
        Args:
            message: User's message to search against
            limit: Maximum number of FAQ matches to return (default: 5)
            
        Returns:
            List of dicts with keys: id, question, answer, score, category
            Returns empty list on error (defensive)
        """
        if not message or not message.strip():
            return []
        
        try:
            from core.db import get_db
            
            # Get database session
            db_gen = get_db()
            db = next(db_gen)
            
            try:
                simple_chatbot = get_simple_chatbot()
                simple_chatbot.db_session = db
                
                # Load FAQs if not already loaded
                if not simple_chatbot.faqs:
                    simple_chatbot.load_faqs_from_db()
                
                # Search for relevant FAQs
                faq_results = simple_chatbot.search_faqs(message, min_score=20.0)
                
                # Convert to the required format and limit results
                matches = []
                for faq in faq_results[:limit]:
                    matches.append({
                        "id": faq.get("id"),
                        "question": faq.get("question", ""),
                        "answer": faq.get("answer", ""),
                        "score": faq.get("score", 0.0),
                        "category": faq.get("category", ""),
                    })
                
                return matches
                
            finally:
                # Complete the generator to trigger cleanup
                try:
                    next(db_gen, None)
                except StopIteration:
                    pass
                    
        except Exception as e:
            # Handle failures defensively - log and return empty list
            logger.warning(f"Error retrieving FAQ matches for message '{message[:50]}...': {e}")
            return []
    
    async def _read_page_context(self, page_url: Optional[str]) -> Dict[str, Any]:
        """
        Read page context from a URL using the same logic as /api/smart-agent/read-url.
        
        This is a helper method that wraps the existing WebContentReader to provide
        page content information for the Smart Agent.
        
        Args:
            page_url: URL to read, or None/empty string
            
        Returns:
            Dict with keys: url, title, description, main_content, metadata
            Or {"error": "..."} if error occurs
            Or {} if page_url is None/empty
        """
        if not page_url or not page_url.strip():
            return {}
        
        try:
            # Use the same WebContentReader that the /api/smart-agent/read-url endpoint uses
            content_dict = await self.web_reader.read_url_content(page_url, max_length=5000)
            
            # If there's an error in the response, return it
            if "error" in content_dict:
                return {"error": content_dict["error"]}
            
            # Extract and truncate main_content if needed (first 4000 chars)
            main_content = content_dict.get("main_content", "")
            if len(main_content) > 4000:
                main_content = main_content[:4000] + "..."
            
            # Return structured dict matching the requirements
            return {
                "url": content_dict.get("url", page_url),
                "title": content_dict.get("title", ""),
                "description": content_dict.get("description", ""),
                "main_content": main_content,
                "metadata": content_dict.get("metadata", {}),
            }
            
        except Exception as e:
            # Handle errors defensively - log and return error dict
            logger.exception(f"Error reading page context from {page_url}: {e}")
            return {"error": f"Failed to read URL: {str(e)}"}
    
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
