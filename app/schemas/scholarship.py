# app/schemas/scholarship.py - SIMPLIFIED VERSION
"""
Streamlined scholarship schemas matching the simplified model
Removed all fields that had 0% usage (47 fields removed)
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ScholarshipType(str, Enum):
    ACADEMIC_MERIT = "academic_merit"
    NEED_BASED = "need_based"
    ATHLETIC = "athletic"
    STEM = "stem"
    ARTS = "arts"
    DIVERSITY = "diversity"
    FIRST_GENERATION = "first_generation"
    COMMUNITY_SERVICE = "community_service"
    LEADERSHIP = "leadership"
    LOCAL_COMMUNITY = "local_community"
    EMPLOYER_SPONSORED = "employer_sponsored"
    MILITARY = "military"
    RELIGIOUS = "religious"
    CAREER_SPECIFIC = "career_specific"
    ESSAY_BASED = "essay_based"
    RENEWABLE = "renewable"


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
    """Base schema with only fields that are actually used"""

    title: str = Field(..., min_length=1, max_length=255)
    organization: str = Field(..., min_length=1, max_length=255)
    scholarship_type: ScholarshipType
    difficulty_level: DifficultyLevel = DifficultyLevel.MODERATE

    # Financial
    amount_exact: int = Field(..., ge=0)
    is_renewable: bool = False

    # Eligibility flags
    need_based_required: bool = False
    international_students_eligible: bool = False
    leadership_required: bool = False
    work_experience_required: bool = False
    military_affiliation_required: bool = False

    # Application requirements
    essay_required: bool = False
    transcript_required: bool = True
    recommendation_letters_required: int = Field(0, ge=0, le=10)
    portfolio_required: bool = False
    interview_required: bool = False

    # Essay requirements
    personal_statement_required: bool = False
    leadership_essay_required: bool = False
    community_service_essay_required: bool = False

    # Deadline
    is_rolling_deadline: bool = False

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

    need_based_required: Optional[bool] = None
    international_students_eligible: Optional[bool] = None
    leadership_required: Optional[bool] = None
    work_experience_required: Optional[bool] = None
    military_affiliation_required: Optional[bool] = None

    essay_required: Optional[bool] = None
    transcript_required: Optional[bool] = None
    recommendation_letters_required: Optional[int] = Field(None, ge=0, le=10)
    portfolio_required: Optional[bool] = None
    interview_required: Optional[bool] = None

    personal_statement_required: Optional[bool] = None
    leadership_essay_required: Optional[bool] = None
    community_service_essay_required: Optional[bool] = None

    is_rolling_deadline: Optional[bool] = None
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
    """Simplified search filters - only for fields that exist"""

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

    # Requirement filters
    requires_essay: Optional[bool] = None
    requires_interview: Optional[bool] = None
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
