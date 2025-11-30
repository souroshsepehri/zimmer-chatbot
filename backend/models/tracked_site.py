"""
Tracked Site Model

SQLAlchemy model for tracking websites that the Smart Agent can read.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from core.db import Base


class TrackedSite(Base):
    """Model for tracked websites that the Smart Agent can access"""
    
    __tablename__ = "tracked_sites"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    url = Column(String(1024), nullable=False, unique=True, index=True)
    domain = Column(String(255), nullable=True, index=True)  # Normalized domain/host for quick lookup
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    @staticmethod
    def normalize_host(host: str) -> str:
        """
        Normalize a host string for matching.
        - Lowercase
        - Remove port (e.g., :443, :8000)
        - Remove www. prefix
        - Remove protocol if present
        """
        if not host:
            return ""
        
        # Remove protocol if present
        host = host.replace("http://", "").replace("https://", "")
        
        # Remove port
        if ":" in host:
            host = host.split(":")[0]
        
        # Lowercase
        host = host.lower()
        
        # Remove www. prefix
        if host.startswith("www."):
            host = host[4:]
        
        return host.strip()















