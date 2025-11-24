# app/schemas/scholarship.py - UPDATED FOR ESSENTIAL FIELDS
"""
Simplified scholarship schemas with essential fields
These are PYDANTIC models for API validation, not SQLAlchemy models
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

from app.models.scholarship import ScholarshipType, ScholarshipStatus, DifficultyLevel


# ===========================
# BASE SCHEMA
# ===========================


class ScholarshipBase(BaseModel):
    """Base schema with essential fields"""

    title: str = Field(..., min_length=1, max_length=255)
    organization: str = Field(..., min_length=1, max_length=255)
    scholarship_type: ScholarshipType
    difficulty_level: DifficultyLevel = DifficultyLevel.MODERATE

    # Financial - using min/max for flexibility
    amount_min: int = Field(..., ge=0)
    amount_max: int = Field(..., ge=0)
    is_renewable: bool = False
    number_of_awards: Optional[int] = Field(None, ge=1)

    # Dates
    deadline: Optional[date] = None
    application_opens: Optional[date] = None
    for_academic_year: Optional[str] = Field(
        None, max_length=20, pattern=r"^\d{4}-\d{4}$"
    )

    # Details
    description: Optional[str] = Field(None, max_length=500)
    website_url: Optional[str] = Field(None, max_length=500)

    # Requirements
    min_gpa: Optional[Decimal] = Field(None, ge=0, le=4.0)

    # Display
    primary_image_url: Optional[str] = Field(None, max_length=500)

    @validator("amount_max")
    def validate_amount_range(cls, v, values):
        """Ensure amount_max >= amount_min"""
        if "amount_min" in values and v < values["amount_min"]:
            raise ValueError("amount_max must be greater than or equal to amount_min")
        return v

    @validator("for_academic_year")
    def validate_academic_year(cls, v):
        """Validate academic year format (e.g., 2027-2028)"""
        if v is not None:
            parts = v.split("-")
            if len(parts) == 2:
                try:
                    year1, year2 = int(parts[0]), int(parts[1])
                    if year2 != year1 + 1:
                        raise ValueError(
                            "Academic year must be consecutive years (e.g., 2027-2028)"
                        )
                except ValueError:
                    raise ValueError("Invalid academic year format")
        return v

    @validator("deadline")
    def validate_deadline(cls, v, values):
        """Ensure deadline is after application_opens if both are set"""
        if (
            v is not None
            and "application_opens" in values
            and values["application_opens"] is not None
        ):
            if v < values["application_opens"]:
                raise ValueError("deadline must be after application_opens")
        return v


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

    # Financial
    amount_min: Optional[int] = Field(None, ge=0)
    amount_max: Optional[int] = Field(None, ge=0)
    is_renewable: Optional[bool] = None
    number_of_awards: Optional[int] = Field(None, ge=1)

    # Dates
    deadline: Optional[date] = None
    application_opens: Optional[date] = None
    for_academic_year: Optional[str] = Field(None, max_length=20)

    # Details
    description: Optional[str] = Field(None, max_length=500)
    website_url: Optional[str] = Field(None, max_length=500)

    # Requirements
    min_gpa: Optional[Decimal] = Field(None, ge=0, le=4.0)

    # Display
    primary_image_url: Optional[str] = Field(None, max_length=500)

    # Metadata
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
    min_gpa_filter: Optional[Decimal] = Field(None, ge=0, le=4.0)

    # Date filters
    deadline_before: Optional[date] = None
    deadline_after: Optional[date] = None
    academic_year: Optional[str] = None

    # Sorting
    sort_by: str = Field(
        "created_at",
        pattern="^(created_at|amount_min|amount_max|deadline|title|views_count)$",
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
