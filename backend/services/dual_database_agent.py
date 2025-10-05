"""
Dual Database Agent - Combines reliable FAQ system with URL agent
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from services.simple_chatbot import get_simple_chatbot
from services.web_scraper import get_web_scraper, WebPage
from services.web_vectorstore import get_web_vectorstore
from core.config import settings
from datetime import datetime

logger = logging.getLogger(__name__)

class DualDatabaseAgent:
    """
    Agent that combines reliable FAQ database with website content
    """
    
    def __init__(self):
        self.simple_chatbot = get_simple_chatbot()
        self.web_scraper = get_web_scraper()
        self.web_vectorstore = get_web_vectorstore()
        
    async def add_website(self, url: str, max_pages: int = 30) -> Dict[str, Any]:
        """
        Add a website to the secondary database
        
        Args:
            url: The website URL to scrape
            max_pages: Maximum number of pages to scrape
            
        Returns:
            Dictionary with operation results
        """
        try:
            logger.info(f"Adding website to secondary database: {url}")
            
            # Check if website already exists
            existing_info = self.web_vectorstore.get_website_info(url)
            if existing_info:
                return {
                    'success': False,
                    'message': f'Website {url} already exists in secondary database',
                    'existing_info': existing_info
                }
            
            # Scrape the website
            self.web_scraper.max_pages = max_pages
            pages = self.web_scraper.scrape_website(url)
            
            if not pages:
                return {
                    'success': False,
                    'message': f'No content found on website: {url}',
                    'pages_scraped': 0
                }
            
            # Add to web vector store
            success = self.web_vectorstore.add_website_content(pages, url)
            
            if success:
                summary = self.web_scraper.get_page_summary(pages)
                return {
                    'success': True,
                    'message': f'Successfully added website to secondary database: {url}',
                    'pages_scraped': len(pages),
                    'summary': summary,
                    'added_at': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'message': f'Failed to add website content to secondary database: {url}',
                    'pages_scraped': len(pages)
                }
                
        except Exception as e:
            logger.error(f"Error adding website {url}: {str(e)}")
            return {
                'success': False,
                'message': f'Error adding website: {str(e)}',
                'error': str(e)
            }
    
    def search_primary_database(self, query: str) -> Dict[str, Any]:
        """
        Search the primary FAQ database (reliable system)
        
        Args:
            query: Search query
            
        Returns:
            Search results from FAQ database
        """
        try:
            # Use the reliable simple chatbot
            result = self.simple_chatbot.get_answer(query)
            
            return {
                'source': 'primary_faq',
                'success': result['success'],
                'answer': result['answer'],
                'faq_id': result.get('faq_id'),
                'question': result.get('question'),
                'category': result.get('category'),
                'score': result.get('score'),
                'all_matches': result.get('all_matches', [])
            }
            
        except Exception as e:
            logger.error(f"Error searching primary database: {e}")
            return {
                'source': 'primary_faq',
                'success': False,
                'answer': f'خطا در جستجوی پایگاه داده اصلی: {str(e)}',
                'error': str(e)
            }
    
    async def search_secondary_database(self, query: str, website_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Search the secondary web content database
        
        Args:
            query: Search query
            website_filter: Filter by specific website
            
        Returns:
            Search results from web content
        """
        try:
            web_results = self.web_vectorstore.semantic_search(
                query=query,
                top_k=3,
                website_filter=website_filter
            )
            
            if web_results:
                best_match = web_results[0]
                return {
                    'source': 'secondary_web',
                    'success': True,
                    'answer': best_match['content'],
                    'url': best_match['url'],
                    'title': best_match['title'],
                    'score': best_match['score'],
                    'all_matches': web_results
                }
            else:
                return {
                    'source': 'secondary_web',
                    'success': False,
                    'answer': 'هیچ محتوای مرتبطی در پایگاه داده ثانویه پیدا نشد.',
                    'all_matches': []
                }
                
        except Exception as e:
            logger.error(f"Error searching secondary database: {e}")
            return {
                'source': 'secondary_web',
                'success': False,
                'answer': f'خطا در جستجوی پایگاه داده ثانویه: {str(e)}',
                'error': str(e)
            }
    
    async def search_dual_database(
        self, 
        query: str, 
        include_primary: bool = True,
        include_secondary: bool = True,
        website_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search both databases and combine results
        
        Args:
            query: Search query
            include_primary: Whether to search primary FAQ database
            include_secondary: Whether to search secondary web database
            website_filter: Filter secondary results by website
            
        Returns:
            Combined search results
        """
        try:
            results = {
                'query': query,
                'primary_results': {},
                'secondary_results': {},
                'combined_answer': '',
                'sources_used': [],
                'search_metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'databases_searched': []
                }
            }
            
            # Search primary database (FAQ)
            if include_primary:
                primary_result = self.search_primary_database(query)
                results['primary_results'] = primary_result
                results['search_metadata']['databases_searched'].append('primary_faq')
                
                if primary_result['success']:
                    results['sources_used'].append('FAQ Database')
            
            # Search secondary database (Web content)
            if include_secondary:
                secondary_result = await self.search_secondary_database(query, website_filter)
                results['secondary_results'] = secondary_result
                results['search_metadata']['databases_searched'].append('secondary_web')
                
                if secondary_result['success']:
                    results['sources_used'].append('Website Content')
            
            # Combine answers intelligently
            combined_answer = self._combine_answers(
                primary_result if include_primary else None,
                secondary_result if include_secondary else None
            )
            
            results['combined_answer'] = combined_answer
            
            return results
            
        except Exception as e:
            logger.error(f"Error in dual database search: {e}")
            return {
                'query': query,
                'error': str(e),
                'primary_results': {},
                'secondary_results': {},
                'combined_answer': f'خطا در جستجوی پایگاه‌های داده: {str(e)}',
                'sources_used': []
            }
    
    def _combine_answers(self, primary_result: Optional[Dict], secondary_result: Optional[Dict]) -> str:
        """
        Intelligently combine answers from both databases
        
        Args:
            primary_result: Results from primary FAQ database
            secondary_result: Results from secondary web database
            
        Returns:
            Combined answer
        """
        try:
            # If only primary database has results
            if primary_result and primary_result['success'] and (not secondary_result or not secondary_result['success']):
                return primary_result['answer']
            
            # If only secondary database has results
            if secondary_result and secondary_result['success'] and (not primary_result or not primary_result['success']):
                return f"بر اساس محتوای وب‌سایت:\n\n{secondary_result['answer']}"
            
            # If both have results, combine them
            if primary_result and primary_result['success'] and secondary_result and secondary_result['success']:
                combined = f"بر اساس پایگاه داده FAQ:\n\n{primary_result['answer']}\n\n"
                combined += f"همچنین بر اساس محتوای وب‌سایت:\n\n{secondary_result['answer']}"
                return combined
            
            # If neither has good results, use primary fallback
            if primary_result:
                return primary_result['answer']
            
            # Final fallback
            return "متأسفانه پاسخ مناسبی برای این سؤال پیدا نکردم. لطفاً سؤال خود را به شکل دیگری مطرح کنید."
            
        except Exception as e:
            logger.error(f"Error combining answers: {e}")
            return "خطا در ترکیب پاسخ‌ها. لطفاً دوباره تلاش کنید."
    
    async def answer_question(
        self, 
        question: str, 
        use_primary_only: bool = False,
        use_secondary_only: bool = False,
        website_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Answer a question using both databases
        
        Args:
            question: The question to answer
            use_primary_only: Use only primary FAQ database
            use_secondary_only: Use only secondary web database
            website_filter: Filter secondary results by website
            
        Returns:
            Answer with context and sources
        """
        try:
            # Determine search strategy
            include_primary = not use_secondary_only
            include_secondary = not use_primary_only
            
            # Search both databases
            search_results = await self.search_dual_database(
                query=question,
                include_primary=include_primary,
                include_secondary=include_secondary,
                website_filter=website_filter
            )
            
            # Prepare response
            response = {
                'answer': search_results['combined_answer'],
                'sources_used': search_results['sources_used'],
                'primary_success': search_results['primary_results'].get('success', False),
                'secondary_success': search_results['secondary_results'].get('success', False),
                'search_metadata': search_results['search_metadata']
            }
            
            # Add detailed results for debugging
            if search_results['primary_results']:
                response['primary_details'] = {
                    'faq_id': search_results['primary_results'].get('faq_id'),
                    'question': search_results['primary_results'].get('question'),
                    'category': search_results['primary_results'].get('category'),
                    'score': search_results['primary_results'].get('score')
                }
            
            if search_results['secondary_results']:
                response['secondary_details'] = {
                    'url': search_results['secondary_results'].get('url'),
                    'title': search_results['secondary_results'].get('title'),
                    'score': search_results['secondary_results'].get('score')
                }
            
            return response
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return {
                'answer': f'خطا در پاسخ به سؤال: {str(e)}',
                'sources_used': [],
                'error': str(e)
            }
    
    def get_primary_database_stats(self) -> Dict[str, Any]:
        """Get statistics for primary FAQ database"""
        return self.simple_chatbot.get_stats()
    
    def get_secondary_database_stats(self) -> Dict[str, Any]:
        """Get statistics for secondary web database"""
        return self.web_vectorstore.get_stats()
    
    def get_combined_stats(self) -> Dict[str, Any]:
        """Get combined statistics for both databases"""
        try:
            primary_stats = self.get_primary_database_stats()
            secondary_stats = self.get_secondary_database_stats()
            
            return {
                'primary_database': primary_stats,
                'secondary_database': secondary_stats,
                'total_databases': 2,
                'status': 'healthy' if primary_stats.get('status') == 'healthy' else 'degraded'
            }
        except Exception as e:
            logger.error(f"Error getting combined stats: {e}")
            return {
                'error': str(e),
                'status': 'error'
            }
    
    def list_websites(self) -> List[Dict[str, Any]]:
        """List all websites in secondary database"""
        return self.web_vectorstore.list_websites()
    
    def remove_website(self, url: str) -> bool:
        """Remove a website from secondary database"""
        return self.web_vectorstore.remove_website(url)

# Global instance
_dual_database_agent = None

def get_dual_database_agent():
    """Get dual database agent instance"""
    global _dual_database_agent
    if _dual_database_agent is None:
        _dual_database_agent = DualDatabaseAgent()
    return _dual_database_agent
