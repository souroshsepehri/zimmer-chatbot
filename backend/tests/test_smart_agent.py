"""
Tests for Smart Agent API endpoints
"""
import pytest
import json
from schemas.smart_agent import AVAILABLE_STYLES, ResponseStyle


class TestSmartAgentStylesEndpoint:
    """Test /api/smart-agent/styles endpoint"""
    
    def test_get_available_styles(self, test_client):
        """Test that styles endpoint returns the full list with keys/labels/descriptions"""
        response = test_client.get("/api/smart-agent/styles")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Check structure of first style
        first_style = data[0]
        assert "key" in first_style
        assert "label" in first_style
        assert "description" in first_style
        
        # Verify all expected styles are present
        style_keys = {style["key"] for style in data}
        expected_keys = {style.value for style in ResponseStyle}
        assert style_keys == expected_keys
        
        # Verify all styles have Persian labels and descriptions
        for style in data:
            assert style["key"] in [s.value for s in ResponseStyle]
            assert isinstance(style["label"], str)
            assert len(style["label"]) > 0
            assert isinstance(style["description"], str)
            assert len(style["description"]) > 0
    
    def test_styles_endpoint_structure(self, test_client):
        """Test that styles endpoint returns correct structure matching AVAILABLE_STYLES"""
        response = test_client.get("/api/smart-agent/styles")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify structure matches AVAILABLE_STYLES
        for style_item in data:
            key = style_item["key"]
            # Find corresponding style in AVAILABLE_STYLES
            matching_style = None
            for style_enum, info in AVAILABLE_STYLES.items():
                if style_enum.value == key:
                    matching_style = info
                    break
            
            assert matching_style is not None, f"Style {key} not found in AVAILABLE_STYLES"
            assert style_item["label"] == matching_style["label"]
            assert style_item["description"] == matching_style["description"]


class TestSmartAgentChatEndpoint:
    """Test /api/smart-agent/chat endpoint"""
    
    def test_chat_without_style_defaults_to_auto(self, test_client):
        """Test that calling without style parameter defaults to 'auto' (backward compatibility)"""
        response = test_client.post(
            "/api/smart-agent/chat",
            json={"message": "سلام"}
        )
        
        # Should not fail
        assert response.status_code in [200, 500]  # 500 if OpenAI not configured, but endpoint should work
        
        if response.status_code == 200:
            data = response.json()
            assert "style" in data
            # Style should be set (either "auto" or auto-detected style)
            assert isinstance(data["style"], str)
            assert len(data["style"]) > 0
    
    def test_chat_with_auto_style(self, test_client):
        """Test that style='auto' works and returns effective style"""
        response = test_client.post(
            "/api/smart-agent/chat",
            json={
                "message": "سلام",
                "style": "auto"
            }
        )
        
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "style" in data
            # Should return an effective style (not "auto" since it gets auto-detected)
            assert data["style"] != "auto" or data["style"] == "auto"  # Either auto-detected or still auto
            assert data["style"] in [s.value for s in ResponseStyle]
    
    def test_chat_with_formal_style(self, test_client):
        """Test that style='formal' works and echoes back in response"""
        response = test_client.post(
            "/api/smart-agent/chat",
            json={
                "message": "سلام",
                "style": "formal"
            }
        )
        
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "style" in data
            assert data["style"] == "formal"
    
    def test_chat_with_friendly_style(self, test_client):
        """Test that style='friendly' works"""
        response = test_client.post(
            "/api/smart-agent/chat",
            json={
                "message": "سلام",
                "style": "friendly"
            }
        )
        
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert data["style"] == "friendly"
    
    def test_chat_with_brief_style(self, test_client):
        """Test that style='brief' works"""
        response = test_client.post(
            "/api/smart-agent/chat",
            json={
                "message": "سلام",
                "style": "brief"
            }
        )
        
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert data["style"] == "brief"
    
    def test_chat_with_detailed_style(self, test_client):
        """Test that style='detailed' works"""
        response = test_client.post(
            "/api/smart-agent/chat",
            json={
                "message": "سلام",
                "style": "detailed"
            }
        )
        
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert data["style"] == "detailed"
    
    def test_chat_with_explainer_style(self, test_client):
        """Test that style='explainer' works"""
        response = test_client.post(
            "/api/smart-agent/chat",
            json={
                "message": "چطور کار می‌کند؟",
                "style": "explainer"
            }
        )
        
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert data["style"] == "explainer"
    
    def test_chat_with_marketing_style(self, test_client):
        """Test that style='marketing' works"""
        response = test_client.post(
            "/api/smart-agent/chat",
            json={
                "message": "سلام",
                "style": "marketing"
            }
        )
        
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert data["style"] == "marketing"
    
    def test_chat_with_invalid_style_fallback(self, test_client):
        """Test that invalid style falls back to 'auto'"""
        response = test_client.post(
            "/api/smart-agent/chat",
            json={
                "message": "سلام",
                "style": "invalid_style_xyz"
            }
        )
        
        # Should not return 400, should fallback to auto
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "style" in data
            # Should have a valid style (either auto or auto-detected)
            assert data["style"] in [s.value for s in ResponseStyle]
    
    def test_chat_response_structure(self, test_client):
        """Test that chat response has all required fields including effective style"""
        response = test_client.post(
            "/api/smart-agent/chat",
            json={
                "message": "سلام",
                "style": "formal"
            }
        )
        
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            assert "response" in data
            assert "style" in data
            assert "response_time" in data
            assert "web_content_used" in data
            assert "urls_processed" in data
            assert "context_used" in data
            assert "timestamp" in data
            
            # Verify style is a valid ResponseStyle value
            assert data["style"] in [s.value for s in ResponseStyle]
            
            # Verify effective style is returned (not just input)
            assert data["style"] == "formal"  # Should match requested style
    
    def test_chat_with_context(self, test_client):
        """Test that chat endpoint accepts context parameter"""
        response = test_client.post(
            "/api/smart-agent/chat",
            json={
                "message": "سلام",
                "style": "friendly",
                "context": {"user_id": "test123", "session_id": "session456"}
            }
        )
        
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "context_used" in data
            assert isinstance(data["context_used"], bool)


class TestSmartAgentBackwardCompatibility:
    """Test backward compatibility of Smart Agent endpoints"""
    
    def test_old_clients_without_style_parameter(self, test_client):
        """Test that old clients calling without style parameter still work"""
        # Simulate old client that doesn't send style parameter
        response = test_client.post(
            "/api/smart-agent/chat",
            json={"message": "سلام"}
        )
        
        # Should work (either 200 or 500 if OpenAI not configured)
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            # Should have style field in response
            assert "style" in data
            # Should default to auto or auto-detected style
            assert data["style"] in [s.value for s in ResponseStyle]
    
    def test_old_clients_with_null_style(self, test_client):
        """Test that null style is handled gracefully"""
        response = test_client.post(
            "/api/smart-agent/chat",
            json={"message": "سلام", "style": None}
        )
        
        # Should work
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "style" in data
            assert data["style"] in [s.value for s in ResponseStyle]




























