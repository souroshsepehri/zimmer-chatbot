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
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())




