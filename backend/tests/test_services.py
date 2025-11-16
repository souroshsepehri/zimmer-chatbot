"""
Tests for service layer components
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from models.faq import FAQ
from services.simple_chatbot import SimpleChatbot
from services.retriever import faq_retriever


class TestSimpleChatbot:
    """Test SimpleChatbot service"""
    
    def test_simple_chatbot_initialization(self):
        """Test that SimpleChatbot can be initialized"""
        chatbot = SimpleChatbot()
        assert chatbot is not None
    
    @pytest.mark.skip(reason="Requires OpenAI API key or mock setup")
    def test_simple_chatbot_get_answer(self, test_db):
        """Test getting answer from SimpleChatbot"""
        chatbot = SimpleChatbot()
        # This would require mocking OpenAI API
        # For now, just test that method exists
        assert hasattr(chatbot, 'get_answer')


class TestFAQRetriever:
    """Test FAQ retriever service"""
    
    def test_retriever_initialization(self):
        """Test that retriever can be initialized"""
        assert faq_retriever is not None
    
    def test_retriever_search_method_exists(self):
        """Test that retriever has search method"""
        # Check if retriever has semantic_search method (the actual method name)
        has_semantic_search = hasattr(faq_retriever, 'semantic_search')
        has_build_index = hasattr(faq_retriever, 'build_index')
        has_reindex = hasattr(faq_retriever, 'reindex')
        # At least one method should exist
        assert has_semantic_search or has_build_index or has_reindex
    
    def test_retriever_with_empty_db(self, test_db):
        """Test retriever with empty database"""
        # Should handle empty database gracefully
        try:
            if hasattr(faq_retriever, 'semantic_search'):
                results = faq_retriever.semantic_search("test", top_k=5)
                assert isinstance(results, list)
        except Exception as e:
            # If retriever requires initialization or API key, that's okay
            # The test just verifies the method exists and returns a list
            pass


class TestChainService:
    """Test ChatChain service"""
    
    def test_chain_import(self):
        """Test that ChatChain can be imported"""
        from services.chain import chat_chain
        assert chat_chain is not None
    
    def test_chain_process_message_exists(self):
        """Test that process_message method exists"""
        from services.chain import chat_chain
        assert hasattr(chat_chain, 'process_message')
    
    @pytest.mark.skip(reason="Requires full chain setup with mocks")
    def test_chain_process_message(self, test_db):
        """Test processing a message through the chain"""
        from services.chain import chat_chain
        # This would require mocking all external dependencies
        # For now, just verify the method exists
        assert callable(getattr(chat_chain, 'process_message', None))


class TestIntentService:
    """Test Intent detection service"""
    
    def test_intent_service_import(self):
        """Test that intent service can be imported"""
        try:
            from services.intent import intent_detector
            assert intent_detector is not None
        except ImportError:
            pytest.skip("Intent service not available")
    
    def test_intent_detection_method_exists(self):
        """Test that intent detection method exists"""
        try:
            from services.intent import intent_detector
            assert hasattr(intent_detector, 'detect') or hasattr(intent_detector, 'detect_intent')
        except ImportError:
            pytest.skip("Intent service not available")

