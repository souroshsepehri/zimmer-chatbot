"""
API Integration Router
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

from services.api_integration import api_integration
from core.db import get_db
from sqlalchemy.orm import Session

router = APIRouter()

class APIRequest(BaseModel):
    query: Optional[str] = None
    params: Optional[Dict[str, Any]] = None

class APIResponse(BaseModel):
    success: bool
    data: Any
    error: Optional[str] = None
    status_code: int = 200
    response_time: float = 0.0
    timestamp: str = ""
    source: str = ""

@router.get("/api-integration/available")
async def get_available_apis():
    """Get list of available APIs"""
    try:
        apis = api_integration.get_available_apis()
        return {
            "available_apis": apis,
            "total_apis": len(apis),
            "cache_stats": api_integration.get_cache_stats()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting available APIs: {str(e)}")

@router.post("/api-integration/news")
async def get_news(
    query: Optional[str] = Query(None, description="Search query for news"),
    country: str = Query("us", description="Country code"),
    category: Optional[str] = Query(None, description="News category"),
    db: Session = Depends(get_db)
):
    """Get news from NewsAPI"""
    try:
        response = await api_integration.get_news(query, country, category)
        return APIResponse(**response.__dict__)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"News API error: {str(e)}")

@router.post("/api-integration/weather")
async def get_weather(
    city: str = Query(..., description="City name"),
    country_code: Optional[str] = Query(None, description="Country code"),
    db: Session = Depends(get_db)
):
    """Get weather information"""
    try:
        response = await api_integration.get_weather(city, country_code)
        return APIResponse(**response.__dict__)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Weather API error: {str(e)}")

@router.post("/api-integration/translate")
async def translate_text(
    text: str = Query(..., description="Text to translate"),
    from_lang: str = Query("auto", description="Source language"),
    to_lang: str = Query("en", description="Target language"),
    db: Session = Depends(get_db)
):
    """Translate text"""
    try:
        response = await api_integration.translate_text(text, from_lang, to_lang)
        return APIResponse(**response.__dict__)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation error: {str(e)}")

@router.post("/api-integration/currency")
async def get_currency_rates(
    base_currency: str = Query("USD", description="Base currency"),
    db: Session = Depends(get_db)
):
    """Get currency exchange rates"""
    try:
        response = await api_integration.get_currency_rates(base_currency)
        return APIResponse(**response.__dict__)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Currency API error: {str(e)}")

@router.post("/api-integration/quote")
async def get_random_quote(
    tags: Optional[List[str]] = Query(None, description="Quote tags"),
    db: Session = Depends(get_db)
):
    """Get random quote"""
    try:
        response = await api_integration.get_random_quote(tags)
        return APIResponse(**response.__dict__)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quote API error: {str(e)}")

@router.post("/api-integration/joke")
async def get_random_joke(
    category: str = Query("general", description="Joke category"),
    db: Session = Depends(get_db)
):
    """Get random joke"""
    try:
        response = await api_integration.get_random_joke(category)
        return APIResponse(**response.__dict__)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Joke API error: {str(e)}")

@router.post("/api-integration/wikipedia")
async def search_wikipedia(
    query: str = Query(..., description="Search query"),
    language: str = Query("en", description="Wikipedia language"),
    db: Session = Depends(get_db)
):
    """Search Wikipedia"""
    try:
        response = await api_integration.search_wikipedia(query, language)
        return APIResponse(**response.__dict__)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Wikipedia API error: {str(e)}")

@router.post("/api-integration/github")
async def get_github_info(
    username: str = Query(..., description="GitHub username"),
    db: Session = Depends(get_db)
):
    """Get GitHub user information"""
    try:
        response = await api_integration.get_github_info(username)
        return APIResponse(**response.__dict__)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GitHub API error: {str(e)}")

@router.post("/api-integration/timezone")
async def get_timezone_info(
    timezone: str = Query(..., description="Timezone identifier"),
    db: Session = Depends(get_db)
):
    """Get timezone information"""
    try:
        response = await api_integration.get_timezone_info(timezone)
        return APIResponse(**response.__dict__)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Timezone API error: {str(e)}")

@router.post("/api-integration/set-key")
async def set_api_key(
    api_name: str = Query(..., description="API name"),
    api_key: str = Query(..., description="API key"),
    db: Session = Depends(get_db)
):
    """Set API key for a service"""
    try:
        api_integration.set_api_key(api_name, api_key)
        return {"message": f"API key set for {api_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting API key: {str(e)}")

@router.post("/api-integration/clear-cache")
async def clear_api_cache(db: Session = Depends(get_db)):
    """Clear API response cache"""
    try:
        api_integration.clear_cache()
        return {"message": "API cache cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing cache: {str(e)}")

@router.get("/api-integration/cache-stats")
async def get_cache_stats(db: Session = Depends(get_db)):
    """Get API cache statistics"""
    try:
        stats = api_integration.get_cache_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting cache stats: {str(e)}")
