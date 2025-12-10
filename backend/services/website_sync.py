"""
Website Sync Service

Service for crawling and storing website pages.
"""

import logging
import hashlib
from typing import Optional, Tuple
from datetime import datetime
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from models.tracked_site import TrackedSite
from models.website_page import WebsitePage

logger = logging.getLogger(__name__)

# Maximum content length to store (10,000 characters)
MAX_CONTENT_LENGTH = 10_000


async def fetch_html(url: str, timeout: int = 15) -> str:
    """
    Fetch HTML content from a URL.
    
    Args:
        url: URL to fetch
        timeout: Request timeout in seconds
        
    Returns:
        HTML content as string
        
    Raises:
        httpx.HTTPError: If request fails
    """
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        raise


def extract_main_content(html: str) -> Tuple[str, str]:
    """
    Extract main content from HTML using BeautifulSoup.
    
    - Extracts <title>
    - Removes <script>, <style>, nav, footer, header where possible
    - Joins text from <main>, <article>, and <p> tags
    - Normalizes whitespace
    - Truncates to MAX_CONTENT_LENGTH
    
    Args:
        html: HTML content as string
        
    Returns:
        Tuple of (title, content)
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract title
        title_tag = soup.find('title')
        title = title_tag.get_text(strip=True) if title_tag else ""
        
        # Remove unwanted elements
        for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        
        # Try to find main content areas
        content_parts = []
        
        # Try <main> tag first
        main_tag = soup.find('main')
        if main_tag:
            content_parts.append(main_tag.get_text(separator=' ', strip=True))
        
        # Try <article> tags
        articles = soup.find_all('article')
        for article in articles:
            content_parts.append(article.get_text(separator=' ', strip=True))
        
        # If no main/article found, use all <p> tags
        if not content_parts:
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                if text:
                    content_parts.append(text)
        
        # If still no content, use body text
        if not content_parts:
            body = soup.find('body')
            if body:
                content_parts.append(body.get_text(separator=' ', strip=True))
        
        # Join all content parts
        content = ' '.join(content_parts)
        
        # Normalize whitespace (replace multiple spaces/newlines with single space)
        import re
        content = re.sub(r'\s+', ' ', content).strip()
        
        # Truncate if too long
        if len(content) > MAX_CONTENT_LENGTH:
            content = content[:MAX_CONTENT_LENGTH] + "..."
        
        return title, content
        
    except Exception as e:
        logger.error(f"Error extracting content from HTML: {e}")
        return "", ""


def generate_default_urls(base_url: str) -> list[str]:
    """
    Generate default URLs to crawl for a website.
    
    Always includes the root URL, and if it looks like a standard domain,
    also tries /about, /services, /contact.
    
    Args:
        base_url: Base URL of the website
        
    Returns:
        List of URLs to crawl
    """
    urls = [base_url]
    
    # Parse the base URL
    parsed = urlparse(base_url)
    base_path = f"{parsed.scheme}://{parsed.netloc}"
    
    # Add common pages
    common_paths = ["/about", "/services", "/contact"]
    for path in common_paths:
        urls.append(urljoin(base_path, path))
    
    return urls


async def sync_website(session: Session, website: TrackedSite, urls: Optional[list[str]] = None) -> None:
    """
    Sync website pages by crawling URLs and storing/updating them in the database.
    
    For each URL:
      - Fetch HTML
      - Extract title and content
      - Compute content_hash (SHA256)
      - Upsert WebsitePage:
        - If page with same URL exists: update title/content/content_hash/last_crawled_at
        - Otherwise: create new WebsitePage
    
    Args:
        session: Database session
        website: TrackedSite instance
        urls: Optional list of URLs to crawl. If None, uses generate_default_urls(website.url)
    """
    if urls is None:
        urls = generate_default_urls(website.url)
    
    logger.info(f"Syncing website {website.id} ({website.url}) with {len(urls)} URLs")
    
    for url in urls:
        try:
            # Fetch HTML
            html = await fetch_html(url)
            
            # Extract content
            title, content = extract_main_content(html)
            
            # Compute content hash
            content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            
            # Check if page already exists
            existing_page = session.query(WebsitePage).filter(
                WebsitePage.website_id == website.id,
                WebsitePage.url == url
            ).first()
            
            if existing_page:
                # Update existing page
                existing_page.title = title
                existing_page.content = content
                existing_page.content_hash = content_hash
                existing_page.last_crawled_at = datetime.now()
                existing_page.is_active = True
                logger.info(f"Updated page: {url}")
            else:
                # Create new page
                new_page = WebsitePage(
                    website_id=website.id,
                    url=url,
                    title=title,
                    content=content,
                    content_hash=content_hash,
                    last_crawled_at=datetime.now(),
                    is_active=True
                )
                session.add(new_page)
                logger.info(f"Created new page: {url}")
            
        except Exception as e:
            logger.error(f"Error syncing URL {url} for website {website.id}: {e}")
            # Continue with other URLs even if one fails
            continue
    
    # Commit all changes
    try:
        session.commit()
        logger.info(f"Successfully synced website {website.id}")
    except Exception as e:
        logger.error(f"Error committing website sync for {website.id}: {e}")
        session.rollback()
        raise


