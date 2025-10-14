# app/schemas/tuition.py
"""
Pydantic schemas for tuition data API endpoints
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from app.models.tuition import ValidationStatus


class AffordabilityCategory(str, Enum):
    """Affordability categories"""

    VERY_AFFORDABLE = "VERY_AFFORDABLE"
    AFFORDABLE = "AFFORDABLE"
    MODERATE = "MODERATE"
    EXPENSIVE = "EXPENSIVE"
    VERY_EXPENSIVE = "VERY_EXPENSIVE"
    UNKNOWN = "UNKNOWN"


# Base schemas
class TuitionDataBase(BaseModel):
    """Base schema for tuition data"""

    ipeds_id: int = Field(..., description="Institution IPEDS ID")
    academic_year: str = Field("2023-24", description="Academic year")
    data_source: str = Field("IC2023_AY", description="Data source")

    # Tuition data
    tuition_in_state: Optional[float] = Field(
        None, ge=0, description="In-state tuition"
    )
    tuition_out_state: Optional[float] = Field(
        None, ge=0, description="Out-of-state tuition"
    )

    # Fees data
    required_fees_in_state: Optional[float] = Field(
        None, ge=0, description="Required fees for in-state students"
    )
    required_fees_out_state: Optional[float] = Field(
        None, ge=0, description="Required fees for out-of-state students"
    )

    # Combined tuition + fees
    tuition_fees_in_state: Optional[float] = Field(
        None, ge=0, description="In-state tuition + fees"
    )
    tuition_fees_out_state: Optional[float] = Field(
        None, ge=0, description="Out-of-state tuition + fees"
    )

    # Living expenses
    room_board_on_campus: Optional[float] = Field(
        None, ge=0, description="On-campus room and board"
    )

    # Data quality indicators
    has_tuition_data: bool = Field(False, description="Has tuition data available")
    has_fees_data: bool = Field(False, description="Has fees data available")
    has_living_data: bool = Field(
        False, description="Has living expenses data available"
    )
    data_completeness_score: int = Field(
        0, ge=0, le=100, description="Data completeness score (0-100)"
    )
    validation_status: ValidationStatus = Field(
        ValidationStatus.PENDING, description="Data validation status"
    )


class TuitionDataCreate(TuitionDataBase):
    """Schema for creating new tuition data records"""

    pass


class TuitionDataUpdate(BaseModel):
    """Schema for updating tuition data records"""

    tuition_in_state: Optional[float] = Field(None, ge=0)
    tuition_out_state: Optional[float] = Field(None, ge=0)
    required_fees_in_state: Optional[float] = Field(None, ge=0)
    required_fees_out_state: Optional[float] = Field(None, ge=0)
    tuition_fees_in_state: Optional[float] = Field(None, ge=0)
    tuition_fees_out_state: Optional[float] = Field(None, ge=0)
    room_board_on_campus: Optional[float] = Field(None, ge=0)
    has_tuition_data: Optional[bool] = None
    has_fees_data: Optional[bool] = None
    has_living_data: Optional[bool] = None
    data_completeness_score: Optional[int] = Field(None, ge=0, le=100)
    validation_status: Optional[ValidationStatus] = None


class CostBreakdown(BaseModel):
    """Detailed cost breakdown"""

    tuition_in_state: Optional[float] = None
    tuition_out_state: Optional[float] = None
    required_fees_in_state: Optional[float] = None
    required_fees_out_state: Optional[float] = None
    tuition_fees_in_state: Optional[float] = None
    tuition_fees_out_state: Optional[float] = None
    room_board_on_campus: Optional[float] = None


class TuitionProjection(BaseModel):
    """Schema for tuition projections"""

    year: str = Field(..., description="Academic year (e.g., '2024-25')")
    tuition_in_state: Optional[float] = Field(
        None, description="Projected in-state tuition"
    )
    tuition_out_state: Optional[float] = Field(
        None, description="Projected out-of-state tuition"
    )
    total_cost_in_state: Optional[float] = Field(
        None, description="Projected total cost in-state"
    )
    total_cost_out_state: Optional[float] = Field(
        None, description="Projected total cost out-of-state"
    )
    inflation_rate: float = Field(..., description="Inflation rate used for projection")


class TuitionProjectionResponse(BaseModel):
    """Response schema for tuition projections"""

    ipeds_id: int
    projections: List[TuitionProjection]
    projection_methodology: str = "Education inflation rates applied to base year data"
    base_year: str = "2023-24"


class AffordabilityAnalysis(BaseModel):
    """Schema for affordability analysis"""

    household_income: float = Field(..., gt=0, description="Annual household income")
    max_recommended_cost: float = Field(
        ..., description="Maximum recommended education cost (10% of income)"
    )
    current_total_cost: float = Field(
        ..., description="Current total cost of attendance"
    )
    is_affordable: bool = Field(
        ..., description="Whether the cost is within recommended guidelines"
    )
    percentage_of_income: float = Field(
        ..., description="Cost as percentage of household income"
    )
    over_budget_amount: float = Field(
        ..., description="Amount over recommended budget (0 if affordable)"
    )


class AffordabilityRequest(BaseModel):
    """Request schema for affordability analysis"""

    household_income: float = Field(
        ..., gt=0, description="Annual household income in USD"
    )
    residency_status: str = Field(
        "in_state", description="'in_state' or 'out_of_state'"
    )

    @validator("residency_status")
    def validate_residency(cls, v):
        if v not in ["in_state", "out_of_state"]:
            raise ValueError(
                'residency_status must be either "in_state" or "out_of_state"'
            )
        return v


class TuitionDataResponse(TuitionDataBase):
    """Schema for tuition data API responses"""

    id: int = Field(..., description="Database record ID")

    # Calculated fields
    total_cost_in_state: Optional[float] = Field(
        None, description="Total cost for in-state students"
    )
    total_cost_out_state: Optional[float] = Field(
        None, description="Total cost for out-of-state students"
    )
    affordability_category: AffordabilityCategory = Field(
        ..., description="Affordability category"
    )
    has_comprehensive_data: bool = Field(
        ..., description="Has comprehensive financial data"
    )

    # Detailed breakdown
    cost_breakdown: CostBreakdown = Field(..., description="Detailed cost breakdown")

    # Timestamps
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

        json_schema_extra = {
            "example": {
                "id": 1,
                "ipeds_id": 100654,
                "academic_year": "2024-2025",
                "data_source": "institution_website",
                "tuition_in_state": 10566,
                "tuition_out_state": 19176,
                "required_fees_in_state": None,
                "required_fees_out_state": None,
                "tuition_fees_in_state": 10566,
                "tuition_fees_out_state": 19176,
                "room_board_on_campus": 9465,
                "has_tuition_data": True,
                "has_fees_data": False,
                "has_living_data": True,
                "data_completeness_score": 100,
                "validation_status": "VALIDATED",
                "total_cost_in_state": 20031,
                "total_cost_out_state": 28641,
                "affordability_category": "AFFORDABLE",
                "has_comprehensive_data": True,
                "cost_breakdown": {
                    "tuition_in_state": 10566,
                    "tuition_out_state": 19176,
                    "required_fees_in_state": None,
                    "required_fees_out_state": None,
                    "tuition_fees_in_state": 10566,
                    "tuition_fees_out_state": 19176,
                    "room_board_on_campus": 9465,
                },
                "created_at": "2024-10-07T08:14:22",
                "updated_at": "2024-10-12T15:28:46",
            }
        }


class TuitionSearchFilters(BaseModel):
    """Schema for tuition search filters"""

    min_tuition_in_state: Optional[float] = Field(
        None, ge=0, description="Minimum in-state tuition"
    )
    max_tuition_in_state: Optional[float] = Field(
        None, ge=0, description="Maximum in-state tuition"
    )
    min_tuition_out_state: Optional[float] = Field(
        None, ge=0, description="Minimum out-of-state tuition"
    )
    max_tuition_out_state: Optional[float] = Field(
        None, ge=0, description="Maximum out-of-state tuition"
    )
    min_total_cost: Optional[float] = Field(
        None, ge=0, description="Minimum total cost"
    )
    max_total_cost: Optional[float] = Field(
        None, ge=0, description="Maximum total cost"
    )
    affordability_category: Optional[AffordabilityCategory] = Field(
        None, description="Affordability category filter"
    )
    has_comprehensive_data: Optional[bool] = Field(
        None, description="Filter by comprehensive data availability"
    )
    validation_status: Optional[ValidationStatus] = Field(
        None, description="Filter by validation status"
    )
    state: Optional[str] = Field(
        None, max_length=2, description="Institution state filter"
    )


class TuitionSearchResponse(BaseModel):
    """Schema for tuition search results"""

    filters: TuitionSearchFilters = Field(..., description="Applied search filters")
    total_count: int = Field(..., description="Total number of matching institutions")
    results: List[TuitionDataResponse] = Field(..., description="Search results")


class TuitionStatistics(BaseModel):
    """Schema for tuition statistics"""

    count: int = Field(..., description="Number of institutions")
    mean: Optional[float] = Field(None, description="Mean value")
    median: Optional[float] = Field(None, description="Median value")
    min: Optional[float] = Field(None, description="Minimum value")
    max: Optional[float] = Field(None, description="Maximum value")
    p25: Optional[float] = Field(None, description="25th percentile")
    p75: Optional[float] = Field(None, description="75th percentile")


class TuitionAnalyticsResponse(BaseModel):
    """Schema for tuition analytics"""

    dataset_info: Dict[str, Any] = Field(..., description="Dataset information")
    tuition_statistics: Dict[str, TuitionStatistics] = Field(
        ..., description="Tuition statistics by category"
    )
    affordability_distribution: Dict[AffordabilityCategory, int] = Field(
        ..., description="Count by affordability category"
    )
    data_quality_metrics: Dict[str, Any] = Field(
        ..., description="Data quality metrics"
    )


class InstitutionWithTuitionData(BaseModel):
    """Schema combining institution info with tuition data"""

    # Institution basic info
    ipeds_id: int = Field(..., description="Institution IPEDS ID")
    name: str = Field(..., description="Institution name")
    city: str = Field(..., description="City")
    state: str = Field(..., description="State")
    control_type: Optional[str] = Field(None, description="Public/Private control type")
    size_category: Optional[str] = Field(None, description="Institution size category")

    # Tuition data (optional)
    tuition_data: Optional[TuitionDataResponse] = Field(
        None, description="Tuition data if available"
    )

    # Summary fields
    has_tuition_data: bool = Field(..., description="Whether tuition data is available")
    tuition_summary: Optional[str] = Field(None, description="Brief tuition summary")


class TuitionDataList(BaseModel):
    """Schema for paginated tuition data list"""

    items: List[TuitionDataResponse] = Field(..., description="List of tuition records")
    total: int = Field(..., description="Total number of records")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Records per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_prev: bool = Field(..., description="Whether there are previous pages")


# Projection-specific schemas
class ProjectionRequest(BaseModel):
    """Request schema for generating projections"""

    years: int = Field(4, ge=1, le=10, description="Number of years to project")
    inflation_rate: Optional[float] = Field(
        None, ge=0, le=0.20, description="Custom inflation rate (0-20%)"
    )

    @validator("inflation_rate")
    def validate_inflation_rate(cls, v):
        if v is not None and (v < 0 or v > 0.20):
            raise ValueError("inflation_rate must be between 0 and 0.20 (0-20%)")
        return v


class ProjectionMethodology(BaseModel):
    """Information about projection methodology"""

    base_year: str = "2023-24"
    default_inflation_rates: Dict[int, float] = {
        2024: 0.045,
        2025: 0.042,
        2026: 0.040,
        2027: 0.038,
        2028: 0.035,
    }
    methodology_description: str = (
        "Projections use education-specific inflation rates based on historical trends"
    )
    confidence_levels: Dict[str, str] = {
        "1-2_years": "high",
        "3-5_years": "medium",
        "6+_years": "low",
    }
