# app/schemas/institution.py - SIMPLIFIED VERSION
"""
Streamlined institution schemas matching the simplified model
Removed all fields that had 0% usage
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ControlType(str, Enum):
    """Institution control types"""

    PUBLIC = "public"
    PRIVATE_NONPROFIT = "private_nonprofit"
    PRIVATE_FOR_PROFIT = "private_for_profit"


# ===========================
# BASE SCHEMA
# ===========================


class InstitutionBase(BaseModel):
    """Base schema with common fields"""

    name: str = Field(..., min_length=1, max_length=255)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=2, max_length=2)
    control_type: ControlType
    primary_image_url: Optional[str] = Field(None, max_length=500)


# ===========================
# CREATE SCHEMA
# ===========================


class InstitutionCreate(InstitutionBase):
    """Schema for creating a new institution"""

    ipeds_id: int = Field(..., gt=0)


# ===========================
# UPDATE SCHEMA
# ===========================


class InstitutionUpdate(BaseModel):
    """Schema for updating an institution - all fields optional"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    state: Optional[str] = Field(None, min_length=2, max_length=2)
    control_type: Optional[ControlType] = None
    primary_image_url: Optional[str] = Field(None, max_length=500)


# ===========================
# RESPONSE SCHEMA
# ===========================


class InstitutionResponse(InstitutionBase):
    """Schema for institution API responses"""

    id: int
    ipeds_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===========================
# LIST RESPONSE
# ===========================


class InstitutionList(BaseModel):
    """Schema for paginated institution list"""

    institutions: list[InstitutionResponse]
    total: int = Field(..., description="Total number of institutions")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Results per page")
    has_more: bool = Field(..., description="Whether more results exist")


# ===========================
# SEARCH FILTERS
# ===========================


class InstitutionSearchFilter(BaseModel):
    """Simplified search filters"""

    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)

    # Filters
    state: Optional[str] = Field(None, min_length=2, max_length=2)
    control_type: Optional[ControlType] = None

    # Search
    search_query: Optional[str] = None

    # Sorting
    sort_by: str = Field("name", pattern="^(name|city|state|created_at)$")
    sort_order: str = Field("asc", pattern="^(asc|desc)$")


# ===========================
# STATS SCHEMA
# ===========================


class InstitutionStats(BaseModel):
    """Schema for institution statistics"""

    total_institutions: int
    by_control_type: dict[str, int]
    by_state: dict[str, int]
    with_images: int

    class Config:
        from_attributes = True
