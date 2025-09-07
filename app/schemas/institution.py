# app/schemas/institution.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from enum import Enum
from datetime import datetime


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
    phone: Optional[str] = None
    president_name: Optional[str] = Field(None, max_length=255)
    president_title: Optional[str] = Field(None, max_length=100)
    control_type: Optional[ControlType] = None
    size_category: Optional[SizeCategory] = None
    # Image fields for updates
    primary_image_url: Optional[str] = Field(
        None, max_length=500, description="CDN URL to primary image"
    )
    primary_image_quality_score: Optional[int] = Field(
        None, ge=0, le=100, description="Image quality score 0-100"
    )
    logo_image_url: Optional[str] = Field(
        None, max_length=500, description="CDN URL to logo image"
    )
    image_extraction_status: Optional[ImageExtractionStatus] = Field(
        None, description="Image extraction status"
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


class InstitutionResponse(InstitutionBase):
    """Schema for API responses - includes all base fields plus database metadata"""

    id: int = Field(..., description="Database ID")
    ipeds_id: int = Field(..., description="IPEDS UNITID")

    # Image fields
    primary_image_url: Optional[str] = Field(
        None, description="CDN URL to standardized 400x300px image"
    )
    primary_image_quality_score: Optional[int] = Field(
        None, description="Image quality score 0-100"
    )
    logo_image_url: Optional[str] = Field(None, description="CDN URL to school logo")
    image_extraction_status: Optional[ImageExtractionStatus] = Field(
        None, description="Image extraction status"
    )
    image_extraction_date: Optional[datetime] = Field(
        None, description="When images were last processed"
    )

    # Computed properties for response
    full_address: Optional[str] = Field(None, description="Formatted full address")
    display_name: str = Field(..., description="Institution name with location")
    is_public: bool = Field(..., description="Whether institution is public")
    is_private: bool = Field(..., description="Whether institution is private")
    display_image_url: Optional[str] = Field(
        None, description="Best available image URL for display"
    )
    has_high_quality_image: bool = Field(
        False, description="Whether institution has high-quality image (80+ score)"
    )
    has_good_image: bool = Field(
        False, description="Whether institution has good image (60+ score)"
    )
    image_needs_attention: bool = Field(
        False, description="Whether image needs manual review"
    )

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
                "primary_image_url": "https://magicscholar-images.nyc3.digitaloceanspaces.com/primary/unh_campus.jpg",
                "primary_image_quality_score": 85,
                "logo_image_url": "https://magicscholar-images.nyc3.digitaloceanspaces.com/logos/unh_logo.jpg",
                "image_extraction_status": "success",
                "image_extraction_date": "2024-01-15T10:30:00",
                "full_address": "105 Main Street, Durham, NH, 03824",
                "display_name": "University of New Hampshire (Durham, NH)",
                "is_public": True,
                "is_private": False,
                "display_image_url": "https://magicscholar-images.nyc3.digitaloceanspaces.com/primary/unh_campus.jpg",
                "has_high_quality_image": True,
                "has_good_image": True,
                "image_needs_attention": False,
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
    # Image-based filters
    min_image_quality: Optional[int] = Field(
        None, ge=0, le=100, description="Minimum image quality score"
    )
    has_image: Optional[bool] = Field(
        None, description="Filter by whether institution has an image"
    )
    image_status: Optional[ImageExtractionStatus] = Field(
        None, description="Filter by image extraction status"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "University",
                "state": "NH",
                "region": "new_england",
                "control_type": "public",
                "size_category": "large",
                "min_image_quality": 60,
                "has_image": True,
                "image_status": "success",
            }
        }


class ImageUpdateRequest(BaseModel):
    """Schema for updating institution image information"""

    primary_image_url: str = Field(
        ..., max_length=500, description="CDN URL to primary image"
    )
    primary_image_quality_score: int = Field(
        ..., ge=0, le=100, description="Image quality score 0-100"
    )
    logo_image_url: Optional[str] = Field(
        None, max_length=500, description="CDN URL to logo image"
    )
    image_extraction_status: ImageExtractionStatus = Field(
        ImageExtractionStatus.SUCCESS, description="Image extraction status"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "primary_image_url": "https://magicscholar-images.nyc3.digitaloceanspaces.com/primary/school_image.jpg",
                "primary_image_quality_score": 85,
                "logo_image_url": "https://magicscholar-images.nyc3.digitaloceanspaces.com/logos/school_logo.jpg",
                "image_extraction_status": "success",
            }
        }


class InstitutionImageStats(BaseModel):
    """Schema for institution image statistics"""

    total_institutions: int
    with_images: int
    with_high_quality_images: int  # 80+ score
    with_good_images: int  # 60+ score
    needs_review: int
    by_status: dict[str, int]
    avg_quality_score: Optional[float]

    class Config:
        json_schema_extra = {
            "example": {
                "total_institutions": 6163,
                "with_images": 4200,
                "with_high_quality_images": 1500,
                "with_good_images": 3200,
                "needs_review": 450,
                "by_status": {
                    "success": 4200,
                    "failed": 300,
                    "needs_review": 450,
                    "pending": 1213,
                },
                "avg_quality_score": 68.5,
            }
        }
