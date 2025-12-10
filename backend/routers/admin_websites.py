"""
Admin Websites API

Endpoints for managing websites and syncing their pages.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
from urllib.parse import urlparse
import asyncio
import logging

from pydantic import BaseModel, HttpUrl
from core.db import get_db
from models.tracked_site import TrackedSite
from models.website_page import WebsitePage
from services.sites_service import extract_domain_from_url
from services.website_sync import sync_website, generate_default_urls
from core.admin_auth import require_admin

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/admin/websites",
    tags=["admin-websites"],
)


class WebsiteResponse(BaseModel):
    """Response model for website list"""
    id: int
    url: str
    title: Optional[str] = None
    is_active: bool
    last_crawled_at: Optional[datetime] = None
    pages_count: int
    
    class Config:
        from_attributes = True


class WebsiteCreateRequest(BaseModel):
    """Request model for creating a website"""
    url: str


class WebsiteSyncResponse(BaseModel):
    """Response model for sync operations"""
    id: int
    url: str
    title: Optional[str] = None
    is_active: bool
    pages_count: int
    last_crawled_at: Optional[datetime] = None


def normalize_url(url: str) -> str:
    """
    Normalize URL: strip spaces, ensure schema.
    
    Args:
        url: Raw URL string
        
    Returns:
        Normalized URL with https:// schema if missing
    """
    url = url.strip()
    
    # If no schema, add https://
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    
    return url


@router.get("", response_model=List[WebsiteResponse])
def list_websites(
    request: Request,
    _: None = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get list of all websites.
    
    Returns:
        List of websites with id, url, title (name), is_active,
        last_crawled_at (max over pages), and pages_count
    """
    websites = db.query(TrackedSite).all()
    
    result = []
    for website in websites:
        # Get pages count and max last_crawled_at
        pages_query = db.query(WebsitePage).filter(
            WebsitePage.website_id == website.id
        )
        pages_count = pages_query.count()
        
        # Get max last_crawled_at
        max_crawled = db.query(func.max(WebsitePage.last_crawled_at)).filter(
            WebsitePage.website_id == website.id
        ).scalar()
        
        result.append(WebsiteResponse(
            id=website.id,
            url=website.url,
            title=website.name,  # Use name as title
            is_active=website.is_active,
            last_crawled_at=max_crawled,
            pages_count=pages_count
        ))
    
    return result


@router.post("", response_model=WebsiteSyncResponse)
async def create_website(
    payload: WebsiteCreateRequest,
    request: Request,
    _: None = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new website or return existing active one.
    
    If a website with the same URL exists and is_active, return it.
    Otherwise create a new Website row (is_active=True).
    After saving, call sync_website with a basic list of URLs.
    
    Returns:
        Website info + minimal sync summary (pages_count, last_crawled_at)
    """
    # Normalize URL
    normalized_url = normalize_url(payload.url)
    
    # Check if website with same URL exists and is_active
    existing = db.query(TrackedSite).filter(
        TrackedSite.url == normalized_url,
        TrackedSite.is_active == True
    ).first()
    
    if existing:
        # Return existing website
        website = existing
        created = False
    else:
        # Create new website
        domain = extract_domain_from_url(normalized_url)
        website = TrackedSite(
            name=normalized_url,  # Use URL as name initially
            url=normalized_url,
            domain=domain,
            is_active=True
        )
        db.add(website)
        db.commit()
        db.refresh(website)
        created = True
    
    # Sync website pages in background
    from core.db import SessionLocal
    
    async def sync_task():
        """Background task that creates its own DB session"""
        bg_db = SessionLocal()
        try:
            # Re-fetch the website in the new session
            bg_website = bg_db.query(TrackedSite).filter(
                TrackedSite.id == website.id
            ).first()
            if bg_website:
                urls = generate_default_urls(bg_website.url)
                await sync_website(bg_db, bg_website, urls=urls)
        except Exception as e:
            logger.error(f"Error in background sync task for website {website.id}: {e}", exc_info=True)
        finally:
            bg_db.close()
    
    # Run sync in background
    asyncio.create_task(sync_task())
    
    # Get initial pages count (will be 0 if just created)
    pages_count = db.query(WebsitePage).filter(
        WebsitePage.website_id == website.id
    ).count()
    
    max_crawled = db.query(func.max(WebsitePage.last_crawled_at)).filter(
        WebsitePage.website_id == website.id
    ).scalar()
    
    return WebsiteSyncResponse(
        id=website.id,
        url=website.url,
        title=website.name,
        is_active=website.is_active,
        pages_count=pages_count,
        last_crawled_at=max_crawled
    )


@router.post("/{website_id}/sync", response_model=WebsiteSyncResponse)
async def sync_website_endpoint(
    website_id: int,
    request: Request,
    _: None = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Sync (crawl) pages for a specific website.
    
    Finds the website, ensures is_active, builds the URL list,
    calls sync_website, and returns updated summary.
    
    Returns:
        Updated website summary (pages_count, last_crawled_at)
    """
    website = db.query(TrackedSite).filter(TrackedSite.id == website_id).first()
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")
    
    if not website.is_active:
        raise HTTPException(
            status_code=400,
            detail="Website is not active. Please activate it first."
        )
    
    # Build URL list
    urls = generate_default_urls(website.url)
    
    # Sync website (this is async, but we'll await it)
    await sync_website(db, website, urls=urls)
    
    # Refresh to get updated data
    db.refresh(website)
    
    # Get updated pages count and last_crawled_at
    pages_count = db.query(WebsitePage).filter(
        WebsitePage.website_id == website.id
    ).count()
    
    max_crawled = db.query(func.max(WebsitePage.last_crawled_at)).filter(
        WebsitePage.website_id == website.id
    ).scalar()
    
    return WebsiteSyncResponse(
        id=website.id,
        url=website.url,
        title=website.name,
        is_active=website.is_active,
        pages_count=pages_count,
        last_crawled_at=max_crawled
    )


