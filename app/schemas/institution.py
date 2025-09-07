# app/schemas/institution.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from enum import Enum


class ControlType(str, Enum):
    """Institution control types"""

    PUBLIC = "public"
    PRIVATE_NONPROFIT = "private_nonprofit"
    PRIVATE_FOR_PROFIT = "private_for_profit"


class SizeCategory(str, Enum):
    """Institution size categories"""

    VERY_SMALL = "very_small"  # <1,000
    SMALL = "small"  # 1,000-2,999
    MEDIUM = "medium"  # 3,000-9,999
    LARGE = "large"  # 10,000-19,999
    VERY_LARGE = "very_large"  # 20,000+


class USRegion(str, Enum):
    """US Regions for institutions"""

    NEW_ENGLAND = "new_england"
    MID_ATLANTIC = "mid_atlantic"
    EAST_NORTH_CENTRAL = "east_north_central"
    WEST_NORTH_CENTRAL = "west_north_central"
    SOUTH_ATLANTIC = "south_atlantic"
    EAST_SOUTH_CENTRAL = "east_south_central"
    WEST_SOUTH_CENTRAL = "west_south_central"
    MOUNTAIN = "mountain"
    PACIFIC = "pacific"


class InstitutionBase(BaseModel):
    """Base schema for Institution with common fields"""

    name: str = Field(..., min_length=1, max_length=255, description="Institution name")
    address: Optional[str] = Field(None, max_length=500, description="Street address")
    city: str = Field(..., min_length=1, max_length=100, description="City name")
    state: str = Field(
        ..., min_length=2, max_length=2, description="Two-letter state code"
    )
    zip_code: Optional[str] = Field(None, max_length=10, description="ZIP code")
    region: Optional[USRegion] = Field(None, description="US Region")
    website: Optional[str] = Field(
        None, max_length=500, description="Institution website"
    )
    phone: Optional[float] = Field(None, description="Phone number")
    president_name: Optional[str] = Field(
        None, max_length=255, description="President/CEO name"
    )
    president_title: Optional[str] = Field(
        None, max_length=100, description="President title"
    )
    control_type: ControlType = Field(
        ..., description="Public, private nonprofit, or private for-profit"
    )
    size_category: Optional[SizeCategory] = Field(
        None, description="Institution size category"
    )

    @validator("state")
    def validate_state_code(cls, v):
        """Ensure state code is uppercase and valid format"""
        if v:
            v = v.upper()
            if len(v) != 2:
                raise ValueError("State code must be exactly 2 characters")
        return v

    @validator("website")
    def validate_website(cls, v):
        """Basic website URL validation"""
        if v and v.strip():
            v = v.strip()
            if not v.startswith(("http://", "https://")):
                v = "https://" + v
        return v if v and v != "https://" else None

    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "name": "University of New Hampshire",
                "address": "105 Main Street",
                "city": "Durham",
                "state": "NH",
                "zip_code": "03824",
                "region": "new_england",
                "website": "https://www.unh.edu",
                "president_name": "James W. Dean Jr.",
                "president_title": "President",
                "control_type": "public",
                "size_category": "large",
            }
        }


class InstitutionCreate(InstitutionBase):
    """Schema for creating a new institution"""

    ipeds_id: int = Field(..., gt=0, description="IPEDS UNITID (must be positive)")

    class Config:
        json_schema_extra = {
            "example": {
                **InstitutionBase.Config.json_schema_extra["example"],
                "ipeds_id": 130794,
            }
        }


class InstitutionUpdate(BaseModel):
    """Schema for updating an institution - all fields optional"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    state: Optional[str] = Field(None, min_length=2, max_length=2)
    zip_code: Optional[str] = Field(None, max_length=10)
    region: Optional[USRegion] = None
    website: Optional[str] = Field(None, max_length=500)
    phone: Optional[float] = None
    president_name: Optional[str] = Field(None, max_length=255)
    president_title: Optional[str] = Field(None, max_length=100)
    control_type: Optional[ControlType] = None
    size_category: Optional[SizeCategory] = None

    @validator("state")
    def validate_state_code(cls, v):
        """Ensure state code is uppercase and valid format"""
        if v:
            v = v.upper()
            if len(v) != 2:
                raise ValueError("State code must be exactly 2 characters")
        return v

    @validator("website")
    def validate_website(cls, v):
        """Basic website URL validation"""
        if v and v.strip():
            v = v.strip()
            if not v.startswith(("http://", "https://")):
                v = "https://" + v
        return v if v and v != "https://" else None


class InstitutionResponse(InstitutionBase):
    """Schema for API responses - includes all base fields plus database metadata"""

    id: int = Field(..., description="Database ID")
    ipeds_id: int = Field(..., description="IPEDS UNITID")

    # Computed properties for response
    full_address: Optional[str] = Field(None, description="Formatted full address")
    display_name: str = Field(..., description="Institution name with location")
    is_public: bool = Field(..., description="Whether institution is public")
    is_private: bool = Field(..., description="Whether institution is private")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "ipeds_id": 130794,
                "name": "University of New Hampshire",
                "address": "105 Main Street",
                "city": "Durham",
                "state": "NH",
                "zip_code": "03824",
                "region": "new_england",
                "website": "https://www.unh.edu",
                "president_name": "James W. Dean Jr.",
                "president_title": "President",
                "control_type": "public",
                "size_category": "large",
                "full_address": "105 Main Street, Durham, NH, 03824",
                "display_name": "University of New Hampshire (Durham, NH)",
                "is_public": True,
                "is_private": False,
            }
        }


class InstitutionList(BaseModel):
    """Schema for paginated institution lists"""

    institutions: list[InstitutionResponse]
    total: int = Field(..., description="Total number of institutions")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")

    class Config:
        json_schema_extra = {
            "example": {
                "institutions": [
                    InstitutionResponse.Config.json_schema_extra["example"]
                ],
                "total": 6163,
                "page": 1,
                "per_page": 50,
                "total_pages": 124,
            }
        }


class InstitutionSearch(BaseModel):
    """Schema for institution search filters"""

    name: Optional[str] = Field(None, description="Search by institution name")
    state: Optional[str] = Field(None, description="Filter by state code")
    city: Optional[str] = Field(None, description="Filter by city")
    region: Optional[USRegion] = Field(None, description="Filter by US region")
    control_type: Optional[ControlType] = Field(
        None, description="Filter by control type"
    )
    size_category: Optional[SizeCategory] = Field(
        None, description="Filter by size category"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "University",
                "state": "NH",
                "region": "new_england",
                "control_type": "public",
                "size_category": "large",
            }
        }
