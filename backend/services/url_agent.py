import os
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from pathlib import Path
from sqlalchemy.orm import Session
from services.web_scraper import get_web_scraper, WebPage
from services.web_vectorstore import get_web_vectorstore
from services.retriever import get_faq_retriever
from services.simple_retriever import simple_faq_retriever
from core.config import settings
from core.db import get_db
import asyncio
from datetime import datetime

# Load .env file to ensure OPENAI_API_KEY is available
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=True)

logger = logging.getLogger(__name__)

class URLAgent:
    """
    Agent that can read URLs and use website content as a second database
    alongside the existing FAQ database.
    """
    
    def __init__(self):
        self.web_scraper = get_web_scraper()
        self.web_vectorstore = get_web_vectorstore()
        self.faq_retriever = get_faq_retriever()
        
    async def add_website(self, url: str, max_pages: int = 50) -> Dict[str, Any]:
        """
        Add a website to the agent's knowledge base
        
        Args:
            url: The website URL to scrape
            max_pages: Maximum number of pages to scrape
            
        Returns:
            Dictionary with operation results
        """
        try:
            logger.info(f"Starting to add website: {url}")
            
            # Check if website already exists
            existing_info = self.web_vectorstore.get_website_info(url)
            if existing_info:
                return {
                    'success': False,
                    'message': f'Website {url} already exists in knowledge base',
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
            
            # Add to vector store
            success = self.web_vectorstore.add_website_content(pages, url)
            
            if success:
                summary = self.web_scraper.get_page_summary(pages)
                return {
                    'success': True,
                    'message': f'Successfully added website: {url}',
                    'pages_scraped': len(pages),
                    'summary': summary,
                    'added_at': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'message': f'Failed to add website content to vector store: {url}',
                    'pages_scraped': len(pages)
                }
                
        except Exception as e:
            logger.error(f"Error adding website {url}: {str(e)}")
            return {
                'success': False,
                'message': f'Error adding website: {str(e)}',
                'error': str(e)
            }
    
    async def search_dual_database(
        self, 
        query: str, 
        include_faq: bool = True,
        include_web: bool = True,
        website_filter: Optional[str] = None,
        top_k: int = None
    ) -> Dict[str, Any]:
        """
        Search both FAQ database and web content
        
        Args:
            query: Search query
            include_faq: Whether to include FAQ results
            include_web: Whether to include web content results
            website_filter: Filter web results by specific website
            top_k: Number of results to return per source
            
        Returns:
            Combined search results
        """
        try:
            results = {
                'query': query,
                'faq_results': [],
                'web_results': [],
                'combined_results': [],
                'search_metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'sources_searched': []
                }
            }
            
            # Search FAQ database with proper database session
            if include_faq:
                try:
                    # Get database session
                    db = next(get_db())
                    
                    # Try simple search first (more reliable)
                    simple_faq_retriever.load_faqs(db)
                    faq_results = simple_faq_retriever.search(
                        query=query,
                        top_k=top_k or settings.retrieval_top_k,
                        threshold=0.2  # Low threshold to catch matches
                    )
                    
                    # If no results from simple search, try semantic search
                    if not faq_results:
                        try:
                            faq_results = self.faq_retriever.semantic_search(
                                query=query,
                                top_k=top_k or settings.retrieval_top_k
                            )
                        except Exception as semantic_error:
                            logger.warning(f"Semantic search failed: {semantic_error}")
                            faq_results = []
                    
                    results['faq_results'] = faq_results
                    results['search_metadata']['sources_searched'].append('faq')
                    logger.info(f"FAQ search found {len(faq_results)} results")
                    
                    db.close()
                    
                except Exception as e:
                    logger.error(f"Error searching FAQ database: {e}")
                    results['faq_results'] = []
            
            # Search web content
            if include_web:
                try:
                    web_results = self.web_vectorstore.semantic_search(
                        query=query,
                        top_k=top_k or settings.retrieval_top_k,
                        website_filter=website_filter
                    )
                    results['web_results'] = web_results
                    results['search_metadata']['sources_searched'].append('web')
                    logger.info(f"Web search found {len(web_results)} results")
                except Exception as e:
                    logger.error(f"Error searching web content: {e}")
                    results['web_results'] = []
            
            # Combine and rank results
            combined_results = []
            
            # Add FAQ results with source marking
            for result in results['faq_results']:
                combined_results.append({
                    'content': result.get('answer', ''),
                    'title': result.get('question', ''),
                    'source': 'faq',
                    'score': result.get('score', 0),
                    'metadata': {
                        'faq_id': result.get('faq_id'),
                        'category': result.get('category'),
                        'type': 'faq'
                    }
                })
            
            # Add web results with source marking
            for result in results['web_results']:
                combined_results.append({
                    'content': result.get('content', ''),
                    'title': result.get('title', ''),
                    'source': 'web',
                    'score': result.get('score', 0),
                    'metadata': {
                        'url': result.get('url', ''),
                        'chunk_index': result.get('chunk_index', 0),
                        'word_count': result.get('word_count', 0),
                        'type': 'web_content'
                    }
                })
            
            # Sort by score (higher is better)
            combined_results.sort(key=lambda x: x['score'], reverse=True)
            results['combined_results'] = combined_results
            
            logger.info(f"Combined search returned {len(combined_results)} total results")
            return results
            
        except Exception as e:
            logger.error(f"Error in dual database search: {e}")
            return {
                'query': query,
                'error': str(e),
                'faq_results': [],
                'web_results': [],
                'combined_results': []
            }
    
    async def answer_question(
        self, 
        question: str, 
        context_preference: str = "both",
        website_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Answer a question using both databases
        
        Args:
            question: The question to answer
            context_preference: "faq", "web", or "both"
            website_filter: Filter web results by specific website
            
        Returns:
            Answer with context and sources
        """
        try:
            # Determine search strategy
            include_faq = context_preference in ["faq", "both"]
            include_web = context_preference in ["web", "both"]
            
            # Search both databases
            search_results = await self.search_dual_database(
                query=question,
                include_faq=include_faq,
                include_web=include_web,
                website_filter=website_filter,
                top_k=3  # Get top 3 from each source
            )
            
            # Prepare context for answer generation
            context_parts = []
            sources = []
            
            # Add FAQ context
            if search_results['faq_results']:
                faq_context = "FAQ Database:\n"
                for i, result in enumerate(search_results['faq_results'][:2], 1):
                    faq_context += f"{i}. Q: {result.get('question', '')}\n"
                    faq_context += f"   A: {result.get('answer', '')}\n\n"
                    sources.append(f"FAQ: {result.get('question', '')}")
                context_parts.append(faq_context)
            
            # Add web context
            if search_results['web_results']:
                web_context = "Website Content:\n"
                for i, result in enumerate(search_results['web_results'][:2], 1):
                    web_context += f"{i}. From: {result.get('title', 'Unknown')}\n"
                    web_context += f"   URL: {result.get('url', '')}\n"
                    web_context += f"   Content: {result.get('content', '')[:500]}...\n\n"
                    sources.append(f"Web: {result.get('title', '')} ({result.get('url', '')})")
                context_parts.append(web_context)
            
            # Combine context
            full_context = "\n".join(context_parts)
            
            # Generate answer using OpenAI
            from langchain_openai import ChatOpenAI
            
            # Get API key from environment variable ONLY
            api_key = os.getenv("OPENAI_API_KEY")
            
            if not api_key or api_key == "":
                raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
            
            llm = ChatOpenAI(
                model=settings.openai_model,
                openai_api_key=api_key,
                temperature=0.3
            )
            
            prompt = f"""
Based on the following context from both FAQ database and website content, please answer the user's question in Persian.

Context:
{full_context}

Question: {question}

Please provide a comprehensive answer in Persian that:
1. Directly addresses the question
2. Uses information from the provided context
3. Is clear and helpful
4. Mentions the sources when relevant

Answer:
"""
            
            response = await llm.ainvoke(prompt)
            answer = response.content if hasattr(response, 'content') else str(response)
            
            return {
                'answer': answer,
                'sources': sources,
                'context_used': {
                    'faq_results_count': len(search_results['faq_results']),
                    'web_results_count': len(search_results['web_results']),
                    'total_sources': len(sources)
                },
                'search_metadata': search_results['search_metadata']
            }
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return {
                'answer': f"متأسفانه در پاسخ به سؤال شما خطایی رخ داد: {str(e)}",
                'sources': [],
                'error': str(e)
            }
    
    def list_websites(self) -> List[Dict[str, Any]]:
        """List all websites in the knowledge base"""
        return self.web_vectorstore.list_websites()
    
    def get_website_info(self, url: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific website"""
        return self.web_vectorstore.get_website_info(url)
    
    def remove_website(self, url: str) -> bool:
        """Remove a website from the knowledge base"""
        return self.web_vectorstore.remove_website(url)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        web_stats = self.web_vectorstore.get_stats()
        return {
            'web_content': web_stats,
            'faq_database': {
                'status': 'available' if self.faq_retriever else 'not_available'
            }
        }

# Global instance
_url_agent = None

def get_url_agent() -> URLAgent:
    """Get URL agent instance"""
    global _url_agent
    if _url_agent is None:
        _url_agent = URLAgent()
    return _url_agent
