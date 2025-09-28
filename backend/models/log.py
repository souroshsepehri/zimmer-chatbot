from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.db import Base


class ChatLog(Base):
    __tablename__ = "chat_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    user_text = Column(Text, nullable=False)
    ai_text = Column(Text, nullable=False)
    intent = Column(String(50), nullable=True)
    source = Column(String(20), nullable=True)  # faq, rag, llm, fallback
    confidence = Column(Float, nullable=True)
    success = Column(Boolean, default=False)
    matched_faq_id = Column(Integer, nullable=True)  # Removed foreign key constraint
    tokens_in = Column(Integer, nullable=True)
    tokens_out = Column(Integer, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)  # JSON string for additional data
    
    # Relationship (commented out to avoid circular import issues)
    # matched_faq = relationship("FAQ", foreign_keys=[matched_faq_id])
