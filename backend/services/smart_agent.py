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
from datetime import datetime
import logging
from urllib.parse import urlparse, urljoin
import time

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

logger = logging.getLogger(__name__)

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
    Advanced AI Agent with multi-style response capabilities and web content reading
    """
    
    def __init__(self):
        # Initialize OpenAI components only if API key is available
        self.openai_available = bool(os.getenv('OPENAI_API_KEY'))
        
        if self.openai_available:
            try:
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
        
        # Response styles
        self.response_styles = {
            "formal": "Provide a formal, professional response with proper structure and detailed explanations.",
            "casual": "Respond in a casual, friendly manner as if talking to a friend.",
            "technical": "Give a technical, detailed response with specific information and examples.",
            "simple": "Provide a simple, easy-to-understand response suitable for beginners.",
            "creative": "Respond in a creative, engaging way with examples and analogies.",
            "persian": "Respond in Persian (Farsi) with proper Persian language structure and cultural context.",
            "analytical": "Provide an analytical response with pros/cons, comparisons, and logical reasoning.",
            "empathetic": "Respond with empathy and understanding, acknowledging the user's feelings."
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
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            memory=self.memory,
            handle_parsing_errors=True,
            max_iterations=5
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
        """Tool function for selecting response style"""
        try:
            # Analyze message to determine appropriate style
            message_lower = message.lower()
            
            if any(word in message_lower for word in ['formal', 'professional', 'business']):
                return "formal"
            elif any(word in message_lower for word in ['casual', 'friendly', 'hey', 'hi']):
                return "casual"
            elif any(word in message_lower for word in ['technical', 'how to', 'explain', 'details']):
                return "technical"
            elif any(word in message_lower for word in ['simple', 'easy', 'beginner']):
                return "simple"
            elif any(word in message_lower for word in ['creative', 'interesting', 'fun']):
                return "creative"
            elif any(word in message_lower for word in ['فارسی', 'persian', 'فارسی']):
                return "persian"
            elif any(word in message_lower for word in ['analyze', 'compare', 'pros', 'cons']):
                return "analytical"
            elif any(word in message_lower for word in ['help', 'problem', 'issue', 'feel']):
                return "empathetic"
            else:
                return "casual"  # Default style
        except Exception as e:
            return "casual"
    
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
    
    async def get_smart_response(self, message: str, style: str = "auto", context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get smart AI response with specified style"""
        start_time = time.time()
        
        try:
            # Auto-detect style if not specified
            if style == "auto":
                style = self._style_selector_tool(message)
            
            # Check if message contains URLs
            urls = self._extract_urls(message)
            web_content = {}
            
            if urls:
                # Read content from URLs
                for url in urls:
                    content = await self.web_reader.read_url_content(url)
                    web_content[url] = content
            
            # If OpenAI is not available, provide a fallback response
            if not self.openai_available:
                response_time = time.time() - start_time
                
                # Create a basic response based on available tools
                fallback_response = self._create_fallback_response(message, style, web_content, context)
                
                result = {
                    "response": fallback_response,
                    "style": style,
                    "response_time": response_time,
                    "web_content_used": bool(web_content),
                    "urls_processed": list(web_content.keys()) if web_content else [],
                    "context_used": bool(context),
                    "timestamp": datetime.now().isoformat(),
                    "debug_info": {
                        "style_detected": style,
                        "urls_found": urls,
                        "web_content_count": len(web_content),
                        "message_length": len(message),
                        "response_length": len(fallback_response),
                        "fallback_mode": True
                    }
                }
                
                # Log to debugger
                debugger.log_request(
                    session_id="smart_agent",
                    user_message=message,
                    response=fallback_response,
                    response_time=response_time,
                    debug_info=result["debug_info"]
                )
                
                return result
            
            # Create system prompt with style
            system_prompt = self._create_system_prompt(style, context)
            
            # Create enhanced prompt with web content
            enhanced_message = self._enhance_message_with_context(message, web_content, context)
            
            # Get AI response
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=enhanced_message)
            ]
            
            response = self.llm.invoke(messages)
            
            response_time = time.time() - start_time
            
            # Prepare result
            result = {
                "response": response.content,
                "style": style,
                "response_time": response_time,
                "web_content_used": bool(web_content),
                "urls_processed": list(web_content.keys()) if web_content else [],
                "context_used": bool(context),
                "timestamp": datetime.now().isoformat(),
                "debug_info": {
                    "style_detected": style,
                    "urls_found": urls,
                    "web_content_count": len(web_content),
                    "message_length": len(message),
                    "response_length": len(response.content)
                }
            }
            
            # Log to debugger
            debugger.log_request(
                session_id="smart_agent",
                user_message=message,
                response=response.content,
                response_time=response_time,
                debug_info=result["debug_info"]
            )
            
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            error_msg = f"Smart agent error: {str(e)}"
            
            # Log error to debugger
            debugger.log_request(
                session_id="smart_agent",
                user_message=message,
                response="",
                response_time=response_time,
                error_message=error_msg
            )
            
            return {
                "response": "I apologize, but I encountered an error while processing your request. Please try again.",
                "style": style,
                "response_time": response_time,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
    
    def _create_system_prompt(self, style: str, context: Dict[str, Any] = None) -> str:
        """Create system prompt based on style and context"""
        base_prompt = f"""You are an advanced AI assistant with the following capabilities:
1. You can read and analyze content from websites and URLs
2. You can respond in multiple styles and languages
3. You have access to web content and can provide up-to-date information
4. You can understand context and provide relevant responses

Current response style: {style}
Style instruction: {self.response_styles.get(style, 'Provide a helpful response.')}

Guidelines:
- Always be helpful and accurate
- If you reference web content, mention the source
- Adapt your response to the specified style
- Provide detailed information when appropriate
- If you don't know something, say so honestly
- Use examples and analogies when helpful
"""
        
        if context:
            base_prompt += f"\nAdditional context: {json.dumps(context, ensure_ascii=False)}"
        
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
    
    def get_available_styles(self) -> Dict[str, str]:
        """Get available response styles"""
        return self.response_styles
    
    def set_response_style(self, style: str) -> bool:
        """Set default response style"""
        if style in self.response_styles:
            self.default_style = style
            return True
        return False
    
    def _create_fallback_response(self, message: str, style: str, web_content: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """Create a fallback response when OpenAI is not available"""
        message_lower = message.lower()
        
        # Extract URLs from message
        urls = self._extract_urls(message)
        
        # Check for common patterns and provide appropriate responses
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'سلام']):
            if style == "persian":
                return "سلام! من یک دستیار هوشمند هستم. متأسفانه در حال حاضر قابلیت‌های پیشرفته AI در دسترس نیست، اما می‌توانم به شما در خواندن محتوای وب و استفاده از API های مختلف کمک کنم."
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
            # Generic fallback response
            if style == "persian":
                return "متأسفانه در حال حاضر قابلیت‌های پیشرفته AI در دسترس نیست. لطفاً API key مربوط به OpenAI را تنظیم کنید تا بتوانم پاسخ‌های هوشمندانه‌تری ارائه دهم. در عین حال، می‌توانم در خواندن محتوای وب و استفاده از API های مختلف به شما کمک کنم."
            else:
                return "I'm currently running in limited mode because the OpenAI API key is not set. To get full AI-powered responses, please set up your OpenAI API key. However, I can still help you with:\n\n• Web content reading and analysis\n• News and weather information\n• Translation services\n• Wikipedia searches\n• Inspirational quotes\n• And more!\n\nWhat would you like to try?"

# Global smart agent instance
smart_agent = SmartAIAgent()
