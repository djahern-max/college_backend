# app/schemas/tuition.py
"""
Simplified Pydantic schemas for tuition data API endpoints
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# Base schemas
class TuitionDataBase(BaseModel):
    """Base schema for tuition data"""

    ipeds_id: int = Field(..., description="Institution IPEDS ID")
    academic_year: str = Field(..., description="Academic year (e.g., '2025-26')")
    data_source: str = Field(..., description="Data source URL or identifier")

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

    # Living expenses
    room_board_on_campus: Optional[float] = Field(
        None, ge=0, description="On-campus room and board"
    )


class TuitionDataCreate(TuitionDataBase):
    """Schema for creating new tuition data records"""

    pass


class TuitionDataUpdate(BaseModel):
    """Schema for updating tuition data records"""

    academic_year: Optional[str] = Field(None, description="Academic year")
    data_source: Optional[str] = Field(None, description="Data source")
    tuition_in_state: Optional[float] = Field(None, ge=0)
    tuition_out_state: Optional[float] = Field(None, ge=0)
    required_fees_in_state: Optional[float] = Field(None, ge=0)
    required_fees_out_state: Optional[float] = Field(None, ge=0)
    room_board_on_campus: Optional[float] = Field(None, ge=0)


class TuitionDataResponse(TuitionDataBase):
    """Schema for tuition data API responses"""

    id: int = Field(..., description="Database record ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class TuitionDataList(BaseModel):
    """Schema for paginated tuition data list"""

    items: list[TuitionDataResponse] = Field(..., description="List of tuition records")
    total: int = Field(..., description="Total number of records")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Records per page")
    total_pages: int = Field(..., description="Total number of pages")
