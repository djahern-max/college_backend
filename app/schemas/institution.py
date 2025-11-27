# app/schemas/institution.py - UPDATED WITH DATA QUALITY TRACKING
"""
Streamlined institution schemas matching the simplified model
UPDATED: Added admissions, enrollment, graduation data, and data quality tracking
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
from decimal import Decimal


class ControlType(str, Enum):
    """Institution control types"""

    PUBLIC = "PUBLIC"
    PRIVATE_NONPROFIT = "PRIVATE_NONPROFIT"
    PRIVATE_FOR_PROFIT = "PRIVATE_FOR_PROFIT"


# ===========================
# NEW: DATA QUALITY SCHEMA
# ===========================


class DataQualityInfo(BaseModel):
    """Data quality and verification information"""

    admin_verified: bool = False
    completeness_score: int = 0
    cost_data_verified: bool = False
    cost_data_verified_at: Optional[datetime] = None
    admissions_data_verified: bool = False
    admissions_data_verified_at: Optional[datetime] = None
    last_admin_update: Optional[datetime] = None
    data_freshness_days: Optional[int] = None  # Calculated field

    class Config:
        from_attributes = True


# ===========================
# NESTED DATA SCHEMAS
# ===========================


class AdmissionsSummary(BaseModel):
    """Summary of admissions data for institution response"""

    academic_year: str
    acceptance_rate: Optional[Decimal] = None

    # SAT ranges
    sat_range: Optional[str] = Field(None, description="e.g. '1050-1250'")
    sat_math_median: Optional[int] = None
    sat_reading_median: Optional[int] = None

    # ACT ranges
    act_range: Optional[str] = Field(None, description="e.g. '21-26'")
    act_composite_median: Optional[int] = None

    # Application stats
    total_applications: Optional[int] = None
    total_admitted: Optional[int] = None
    total_enrolled: Optional[int] = None

    class Config:
        from_attributes = True


class EnrollmentSummary(BaseModel):
    """Summary of enrollment data"""

    academic_year: str
    total_enrollment: Optional[int] = None
    percent_full_time: Optional[Decimal] = None
    percent_in_state: Optional[Decimal] = None

    class Config:
        from_attributes = True


class GraduationSummary(BaseModel):
    """Summary of graduation/retention data"""

    cohort_year: str
    retention_rate: Optional[Decimal] = None
    graduation_rate_6_year: Optional[Decimal] = None

    class Config:
        from_attributes = True


# ===========================
# BASE SCHEMA (UPDATED)
# ===========================


class InstitutionBase(BaseModel):
    """Base schema with common fields"""

    name: str = Field(..., min_length=1, max_length=255)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=2, max_length=2)
    control_type: ControlType
    primary_image_url: Optional[str] = Field(None, max_length=500)

    # Static institutional characteristics
    student_faculty_ratio: Optional[Decimal] = Field(
        None, description="Student-faculty ratio"
    )
    size_category: Optional[str] = Field(
        None, description="Small/Medium/Large/Very Large"
    )
    locale: Optional[str] = Field(None, description="City/Suburban/Town/Rural")


# ===========================
# CREATE SCHEMA (UPDATED)
# ===========================


class InstitutionCreate(InstitutionBase):
    """Schema for creating a new institution"""

    ipeds_id: int = Field(..., gt=0)


# ===========================
# UPDATE SCHEMA (UPDATED)
# ===========================


class InstitutionUpdate(BaseModel):
    """Schema for updating an institution - all fields optional"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    state: Optional[str] = Field(None, min_length=2, max_length=2)
    control_type: Optional[ControlType] = None
    primary_image_url: Optional[str] = Field(None, max_length=500)

    # Static characteristics
    student_faculty_ratio: Optional[Decimal] = None
    size_category: Optional[str] = None
    locale: Optional[str] = None


# ===========================
# RESPONSE SCHEMA (UPDATED)
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
# DETAILED RESPONSE WITH RELATED DATA
# ===========================


class InstitutionDetailResponse(InstitutionBase):
    """
    Complete institution details including related data
    Use this for individual institution pages
    """

    id: int
    ipeds_id: int
    created_at: datetime
    updated_at: datetime

    # Related data (optional - only included when requested)
    admissions: Optional[AdmissionsSummary] = Field(
        None, description="Latest admissions data"
    )
    enrollment: Optional[EnrollmentSummary] = Field(
        None, description="Latest enrollment data"
    )
    graduation: Optional[GraduationSummary] = Field(
        None, description="Latest graduation data"
    )

    # NEW: Data quality information
    data_quality: Optional[DataQualityInfo] = Field(
        None, description="Data verification and quality metrics"
    )

    class Config:
        from_attributes = True


# ===========================
# LIST RESPONSE (UNCHANGED)
# ===========================


class InstitutionList(BaseModel):
    """Schema for paginated institution list"""

    institutions: list[InstitutionResponse]
    total: int = Field(..., description="Total number of institutions")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Results per page")
    has_more: bool = Field(..., description="Whether more results exist")


# ===========================
# SEARCH FILTERS (UPDATED)
# ===========================


class InstitutionSearchFilter(BaseModel):
    """Search filters with new fields"""

    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)

    # Existing filters
    state: Optional[str] = Field(None, min_length=2, max_length=2)
    control_type: Optional[ControlType] = None

    # Search
    search_query: Optional[str] = None

    # Additional filters
    size_category: Optional[str] = Field(
        None, description="Small/Medium/Large/Very Large"
    )
    min_acceptance_rate: Optional[float] = Field(None, ge=0, le=100)
    max_acceptance_rate: Optional[float] = Field(None, ge=0, le=100)
    min_sat: Optional[int] = Field(None, ge=400, le=1600)
    max_sat: Optional[int] = Field(None, ge=400, le=1600)

    # Sorting (updated with new fields)
    sort_by: str = Field(
        "name",
        pattern="^(name|city|state|created_at|acceptance_rate|total_enrollment|graduation_rate_6_year)$",
    )
    sort_order: str = Field("asc", pattern="^(asc|desc)$")


# ===========================
# STATS SCHEMA (UPDATED)
# ===========================


class InstitutionStats(BaseModel):
    """Schema for institution statistics"""

    total_institutions: int
    by_control_type: dict[str, int]
    by_state: dict[str, int]
    with_images: int

    # Additional stats
    by_size_category: Optional[dict[str, int]] = None
    avg_acceptance_rate: Optional[Decimal] = None
    avg_graduation_rate: Optional[Decimal] = None

    class Config:
        from_attributes = True
