"""
Pytest configuration and fixtures for chatbot tests
"""
import pytest
import os
import tempfile
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator

# Set test environment variables before importing app
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["OPENAI_API_KEY"] = "test-key-12345"

# Import in correct order to avoid circular imports
from core.db import Base, get_db
from core.config import settings

# Import models first to register them
from models import faq, log

# Import app last
from main import app


@pytest.fixture(scope="function")
def test_db():
    """Create a test database using temporary file"""
    # Use temporary file database instead of in-memory for better compatibility
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    db_path = temp_db.name
    
    engine = None
    try:
        engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False}
        )
        
        # Import all models to ensure they're registered
        from models.faq import FAQ, Category
        from models.log import ChatLog
        
        # Create all tables on the engine
        Base.metadata.create_all(bind=engine)
        
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        db = TestingSessionLocal()
        # Store engine reference for later use
        db.bind = engine
        db._temp_db_path = db_path  # Store path for cleanup
        try:
            yield db
        finally:
            db.close()
            # Close all connections before dropping
            if engine:
                engine.dispose()
                Base.metadata.drop_all(bind=engine)
    finally:
        # Clean up temporary file - wait a bit for file handles to close
        import time
        time.sleep(0.1)
        if os.path.exists(db_path):
            try:
                os.unlink(db_path)
            except (PermissionError, OSError):
                # File might still be in use, that's okay for tests
                pass


@pytest.fixture(scope="function")
def test_client(test_db):
    """Create a test client with test database"""
    from fastapi.testclient import TestClient
    
    # Get the engine from test_db session
    engine = test_db.bind
    
    # Ensure tables exist in the test database engine
    from models.faq import FAQ, Category
    from models.log import ChatLog
    Base.metadata.create_all(bind=engine)
    
    def override_get_db():
        # Return the test_db session
        try:
            yield test_db
        finally:
            # Don't close here, it's managed by test_db fixture
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    client = TestClient(app)
    yield client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_faq_data():
    """Sample FAQ data for testing"""
    return {
        "question": "چطور می‌توانم با پشتیبانی تماس بگیرم؟",
        "answer": "شما می‌توانید از طریق ایمیل یا تلفن با پشتیبانی تماس بگیرید.",
        "category_id": None
    }


@pytest.fixture
def sample_chat_request():
    """Sample chat request for testing"""
    return {
        "message": "سلام",
        "debug": False,
        "category_filter": None
    }

