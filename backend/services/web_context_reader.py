"""
Web Context Reader Service

Provides async function to read and extract content from web pages.
Used by SmartAIAgent to enrich context with page content.
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from urllib.parse import urlparse, urljoin
import logging
import re

logger = logging.getLogger(__name__)


@dataclass
class WebPageContent:
    """Dataclass representing extracted web page content"""
    url: str
    title: str
    description: str
    main_content: str
    links: List[Dict[str, str]]
    images: List[Dict[str, str]]
    metadata: Dict[str, Any]
    timestamp: str
    error: Optional[str] = None


async def read_url_content(url: str, max_length: int = 5000) -> WebPageContent:
    """
    Read and extract content from a URL asynchronously.
    
    Args:
        url: URL to read
        max_length: Maximum length of main_content to extract
        
    Returns:
        WebPageContent dataclass with extracted information
    """
    start_time = datetime.now(timezone.utc)
    
    try:
        # Validate URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return WebPageContent(
                url=url,
                title="",
                description="",
                main_content="",
                links=[],
                images=[],
                metadata={},
                timestamp=start_time.isoformat(),
                error="Invalid URL format"
            )
        
        # Add protocol if missing
        if not parsed_url.scheme:
            url = "https://" + url
            parsed_url = urlparse(url)
        
        # Fetch content asynchronously
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with session.get(url, headers=headers, ssl=True) as response:
                response.raise_for_status()
                
                # Check content type
                content_type = response.headers.get('Content-Type', '').lower()
                if 'text/html' not in content_type:
                    return WebPageContent(
                        url=url,
                        title="",
                        description="",
                        main_content="",
                        links=[],
                        images=[],
                        metadata={"content_type": content_type},
                        timestamp=start_time.isoformat(),
                        error=f"Non-HTML content type: {content_type}"
                    )
                
                html_content = await response.text()
                final_url = str(response.url)
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract title
        title = ""
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
        
        # Try Open Graph title
        if not title:
            og_title = soup.find('meta', property='og:title')
            if og_title:
                title = og_title.get('content', '').strip()
        
        # Extract description
        description = ""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            description = meta_desc.get('content', '').strip()
        
        # Try Open Graph description
        if not description:
            og_desc = soup.find('meta', property='og:description')
            if og_desc:
                description = og_desc.get('content', '').strip()
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'noscript']):
            element.decompose()
        
        # Extract main content
        main_content = ""
        content_selectors = [
            'main', 'article', '.content', '.post', '.entry',
            '.main-content', '.article-content', '.post-content', '#content'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                main_content = content_elem.get_text(separator=' ', strip=True)
                break
        
        # Fallback to body if no main content found
        if not main_content:
            body = soup.find('body')
            if body:
                main_content = body.get_text(separator=' ', strip=True)
        
        # Clean and normalize whitespace
        main_content = re.sub(r'\s+', ' ', main_content).strip()
        
        # Truncate if needed
        if len(main_content) > max_length:
            main_content = main_content[:max_length] + "..."
        
        # Extract links
        links = []
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            text = link.get_text().strip()
            
            if href and text and len(text) > 3:
                absolute_url = urljoin(final_url, href)
                links.append({
                    "url": absolute_url,
                    "text": text[:100]  # Limit text length
                })
        
        # Limit to 10 links
        links = links[:10]
        
        # Extract images
        images = []
        for img in soup.find_all('img', src=True):
            src = img.get('src')
            alt = img.get('alt', '')
            
            if src:
                absolute_url = urljoin(final_url, src)
                images.append({
                    "url": absolute_url,
                    "alt": alt[:100]  # Limit alt text length
                })
        
        # Limit to 5 images
        images = images[:5]
        
        # Extract metadata
        metadata = {}
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            
            if name and content:
                metadata[name] = content
        
        # Add additional metadata
        metadata.update({
            "status_code": response.status,
            "text_length": len(main_content),
            "final_url": final_url,
            "links_count": len(links),
            "images_count": len(images),
        })
        
        return WebPageContent(
            url=final_url,
            title=title or "No title found",
            description=description,
            main_content=main_content,
            links=links,
            images=images,
            metadata=metadata,
            timestamp=datetime.now(timezone.utc).isoformat(),
            error=None
        )
        
    except asyncio.TimeoutError:
        logger.warning(f"Timeout reading URL: {url}")
        return WebPageContent(
            url=url,
            title="",
            description="",
            main_content="",
            links=[],
            images=[],
            metadata={},
            timestamp=start_time.isoformat(),
            error="Request timeout"
        )
    except aiohttp.ClientError as e:
        logger.warning(f"HTTP error reading URL {url}: {e}")
        return WebPageContent(
            url=url,
            title="",
            description="",
            main_content="",
            links=[],
            images=[],
            metadata={},
            timestamp=start_time.isoformat(),
            error=f"HTTP error: {str(e)}"
        )
    except Exception as e:
        logger.exception(f"Error reading URL {url}: {e}")
        return WebPageContent(
            url=url,
            title="",
            description="",
            main_content="",
            links=[],
            images=[],
            metadata={},
            timestamp=start_time.isoformat(),
            error=f"Failed to read URL: {str(e)}"
        )


























