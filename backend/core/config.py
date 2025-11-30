from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # OpenAI Configuration
    openai_api_key: str = ""
    openai_model: str = "gpt-3.5-turbo"  # Using GPT-3.5 Turbo model
    embedding_model: str = "text-embedding-3-small"
    
    # External API Configuration
    external_api_url: str = "http://85.208.254.187"
    external_api_port: int = 8000
    external_api_timeout: int = 30
    external_api_enabled: bool = False
    
    # Retrieval Configuration
    retrieval_top_k: int = 4
    retrieval_threshold: float = 0.82
    
    # Database Configuration
    database_url: str = "sqlite:///./app.db"
    
    # Server Configuration
    server_port: int = 8001
    server_host: str = "0.0.0.0"
    
    # Intent Detection
    intent_system_prompt: str = "تو یک دسته‌بند نیت کاربر هستی. فقط یکی از برچسب‌ها را با احتمال برگردان. خروجی JSON بده."
    
    # Vector Store
    vectorstore_path: str = "./vectorstore"
    
    # Smart Agent Configuration
    smart_agent_enabled: bool = True
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"  # Allow extra fields from environment variables
    )


settings = Settings()
