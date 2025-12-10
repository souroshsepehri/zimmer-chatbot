"""
Sites Service

Utility functions for resolving and managing tracked sites.
"""

from typing import Optional
from sqlalchemy.orm import Session
from models.tracked_site import TrackedSite


def resolve_site_by_host(db: Session, host: str) -> Optional[TrackedSite]:
    """
    Resolve a host string to a TrackedSite record.
    
    Normalizes the host (lowercase, remove port, remove www.) and matches
    against TrackedSite.domain or extracts domain from TrackedSite.url.
    
    Args:
        db: Database session
        host: Host string (e.g., "example.com", "www.example.com:443", "https://example.com")
        
    Returns:
        TrackedSite if found and active, None otherwise
    """
    if not host:
        return None
    
    # Normalize the input host
    normalized_host = TrackedSite.normalize_host(host)
    
    if not normalized_host:
        return None
    
    # Try to find by domain field first
    site = db.query(TrackedSite).filter(
        TrackedSite.domain == normalized_host,
        TrackedSite.is_active == True
    ).first()
    
    if site:
        return site
    
    # Fallback: try to match by extracting domain from URL
    # This handles cases where domain wasn't set during creation
    all_sites = db.query(TrackedSite).filter(
        TrackedSite.is_active == True
    ).all()
    
    for site in all_sites:
        if site.url:
            site_domain = TrackedSite.normalize_host(site.url)
            if site_domain == normalized_host:
                # Update the domain field for future lookups
                if not site.domain:
                    site.domain = normalized_host
                    db.commit()
                return site
    
    return None


def extract_domain_from_url(url: str) -> str:
    """
    Extract and normalize domain from a URL.
    
    Args:
        url: Full URL (e.g., "https://www.example.com/path")
        
    Returns:
        Normalized domain (e.g., "example.com")
    """
    return TrackedSite.normalize_host(url)












