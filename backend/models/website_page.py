"""
Website Page Model

SQLAlchemy model for storing crawled pages from tracked websites.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.db import Base


class WebsitePage(Base):
    """Model for storing crawled pages from tracked websites"""
    
    __tablename__ = "website_pages"
    
    id = Column(Integer, primary_key=True, index=True)
    website_id = Column(Integer, ForeignKey("tracked_sites.id"), nullable=False, index=True)
    url = Column(String(2048), nullable=False, index=True)
    title = Column(String(512), nullable=True)
    content = Column(Text, nullable=True)
    content_hash = Column(String(64), nullable=True, index=True)  # SHA256 hash
    last_crawled_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    website = relationship("TrackedSite", back_populates="pages")


