# app/schemas/enrollment.py
"""
Pydantic schemas for enrollment and graduation data
"""

from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal


# ============= ENROLLMENT SCHEMAS =============


class EnrollmentDataBase(BaseModel):
    """Base schema for enrollment data"""

    academic_year: str = Field(..., description="Academic year (e.g., 2023-24)")

    total_enrollment: Optional[int] = Field(
        None, description="Total undergraduate enrollment"
    )
    full_time_enrollment: Optional[int] = Field(
        None, description="Full-time enrollment"
    )
    part_time_enrollment: Optional[int] = Field(
        None, description="Part-time enrollment"
    )

    enrollment_men: Optional[int] = Field(None, description="Male students")
    enrollment_women: Optional[int] = Field(None, description="Female students")

    enrollment_in_state: Optional[int] = Field(None, description="In-state students")
    enrollment_out_of_state: Optional[int] = Field(
        None, description="Out-of-state students"
    )

    percent_full_time: Optional[Decimal] = Field(None, description="% full-time")
    percent_in_state: Optional[Decimal] = Field(None, description="% in-state")


class EnrollmentDataCreate(EnrollmentDataBase):
    """Schema for creating enrollment data"""

    ipeds_id: int = Field(..., description="IPEDS institution ID")


class EnrollmentDataResponse(EnrollmentDataBase):
    """Schema for enrollment data API response"""

    id: int
    ipeds_id: int

    class Config:
        from_attributes = True


class EnrollmentDataSummary(BaseModel):
    """Simplified summary for institution profile pages"""

    academic_year: str
    total_enrollment: Optional[int] = None
    percent_full_time: Optional[Decimal] = None
    percent_in_state: Optional[Decimal] = None

    class Config:
        from_attributes = True


# ============= GRADUATION SCHEMAS =============


class GraduationDataBase(BaseModel):
    """Base schema for graduation data"""

    cohort_year: str = Field(..., description="Starting cohort year")

    retention_rate: Optional[Decimal] = Field(
        None, description="First-year retention rate (%)"
    )
    graduation_rate_4_year: Optional[Decimal] = Field(
        None, description="4-year graduation rate (%)"
    )
    graduation_rate_6_year: Optional[Decimal] = Field(
        None, description="6-year graduation rate (%)"
    )
    graduation_rate_8_year: Optional[Decimal] = Field(
        None, description="8-year graduation rate (%)"
    )

    cohort_size: Optional[int] = Field(None, description="Size of entering cohort")


class GraduationDataCreate(GraduationDataBase):
    """Schema for creating graduation data"""

    ipeds_id: int = Field(..., description="IPEDS institution ID")


class GraduationDataResponse(GraduationDataBase):
    """Schema for graduation data API response"""

    id: int
    ipeds_id: int

    class Config:
        from_attributes = True


class GraduationDataSummary(BaseModel):
    """Simplified summary for institution profile pages"""

    cohort_year: str
    retention_rate: Optional[Decimal] = None
    graduation_rate_6_year: Optional[Decimal] = None

    class Config:
        from_attributes = True
