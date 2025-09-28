from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum


class QuestionType(str, Enum):
    """Types of questions supported"""
    DIRECT = "direct"  # Direct question-answer pair
    CONTEXTUAL = "contextual"  # Question that needs context
    MULTI_STEP = "multi_step"  # Question requiring multiple steps
    CONDITIONAL = "conditional"  # Question with conditions


class AnswerFormat(str, Enum):
    """Format of the answer"""
    TEXT = "text"
    LIST = "list"
    STRUCTURED = "structured"
    STEP_BY_STEP = "step_by_step"


class QuestionVariant(BaseModel):
    """Alternative ways to ask the same question"""
    text: str = Field(..., description="Alternative question text")
    language: str = Field(default="fa", description="Language code (fa for Persian)")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score for this variant")


class AnswerComponent(BaseModel):
    """Component of a structured answer"""
    type: str = Field(..., description="Type of component (text, list, code, link, etc.)")
    content: str = Field(..., description="Content of the component")
    order: int = Field(default=0, description="Display order")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class StructuredAnswer(BaseModel):
    """Structured answer with multiple components"""
    format: AnswerFormat = Field(default=AnswerFormat.TEXT)
    components: List[AnswerComponent] = Field(default_factory=list)
    summary: Optional[str] = Field(default=None, description="Brief summary of the answer")
    related_questions: List[str] = Field(default_factory=list, description="Related question IDs")


class ContextRequirement(BaseModel):
    """Context needed for answering the question"""
    type: str = Field(..., description="Type of context needed")
    description: str = Field(..., description="Description of required context")
    required: bool = Field(default=True, description="Whether this context is required")


class JSONFAQ(BaseModel):
    """Enhanced FAQ structure with JSON support"""
    id: Optional[str] = Field(default=None, description="Unique identifier")
    question: str = Field(..., description="Main question text")
    question_type: QuestionType = Field(default=QuestionType.DIRECT)
    question_variants: List[QuestionVariant] = Field(default_factory=list)
    
    # Answer structure
    answer: str = Field(..., description="Main answer text")
    structured_answer: Optional[StructuredAnswer] = Field(default=None)
    
    # Metadata
    category: Optional[str] = Field(default=None, description="Category name")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    priority: int = Field(default=1, ge=1, le=10, description="Priority level (1-10)")
    
    # Context and conditions
    context_requirements: List[ContextRequirement] = Field(default_factory=list)
    conditions: Optional[Dict[str, Any]] = Field(default=None, description="Conditions for this FAQ")
    
    # Quality and usage
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence in this answer")
    usage_count: int = Field(default=0, description="How many times this FAQ was used")
    last_used: Optional[datetime] = Field(default=None, description="Last time this FAQ was used")
    
    # Relationships
    related_faqs: List[str] = Field(default_factory=list, description="Related FAQ IDs")
    follow_up_questions: List[str] = Field(default_factory=list, description="Suggested follow-up questions")
    
    # Status
    is_active: bool = Field(default=True, description="Whether this FAQ is active")
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    
    @validator('question_variants')
    def validate_question_variants(cls, v):
        """Ensure at least one variant exists"""
        if not v:
            return [QuestionVariant(text="", language="fa")]
        return v
    
    @validator('tags')
    def validate_tags(cls, v):
        """Clean and validate tags"""
        return [tag.strip().lower() for tag in v if tag.strip()]


class JSONFAQCreate(BaseModel):
    """Schema for creating a new JSON FAQ"""
    question: str
    answer: str
    question_type: QuestionType = QuestionType.DIRECT
    question_variants: List[QuestionVariant] = []
    structured_answer: Optional[StructuredAnswer] = None
    category: Optional[str] = None
    tags: List[str] = []
    priority: int = 1
    context_requirements: List[ContextRequirement] = []
    conditions: Optional[Dict[str, Any]] = None
    confidence_score: float = 1.0
    related_faqs: List[str] = []
    follow_up_questions: List[str] = []
    is_active: bool = True


class JSONFAQUpdate(BaseModel):
    """Schema for updating a JSON FAQ"""
    question: Optional[str] = None
    answer: Optional[str] = None
    question_type: Optional[QuestionType] = None
    question_variants: Optional[List[QuestionVariant]] = None
    structured_answer: Optional[StructuredAnswer] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    priority: Optional[int] = None
    context_requirements: Optional[List[ContextRequirement]] = None
    conditions: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = None
    related_faqs: Optional[List[str]] = None
    follow_up_questions: Optional[List[str]] = None
    is_active: Optional[bool] = None


class JSONFAQResponse(BaseModel):
    """Response schema for JSON FAQ"""
    id: str
    question: str
    answer: str
    question_type: QuestionType
    question_variants: List[QuestionVariant]
    structured_answer: Optional[StructuredAnswer]
    category: Optional[str]
    tags: List[str]
    priority: int
    confidence_score: float
    usage_count: int
    last_used: Optional[datetime]
    related_faqs: List[str]
    follow_up_questions: List[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]


class JSONFAQListResponse(BaseModel):
    """Response schema for paginated JSON FAQ list"""
    items: List[JSONFAQResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class JSONFAQImport(BaseModel):
    """Schema for importing multiple JSON FAQs"""
    faqs: List[JSONFAQCreate]
    overwrite_existing: bool = Field(default=False, description="Whether to overwrite existing FAQs")
    validate_only: bool = Field(default=False, description="Only validate, don't import")


class JSONFAQExport(BaseModel):
    """Schema for exporting JSON FAQs"""
    faqs: List[JSONFAQResponse]
    export_metadata: Dict[str, Any] = Field(default_factory=dict)
    exported_at: datetime = Field(default_factory=datetime.now)
