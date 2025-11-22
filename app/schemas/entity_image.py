# app/schemas/entity_image.py
from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime


class EntityImageResponse(BaseModel):
    """Schema for entity image responses - READ ONLY"""

    id: int
    entity_type: str
    entity_id: int
    image_url: str
    cdn_url: str
    filename: str
    caption: Optional[str] = None
    display_order: int
    is_featured: bool
    image_type: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
