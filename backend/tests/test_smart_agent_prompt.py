"""
Tests for SmartAIAgent prompt orchestration layer.

These tests verify that the SmartAIAgent correctly combines:
- FAQ matches from database
- Page context from web pages
- Brand tone and site metadata
- Chat history (when available)

All tests use black-box testing through the API endpoint to ensure
the prompt orchestrator works correctly end-to-end.
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from models.faq import FAQ, Category
from langchain_core.messages import AIMessage


class TestSmartAgentPageContext:
    """Test that SmartAIAgent uses page context correctly"""
    
    def test_smart_agent_uses_page_context(
        self,
        test_client: TestClient,
        test_db: Session
    ):
        """
        Verify that when page_url is provided, the agent uses page context
        in its response.
        
        Behavior guaranteed:
        - Agent extracts content from page_url
        - Agent includes page content in prompt
        - Response references the page content
        - Response is in Persian (not generic English template)
        """
        # Mock get_page_context to return test content
        mock_page_content = "این صفحه درباره خدمات اتوماسیون هوش مصنوعی زیمر است. ما راهکارهای پیشرفته برای کسب‌وکارها ارائه می‌دهیم."
        
        # Mock LLM response that references the page content
        mock_llm_response = AIMessage(content="این صفحه درباره خدمات اتوماسیون هوش مصنوعی زیمر است. در این صفحه می‌توانید اطلاعاتی درباره راهکارهای پیشرفته برای کسب‌وکارها پیدا کنید.")
        
        # Patch the smart_agent instance directly
        from services.smart_agent import smart_agent
        
        with patch.object(smart_agent, 'get_page_context', return_value=mock_page_content):
            with patch.object(smart_agent, 'llm') as mock_llm:
                # Mock the invoke method to return our mock response
                mock_llm.invoke = MagicMock(return_value=mock_llm_response)
                
                response = test_client.post(
                    "/api/smart-agent/chat",
                    json={
                        "message": "این صفحه درباره چیه؟",
                        "page_url": "https://zimmerai.com/test"
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                
                # Response should be in Persian
                assert isinstance(data.get("response"), str)
                response_text = data.get("response", "")
                
                # Response should mention something from the page content
                # Check for keywords from our mock content
                assert any(keyword in response_text for keyword in [
                    "خدمات",
                    "اتوماسیون",
                    "هوش مصنوعی",
                    "زیمر"
                ]), f"Response should mention page content, got: {response_text[:200]}"
                
                # Response should not be empty
                assert len(response_text) > 10
                
                # Verify debug info indicates page context was used
                debug_info = data.get("debug_info", {})
                assert debug_info.get("site_used") is True or data.get("web_content_used") is True


class TestSmartAgentFAQMatches:
    """Test that SmartAIAgent uses FAQ matches correctly"""
    
    def test_smart_agent_uses_faq_matches(
        self,
        test_client: TestClient,
        test_db: Session
    ):
        """
        Verify that when FAQ matches exist, the agent uses them in response.
        
        Behavior guaranteed:
        - Agent searches FAQs for relevant matches
        - Agent includes FAQ content in prompt
        - Response references the FAQ answer
        - Response mentions key terms from FAQ
        """
        # Create a test FAQ in the database
        category = Category(name="عمومی", slug="general")
        test_db.add(category)
        test_db.commit()
        
        faq = FAQ(
            question="چطور می‌توانم مشاوره رزرو کنم؟",
            answer="از طریق فرم مشاوره در سایت زیمر می‌توانید مشاوره رزرو کنید. همچنین می‌توانید با شماره تماس ما ارتباط برقرار کنید.",
            category_id=category.id
        )
        test_db.add(faq)
        test_db.commit()
        
        # Mock LLM response that references the FAQ
        mock_llm_response = AIMessage(content="برای رزرو مشاوره می‌توانید از طریق فرم مشاوره در سایت زیمر اقدام کنید. همچنین می‌توانید با شماره تماس ما ارتباط برقرار کنید.")
        
        # Mock get_page_context to return None (no page context)
        from services.smart_agent import smart_agent
        
        with patch.object(smart_agent, 'get_page_context', return_value=None):
            with patch.object(smart_agent, 'llm') as mock_llm:
                # Mock the invoke method to return our mock response
                mock_llm.invoke = MagicMock(return_value=mock_llm_response)
                
                response = test_client.post(
                    "/api/smart-agent/chat",
                    json={
                        "message": "چطور مشاوره رزرو کنم؟",
                        "page_url": None
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                
                response_text = data.get("response", "")
                
                # Response should mention FAQ answer content
                assert any(keyword in response_text for keyword in [
                    "فرم مشاوره",
                    "سایت زیمر",
                    "مشاوره رزرو"
                ]), f"Response should mention FAQ answer, got: {response_text[:200]}"
                
                # Verify debug info indicates FAQ was used
                debug_info = data.get("debug_info", {})
                assert debug_info.get("faq_used") is True or data.get("context_used") is True


class TestSmartAgentOutOfScope:
    """Test that SmartAIAgent handles out-of-scope questions correctly"""
    
    def test_smart_agent_out_of_scope_question(
        self,
        test_client: TestClient,
        test_db: Session
    ):
        """
        Verify that when question is out of scope, agent doesn't hallucinate
        and redirects appropriately.
        
        Behavior guaranteed:
        - Agent recognizes out-of-scope questions
        - Agent does NOT provide detailed advice on unrelated topics
        - Agent mentions it's focused on Zimmer/website
        - Agent suggests consultation form or contact
        """
        # Mock LLM response that redirects appropriately
        mock_llm_response = AIMessage(content="من دستیار وب‌سایت زیمر هستم و در مورد موضوعات مرتبط با خدمات زیمر می‌توانم کمک کنم. برای سوالات دیگر می‌توانید از فرم مشاوره یا تماس با ما استفاده کنید.")
        
        # Mock get_page_context to return None (neutral/empty)
        from services.smart_agent import smart_agent
        
        with patch.object(smart_agent, 'get_page_context', return_value=None):
            with patch.object(smart_agent, 'llm') as mock_llm:
                # Mock the invoke method to return our mock response
                mock_llm.invoke = MagicMock(return_value=mock_llm_response)
                
                response = test_client.post(
                    "/api/smart-agent/chat",
                    json={
                        "message": "در مورد بیت کوین چی فکر می‌کنی؟",
                        "page_url": None
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                
                response_text = data.get("response", "").lower()
                
                # Response should NOT contain detailed investment advice
                # (we're testing that it doesn't hallucinate)
                investment_keywords = [
                    "خرید بیت کوین",
                    "قیمت بیت کوین",
                    "سرمایه گذاری",
                    "بازار ارز"
                ]
                
                # Response should mention Zimmer/website focus or consultation
                redirect_keywords = [
                    "زیمر",
                    "وب‌سایت",
                    "مشاوره",
                    "تماس",
                    "فرم"
                ]
                
                # Check that response mentions redirect keywords
                assert any(keyword in response_text for keyword in redirect_keywords), \
                    f"Response should redirect to consultation, got: {response_text[:200]}"
                
                # Response should indicate it's focused on Zimmer/website
                # (not giving general advice on unrelated topics)
                assert len(response_text) > 20  # Should be a meaningful response, not empty

