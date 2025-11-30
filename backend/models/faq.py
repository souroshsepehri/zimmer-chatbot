from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, BLOB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.db import Base


class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    slug = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    faqs = relationship("FAQ", back_populates="category")


class FAQ(Base):
    __tablename__ = "faqs"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    tracked_site_id = Column(Integer, ForeignKey("tracked_sites.id"), nullable=True, index=True)  # Site-scoped FAQs
    embedding = Column(BLOB, nullable=True)  # Store FAISS vector as binary
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    category = relationship("Category", back_populates="faqs")
