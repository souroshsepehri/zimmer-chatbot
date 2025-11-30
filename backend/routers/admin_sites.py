"""
Admin Sites API

CRUD endpoints for managing tracked sites used by the Smart Agent.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from core.db import get_db
from models.tracked_site import TrackedSite
from schemas.tracked_site import (
    TrackedSiteCreate,
    TrackedSiteUpdate,
    TrackedSiteRead,
)

router = APIRouter(
    prefix="/api/admin/sites",
    tags=["admin-sites"],
)


@router.get("", response_model=List[TrackedSiteRead])
def list_sites(db: Session = Depends(get_db)):
    """
    Get list of all tracked sites.
    
    Returns:
        List of TrackedSiteRead objects, ordered by creation date (newest first)
    """
    q = db.query(TrackedSite).order_by(TrackedSite.created_at.desc())
    return q.all()


@router.post("", response_model=TrackedSiteRead)
def create_site(payload: TrackedSiteCreate, db: Session = Depends(get_db)):
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
    
    obj = TrackedSite(
        name=payload.name,
        url=str(payload.url),
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
                setattr(obj, key, str(value))
            else:
                setattr(obj, key, value)
    
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{site_id}")
def delete_site(site_id: int, db: Session = Depends(get_db)):
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















