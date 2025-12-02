"""
Tracked Site Pydantic Schemas

Request and response models for TrackedSite CRUD operations.
"""

from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime


class TrackedSiteBase(BaseModel):
    """Base schema for TrackedSite"""
    name: str = Field(..., description="نام سایت")
    url: HttpUrl = Field(..., description="آدرس URL سایت")
    description: Optional[str] = Field(None, description="توضیحات")
    is_active: bool = Field(True, description="آیا فعال است؟")


class TrackedSiteCreate(TrackedSiteBase):
    """Schema for creating a new TrackedSite"""
    pass


class TrackedSiteUpdate(BaseModel):
    """Schema for updating a TrackedSite"""
    name: Optional[str] = Field(None, description="نام سایت")
    url: Optional[HttpUrl] = Field(None, description="آدرس URL سایت")
    description: Optional[str] = Field(None, description="توضیحات")
    is_active: Optional[bool] = Field(None, description="آیا فعال است؟")


class TrackedSiteRead(TrackedSiteBase):
    """Schema for reading a TrackedSite"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
















