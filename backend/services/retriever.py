import os
import json
import pickle
import numpy as np
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from pathlib import Path
from sqlalchemy.orm import Session
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from models.faq import FAQ
from core.config import settings

# Load .env file to ensure OPENAI_API_KEY is available
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=True)


class FAQRetriever:
    def __init__(self):
        # Get API key from environment variable ONLY
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key or api_key == "":
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
        
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=api_key
        )
        self.vectorstore_path = settings.vectorstore_path
        self.index_path = os.path.join(self.vectorstore_path, "faiss.index")
        self.mapping_path = os.path.join(self.vectorstore_path, "mapping.pkl")
        
        # Ensure vectorstore directory exists
        os.makedirs(self.vectorstore_path, exist_ok=True)
        
        self.vectorstore = None
        self.faq_mapping = {}
        
    def _load_vectorstore(self):
        """Load existing FAISS index and mapping"""
        if os.path.exists(self.index_path) and os.path.exists(self.mapping_path):
            try:
                self.vectorstore = FAISS.load_local(
                    self.vectorstore_path, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                with open(self.mapping_path, 'rb') as f:
                    self.faq_mapping = pickle.load(f)
                return True
            except Exception as e:
                print(f"Error loading vectorstore: {e}")
                return False
        return False
    
    def _save_vectorstore(self):
        """Save FAISS index and mapping"""
        if self.vectorstore:
            self.vectorstore.save_local(self.vectorstore_path)
            with open(self.mapping_path, 'wb') as f:
                pickle.dump(self.faq_mapping, f)
    
    def build_index(self, db: Session, category_filter: Optional[str] = None):
        """Build FAISS index from active FAQs"""
        # Get active FAQs
        query = db.query(FAQ).filter(FAQ.is_active == True)
        if category_filter:
            query = query.join(FAQ.category).filter(
                FAQ.category.has(slug=category_filter)
            )
        
        faqs = query.all()
        
        if not faqs:
            print("No active FAQs found")
            return
        
        # Prepare documents and metadata
        documents = []
        metadatas = []
        self.faq_mapping = {}
        
        for i, faq in enumerate(faqs):
            # Combine question and answer for better retrieval
            doc_text = f"{faq.question}\n{faq.answer}"
            documents.append(doc_text)
            
            metadata = {
                "faq_id": faq.id,
                "question": faq.question,
                "answer": faq.answer,
                "category": faq.category.name if faq.category else None
            }
            metadatas.append(metadata)
            
            # Store mapping for quick lookup
            self.faq_mapping[i] = faq.id
        
        # Create embeddings and FAISS index
        if documents:
            self.vectorstore = FAISS.from_texts(
                documents, 
                self.embeddings,
                metadatas=metadatas
            )
            self._save_vectorstore()
            print(f"Built index with {len(documents)} FAQs")
    
    def semantic_search(
        self, 
        query: str, 
        top_k: int = None, 
        threshold: float = None,
        category_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Perform semantic search on FAQs"""
        if not self.vectorstore:
            if not self._load_vectorstore():
                return []
        
        top_k = top_k or settings.retrieval_top_k
        threshold = threshold or settings.retrieval_threshold
        
        # Perform search
        results = self.vectorstore.similarity_search_with_score(
            query, k=top_k
        )
        
        # Filter by threshold and format results
        filtered_results = []
        for doc, score in results:
            if score >= threshold:
                metadata = doc.metadata
                filtered_results.append({
                    "faq_id": metadata["faq_id"],
                    "question": metadata["question"],
                    "answer": metadata["answer"],
                    "score": float(score),
                    "category": metadata["category"]
                })
        
        return filtered_results
    
    def reindex(self, db: Session):
        """Rebuild the entire index"""
        self.build_index(db)
        print("Reindexing completed")


# Global instance - lazy initialization
_faq_retriever = None

def get_faq_retriever():
    """Get the FAQ retriever instance with lazy initialization"""
    global _faq_retriever
    if _faq_retriever is None:
        _faq_retriever = FAQRetriever()
    return _faq_retriever

# Create a proxy object that initializes lazily
class LazyFAQRetriever:
    def __getattr__(self, name):
        return getattr(get_faq_retriever(), name)

faq_retriever = LazyFAQRetriever()
