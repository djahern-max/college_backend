from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from app.models.scholarship import ScholarshipStatus, ScholarshipType


class ScholarshipBase(BaseModel):
    """Base scholarship schema with common fields"""
    title: str = Field(..., min_length=1, max_length=255, description="Scholarship title")
    description: Optional[str] = Field(None, description="Detailed description")
    provider: str = Field(..., min_length=1, max_length=255, description="Organization providing scholarship")
    
    # Financial fields
    amount_min: Optional[Decimal] = Field(None, ge=0, description="Minimum award amount")
    amount_max: Optional[Decimal] = Field(None, ge=0, description="Maximum award amount")
    amount_exact: Optional[Decimal] = Field(None, ge=0, description="Exact award amount")
    renewable: bool = Field(default=False, description="Whether scholarship is renewable")
    max_renewals: Optional[str] = Field(None, max_length=50, description="Maximum renewal period")
    
    # Dates
    deadline: Optional[date] = Field(None, description="Application deadline")
    start_date: Optional[date] = Field(None, description="Scholarship period start")
    end_date: Optional[date] = Field(None, description="Scholarship period end")
    
    # Contact and application
    application_url: Optional[str] = Field(None, max_length=500, description="Application URL")
    contact_email: Optional[str] = Field(None, max_length=255, description="Contact email")
    contact_phone: Optional[str] = Field(None, max_length=20, description="Contact phone")
    
    # Criteria (as JSON objects)
    eligibility_criteria: Optional[Dict[str, Any]] = Field(None, description="Eligibility requirements")
    required_documents: Optional[List[str]] = Field(None, description="Required documents")
    academic_requirements: Optional[Dict[str, Any]] = Field(None, description="Academic requirements")
    demographic_criteria: Optional[Dict[str, Any]] = Field(None, description="Demographic requirements")
    
    # Classification
    categories: Optional[List[str]] = Field(None, description="Scholarship categories")
    scholarship_type: ScholarshipType = Field(default=ScholarshipType.MERIT, description="Type of scholarship")
    keywords: Optional[List[str]] = Field(None, description="Search keywords")
    
    @field_validator('amount_max')
    @classmethod
    def validate_amount_range(cls, v, info):
        """Ensure max amount is greater than min amount"""
        if v is not None and 'amount_min' in info.data and info.data['amount_min'] is not None:
            if v < info.data['amount_min']:
                raise ValueError('Maximum amount must be greater than or equal to minimum amount')
        return v
    
    @field_validator('end_date')
    @classmethod
    def validate_date_range(cls, v, info):
        """Ensure end date is after start date"""
        if v is not None and 'start_date' in info.data and info.data['start_date'] is not None:
            if v < info.data['start_date']:
                raise ValueError('End date must be after start date')
        return v


class ScholarshipCreate(ScholarshipBase):
    """Schema for creating a new scholarship"""
    # All fields from base, no additional requirements for creation
    pass


class ScholarshipUpdate(BaseModel):
    """Schema for updating a scholarship (all fields optional)"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    provider: Optional[str] = Field(None, min_length=1, max_length=255)
    
    amount_min: Optional[Decimal] = Field(None, ge=0)
    amount_max: Optional[Decimal] = Field(None, ge=0)
    amount_exact: Optional[Decimal] = Field(None, ge=0)
    renewable: Optional[bool] = None
    max_renewals: Optional[str] = Field(None, max_length=50)
    
    deadline: Optional[date] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    
    application_url: Optional[str] = Field(None, max_length=500)
    contact_email: Optional[str] = Field(None, max_length=255)
    contact_phone: Optional[str] = Field(None, max_length=20)
    
    eligibility_criteria: Optional[Dict[str, Any]] = None
    required_documents: Optional[List[str]] = None
    academic_requirements: Optional[Dict[str, Any]] = None
    demographic_criteria: Optional[Dict[str, Any]] = None
    
    categories: Optional[List[str]] = None
    scholarship_type: Optional[ScholarshipType] = None
    keywords: Optional[List[str]] = None
    
    status: Optional[ScholarshipStatus] = None
    verified: Optional[bool] = None


class ScholarshipResponse(ScholarshipBase):
    """Schema for scholarship responses"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    status: ScholarshipStatus
    external_id: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    verified: bool
    last_verified: Optional[date] = None
    application_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class ScholarshipSearch(BaseModel):
    """Schema for scholarship search parameters"""
    query: Optional[str] = Field(None, description="Search query for title/description")
    provider: Optional[str] = Field(None, description="Filter by provider")
    scholarship_type: Optional[ScholarshipType] = Field(None, description="Filter by type")
    categories: Optional[List[str]] = Field(None, description="Filter by categories")
    
    # Financial filters
    min_amount: Optional[Decimal] = Field(None, ge=0, description="Minimum award amount")
    max_amount: Optional[Decimal] = Field(None, ge=0, description="Maximum award amount")
    
    # Date filters
    deadline_after: Optional[date] = Field(None, description="Deadline after this date")
    deadline_before: Optional[date] = Field(None, description="Deadline before this date")
    
    # Status filters
    status: Optional[ScholarshipStatus] = Field(None, description="Filter by status")
    verified_only: bool = Field(default=False, description="Show only verified scholarships")
    renewable_only: bool = Field(default=False, description="Show only renewable scholarships")
    
    # Pagination
    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=50, ge=1, le=100, description="Number of records to return")
    
    # Sorting
    sort_by: str = Field(default="created_at", description="Field to sort by")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$", description="Sort order")


class ScholarshipSummary(BaseModel):
    """Schema for scholarship summary/list view"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    provider: str
    amount_min: Optional[Decimal] = None
    amount_max: Optional[Decimal] = None
    amount_exact: Optional[Decimal] = None
    deadline: Optional[date] = None
    scholarship_type: ScholarshipType
    categories: Optional[List[str]] = None
    verified: bool
    
    # 🔧 ADD THESE MISSING FIELDS:
    renewable: bool = False
    application_url: Optional[str] = Field(None, max_length=500)
    contact_email: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    created_at: datetime