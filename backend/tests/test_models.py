"""
Tests for database models
"""
import pytest
from datetime import datetime
from models.faq import FAQ, Category
from models.log import ChatLog


class TestFAQModel:
    """Test FAQ model"""
    
    def test_create_faq(self, test_db):
        """Test creating a FAQ"""
        faq = FAQ(
            question="سوال تستی؟",
            answer="پاسخ تستی",
            is_active=True
        )
        test_db.add(faq)
        test_db.commit()
        test_db.refresh(faq)
        
        assert faq.id is not None
        assert faq.question == "سوال تستی؟"
        assert faq.answer == "پاسخ تستی"
        assert faq.is_active is True
        assert faq.created_at is not None
    
    def test_faq_with_category(self, test_db):
        """Test FAQ with category"""
        category = Category(name="عمومی", slug="general")
        test_db.add(category)
        test_db.commit()
        test_db.refresh(category)
        
        faq = FAQ(
            question="سوال؟",
            answer="پاسخ",
            category_id=category.id
        )
        test_db.add(faq)
        test_db.commit()
        test_db.refresh(faq)
        
        assert faq.category_id == category.id
        assert faq.category.name == "عمومی"


class TestCategoryModel:
    """Test Category model"""
    
    def test_create_category(self, test_db):
        """Test creating a category"""
        category = Category(name="پشتیبانی", slug="support")
        test_db.add(category)
        test_db.commit()
        test_db.refresh(category)
        
        assert category.id is not None
        assert category.name == "پشتیبانی"
        assert category.slug == "support"
        assert category.created_at is not None


class TestChatLogModel:
    """Test ChatLog model"""
    
    def test_create_chatlog(self, test_db):
        """Test creating a chat log"""
        log = ChatLog(
            user_text="سلام",
            ai_text="سلام! چطور می‌تونم کمکتون کنم؟",
            intent="greeting",
            source="faq",
            confidence=0.95,
            success=True
        )
        test_db.add(log)
        test_db.commit()
        test_db.refresh(log)
        
        assert log.id is not None
        assert log.user_text == "سلام"
        assert log.intent == "greeting"
        assert log.source == "faq"
        assert log.confidence == 0.95
        assert log.success is True
        assert log.timestamp is not None
    
    def test_chatlog_optional_fields(self, test_db):
        """Test ChatLog with optional fields"""
        log = ChatLog(
            user_text="Test",
            ai_text="Response"
        )
        test_db.add(log)
        test_db.commit()
        test_db.refresh(log)
        
        assert log.id is not None
        assert log.intent is None
        assert log.source is None
        assert log.success is False  # Default value











