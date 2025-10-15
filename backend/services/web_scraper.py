import requests
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from urllib.parse import urlparse, urljoin
import logging

logger = logging.getLogger(__name__)
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Any, Optional
import time
import re
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class WebPage:
    url: str
    title: str
    content: str
    links: List[str]
    metadata: Dict[str, Any]

class WebScraper:
    def __init__(self, max_pages: int = 50, delay: float = 1.0):
        self.max_pages = max_pages
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.visited_urls = set()
        self.scraped_pages = []
    
    def is_valid_url(self, url: str, base_domain: str) -> bool:
        """Check if URL is valid and belongs to the same domain"""
        try:
            parsed = urlparse(url)
            base_parsed = urlparse(base_domain)
            
            # Must be http or https
            if parsed.scheme not in ['http', 'https']:
                return False
            
            # Must be same domain
            if parsed.netloc != base_parsed.netloc:
                return False
            
            # Skip common non-content URLs
            skip_patterns = [
                r'\.(pdf|doc|docx|xls|xlsx|ppt|pptx|zip|rar|jpg|jpeg|png|gif|svg|css|js)$',
                r'#.*$',  # Skip anchors
                r'\?.*$',  # Skip query parameters for now
            ]
            
            for pattern in skip_patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    return False
            
            return True
        except:
            return False
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common unwanted elements
        text = re.sub(r'[^\w\s\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF.,!?;:()\-]', '', text)
        
        return text.strip()
    
    def extract_content(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract structured content from HTML"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Extract title
        title = ""
        title_tag = soup.find('title')
        if title_tag:
            title = self.clean_text(title_tag.get_text())
        
        # Extract main content
        content = ""
        
        # Try to find main content areas
        main_selectors = [
            'main', 'article', '.content', '.main-content', 
            '.post-content', '.entry-content', '#content'
        ]
        
        main_content = None
        for selector in main_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        if main_content:
            content = self.clean_text(main_content.get_text())
        else:
            # Fallback to body content
            body = soup.find('body')
            if body:
                content = self.clean_text(body.get_text())
        
        # Extract links
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(url, href)
            if self.is_valid_url(full_url, url):
                links.append(full_url)
        
        # Extract metadata
        metadata = {
            'title': title,
            'word_count': len(content.split()),
            'link_count': len(links),
            'scraped_at': time.time()
        }
        
        return {
            'title': title,
            'content': content,
            'links': links,
            'metadata': metadata
        }
    
    def scrape_page(self, url: str) -> Optional[WebPage]:
        """Scrape a single page"""
        try:
            logger.info(f"Scraping: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Check if it's HTML
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                logger.warning(f"Skipping non-HTML content: {url}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            extracted = self.extract_content(soup, url)
            
            if not extracted['content'] or len(extracted['content']) < 50:
                logger.warning(f"Insufficient content: {url}")
                return None
            
            page = WebPage(
                url=url,
                title=extracted['title'],
                content=extracted['content'],
                links=extracted['links'],
                metadata=extracted['metadata']
            )
            
            self.visited_urls.add(url)
            self.scraped_pages.append(page)
            
            logger.info(f"Successfully scraped: {url} ({extracted['metadata']['word_count']} words)")
            return page
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return None
    
    def scrape_website(self, start_url: str) -> List[WebPage]:
        """Scrape entire website starting from a URL"""
        logger.info(f"Starting website scrape from: {start_url}")
        
        # Reset state
        self.visited_urls = set()
        self.scraped_pages = []
        
        # Parse base domain
        base_domain = start_url
        
        # Start with the initial URL
        urls_to_visit = [start_url]
        
        while urls_to_visit and len(self.scraped_pages) < self.max_pages:
            current_url = urls_to_visit.pop(0)
            
            if current_url in self.visited_urls:
                continue
            
            # Scrape the page
            page = self.scrape_page(current_url)
            
            if page:
                # Add new links to visit
                for link in page.links:
                    if link not in self.visited_urls and link not in urls_to_visit:
                        urls_to_visit.append(link)
            
            # Delay between requests
            time.sleep(self.delay)
        
        logger.info(f"Scraping completed. Total pages: {len(self.scraped_pages)}")
        return self.scraped_pages
    
    def get_page_summary(self, pages: List[WebPage]) -> Dict[str, Any]:
        """Get summary of scraped pages"""
        total_words = sum(page.metadata['word_count'] for page in pages)
        total_links = sum(page.metadata['link_count'] for page in pages)
        
        return {
            'total_pages': len(pages),
            'total_words': total_words,
            'total_links': total_links,
            'average_words_per_page': total_words / len(pages) if pages else 0,
            'domains': list(set(urlparse(page.url).netloc for page in pages))
        }

# Global instance
_web_scraper = None

def get_web_scraper() -> WebScraper:
    """Get web scraper instance"""
    global _web_scraper
    if _web_scraper is None:
        _web_scraper = WebScraper()
    return _web_scraper
