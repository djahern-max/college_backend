# app/schemas/institution.py
"""
Institution schemas for MagicScholar (Student-Facing App)
Matches unified database structure
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
# NESTED DATA SCHEMAS (for compatibility with other parts of app)
# ===========================


class AdmissionsSummary(BaseModel):
    """Summary of admissions data"""

    academic_year: str
    acceptance_rate: Optional[Decimal] = None
    sat_range: Optional[str] = None
    sat_math_median: Optional[int] = None
    sat_reading_median: Optional[int] = None
    act_range: Optional[str] = None
    act_composite_median: Optional[int] = None
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
# BASE SCHEMA
# ===========================


class InstitutionBase(BaseModel):
    """Base schema with common fields"""

    name: str = Field(..., min_length=1, max_length=255)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=2, max_length=2)
    control_type: ControlType
    primary_image_url: Optional[str] = Field(None, max_length=500)
    website: Optional[str] = Field(None, max_length=500)

    # Characteristics
    student_faculty_ratio: Optional[Decimal] = None
    size_category: Optional[str] = None
    locale: Optional[str] = None


# ===========================
# RESPONSE SCHEMAS
# ===========================


class InstitutionResponse(InstitutionBase):
    """Standard institution response for public (student) endpoints"""

    # Core Identity
    id: int
    ipeds_id: int

    # Additional IPEDS fields
    level: Optional[int] = None
    control: Optional[int] = None

    # Cost Data
    tuition_in_state: Optional[Decimal] = None
    tuition_out_of_state: Optional[Decimal] = None
    tuition_private: Optional[Decimal] = None
    tuition_in_district: Optional[Decimal] = None
    room_cost: Optional[Decimal] = None
    board_cost: Optional[Decimal] = None
    room_and_board: Optional[Decimal] = None
    application_fee_undergrad: Optional[Decimal] = None
    application_fee_grad: Optional[Decimal] = None

    # Admissions Data
    acceptance_rate: Optional[Decimal] = None
    sat_reading_25th: Optional[int] = None
    sat_reading_75th: Optional[int] = None
    sat_math_25th: Optional[int] = None
    sat_math_75th: Optional[int] = None
    act_composite_25th: Optional[int] = None
    act_composite_75th: Optional[int] = None

    # Data Quality (students can see this to know data reliability)
    data_completeness_score: int
    data_source: Optional[str] = None
    ipeds_year: Optional[str] = None
    is_featured: bool
    admin_verified: bool

    # Timestamps
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InstitutionSummary(BaseModel):
    """Lightweight summary for list views (faster loading)"""

    id: int
    ipeds_id: int
    name: str
    city: str
    state: str
    control_type: ControlType
    primary_image_url: Optional[str] = None
    student_faculty_ratio: Optional[Decimal] = None
    data_completeness_score: int
    is_featured: bool

    # Key stats for preview
    tuition_in_state: Optional[Decimal] = None
    tuition_out_of_state: Optional[Decimal] = None
    acceptance_rate: Optional[Decimal] = None

    class Config:
        from_attributes = True


class InstitutionDetailResponse(InstitutionResponse):
    """
    Detailed institution response with additional computed fields.
    Use this for individual institution detail pages.
    """

    # Inherits all fields from InstitutionResponse
    # Can add computed fields here if needed in the future

    class Config:
        from_attributes = True


class PaginatedInstitutionResponse(BaseModel):
    """Paginated response wrapper"""

    institutions: list[InstitutionResponse]
    total: int
    page: int
    limit: int
    has_more: bool


# Alias for compatibility
InstitutionList = PaginatedInstitutionResponse


class InstitutionStats(BaseModel):
    """Statistics about institutions"""

    total_institutions: int
    by_control_type: dict
    by_state: dict
    with_images: int = 0

    class Config:
        from_attributes = True


class InstitutionSearchFilter(BaseModel):
    """Search filter parameters"""

    page: int = Field(1, ge=1)
    limit: int = Field(50, ge=1, le=100)
    state: Optional[str] = Field(None, min_length=2, max_length=2)
    control_type: Optional[ControlType] = None
    search_query: Optional[str] = None
    sort_by: str = Field("name", pattern="^(name|city|state|data_completeness_score)$")
    sort_order: str = Field("asc", pattern="^(asc|desc)$")


# ===========================
# CREATE/UPDATE SCHEMAS (for compatibility)
# ===========================


class InstitutionCreate(InstitutionBase):
    """Schema for creating institution (admin use only - not used in MagicScholar)"""

    ipeds_id: int = Field(..., gt=0)


class InstitutionUpdate(BaseModel):
    """Schema for updating institution (admin use only - not used in MagicScholar)"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    state: Optional[str] = Field(None, min_length=2, max_length=2)
    control_type: Optional[ControlType] = None
    primary_image_url: Optional[str] = Field(None, max_length=500)
    student_faculty_ratio: Optional[Decimal] = None
    size_category: Optional[str] = None
    locale: Optional[str] = None
