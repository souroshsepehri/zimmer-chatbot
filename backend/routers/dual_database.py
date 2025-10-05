"""
Dual Database API endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from services.dual_database_agent import get_dual_database_agent
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response models
class DualSearchRequest(BaseModel):
    query: str
    include_primary: bool = True
    include_secondary: bool = True
    website_filter: Optional[str] = None

class DualAnswerRequest(BaseModel):
    question: str
    use_primary_only: bool = False
    use_secondary_only: bool = False
    website_filter: Optional[str] = None

class AddWebsiteRequest(BaseModel):
    url: str
    max_pages: int = 30

@router.post("/dual-search")
async def search_dual_database(request: DualSearchRequest):
    """Search both primary FAQ database and secondary web database"""
    try:
        agent = get_dual_database_agent()
        
        results = await agent.search_dual_database(
            query=request.query,
            include_primary=request.include_primary,
            include_secondary=request.include_secondary,
            website_filter=request.website_filter
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Error in dual search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/dual-answer")
async def answer_with_dual_database(request: DualAnswerRequest):
    """Get answer using both databases"""
    try:
        agent = get_dual_database_agent()
        
        result = await agent.answer_question(
            question=request.question,
            use_primary_only=request.use_primary_only,
            use_secondary_only=request.use_secondary_only,
            website_filter=request.website_filter
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in dual answer: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add-website")
async def add_website_to_secondary(request: AddWebsiteRequest):
    """Add a website to the secondary database"""
    try:
        agent = get_dual_database_agent()
        
        result = await agent.add_website(
            url=request.url,
            max_pages=request.max_pages
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error adding website: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/primary-stats")
async def get_primary_database_stats():
    """Get statistics for primary FAQ database"""
    try:
        agent = get_dual_database_agent()
        stats = agent.get_primary_database_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting primary stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/secondary-stats")
async def get_secondary_database_stats():
    """Get statistics for secondary web database"""
    try:
        agent = get_dual_database_agent()
        stats = agent.get_secondary_database_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting secondary stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/combined-stats")
async def get_combined_stats():
    """Get combined statistics for both databases"""
    try:
        agent = get_dual_database_agent()
        stats = agent.get_combined_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting combined stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/websites")
async def list_websites():
    """List all websites in secondary database"""
    try:
        agent = get_dual_database_agent()
        websites = agent.list_websites()
        return {"websites": websites}
        
    except Exception as e:
        logger.error(f"Error listing websites: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/websites/{website_url:path}")
async def remove_website(website_url: str):
    """Remove a website from secondary database"""
    try:
        agent = get_dual_database_agent()
        success = agent.remove_website(website_url)
        
        if success:
            return {"success": True, "message": f"Website {website_url} removed successfully"}
        else:
            raise HTTPException(status_code=404, detail="Website not found or could not be removed")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing website: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-dual-system")
async def test_dual_system():
    """Test the dual database system"""
    try:
        agent = get_dual_database_agent()
        
        # Test primary database
        primary_test = agent.search_primary_database("تست")
        primary_working = primary_test['success']
        
        # Test secondary database
        secondary_test = await agent.search_secondary_database("تست")
        secondary_working = secondary_test['success']
        
        # Test combined search
        combined_test = await agent.search_dual_database("تست")
        
        return {
            "status": "success",
            "primary_database": {
                "working": primary_working,
                "test_result": primary_test
            },
            "secondary_database": {
                "working": secondary_working,
                "test_result": secondary_test
            },
            "combined_system": {
                "working": True,
                "sources_used": combined_test.get('sources_used', [])
            },
            "message": "Dual database system test completed"
        }
        
    except Exception as e:
        logger.error(f"Error testing dual system: {e}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Dual database system test failed"
        }

@router.post("/bulk-add-websites")
async def bulk_add_websites(websites: List[str]):
    """Add multiple websites at once"""
    try:
        agent = get_dual_database_agent()
        results = []
        
        for url in websites:
            result = await agent.add_website(url, max_pages=30)
            results.append({
                "url": url,
                "success": result['success'],
                "message": result['message'],
                "pages_scraped": result.get('pages_scraped', 0)
            })
        
        success_count = sum(1 for r in results if r['success'])
        
        return {
            "status": "completed",
            "total_websites": len(websites),
            "successful": success_count,
            "failed": len(websites) - success_count,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error in bulk add websites: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/website-details/{website_url:path}")
async def get_website_details(website_url: str):
    """Get detailed information about a specific website"""
    try:
        agent = get_dual_database_agent()
        info = agent.get_website_info(website_url)
        
        if not info:
            raise HTTPException(status_code=404, detail="Website not found")
        
        # Get additional stats
        stats = agent.get_secondary_database_stats()
        
        return {
            "website_info": info,
            "system_stats": stats,
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting website details: {e}")
        raise HTTPException(status_code=500, detail=str(e))
