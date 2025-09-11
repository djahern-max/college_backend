# app/schemas/institution.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from enum import Enum
from datetime import datetime
from pydantic import computed_field


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


class ImageExtractionStatus(str, Enum):
    """Status of image extraction process"""

    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"
    FALLBACK_APPLIED = "fallback_applied"


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
    phone: Optional[str] = Field(None, description="Phone number")
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


class InstitutionCreate(BaseModel):
    """Schema for creating new institutions - matches your database schema"""

    ipeds_id: int = Field(..., description="IPEDS ID")
    name: str = Field(..., min_length=1, max_length=255, description="Institution name")
    city: str = Field(..., min_length=1, max_length=100, description="City")
    state: str = Field(..., min_length=2, max_length=2, description="State code")
    control_type: ControlType = Field(..., description="Control type")

    # Optional fields that match your database
    address: Optional[str] = Field(None, max_length=500, description="Street address")
    zip_code: Optional[str] = Field(None, max_length=10, description="ZIP code")
    region: Optional[USRegion] = Field(None, description="US Region")
    website: Optional[str] = Field(None, max_length=500, description="Website URL")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    president_name: Optional[str] = Field(
        None, max_length=255, description="President name"
    )
    president_title: Optional[str] = Field(
        None, max_length=100, description="President title"
    )
    size_category: Optional[SizeCategory] = Field(None, description="Size category")
    customer_rank: Optional[int] = Field(
        None, ge=0, le=100, description="Customer ranking"
    )


