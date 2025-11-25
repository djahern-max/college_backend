"""
Schemas for entity images (gallery).
Used for API responses when displaying institution/scholarship galleries.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class EntityImageBase(BaseModel):
    """Base schema for entity images"""
    caption: Optional[str] = None
    image_type: Optional[str] = None


class EntityImageResponse(EntityImageBase):
    """Schema for entity image responses"""
    id: int
    entity_type: str
    entity_id: int
    image_url: str
    cdn_url: str
    filename: str
    display_order: int
    is_featured: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
