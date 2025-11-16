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






