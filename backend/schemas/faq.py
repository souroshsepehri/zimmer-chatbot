from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CategoryBase(BaseModel):
    name: str
    slug: str


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None


class Category(CategoryBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class FAQBase(BaseModel):
    question: str
    answer: str
    category_id: Optional[int] = None
    is_active: bool = True


class FAQCreate(FAQBase):
    pass


class FAQUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    category_id: Optional[int] = None
    is_active: Optional[bool] = None


class FAQ(FAQBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    category: Optional[Category] = None
    
    class Config:
        from_attributes = True


class FAQListResponse(BaseModel):
    items: List[FAQ]
    total: int
    page: int
    page_size: int
    total_pages: int
