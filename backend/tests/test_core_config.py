"""
Tests for core configuration
"""
import pytest
import os
from core.config import settings


class TestConfig:
    """Test configuration settings"""
    
    def test_settings_loaded(self):
        """Test that settings are loaded correctly"""
        assert settings is not None
        assert hasattr(settings, 'database_url')
        assert hasattr(settings, 'server_port')
        assert hasattr(settings, 'server_host')
    
    def test_database_url(self):
        """Test database URL configuration"""
        assert isinstance(settings.database_url, str)
        assert len(settings.database_url) > 0
    
    def test_server_config(self):
        """Test server configuration"""
        assert isinstance(settings.server_port, int)
        assert settings.server_port > 0
        assert isinstance(settings.server_host, str)
        assert len(settings.server_host) > 0
    
    def test_retrieval_config(self):
        """Test retrieval configuration"""
        assert isinstance(settings.retrieval_top_k, int)
        assert settings.retrieval_top_k > 0
        assert isinstance(settings.retrieval_threshold, float)
        assert 0 <= settings.retrieval_threshold <= 1
    
    def test_openai_config(self):
        """Test OpenAI configuration"""
        assert isinstance(settings.openai_api_key, str)
        assert isinstance(settings.openai_model, str)
        assert len(settings.openai_model) > 0











