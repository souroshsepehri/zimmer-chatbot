"""
Tests for database connection and operations
"""
import pytest
from sqlalchemy import text
from core.db import engine, Base, get_db
from models.faq import FAQ, Category
from models.log import ChatLog


class TestDatabase:
    """Test database functionality"""
    
    def test_database_connection(self, test_db):
        """Test that database connection works"""
        result = test_db.execute(text("SELECT 1"))
        assert result.scalar() == 1
    
    def test_database_tables_exist(self, test_db):
        """Test that all tables exist"""
        inspector = pytest.importorskip("sqlalchemy.inspect")
        inspector_obj = inspector.inspect(engine)
        tables = inspector_obj.get_table_names()
        
        assert 'faqs' in tables or 'categories' in tables or 'chat_logs' in tables
    
    def test_faq_model(self, test_db):
        """Test FAQ model creation"""
        faq = FAQ(
            question="Test question?",
            answer="Test answer."
        )
        test_db.add(faq)
        test_db.commit()
        test_db.refresh(faq)
        
        assert faq.id is not None
        assert faq.question == "Test question?"
        assert faq.answer == "Test answer."
    
    def test_chatlog_model(self, test_db):
        """Test ChatLog model creation"""
        log = ChatLog(
            user_text="Test message",
            ai_text="Test response",
            success=True
        )
        test_db.add(log)
        test_db.commit()
        test_db.refresh(log)
        
        assert log.id is not None
        assert log.user_text == "Test message"
        assert log.ai_text == "Test response"
        assert log.success is True
    
    def test_get_db_generator(self):
        """Test get_db dependency generator"""
        db_gen = get_db()
        db = next(db_gen)
        assert db is not None
        try:
            next(db_gen)  # Should raise StopIteration after close
        except StopIteration:
            pass






