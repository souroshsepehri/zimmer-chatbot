"""
External API Router for connecting to remote chatbot APIs
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.external_api import get_external_api_service
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class ExternalChatRequest(BaseModel):
    message: str
    endpoint: Optional[str] = "/api/chat"
    debug: Optional[bool] = False

class ExternalChatResponse(BaseModel):
    success: bool
    answer: Optional[str] = None
    source: str = "external_api"
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    url: Optional[str] = None

@router.get("/external-api/status")
async def get_external_api_status():
    """Get the status of external API connection"""
    try:
        service = get_external_api_service()
        result = await service.test_connection()
        return result
    except Exception as e:
        logger.error(f"Error checking external API status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/external-api/endpoints")
async def get_external_api_endpoints():
    """Get available endpoints from external API"""
    try:
        service = get_external_api_service()
        result = await service.get_available_endpoints()
        return result
    except Exception as e:
        logger.error(f"Error getting external API endpoints: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/external-api/chat", response_model=ExternalChatResponse)
async def external_api_chat(request: ExternalChatRequest):
    """Send a message to external API"""
    try:
        service = get_external_api_service()
        result = await service.send_message(
            message=request.message,
            endpoint=request.endpoint
        )
        
        if result["success"]:
            return ExternalChatResponse(
                success=True,
                answer=result["data"].get("answer", "No answer received"),
                source="external_api",
                details=result["data"],
                url=result["url"]
            )
        else:
            return ExternalChatResponse(
                success=False,
                error=result["error"],
                details=result,
                url=result.get("url")
            )
            
    except Exception as e:
        logger.error(f"Error in external API chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/external-api/test")
async def test_external_api_connection():
    """Test connection to external API with detailed diagnostics"""
    try:
        service = get_external_api_service()
        
        # Test basic connection
        connection_result = await service.test_connection()
        
        # Test available endpoints
        endpoints_result = await service.get_available_endpoints()
        
        # Test a simple message if connection is successful
        message_result = None
        if connection_result.get("status") == "connected":
            message_result = await service.send_message("سلام", "/api/chat")
        
        return {
            "connection": connection_result,
            "endpoints": endpoints_result,
            "message_test": message_result,
            "configuration": {
                "enabled": service.enabled,
                "base_url": service.base_url,
                "port": service.port,
                "timeout": service.timeout,
                "full_url": service.api_url
            }
        }
        
    except Exception as e:
        logger.error(f"Error testing external API: {e}")
        raise HTTPException(status_code=500, detail=str(e))
