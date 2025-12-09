import os
import json
import pickle
import numpy as np
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from pathlib import Path
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from services.web_scraper import WebPage
from core.config import settings
import logging

# Load .env file to ensure OPENAI_API_KEY is available
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=True)

logger = logging.getLogger(__name__)

class WebVectorStore:
    def __init__(self):
        # Get API key from environment variable ONLY
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key or api_key == "":
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
        
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=api_key
        )
        self.vectorstore_path = os.path.join(settings.vectorstore_path, "web_content")
        self.index_path = os.path.join(self.vectorstore_path, "web_faiss.index")
        self.mapping_path = os.path.join(self.vectorstore_path, "web_mapping.pkl")
        self.metadata_path = os.path.join(self.vectorstore_path, "web_metadata.json")
        
        # Ensure vectorstore directory exists
        os.makedirs(self.vectorstore_path, exist_ok=True)
        
        # Text splitter for chunking large documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        self.vectorstore = None
        self.web_mapping = {}
        self.website_metadata = {}
        
    def _load_vectorstore(self) -> bool:
        """Load existing FAISS index and mapping"""
        try:
            if (os.path.exists(self.index_path) and 
                os.path.exists(self.mapping_path) and 
                os.path.exists(self.metadata_path)):
                
                self.vectorstore = FAISS.load_local(
                    self.vectorstore_path, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                
                with open(self.mapping_path, 'rb') as f:
                    self.web_mapping = pickle.load(f)
                
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    self.website_metadata = json.load(f)
                
                logger.info(f"Loaded web vectorstore with {len(self.web_mapping)} chunks")
                return True
            else:
                logger.info("No existing web vectorstore found, will create new one")
                return False
        except Exception as e:
            logger.error(f"Error loading web vectorstore: {e}")
            # Initialize empty structures
            self.web_mapping = {}
            self.website_metadata = {}
            return False
    
    def _save_vectorstore(self):
        """Save FAISS index and mapping"""
        if self.vectorstore:
            self.vectorstore.save_local(self.vectorstore_path)
            with open(self.mapping_path, 'wb') as f:
                pickle.dump(self.web_mapping, f)
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.website_metadata, f, ensure_ascii=False, indent=2)
            logger.info("Web vectorstore saved successfully")
    
    def _chunk_page_content(self, page: WebPage) -> List[Dict[str, Any]]:
        """Split page content into chunks"""
        chunks = []
        
        # Split content into chunks
        text_chunks = self.text_splitter.split_text(page.content)
        
        for i, chunk_text in enumerate(text_chunks):
            if len(chunk_text.strip()) < 50:  # Skip very small chunks
                continue
                
            chunk_data = {
                'text': chunk_text,
                'metadata': {
                    'url': page.url,
                    'title': page.title,
                    'chunk_index': i,
                    'total_chunks': len(text_chunks),
                    'word_count': len(chunk_text.split()),
                    'scraped_at': page.metadata['scraped_at']
                }
            }
            chunks.append(chunk_data)
        
        return chunks
    
    def add_website_content(self, pages: List[WebPage], website_url: str) -> bool:
        """Add website content to vector store"""
        try:
            logger.info(f"Adding {len(pages)} pages from {website_url} to vector store")
            
            # Prepare documents and metadata
            documents = []
            metadatas = []
            chunk_index = 0
            
            # Store website metadata
            self.website_metadata[website_url] = {
                'url': website_url,
                'total_pages': len(pages),
                'total_words': sum(page.metadata['word_count'] for page in pages),
                'added_at': pages[0].metadata['scraped_at'] if pages else 0,
                'domain': pages[0].url.split('/')[2] if pages else ''
            }
            
            for page in pages:
                chunks = self._chunk_page_content(page)
                
                for chunk in chunks:
                    documents.append(chunk['text'])
                    metadatas.append(chunk['metadata'])
                    
                    # Store mapping for quick lookup
                    self.web_mapping[chunk_index] = {
                        'url': page.url,
                        'title': page.title,
                        'chunk_index': chunk['metadata']['chunk_index']
                    }
                    chunk_index += 1
            
            if not documents:
                logger.warning("No valid content chunks found")
                return False
            
            # Create or update vector store
            if self.vectorstore is None:
                # Create new vector store
                self.vectorstore = FAISS.from_texts(
                    documents, 
                    self.embeddings,
                    metadatas=metadatas
                )
            else:
                # Add to existing vector store
                new_vectorstore = FAISS.from_texts(
                    documents, 
                    self.embeddings,
                    metadatas=metadatas
                )
                self.vectorstore.merge_from(new_vectorstore)
            
            self._save_vectorstore()
            logger.info(f"Successfully added {len(documents)} chunks to web vector store")
            return True
            
        except Exception as e:
            logger.error(f"Error adding website content: {e}")
            return False
    
    def semantic_search(
        self, 
        query: str, 
        top_k: int = None, 
        threshold: float = None,
        website_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Perform semantic search on web content"""
        try:
            if not self.vectorstore:
                if not self._load_vectorstore():
                    logger.warning("No web vectorstore available")
                    return []
            
            top_k = top_k or settings.retrieval_top_k
            threshold = threshold or settings.retrieval_threshold
            
            # Perform search
            results = self.vectorstore.similarity_search_with_score(
                query, k=top_k
            )
            
            # Filter by threshold and website
            filtered_results = []
            for doc, score in results:
                if score >= threshold:
                    metadata = doc.metadata
                    
                    # Apply website filter if specified
                    if website_filter and website_filter not in metadata.get('url', ''):
                        continue
                    
                    filtered_results.append({
                        'content': doc.page_content,
                        'url': metadata.get('url', ''),
                        'title': metadata.get('title', ''),
                        'score': float(score),
                        'chunk_index': metadata.get('chunk_index', 0),
                        'word_count': metadata.get('word_count', 0)
                    })
            
            logger.info(f"Web search returned {len(filtered_results)} results")
            return filtered_results
            
        except Exception as e:
            logger.error(f"Error in web semantic search: {e}")
            return []
    
    def get_website_info(self, website_url: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific website"""
        return self.website_metadata.get(website_url)
    
    def list_websites(self) -> List[Dict[str, Any]]:
        """List all websites in the vector store"""
        return list(self.website_metadata.values())
    
    def remove_website(self, website_url: str) -> bool:
        """Remove a website from the vector store"""
        try:
            if website_url not in self.website_metadata:
                return False
            
            # This is a simplified removal - in production you might want
            # to rebuild the entire index without the website content
            del self.website_metadata[website_url]
            
            # Remove chunks from mapping
            chunks_to_remove = [
                chunk_id for chunk_id, chunk_data in self.web_mapping.items()
                if chunk_data['url'].startswith(website_url)
            ]
            
            for chunk_id in chunks_to_remove:
                del self.web_mapping[chunk_id]
            
            self._save_vectorstore()
            logger.info(f"Removed website: {website_url}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing website: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        if not self._load_vectorstore():
            return {'status': 'not_loaded'}
        
        return {
            'total_chunks': len(self.web_mapping),
            'total_websites': len(self.website_metadata),
            'websites': list(self.website_metadata.keys())
        }

# Global instance
_web_vectorstore = None

def get_web_vectorstore() -> WebVectorStore:
    """Get web vector store instance"""
    global _web_vectorstore
    if _web_vectorstore is None:
        _web_vectorstore = WebVectorStore()
    return _web_vectorstore
