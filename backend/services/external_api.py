"""
External API Service for connecting to remote chatbot APIs
"""

import asyncio
import aiohttp
import logging
from typing import Dict, Any, Optional
from core.config import settings

logger = logging.getLogger(__name__)

class ExternalAPIService:
    """Service for connecting to external chatbot APIs"""
    
    def __init__(self):
        self.base_url = settings.external_api_url
        self.port = settings.external_api_port
        self.timeout = settings.external_api_timeout
        self.enabled = settings.external_api_enabled
        
        # Construct full API URL
        if self.port and self.port != 80 and self.port != 443:
            self.api_url = f"{self.base_url}:{self.port}"
        else:
            self.api_url = self.base_url
            
        logger.info(f"External API Service initialized: {self.api_url}")
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to external API"""
        if not self.enabled:
            return {
                "status": "disabled",
                "message": "External API is disabled"
            }
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                # Try health endpoint first
                health_url = f"{self.api_url}/health"
                async with session.get(health_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "status": "connected",
                            "url": self.api_url,
                            "response": data,
                            "message": "Successfully connected to external API"
                        }
                    else:
                        return {
                            "status": "error",
                            "url": self.api_url,
                            "error": f"HTTP {response.status}",
                            "message": "External API returned error status"
                        }
        except asyncio.TimeoutError:
            return {
                "status": "timeout",
                "url": self.api_url,
                "error": "Connection timeout",
                "message": f"External API did not respond within {self.timeout} seconds"
            }
        except aiohttp.ClientError as e:
            return {
                "status": "error",
                "url": self.api_url,
                "error": str(e),
                "message": "Failed to connect to external API"
            }
        except Exception as e:
            return {
                "status": "error",
                "url": self.api_url,
                "error": str(e),
                "message": "Unexpected error connecting to external API"
            }
    
    async def send_message(self, message: str, endpoint: str = "/api/chat") -> Dict[str, Any]:
        """Send a message to the external API"""
        if not self.enabled:
            return {
                "success": False,
                "error": "External API is disabled",
                "message": "External API integration is not enabled"
            }
        
        try:
            url = f"{self.api_url}{endpoint}"
            payload = {
                "message": message,
                "debug": False
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "data": data,
                            "source": "external_api",
                            "url": url
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}",
                            "details": error_text,
                            "url": url
                        }
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "timeout",
                "message": f"External API did not respond within {self.timeout} seconds",
                "url": f"{self.api_url}{endpoint}"
            }
        except aiohttp.ClientError as e:
            return {
                "success": False,
                "error": "connection_error",
                "details": str(e),
                "url": f"{self.api_url}{endpoint}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": "unexpected_error",
                "details": str(e),
                "url": f"{self.api_url}{endpoint}"
            }
    
    async def get_available_endpoints(self) -> Dict[str, Any]:
        """Get available endpoints from external API"""
        if not self.enabled:
            return {
                "status": "disabled",
                "endpoints": []
            }
        
        # Common endpoints to test
        endpoints_to_test = [
            "/health",
            "/api/chat",
            "/api/simple-chat",
            "/api/smart-chat",
            "/api/faqs",
            "/docs",
            "/openapi.json"
        ]
        
        available_endpoints = []
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                for endpoint in endpoints_to_test:
                    try:
                        url = f"{self.api_url}{endpoint}"
                        async with session.get(url) as response:
                            if response.status in [200, 404]:  # 404 is also valid (endpoint exists but method not allowed)
                                available_endpoints.append({
                                    "endpoint": endpoint,
                                    "status": response.status,
                                    "url": url
                                })
                    except:
                        continue  # Skip failed endpoints
                        
        except Exception as e:
            logger.error(f"Error testing endpoints: {e}")
        
        return {
            "status": "success" if available_endpoints else "no_endpoints",
            "endpoints": available_endpoints,
            "base_url": self.api_url
        }

# Global instance
_external_api_service = None

def get_external_api_service() -> ExternalAPIService:
    """Get external API service instance"""
    global _external_api_service
    if _external_api_service is None:
        _external_api_service = ExternalAPIService()
    return _external_api_service