class InstitutionUpdate(BaseModel):
    """Schema for updating institutions - matches your database schema"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    state: Optional[str] = Field(None, min_length=2, max_length=2)
    zip_code: Optional[str] = Field(None, max_length=10)
    region: Optional[USRegion] = None
    website: Optional[str] = Field(None, max_length=500)
    phone: Optional[str] = Field(None, max_length=20)
    president_name: Optional[str] = Field(None, max_length=255)
    president_title: Optional[str] = Field(None, max_length=100)
    control_type: Optional[ControlType] = None
    size_category: Optional[SizeCategory] = None
    customer_rank: Optional[int] = Field(
        None, ge=0, le=100, description="Customer ranking"
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


class CustomerRankUpdate(BaseModel):
    """Schema for updating customer rank only"""

    customer_rank: int = Field(..., ge=0, le=100, description="New customer ranking")


class InstitutionResponse(BaseModel):
    """Schema for institution API responses with customer ranking"""

    id: int = Field(..., description="Unique institution ID")
    ipeds_id: int = Field(..., description="IPEDS ID")
    name: str = Field(..., description="Institution name")
    address: Optional[str] = Field(None, description="Street address")
    city: str = Field(..., description="City")
    state: str = Field(..., description="State code")
    zip_code: Optional[str] = Field(None, description="ZIP code")
    region: Optional[USRegion] = Field(None, description="US Region")
    website: Optional[str] = Field(None, description="Website URL")
    phone: Optional[str] = Field(None, description="Phone number")
    president_name: Optional[str] = Field(None, description="President name")
    president_title: Optional[str] = Field(None, description="President title")
    control_type: ControlType = Field(..., description="Control type")
    size_category: Optional[SizeCategory] = Field(None, description="Size category")

    # Image and ranking fields
    primary_image_url: Optional[str] = Field(None, description="Primary image URL")
    primary_image_quality_score: Optional[int] = Field(
        None, ge=0, le=100, description="Image quality score"
    )
    customer_rank: Optional[int] = Field(
        None,
        description="Customer ranking for advertising priority (higher = better placement)",
    )
    logo_image_url: Optional[str] = Field(None, description="Logo image URL")
    image_extraction_status: Optional[ImageExtractionStatus] = Field(
        None, description="Image extraction status"
    )
    image_extraction_date: Optional[datetime] = Field(
        None, description="When images were last extracted/updated"
    )

    # Computed fields for frontend convenience
    @computed_field
    @property
    def display_name(self) -> str:
        """Formatted display name"""
        return self.name

    @computed_field
    @property
    def display_image_url(self) -> Optional[str]:
        """Best available image URL for display"""
        return self.primary_image_url

    @computed_field
    @property
    def full_address(self) -> str:
        """Full address string"""
        return f"{self.city}, {self.state}"

    @computed_field
    @property
    def has_high_quality_image(self) -> bool:
        """Whether institution has high quality image"""
        return (
            self.primary_image_quality_score is not None
            and self.primary_image_quality_score >= 80
        )

    @computed_field
    @property
    def has_good_image(self) -> bool:
        """Whether institution has good quality image"""
        return (
            self.primary_image_quality_score is not None
            and self.primary_image_quality_score >= 60
        )

    @computed_field
    @property
    def is_premium_customer(self) -> bool:
        """Whether institution is a premium advertising customer"""
        return self.customer_rank is not None and self.customer_rank >= 80

    @computed_field
    @property
    def is_public(self) -> bool:
        """Whether institution is public"""
        return self.control_type == ControlType.PUBLIC

    @computed_field
    @property
    def is_private(self) -> bool:
        """Whether institution is private"""
        return self.control_type in [
            ControlType.PRIVATE_NONPROFIT,
            ControlType.PRIVATE_FOR_PROFIT,
        ]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "ipeds_id": 100654,
                "name": "University of New Hampshire-Main Campus",
                "address": "105 Main Street",
                "city": "Durham",
                "state": "NH",
                "zip_code": "03824",
                "region": "NEW_ENGLAND",
                "website": "https://unh.edu",
                "phone": "(603) 862-1234",
                "president_name": "James W. Dean Jr.",
                "president_title": "President",
                "control_type": "public",
                "size_category": "large",
                "primary_image_url": "https://example.com/unh_campus.jpg",
                "primary_image_quality_score": 85,
                "customer_rank": 90,  # Premium customer
                "logo_image_url": "https://example.com/unh_logo.jpg",
                "image_extraction_status": "SUCCESS",
                "image_extraction_date": "2024-09-09T12:00:00",
                "display_name": "University of New Hampshire-Main Campus",
                "display_image_url": "https://example.com/unh_campus.jpg",
                "full_address": "Durham, NH",
                "has_high_quality_image": True,
                "has_good_image": True,
                "is_premium_customer": True,
                "is_public": True,
                "is_private": False,
            }
        }


class InstitutionSearch(BaseModel):
    """Schema for institution search filters"""

    # Generic search query (searches across name, city, state)
    query: Optional[str] = Field(
        None, description="Search across name, city, and state"
    )

    # Specific field searches (for advanced filtering)
    name: Optional[str] = Field(None, description="Search by institution name")
    state: Optional[str] = Field(None, description="Filter by state code")
    city: Optional[str] = Field(None, description="Filter by city")
    region: Optional[str] = Field(None, description="Filter by US region")
    control_type: Optional[str] = Field(None, description="Filter by control type")
    size_category: Optional[str] = Field(None, description="Filter by size category")

    # Image-based filters
    min_image_quality: Optional[int] = Field(
        None, ge=0, le=100, description="Minimum image quality score"
    )
    has_image: Optional[bool] = Field(None, description="Filter by image availability")
    image_status: Optional[str] = Field(
        None, description="Filter by image extraction status"
    )


class ImageUpdateRequest(BaseModel):
    """Schema for updating institution image information"""

    primary_image_url: Optional[str] = Field(None, description="Primary image URL")
    primary_image_quality_score: Optional[int] = Field(
        None, ge=0, le=100, description="Image quality score"
    )
    logo_image_url: Optional[str] = Field(None, description="Logo image URL")
    image_extraction_status: Optional[ImageExtractionStatus] = Field(
        None, description="Image extraction status"
    )


class InstitutionImageStats(BaseModel):
    """Schema for institution image statistics"""

    total_institutions: int
    with_images: int
    with_high_quality_images: int
    with_good_images: int
    needs_review: int
    by_status: dict
    avg_quality_score: Optional[float]


class InstitutionList(BaseModel):
    """Schema for paginated institution lists"""

    institutions: List[InstitutionResponse]
    total: int = Field(..., description="Total number of institutions")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")

    class Config:
        json_schema_extra = {
            "example": {
                "institutions": [
                    # Would contain InstitutionResponse objects
                ],
                "total": 6163,
                "page": 1,
                "per_page": 50,
                "total_pages": 124,
            }
        }


from typing import List
