# app/schemas/scholarship.py - TRULY SIMPLIFIED
"""
Simplified scholarship schemas - removed excessive boolean flags
These are PYDANTIC models for API validation, not SQLAlchemy models
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ScholarshipType(str, Enum):
    """Types of scholarships - matches UI filter categories"""

    ACADEMIC_MERIT = "academic_merit"
    NEED_BASED = "need_based"
    STEM = "stem"
    ARTS = "arts"
    DIVERSITY = "diversity"
    ATHLETIC = "athletic"
    LEADERSHIP = "leadership"
    MILITARY = "military"
    CAREER_SPECIFIC = "career_specific"
    OTHER = "other"


class ScholarshipStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MODERATE = "moderate"
    HARD = "hard"
    VERY_HARD = "very_hard"


# ===========================
# BASE SCHEMA
# ===========================


class ScholarshipBase(BaseModel):
    """Base schema - simplified without boolean flags"""

    title: str = Field(..., min_length=1, max_length=255)
    organization: str = Field(..., min_length=1, max_length=255)
    scholarship_type: ScholarshipType
    difficulty_level: DifficultyLevel = DifficultyLevel.MODERATE

    # Financial
    amount_exact: int = Field(..., ge=0)
    is_renewable: bool = False

    # Display
    primary_image_url: Optional[str] = Field(None, max_length=500)


# ===========================
# CREATE SCHEMA
# ===========================


class ScholarshipCreate(ScholarshipBase):
    """Schema for creating a new scholarship"""

    pass


# ===========================
# UPDATE SCHEMA
# ===========================


class ScholarshipUpdate(BaseModel):
    """Schema for updating a scholarship - all fields optional"""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    organization: Optional[str] = Field(None, min_length=1, max_length=255)
    scholarship_type: Optional[ScholarshipType] = None
    difficulty_level: Optional[DifficultyLevel] = None
    status: Optional[ScholarshipStatus] = None

    amount_exact: Optional[int] = Field(None, ge=0)
    is_renewable: Optional[bool] = None

    primary_image_url: Optional[str] = Field(None, max_length=500)

    verified: Optional[bool] = None
    featured: Optional[bool] = None


# ===========================
# RESPONSE SCHEMA
# ===========================


class ScholarshipResponse(ScholarshipBase):
    """Schema for scholarship API responses"""

    id: int
    status: ScholarshipStatus
    verified: bool
    featured: bool
    views_count: int
    applications_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ===========================
# SEARCH FILTERS
# ===========================


class ScholarshipSearchFilter(BaseModel):
    """Simplified search filters"""

    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)

    # Basic filters
    scholarship_type: Optional[ScholarshipType] = None
    active_only: bool = True
    verified_only: bool = False
    featured_only: bool = False

    # Search
    search_query: Optional[str] = None

    # Financial filters
    min_amount: Optional[int] = Field(None, ge=0)
    max_amount: Optional[int] = Field(None, ge=0)

    # Simple filters
    renewable_only: Optional[bool] = None

    # Sorting
    sort_by: str = Field(
        "created_at", pattern="^(created_at|amount_exact|title|views_count)$"
    )
    sort_order: str = Field("desc", pattern="^(asc|desc)$")


# ===========================
# BULK OPERATIONS
# ===========================


class BulkScholarshipCreate(BaseModel):
    """Schema for bulk scholarship creation"""

    scholarships: list[ScholarshipCreate]

    @validator("scholarships")
    def validate_scholarships_list(cls, v):
        if len(v) == 0:
            raise ValueError("At least one scholarship is required")
        if len(v) > 100:
            raise ValueError("Maximum 100 scholarships per batch")
        return v
