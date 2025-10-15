"""
API Integration Service for Smart Agent
Provides integration with various external APIs and services
"""

import asyncio
import aiohttp
import requests
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)

@dataclass
class APIResponse:
    """Standardized API response format"""
    success: bool
    data: Any
    error: Optional[str] = None
    status_code: int = 200
    response_time: float = 0.0
    timestamp: str = ""
    source: str = ""

class APIIntegration:
    """
    Advanced API integration service for various external APIs
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Smart-Agent/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        # API configurations
        self.api_configs = {
            'news': {
                'base_url': 'https://newsapi.org/v2',
                'api_key': None,  # Set via environment variable
                'endpoints': {
                    'top_headlines': '/top-headlines',
                    'everything': '/everything',
                    'sources': '/sources'
                }
            },
            'weather': {
                'base_url': 'https://api.openweathermap.org/data/2.5',
                'api_key': None,  # Set via environment variable
                'endpoints': {
                    'current': '/weather',
                    'forecast': '/forecast',
                    'onecall': '/onecall'
                }
            },
            'translate': {
                'base_url': 'https://api.mymemory.translated.net',
                'endpoints': {
                    'translate': '/get'
                }
            },
            'currency': {
                'base_url': 'https://api.exchangerate-api.com/v4',
                'endpoints': {
                    'latest': '/latest',
                    'historical': '/history'
                }
            },
            'quotes': {
                'base_url': 'https://api.quotable.io',
                'endpoints': {
                    'random': '/random',
                    'quotes': '/quotes',
                    'authors': '/authors'
                }
            },
            'jokes': {
                'base_url': 'https://official-joke-api.appspot.com',
                'endpoints': {
                    'random': '/random_joke',
                    'ten': '/random_ten',
                    'programming': '/jokes/programming/random'
                }
            }
        }
        
        # Cache for API responses
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def _get_cache_key(self, api_name: str, endpoint: str, params: Dict) -> str:
        """Generate cache key for API request"""
        return f"{api_name}:{endpoint}:{json.dumps(params, sort_keys=True)}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid"""
        if cache_key not in self.cache:
            return False
        
        cache_entry = self.cache[cache_key]
        cache_time = cache_entry.get('timestamp', 0)
        return time.time() - cache_time < self.cache_ttl
    
    def _get_cached_response(self, cache_key: str) -> Optional[APIResponse]:
        """Get cached API response"""
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['response']
        return None
    
    def _cache_response(self, cache_key: str, response: APIResponse):
        """Cache API response"""
        self.cache[cache_key] = {
            'response': response,
            'timestamp': time.time()
        }
    
    async def _make_request(self, url: str, params: Dict = None, headers: Dict = None) -> APIResponse:
        """Make HTTP request with error handling"""
        start_time = time.time()
        
        try:
            request_headers = self.session.headers.copy()
            if headers:
                request_headers.update(headers)
            
            response = self.session.get(url, params=params, headers=request_headers, timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    data = response.text
                
                return APIResponse(
                    success=True,
                    data=data,
                    status_code=response.status_code,
                    response_time=response_time,
                    timestamp=datetime.now().isoformat()
                )
            else:
                return APIResponse(
                    success=False,
                    data=None,
                    error=f"HTTP {response.status_code}: {response.text}",
                    status_code=response.status_code,
                    response_time=response_time,
                    timestamp=datetime.now().isoformat()
                )
                
        except Exception as e:
            response_time = time.time() - start_time
            return APIResponse(
                success=False,
                data=None,
                error=str(e),
                response_time=response_time,
                timestamp=datetime.now().isoformat()
            )
    
    async def get_news(self, query: str = None, country: str = 'us', category: str = None) -> APIResponse:
        """Get news from NewsAPI"""
        cache_key = self._get_cache_key('news', 'top_headlines', {
            'query': query, 'country': country, 'category': category
        })
        
        cached = self._get_cached_response(cache_key)
        if cached:
            return cached
        
        config = self.api_configs['news']
        api_key = config.get('api_key') or 'demo'  # Use demo key if no API key
        
        params = {
            'apiKey': api_key,
            'country': country
        }
        
        if query:
            params['q'] = query
        if category:
            params['category'] = category
        
        url = config['base_url'] + config['endpoints']['top_headlines']
        response = await self._make_request(url, params)
        response.source = 'newsapi'
        
        self._cache_response(cache_key, response)
        return response
    
    async def get_weather(self, city: str, country_code: str = None) -> APIResponse:
        """Get weather information"""
        cache_key = self._get_cache_key('weather', 'current', {'city': city, 'country': country_code})
        
        cached = self._get_cached_response(cache_key)
        if cached:
            return cached
        
        config = self.api_configs['weather']
        api_key = config.get('api_key') or 'demo'
        
        location = f"{city},{country_code}" if country_code else city
        params = {
            'q': location,
            'appid': api_key,
            'units': 'metric'
        }
        
        url = config['base_url'] + config['endpoints']['current']
        response = await self._make_request(url, params)
        response.source = 'openweathermap'
        
        self._cache_response(cache_key, response)
        return response
    
    async def translate_text(self, text: str, from_lang: str = 'auto', to_lang: str = 'en') -> APIResponse:
        """Translate text using MyMemory API"""
        cache_key = self._get_cache_key('translate', 'translate', {
            'text': text, 'from': from_lang, 'to': to_lang
        })
        
        cached = self._get_cached_response(cache_key)
        if cached:
            return cached
        
        config = self.api_configs['translate']
        params = {
            'q': text,
            'langpair': f"{from_lang}|{to_lang}"
        }
        
        url = config['base_url'] + config['endpoints']['translate']
        response = await self._make_request(url, params)
        response.source = 'mymemory'
        
        self._cache_response(cache_key, response)
        return response
    
    async def get_currency_rates(self, base_currency: str = 'USD') -> APIResponse:
        """Get currency exchange rates"""
        cache_key = self._get_cache_key('currency', 'latest', {'base': base_currency})
        
        cached = self._get_cached_response(cache_key)
        if cached:
            return cached
        
        config = self.api_configs['currency']
        url = f"{config['base_url']}{config['endpoints']['latest']}/{base_currency}"
        
        response = await self._make_request(url)
        response.source = 'exchangerate'
        
        self._cache_response(cache_key, response)
        return response
    
    async def get_random_quote(self, tags: List[str] = None) -> APIResponse:
        """Get random quote"""
        cache_key = self._get_cache_key('quotes', 'random', {'tags': tags})
        
        cached = self._get_cached_response(cache_key)
        if cached:
            return cached
        
        config = self.api_configs['quotes']
        params = {}
        if tags:
            params['tags'] = ','.join(tags)
        
        url = config['base_url'] + config['endpoints']['random']
        response = await self._make_request(url, params)
        response.source = 'quotable'
        
        self._cache_response(cache_key, response)
        return response
    
    async def get_random_joke(self, category: str = 'general') -> APIResponse:
        """Get random joke"""
        cache_key = self._get_cache_key('jokes', 'random', {'category': category})
        
        cached = self._get_cached_response(cache_key)
        if cached:
            return cached
        
        config = self.api_configs['jokes']
        
        if category == 'programming':
            endpoint = config['endpoints']['programming']
        else:
            endpoint = config['endpoints']['random']
        
        url = config['base_url'] + endpoint
        response = await self._make_request(url)
        response.source = 'jokeapi'
        
        self._cache_response(cache_key, response)
        return response
    
    async def search_wikipedia(self, query: str, language: str = 'en') -> APIResponse:
        """Search Wikipedia for information"""
        cache_key = self._get_cache_key('wikipedia', 'search', {'query': query, 'lang': language})
        
        cached = self._get_cached_response(cache_key)
        if cached:
            return cached
        
        # Wikipedia API
        params = {
            'action': 'query',
            'format': 'json',
            'list': 'search',
            'srsearch': query,
            'srlimit': 5
        }
        
        url = f"https://{language}.wikipedia.org/w/api.php"
        response = await self._make_request(url, params)
        response.source = 'wikipedia'
        
        self._cache_response(cache_key, response)
        return response
    
    async def get_github_info(self, username: str) -> APIResponse:
        """Get GitHub user information"""
        cache_key = self._get_cache_key('github', 'user', {'username': username})
        
        cached = self._get_cached_response(cache_key)
        if cached:
            return cached
        
        url = f"https://api.github.com/users/{username}"
        response = await self._make_request(url)
        response.source = 'github'
        
        self._cache_response(cache_key, response)
        return response
    
    async def get_timezone_info(self, timezone: str) -> APIResponse:
        """Get timezone information"""
        cache_key = self._get_cache_key('timezone', 'info', {'timezone': timezone})
        
        cached = self._get_cached_response(cache_key)
        if cached:
            return cached
        
        url = f"http://worldtimeapi.org/api/timezone/{timezone}"
        response = await self._make_request(url)
        response.source = 'worldtimeapi'
        
        self._cache_response(cache_key, response)
        return response
    
    def get_available_apis(self) -> Dict[str, List[str]]:
        """Get list of available APIs and their endpoints"""
        return {
            api_name: list(config['endpoints'].keys())
            for api_name, config in self.api_configs.items()
        }
    
    def set_api_key(self, api_name: str, api_key: str):
        """Set API key for a specific service"""
        if api_name in self.api_configs:
            self.api_configs[api_name]['api_key'] = api_key
            logger.info(f"API key set for {api_name}")
        else:
            logger.warning(f"Unknown API: {api_name}")
    
    def clear_cache(self):
        """Clear API response cache"""
        self.cache.clear()
        logger.info("API cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_entries = len(self.cache)
        valid_entries = sum(1 for key in self.cache if self._is_cache_valid(key))
        
        return {
            'total_entries': total_entries,
            'valid_entries': valid_entries,
            'expired_entries': total_entries - valid_entries,
            'cache_ttl': self.cache_ttl
        }

# Global API integration instance
api_integration = APIIntegration()
