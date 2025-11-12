import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = "gpt-3.5-turbo"
    embedding_model: str = "text-embedding-3-small"
    
    # External API Configuration
    external_api_url: str = os.getenv("EXTERNAL_API_URL", "http://85.208.254.187")
    external_api_port: int = int(os.getenv("EXTERNAL_API_PORT", "8000"))
    external_api_timeout: int = int(os.getenv("EXTERNAL_API_TIMEOUT", "30"))
    external_api_enabled: bool = os.getenv("EXTERNAL_API_ENABLED", "false").lower() == "true"
    
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
