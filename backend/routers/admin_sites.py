"""
Admin Sites API

CRUD endpoints for managing tracked sites used by the Smart Agent.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional

from core.db import get_db
from models.tracked_site import TrackedSite
from schemas.tracked_site import (
    TrackedSiteCreate,
    TrackedSiteUpdate,
    TrackedSiteRead,
)
from services.sites_service import extract_domain_from_url
from services.website_sync import sync_website
from core.admin_auth import require_admin

router = APIRouter(
    prefix="/api/admin/sites",
    tags=["admin-sites"],
)


@router.get("", response_model=List[TrackedSiteRead])
def list_sites(request: Request, _: None = Depends(require_admin), db: Session = Depends(get_db)):
    """
    Get list of all tracked sites.
    
    Returns:
        List of TrackedSiteRead objects, ordered by creation date (newest first)
    """
    q = db.query(TrackedSite).order_by(TrackedSite.created_at.desc())
    return q.all()


@router.get("/{site_id}", response_model=TrackedSiteRead)
def get_site(site_id: int, request: Request, _: None = Depends(require_admin), db: Session = Depends(get_db)):
    """
    Get a single tracked site by ID.
    
    Args:
        site_id: ID of the site to retrieve
        
    Returns:
        TrackedSiteRead object
        
    Raises:
        HTTPException: If site not found
    """
    site = db.query(TrackedSite).filter(TrackedSite.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site


@router.post("", response_model=TrackedSiteRead)
def create_site(payload: TrackedSiteCreate, request: Request, _: None = Depends(require_admin), db: Session = Depends(get_db)):
    """
    Create a new tracked site.
    
    Args:
        payload: TrackedSiteCreate with site information
        
    Returns:
        Created TrackedSiteRead object
        
    Raises:
        HTTPException: If site with same URL already exists
    """
    existing = db.query(TrackedSite).filter(TrackedSite.url == str(payload.url)).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Site with this URL already exists"
        )
    
    # Extract domain from URL
    domain = extract_domain_from_url(str(payload.url))
    
    obj = TrackedSite(
        name=payload.name,
        url=str(payload.url),
        domain=domain,
        description=payload.description,
        is_active=payload.is_active,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/{site_id}", response_model=TrackedSiteRead)
def update_site(
    site_id: int,
    payload: TrackedSiteUpdate,
    request: Request,
    _: None = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Update an existing tracked site.
    
    Args:
        site_id: ID of the site to update
        payload: TrackedSiteUpdate with fields to update
        
    Returns:
        Updated TrackedSiteRead object
        
    Raises:
        HTTPException: If site not found
    """
    obj = db.query(TrackedSite).filter(TrackedSite.id == site_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Site not found")
    
    # Update only provided fields
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        if value is not None:
            # Convert HttpUrl to string if needed
            if key == "url" and value:
                url_str = str(value)
                setattr(obj, key, url_str)
                # Update domain when URL changes
                obj.domain = extract_domain_from_url(url_str)
            else:
                setattr(obj, key, value)
    
    # If domain is not set but URL is, extract it
    if not obj.domain and obj.url:
        obj.domain = extract_domain_from_url(obj.url)
    
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{site_id}")
def delete_site(site_id: int, request: Request, _: None = Depends(require_admin), db: Session = Depends(get_db)):
    """
    Delete a tracked site.
    
    Args:
        site_id: ID of the site to delete
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If site not found
    """
    obj = db.query(TrackedSite).filter(TrackedSite.id == site_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Site not found")
    
    db.delete(obj)
    db.commit()
    return {"success": True}


@router.post("/{site_id}/sync")
async def sync_site(
    site_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    _: None = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Sync (crawl) pages for a tracked site.
    
    This endpoint triggers a background task to crawl the website's pages
    and store them in the database.
    
    Args:
        site_id: ID of the site to sync
        background_tasks: FastAPI background tasks
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If site not found
    """
    site = db.query(TrackedSite).filter(TrackedSite.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    
    # Create a new session for the background task
    from core.db import SessionLocal
    import asyncio
    import logging
    
    logger = logging.getLogger(__name__)
    
    async def sync_task():
        """Background task that creates its own DB session"""
        bg_db = SessionLocal()
        try:
            # Re-fetch the site in the new session
            bg_site = bg_db.query(TrackedSite).filter(TrackedSite.id == site_id).first()
            if bg_site:
                await sync_website(bg_db, bg_site)
        except Exception as e:
            logger.error(f"Error in background sync task for site {site_id}: {e}", exc_info=True)
        finally:
            bg_db.close()
    
    # Run sync in background
    # Use asyncio.create_task to run async function in background
    # This will run even after the request completes
    asyncio.create_task(sync_task())
    
    return {
        "success": True,
        "message": f"Sync started for site {site_id}. Pages will be crawled in the background."
    }















