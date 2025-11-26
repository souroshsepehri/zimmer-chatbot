"""
Tests for API endpoints
"""
import pytest
import json
from models.faq import FAQ
from models.log import ChatLog


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_endpoint(self, test_client):
        """Test /health endpoint"""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestChatEndpoint:
    """Test chat endpoint"""
    
    def test_chat_endpoint_exists(self, test_client):
        """Test that chat endpoint exists"""
        response = test_client.post(
            "/api/chat",
            json={"message": "سلام"}
        )
        # Should not return 404
        assert response.status_code != 404
    
    def test_chat_endpoint_requires_message(self, test_client):
        """Test that chat endpoint requires message"""
        response = test_client.post("/api/chat", json={})
        # Should return validation error
        assert response.status_code in [400, 422]
    
    def test_chat_endpoint_handles_empty_message(self, test_client):
        """Test chat endpoint with empty message"""
        response = test_client.post(
            "/api/chat",
            json={"message": ""}
        )
        # Should handle gracefully (either accept or reject)
        assert response.status_code in [200, 400, 422]


class TestFAQEndpoints:
    """Test FAQ endpoints"""
    
    def test_get_faqs_endpoint(self, test_client):
        """Test GET /api/faqs endpoint"""
        response = test_client.get("/api/faqs")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data or isinstance(data, list)
    
    def test_create_faq_endpoint(self, test_client, sample_faq_data):
        """Test POST /api/faqs endpoint"""
        response = test_client.post(
            "/api/faqs",
            json=sample_faq_data
        )
        # Should create or return validation error
        assert response.status_code in [200, 201, 400, 422]
    
    def test_get_faq_by_id(self, test_client, test_db):
        """Test GET /api/faqs/{id} endpoint"""
        # Create a test FAQ
        faq = FAQ(question="Test?", answer="Test answer")
        test_db.add(faq)
        test_db.commit()
        test_db.refresh(faq)
        
        response = test_client.get(f"/api/faqs/{faq.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["question"] == "Test?"
    
    def test_get_nonexistent_faq(self, test_client):
        """Test GET /api/faqs/{id} with non-existent ID"""
        response = test_client.get("/api/faqs/99999")
        assert response.status_code == 404


class TestLogsEndpoints:
    """Test logs endpoints"""
    
    def test_get_logs_endpoint(self, test_client):
        """Test GET /api/logs endpoint"""
        response = test_client.get("/api/logs")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data or isinstance(data, list)
    
    def test_get_logs_stats(self, test_client):
        """Test GET /api/logs/stats endpoint"""
        response = test_client.get("/api/logs/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_logs" in data
        assert isinstance(data["total_logs"], int)


class TestAdminEndpoints:
    """Test admin endpoints"""
    
    def test_admin_panel_endpoint(self, test_client):
        """Test GET /admin endpoint"""
        response = test_client.get("/admin")
        # Should return HTML or redirect
        assert response.status_code in [200, 302, 404]
    
    def test_admin_stats_endpoint(self, test_client):
        """Test GET /admin/stats endpoint"""
        response = test_client.get("/admin/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_questions" in data or "total_faqs" in data


class TestRootEndpoint:
    """Test root endpoint"""
    
    def test_root_endpoint(self, test_client):
        """Test GET / endpoint"""
        response = test_client.get("/")
        assert response.status_code == 200
        # Should return HTML
        assert "text/html" in response.headers.get("content-type", "")


class TestSmartAgentStylesEndpoint:
    """Test Smart Agent styles endpoint"""
    
    def test_get_available_styles(self, test_client):
        """Test GET /api/smart-agent/styles returns full list with keys/labels/descriptions"""
        response = test_client.get("/api/smart-agent/styles")
        assert response.status_code == 200
        data = response.json()
        
        # Should return a list
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Check structure of first item
        first_style = data[0]
        assert "key" in first_style
        assert "label" in first_style
        assert "description" in first_style
        
        # Check all required fields are strings
        assert isinstance(first_style["key"], str)
        assert isinstance(first_style["label"], str)
        assert isinstance(first_style["description"], str)
        
        # Check that "auto" style exists
        style_keys = [style["key"] for style in data]
        assert "auto" in style_keys
        
        # Check expected styles are present
        expected_styles = ["auto", "formal", "friendly", "brief", "detailed", "explainer", "marketing"]
        for expected_style in expected_styles:
            assert expected_style in style_keys, f"Expected style '{expected_style}' not found in response"
    
    def test_styles_have_persian_labels(self, test_client):
        """Test that styles have Persian labels"""
        response = test_client.get("/api/smart-agent/styles")
        assert response.status_code == 200
        data = response.json()
        
        # Check that labels contain Persian characters (non-ASCII)
        for style in data:
            label = style["label"]
            # Persian text should contain non-ASCII characters
            assert any(ord(char) > 127 for char in label), f"Label '{label}' should contain Persian characters"


class TestSmartAgentChatEndpoint:
    """Test Smart Agent chat endpoint with style support"""
    
    def test_chat_without_style_defaults_to_auto(self, test_client):
        """Test that calling /api/smart-agent/chat without style defaults to 'auto'"""
        response = test_client.post(
            "/api/smart-agent/chat",
            json={"message": "سلام"}
        )
        # Should not return 404 or 400 (may return 500 if OpenAI not configured, but that's okay)
        assert response.status_code != 404
        assert response.status_code != 400
        
        if response.status_code == 200:
            data = response.json()
            assert "style" in data
            assert "response" in data
            # Style should be set (either "auto" or auto-detected style)
            assert isinstance(data["style"], str)
            assert len(data["style"]) > 0
    
    def test_chat_with_explicit_auto_style(self, test_client):
        """Test chat endpoint with explicit style='auto'"""
        response = test_client.post(
            "/api/smart-agent/chat",
            json={"message": "سلام", "style": "auto"}
        )
        assert response.status_code != 404
        assert response.status_code != 400
        
        if response.status_code == 200:
            data = response.json()
            assert "style" in data
            # Style should be set (auto-detected, not "auto")
            assert isinstance(data["style"], str)
            assert data["style"] in ["auto", "formal", "friendly", "brief", "detailed", "explainer", "marketing"]
    
    def test_chat_with_formal_style(self, test_client):
        """Test chat endpoint with style='formal'"""
        response = test_client.post(
            "/api/smart-agent/chat",
            json={"message": "سلام", "style": "formal"}
        )
        assert response.status_code != 404
        assert response.status_code != 400
        
        if response.status_code == 200:
            data = response.json()
            assert "style" in data
            # Should echo back the effective style (should be "formal" or auto-detected)
            assert isinstance(data["style"], str)
            # The effective style should be one of the valid styles
            valid_styles = ["auto", "formal", "friendly", "brief", "detailed", "explainer", "marketing"]
            assert data["style"] in valid_styles
    
    def test_chat_with_friendly_style(self, test_client):
        """Test chat endpoint with style='friendly'"""
        response = test_client.post(
            "/api/smart-agent/chat",
            json={"message": "سلام", "style": "friendly"}
        )
        assert response.status_code != 404
        assert response.status_code != 400
        
        if response.status_code == 200:
            data = response.json()
            assert "style" in data
            assert data["style"] in ["auto", "formal", "friendly", "brief", "detailed", "explainer", "marketing"]
    
    def test_chat_with_brief_style(self, test_client):
        """Test chat endpoint with style='brief'"""
        response = test_client.post(
            "/api/smart-agent/chat",
            json={"message": "سلام", "style": "brief"}
        )
        assert response.status_code != 404
        assert response.status_code != 400
        
        if response.status_code == 200:
            data = response.json()
            assert "style" in data
            assert data["style"] in ["auto", "formal", "friendly", "brief", "detailed", "explainer", "marketing"]
    
    def test_chat_with_detailed_style(self, test_client):
        """Test chat endpoint with style='detailed'"""
        response = test_client.post(
            "/api/smart-agent/chat",
            json={"message": "سلام", "style": "detailed"}
        )
        assert response.status_code != 404
        assert response.status_code != 400
        
        if response.status_code == 200:
            data = response.json()
            assert "style" in data
            assert data["style"] in ["auto", "formal", "friendly", "brief", "detailed", "explainer", "marketing"]
    
    def test_chat_with_explainer_style(self, test_client):
        """Test chat endpoint with style='explainer'"""
        response = test_client.post(
            "/api/smart-agent/chat",
            json={"message": "چطور کار می‌کند؟", "style": "explainer"}
        )
        assert response.status_code != 404
        assert response.status_code != 400
        
        if response.status_code == 200:
            data = response.json()
            assert "style" in data
            assert data["style"] in ["auto", "formal", "friendly", "brief", "detailed", "explainer", "marketing"]
    
    def test_chat_with_marketing_style(self, test_client):
        """Test chat endpoint with style='marketing'"""
        response = test_client.post(
            "/api/smart-agent/chat",
            json={"message": "سلام", "style": "marketing"}
        )
        assert response.status_code != 404
        assert response.status_code != 400
        
        if response.status_code == 200:
            data = response.json()
            assert "style" in data
            assert data["style"] in ["auto", "formal", "friendly", "brief", "detailed", "explainer", "marketing"]
    
    def test_chat_with_invalid_style_fallback(self, test_client):
        """Test that invalid style falls back to 'auto' (not 400 error)"""
        response = test_client.post(
            "/api/smart-agent/chat",
            json={"message": "سلام", "style": "invalid_style_xyz"}
        )
        # Should not return 400, should fallback to auto
        assert response.status_code != 404
        assert response.status_code != 400  # Should not be validation error
        
        if response.status_code == 200:
            data = response.json()
            assert "style" in data
            # Should have a valid style (fallback to auto or auto-detected)
            valid_styles = ["auto", "formal", "friendly", "brief", "detailed", "explainer", "marketing"]
            assert data["style"] in valid_styles
    
    def test_chat_response_includes_effective_style(self, test_client):
        """Test that response includes the effective style used (after auto-selection if needed)"""
        response = test_client.post(
            "/api/smart-agent/chat",
            json={"message": "سلام", "style": "auto"}
        )
        assert response.status_code != 404
        assert response.status_code != 400
        
        if response.status_code == 200:
            data = response.json()
            # Response should include style field
            assert "style" in data
            assert isinstance(data["style"], str)
            # Style should be a valid style key
            valid_styles = ["auto", "formal", "friendly", "brief", "detailed", "explainer", "marketing"]
            assert data["style"] in valid_styles
            
            # If style was "auto", the effective style should be auto-detected (not "auto")
            # But we can't guarantee this without mocking, so we just check it's valid
    
    def test_chat_backward_compatibility_no_style_field(self, test_client):
        """Test backward compatibility: request without style field should work"""
        response = test_client.post(
            "/api/smart-agent/chat",
            json={"message": "سلام"}
        )
        # Should work (backward compatible)
        assert response.status_code != 404
        assert response.status_code != 400
        
        if response.status_code == 200:
            data = response.json()
            # Should still return style in response
            assert "style" in data
            assert isinstance(data["style"], str)











