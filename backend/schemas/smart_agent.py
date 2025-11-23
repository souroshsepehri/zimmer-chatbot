"""
Smart Agent Pydantic schemas and style definitions
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List, Literal, TypedDict
from enum import Enum


class ResponseStyle(str, Enum):
    """Enumeration of available response styles"""
    AUTO = "auto"
    FORMAL = "formal"
    FRIENDLY = "friendly"
    BRIEF = "brief"
    DETAILED = "detailed"
    EXPLAINER = "explainer"
    MARKETING = "marketing"


class ResponseStyleInfo(TypedDict):
    """Type definition for style information"""
    key: str
    label: str
    description: str
    # Optional: extra metadata later (max_length, etc.)


# Style definitions with Persian labels and descriptions
AVAILABLE_STYLES: Dict[ResponseStyle, ResponseStyleInfo] = {
    ResponseStyle.AUTO: {
        "key": "auto",
        "label": "خودکار",
        "description": "سیستم خودش بسته به سوال و زمینه، لحن مناسب را انتخاب می‌کند.",
    },
    ResponseStyle.FORMAL: {
        "key": "formal",
        "label": "رسمی و حرفه‌ای",
        "description": "لحن رسمی، محترمانه، مناسب مستندات و ارتباط B2B.",
    },
    ResponseStyle.FRIENDLY: {
        "key": "friendly",
        "label": "صمیمی و محاوره‌ای",
        "description": "لحن صمیمی شبیه چت اینستاگرام، اما همچنان محترمانه.",
    },
    ResponseStyle.BRIEF: {
        "key": "brief",
        "label": "خیلی خلاصه",
        "description": "جواب‌های خیلی کوتاه، مستقیم و بدون حاشیه.",
    },
    ResponseStyle.DETAILED: {
        "key": "detailed",
        "label": "کامل و توضیحی",
        "description": "جواب‌های طولانی‌تر با توضیح جزئیات و مثال.",
    },
    ResponseStyle.EXPLAINER: {
        "key": "explainer",
        "label": "آموزشی مرحله‌به‌مرحله",
        "description": "توضیح پاسخ به صورت گام‌به‌گام برای آموزش.",
    },
    ResponseStyle.MARKETING: {
        "key": "marketing",
        "label": "مارکتینگی و ترغیب‌کننده",
        "description": "لحن تبلیغاتی ملایم، مناسب معرفی سرویس به مشتری.",
    },
}

# Create instruction prompts for each style (used in system prompts)
STYLE_INSTRUCTIONS: Dict[str, str] = {
    "auto": "Analyze the user's message and choose the most appropriate response style automatically.",
    "formal": "Provide a formal, professional response with proper structure and detailed explanations. Use respectful and business-appropriate language.",
    "friendly": "Respond in a friendly, conversational manner similar to Instagram chat, but still respectful and appropriate.",
    "brief": "Provide a very brief, direct response without unnecessary details. Be concise and to the point.",
    "detailed": "Provide a comprehensive, detailed response with thorough explanations and examples.",
    "explainer": "Explain the answer step-by-step in an educational manner, breaking down complex concepts into clear steps.",
    "marketing": "Respond in a gentle marketing tone, suitable for introducing services to customers. Be persuasive but not pushy.",
}

# Legacy compatibility: create a dict format for backward compatibility
STYLE_DEFINITIONS: Dict[str, Dict[str, str]] = {
    style.value: {
        "name": info["label"],
        "description": info["description"],
        "instruction": STYLE_INSTRUCTIONS.get(style.value, "Provide a helpful response."),
    }
    for style, info in AVAILABLE_STYLES.items()
}


# Create Literal type for style validation (for OpenAPI docs)
StyleLiteral = Literal[
    "auto",
    "formal",
    "friendly",
    "brief",
    "detailed",
    "explainer",
    "marketing"
]


class SmartAgentRequest(BaseModel):
    """Request model for Smart Agent chat endpoint"""
    message: str = Field(..., description="The user's message to the smart agent")
    style: Optional[str] = Field(
        default="auto",
        description="Response style. Use 'auto' for automatic selection, or choose from available styles: auto, formal, friendly, brief, detailed, explainer, marketing."
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional context to provide to the agent"
    )

    @field_validator('style')
    @classmethod
    def validate_style(cls, v: Optional[str]) -> str:
        """Validate that the style is one of the available styles, default to 'auto' if invalid"""
        if v is None:
            return ResponseStyle.AUTO.value
        v_lower = v.lower().strip()
        # Check against ResponseStyle enum values
        valid_styles = [style.value for style in ResponseStyle]
        if v_lower in valid_styles:
            return v_lower
        # If style is not recognized, default to auto
        return ResponseStyle.AUTO.value


class SmartAgentResponse(BaseModel):
    """Response model for Smart Agent chat endpoint"""
    response: str = Field(..., description="The agent's response text")
    style: str = Field(
        ..., 
        description="The effective style that was used for this response. If the request had style='auto', this will show the auto-selected style (e.g., 'friendly', 'formal'). Otherwise, it matches the requested style after normalization."
    )
    response_time: float = Field(..., description="Time taken to generate the response in seconds")
    web_content_used: bool = Field(..., description="Whether web content was used in generating the response")
    urls_processed: List[str] = Field(default_factory=list, description="List of URLs that were processed")
    context_used: bool = Field(..., description="Whether additional context was used")
    timestamp: str = Field(..., description="ISO timestamp of when the response was generated")
    debug_info: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional debug information (only included in debug mode)"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if an error occurred"
    )


class StyleInfo(BaseModel):
    """Information about a response style"""
    key: str = Field(..., description="Style identifier/key")
    label: str = Field(..., description="Human-readable style label (Persian)")
    description: str = Field(..., description="Description of the style (Persian)")




class URLReadRequest(BaseModel):
    """Request model for URL reading endpoint"""
    url: str = Field(..., description="URL to read and extract content from")
    max_length: Optional[int] = Field(
        default=5000,
        description="Maximum length of extracted content"
    )


class URLReadResponse(BaseModel):
    """Response model for URL reading endpoint"""
    url: str = Field(..., description="The URL that was processed")
    title: str = Field(..., description="Title of the webpage")
    description: str = Field(..., description="Description or meta description of the webpage")
    main_content: str = Field(..., description="Main content extracted from the webpage")
    links: List[Dict[str, str]] = Field(default_factory=list, description="List of links found on the page")
    images: List[Dict[str, str]] = Field(default_factory=list, description="List of images found on the page")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Additional metadata from the page")
    timestamp: str = Field(..., description="ISO timestamp of when the content was extracted")
    error: Optional[str] = Field(
        default=None,
        description="Error message if an error occurred"
    )

