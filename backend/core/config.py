import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    
    # Retrieval Configuration
    retrieval_top_k: int = 4
    retrieval_threshold: float = 0.82
    
    # Database Configuration
    database_url: str = "sqlite:///./app.db"
    
    # Intent Detection
    intent_system_prompt: str = "تو یک دسته‌بند نیت کاربر هستی. فقط یکی از برچسب‌ها را با احتمال برگردان. خروجی JSON بده."
    
    # Vector Store
    vectorstore_path: str = "./vectorstore"
    
    class Config:
        env_file = ".env"  # Enable .env file loading
        case_sensitive = False


settings = Settings()
