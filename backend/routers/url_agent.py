from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Any, Optional
from services.url_agent import get_url_agent
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response models
class AddWebsiteRequest(BaseModel):
    url: str
    max_pages: int = 50

class AddWebsiteResponse(BaseModel):
    success: bool
    message: str
    pages_scraped: Optional[int] = None
    summary: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class SearchRequest(BaseModel):
    query: str
    include_faq: bool = True
    include_web: bool = True
    website_filter: Optional[str] = None
    top_k: Optional[int] = None

class AnswerRequest(BaseModel):
    question: str
    context_preference: str = "both"  # "faq", "web", or "both"
    website_filter: Optional[str] = None

class WebsiteInfo(BaseModel):
    url: str
    total_pages: int
    total_words: int
    added_at: float
    domain: str

@router.post("/add-website", response_model=AddWebsiteResponse)
async def add_website(request: AddWebsiteRequest, background_tasks: BackgroundTasks):
    """Add a website to the agent's knowledge base"""
    try:
        url_agent = get_url_agent()
        
        # Validate URL
        if not request.url.startswith(('http://', 'https://')):
            request.url = 'https://' + request.url
        
        # Add website (this is a long-running operation)
        result = await url_agent.add_website(
            url=request.url,
            max_pages=request.max_pages
        )
        
        return AddWebsiteResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in add_website endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search")
async def search_dual_database(request: SearchRequest):
    """Search both FAQ database and web content"""
    try:
        url_agent = get_url_agent()
        
        results = await url_agent.search_dual_database(
            query=request.query,
            include_faq=request.include_faq,
            include_web=request.include_web,
            website_filter=request.website_filter,
            top_k=request.top_k
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/answer")
async def answer_question(request: AnswerRequest):
    """Answer a question using both databases"""
    try:
        url_agent = get_url_agent()
        
        result = await url_agent.answer_question(
            question=request.question,
            context_preference=request.context_preference,
            website_filter=request.website_filter
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in answer endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/websites", response_model=List[WebsiteInfo])
async def list_websites():
    """List all websites in the knowledge base"""
    try:
        url_agent = get_url_agent()
        websites = url_agent.list_websites()
        
        return [WebsiteInfo(**website) for website in websites]
        
    except Exception as e:
        logger.error(f"Error in list_websites endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/websites/{website_url:path}")
async def get_website_info(website_url: str):
    """Get information about a specific website"""
    try:
        url_agent = get_url_agent()
        info = url_agent.get_website_info(website_url)
        
        if not info:
            raise HTTPException(status_code=404, detail="Website not found")
        
        return info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_website_info endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/websites/{website_url:path}")
async def remove_website(website_url: str):
    """Remove a website from the knowledge base"""
    try:
        url_agent = get_url_agent()
        success = url_agent.remove_website(website_url)
        
        if not success:
            raise HTTPException(status_code=404, detail="Website not found or could not be removed")
        
        return {"success": True, "message": f"Website {website_url} removed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in remove_website endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_stats():
    """Get statistics about the knowledge base"""
    try:
        url_agent = get_url_agent()
        stats = url_agent.get_stats()
        
        return stats
        
    except Exception as e:
        logger.error(f"Error in get_stats endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat-with-url")
async def chat_with_url_support(request: AnswerRequest):
    """
    Enhanced chat endpoint that uses both FAQ database and web content
    This is the main endpoint for the URL agent functionality
    """
    try:
        url_agent = get_url_agent()
        
        # Use the answer_question method which provides comprehensive responses
        result = await url_agent.answer_question(
            question=request.question,
            context_preference=request.context_preference,
            website_filter=request.website_filter
        )
        
        return {
            "answer": result["answer"],
            "sources": result.get("sources", []),
            "context_used": result.get("context_used", {}),
            "search_metadata": result.get("search_metadata", {}),
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error in chat_with_url_support endpoint: {e}")
        return {
            "answer": f"متأسفانه در پاسخ به سؤال شما خطایی رخ داد. لطفاً دوباره تلاش کنید.",
            "sources": [],
            "error": str(e),
            "success": False
        }
