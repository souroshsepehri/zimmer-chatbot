"""
Bot Settings Pydantic Model

Defines the configuration model for the chatbot settings.
"""

from pydantic import BaseModel, Field
from typing import Literal


class BotSettings(BaseModel):
    """Bot configuration settings with Persian-friendly defaults"""
    
    enabled: bool = Field(
        default=True,
        description="آیا بات فعال است؟",
    )
    
    default_style: Literal["auto", "formal", "casual"] = Field(
        default="auto",
        description="استایل پیش‌فرض پاسخ‌گویی",
    )
    
    use_faq: bool = Field(
        default=True,
        description="آیا از FAQ داخلی استفاده شود؟",
    )
    
    use_web_context: bool = Field(
        default=True,
        description="آیا از محتوای صفحات وب استفاده شود؟",
    )
    
    max_answer_chars: int = Field(
        default=800,
        description="حداکثر طول پاسخ (کاراکتر)",
    )
    
    temperature: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="درجه خلاقیت مدل",
    )

