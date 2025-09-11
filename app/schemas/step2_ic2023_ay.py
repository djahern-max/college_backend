# app/schemas/step2_ic2023_ay.py
"""
Fixed Pydantic schemas for Step2_IC2023_AY financial data
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class ValidationStatus(str, Enum):
    PENDING = "pending"
    VALID = "valid"
    ISSUES = "issues"
    CLEAN = "clean"  # Added this to match your data


class Step2_IC2023_AYBase(BaseModel):
    """Base schema for Step2_IC2023_AY financial data"""

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
    required_fees: Optional[float] = Field(None, ge=0, description="Required fees")
    tuition_fees_in_state: Optional[float] = Field(
        None, ge=0, description="In-state tuition + fees"
    )
    tuition_fees_out_state: Optional[float] = Field(
        None, ge=0, description="Out-of-state tuition + fees"
    )

    # Room & board
    room_board_on_campus: Optional[float] = Field(
        None, ge=0, description="On-campus room and board"
    )
    room_board_off_campus: Optional[float] = Field(
        None, ge=0, description="Off-campus room and board"
    )

    # Other costs
    books_supplies: Optional[float] = Field(
        None, ge=0, description="Books and supplies"
    )
    personal_expenses: Optional[float] = Field(
        None, ge=0, description="Personal expenses"
    )
    transportation: Optional[float] = Field(
        None, ge=0, description="Transportation costs"
    )

    # Data quality
    has_tuition_data: bool = Field(False, description="Has tuition data available")
    has_fees_data: bool = Field(False, description="Has fees data available")
    data_completeness_score: int = Field(
        0, ge=0, le=100, description="Data completeness score (0-100)"
    )
    validation_status: ValidationStatus = Field(
        ValidationStatus.PENDING, description="Data validation status"
    )
    validation_issues: Optional[str] = Field(None, description="Any validation issues")


class Step2_IC2023_AYResponse(Step2_IC2023_AYBase):
    """Schema for Step2_IC2023_AY API responses"""

    id: int = Field(..., description="Database record ID")

    # Computed fields
    total_cost_in_state: Optional[float] = Field(
        None, description="Total cost for in-state students"
    )
    total_cost_out_state: Optional[float] = Field(
        None, description="Total cost for out-of-state students"
    )
    has_comprehensive_data: bool = Field(
        False, description="Has comprehensive financial data"
    )

    # Cost breakdown for display - MADE OPTIONAL
    cost_breakdown: Optional[Dict[str, Optional[float]]] = Field(
        None, description="Breakdown of all costs"
    )

    # Timestamps
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Step2_IC2023_AYCreate(Step2_IC2023_AYBase):
    """Schema for creating new Step2_IC2023_AY records"""

    pass


class Step2_IC2023_AYUpdate(BaseModel):
    """Schema for updating Step2_IC2023_AY records"""

    tuition_in_state: Optional[float] = Field(None, ge=0)
    tuition_out_state: Optional[float] = Field(None, ge=0)
    required_fees: Optional[float] = Field(None, ge=0)
    tuition_fees_in_state: Optional[float] = Field(None, ge=0)
    tuition_fees_out_state: Optional[float] = Field(None, ge=0)
    room_board_on_campus: Optional[float] = Field(None, ge=0)
    room_board_off_campus: Optional[float] = Field(None, ge=0)
    books_supplies: Optional[float] = Field(None, ge=0)
    personal_expenses: Optional[float] = Field(None, ge=0)
    transportation: Optional[float] = Field(None, ge=0)
    has_tuition_data: Optional[bool] = None
    has_fees_data: Optional[bool] = None
    data_completeness_score: Optional[int] = Field(None, ge=0, le=100)
    validation_status: Optional[ValidationStatus] = None
    validation_issues: Optional[str] = None


class Step2_IC2023_AYSummary(BaseModel):
    """Simplified financial summary for institution cards"""

    tuition_in_state: Optional[float] = Field(None, description="In-state tuition")
    tuition_out_state: Optional[float] = Field(None, description="Out-of-state tuition")
    total_cost_in_state: Optional[float] = Field(
        None, description="Total cost for in-state students"
    )
    total_cost_out_state: Optional[float] = Field(
        None, description="Total cost for out-of-state students"
    )
    room_board: Optional[float] = Field(None, description="Room and board costs")
    has_comprehensive_data: bool = Field(
        False, description="Has comprehensive financial data"
    )

    class Config:
        from_attributes = True


class Step2_IC2023_AYSearch(BaseModel):
    """Schema for searching Step2_IC2023_AY records"""

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
    has_financial_data: Optional[bool] = Field(
        None, description="Filter institutions with financial data"
    )
    validation_status: Optional[ValidationStatus] = Field(
        None, description="Filter by validation status"
    )
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=1000, description="Number of records to return")


class Step2_IC2023_AYStats(BaseModel):
    """Schema for financial statistics"""

    total_institutions_with_data: int = Field(
        ..., description="Total institutions with financial data"
    )
    avg_tuition_in_state: Optional[float] = Field(
        None, description="Average in-state tuition"
    )
    avg_tuition_out_state: Optional[float] = Field(
        None, description="Average out-of-state tuition"
    )
    median_tuition_in_state: Optional[float] = Field(
        None, description="Median in-state tuition"
    )
    median_tuition_out_state: Optional[float] = Field(
        None, description="Median out-of-state tuition"
    )
    avg_total_cost_in_state: Optional[float] = Field(
        None, description="Average total cost in-state"
    )
    avg_total_cost_out_state: Optional[float] = Field(
        None, description="Average total cost out-of-state"
    )
    cost_ranges: Dict[str, Dict[str, float]] = Field(
        default_factory=dict, description="Cost ranges by percentile"
    )
    validation_breakdown: Dict[str, int] = Field(
        default_factory=dict, description="Count by validation status"
    )


class Step2_IC2023_AYList(BaseModel):
    """Schema for paginated list of Step2_IC2023_AY records"""

    items: List[Step2_IC2023_AYResponse] = Field(
        ..., description="List of financial records"
    )
    total: int = Field(..., description="Total number of records")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Records per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_prev: bool = Field(..., description="Whether there are previous pages")


class InstitutionWithFinancialData(BaseModel):
    """Schema for institution data combined with financial data"""

    # Institution basic info
    ipeds_id: int = Field(..., description="Institution IPEDS ID")
    name: str = Field(..., description="Institution name")
    city: str = Field(..., description="City")
    state: str = Field(..., description="State")
    control_type: str = Field(..., description="Public/Private control type")

    # Financial data (optional - may not exist for all institutions)
    financial_data: Optional[Step2_IC2023_AYResponse] = Field(
        None, description="Financial data if available"
    )

    # Combined display data
    has_financial_data: bool = Field(
        ..., description="Whether financial data is available"
    )
    financial_summary: Optional[str] = Field(
        None, description="Brief financial summary"
    )
