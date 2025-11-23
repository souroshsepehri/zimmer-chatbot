"""
Basic test for get_smart_response method to verify it works correctly.
"""
import pytest
import asyncio
from unittest.mock import patch, MagicMock
from schemas.smart_agent import SmartAgentRequest, SmartAgentResponse
from services.smart_agent import smart_agent
from langchain_core.messages import AIMessage


class TestGetSmartResponseBasic:
    """Basic tests for get_smart_response method"""
    
    @pytest.mark.asyncio
    async def test_get_smart_response_returns_smart_agent_response(self):
        """
        Verify that get_smart_response returns a SmartAgentResponse
        with a non-empty response string.
        """
        # Mock LLM response
        mock_llm_response = AIMessage(content="این صفحه درباره خدمات اتوماسیون هوش مصنوعی زیمر است.")
        
        with patch.object(smart_agent, 'llm') as mock_llm:
            mock_llm.invoke = MagicMock(return_value=mock_llm_response)
            
            # Create request
            request = SmartAgentRequest(
                message="این صفحه دقیقا درباره چی توضیح میده؟",
                context={
                    "page_url": "https://zimmerai.com",
                    "history": []
                }
            )
            
            # Mock get_page_context to return test content
            with patch.object(smart_agent, 'get_page_context', return_value="این صفحه درباره خدمات اتوماسیون هوش مصنوعی زیمر است."):
                # Call the method (async)
                result = await smart_agent.get_smart_response(request)
                
                # Verify it's a SmartAgentResponse
                assert isinstance(result, SmartAgentResponse)
                
                # Verify response is a non-empty string
                assert isinstance(result.response, str)
                assert len(result.response) > 0
                
                # Verify required fields are present
                assert result.style is not None
                assert result.response_time >= 0
                assert isinstance(result.web_content_used, bool)
                assert isinstance(result.urls_processed, list)
                assert isinstance(result.context_used, bool)
                assert result.timestamp is not None
                assert result.error is None or isinstance(result.error, str)
    
    @pytest.mark.asyncio
    async def test_get_smart_response_includes_page_context_in_debug_info(self):
        """
        Verify that get_smart_response includes page context information
        in debug_info when page_url is provided.
        """
        # Mock page context reading
        mock_page_ctx = {
            "url": "https://zimmerai.com",
            "title": "Zimmer AI - خدمات اتوماسیون",
            "description": "خدمات اتوماسیون هوش مصنوعی",
            "main_content": "این صفحه درباره خدمات اتوماسیون هوش مصنوعی زیمر است. ما راهکارهای پیشرفته برای کسب‌وکارها ارائه می‌دهیم.",
            "metadata": {}
        }
        
        # Mock LLM response
        mock_llm_response = AIMessage(content="این صفحه درباره خدمات اتوماسیون هوش مصنوعی زیمر است.")
        
        with patch.object(smart_agent, 'llm') as mock_llm:
            mock_llm.invoke = MagicMock(return_value=mock_llm_response)
            
            # Mock _read_page_context
            with patch.object(smart_agent, '_read_page_context', return_value=mock_page_ctx):
                # Create request with page_url
                request = SmartAgentRequest(
                    message="این صفحه دقیقا درباره چی توضیح میده؟",
                    style="auto",
                    context={
                        "session_id": "test-session-1",
                        "page_url": "https://zimmerai.com",
                        "history": []
                    }
                )
                
                # Call the method
                result = await smart_agent.get_smart_response(request)
                
                # Verify it's a SmartAgentResponse
                assert isinstance(result, SmartAgentResponse)
                
                # Verify debug_info exists and contains page context fields
                assert result.debug_info is not None
                assert "page_url" in result.debug_info
                assert "has_page_content" in result.debug_info
                
                # Verify page_url is set
                assert result.debug_info["page_url"] == "https://zimmerai.com"
                
                # Verify page details are included
                assert "page_title" in result.debug_info
                assert "page_description" in result.debug_info
                assert "page_content_preview" in result.debug_info
                
                # Verify has_page_content is True when content exists
                assert result.debug_info["has_page_content"] is True
                
                # Verify preview is truncated to reasonable length
                preview = result.debug_info.get("page_content_preview", "")
                assert len(preview) <= 300

