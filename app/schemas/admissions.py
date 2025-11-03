# app/schemas/admissions.py
"""
Pydantic schemas for admissions data API responses
"""

from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal


class AdmissionsDataBase(BaseModel):
    """Base schema for admissions data"""

    academic_year: str = Field(..., description="Academic year (e.g., 2023-24)")

    # Application numbers
    applications_total: Optional[int] = Field(
        None, description="Total applications received"
    )
    admissions_total: Optional[int] = Field(None, description="Total students admitted")
    enrolled_total: Optional[int] = Field(None, description="Total students enrolled")

    # Rates
    acceptance_rate: Optional[Decimal] = Field(None, description="Acceptance rate (%)")
    yield_rate: Optional[Decimal] = Field(None, description="Yield rate (%)")

    # SAT scores
    sat_reading_25th: Optional[int] = Field(
        None, description="SAT Reading 25th percentile"
    )
    sat_reading_50th: Optional[int] = Field(None, description="SAT Reading median")
    sat_reading_75th: Optional[int] = Field(
        None, description="SAT Reading 75th percentile"
    )
    sat_math_25th: Optional[int] = Field(None, description="SAT Math 25th percentile")
    sat_math_50th: Optional[int] = Field(None, description="SAT Math median")
    sat_math_75th: Optional[int] = Field(None, description="SAT Math 75th percentile")

    # Test submission rates
    percent_submitting_sat: Optional[Decimal] = Field(
        None, description="% submitting SAT"
    )


class AdmissionsDataCreate(AdmissionsDataBase):
    """Schema for creating admissions data"""

    ipeds_id: int = Field(..., description="IPEDS institution ID")


class AdmissionsDataResponse(AdmissionsDataBase):
    """Schema for admissions data API response"""

    id: int
    ipeds_id: int

    class Config:
        from_attributes = True


class AdmissionsDataSummary(BaseModel):
    """Simplified summary for institution profile pages"""

    academic_year: str
    acceptance_rate: Optional[Decimal] = None

    # SAT range (middle 50%)
    sat_range: Optional[str] = Field(None, description="SAT range e.g. '1050-1250'")
    sat_math_median: Optional[int] = None
    sat_reading_median: Optional[int] = None

    # ACT range (middle 50%)
    act_range: Optional[str] = Field(None, description="ACT range e.g. '21-26'")
    act_composite_median: Optional[int] = None

    # Application stats
    total_applications: Optional[int] = None
    total_admitted: Optional[int] = None
    total_enrolled: Optional[int] = None

    class Config:
        from_attributes = True
