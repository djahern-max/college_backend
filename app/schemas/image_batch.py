# app/schemas/image_batch.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class ImageData(BaseModel):
    """Schema for individual image data"""

    data: bytes = Field(..., description="Image data as bytes")
    type: str = Field(..., description="Image type (og_image, hero, logo, etc.)")
    width: int = Field(..., description="Original image width")
    height: int = Field(..., description="Original image height")
    size_bytes: int = Field(..., description="Original file size in bytes")


class InstitutionImageBatch(BaseModel):
    """Schema for a single institution's image data"""

    ipeds_id: int = Field(..., description="IPEDS ID of the institution")
    name: str = Field(..., description="Institution name")
    images: Dict[str, ImageData] = Field(
        ..., description="Dictionary of image data (primary, logo, etc.)"
    )


class BatchUploadRequest(BaseModel):
    """Schema for batch upload request"""

    institutions: List[InstitutionImageBatch] = Field(
        ..., description="List of institutions with image data"
    )
    batch_name: Optional[str] = Field(None, description="Optional name for this batch")

    class Config:
        json_schema_extra = {
            "example": {
                "batch_name": "Alabama Universities Batch 1",
                "institutions": [
                    {
                        "ipeds_id": 100654,
                        "name": "Alabama A & M University",
                        "images": {
                            "primary": {
                                "data": "base64_encoded_image_data",
                                "type": "og_image",
                                "width": 1200,
                                "height": 630,
                                "size_bytes": 150000,
                            },
                            "logo": {
                                "data": "base64_encoded_logo_data",
                                "type": "logo",
                                "width": 400,
                                "height": 400,
                                "size_bytes": 25000,
                            },
                        },
                    }
                ],
            }
        }


class BatchUploadResponse(BaseModel):
    """Schema for batch upload response"""

    success: bool = Field(
        ..., description="Whether the batch was processed successfully"
    )
    processed: int = Field(
        ..., description="Number of institutions processed successfully"
    )
    failed: int = Field(..., description="Number of institutions that failed")
    batch_id: Optional[str] = Field(None, description="Unique batch identifier")
    uploaded_urls: Dict[int, Dict[str, Any]] = Field(
        ..., description="Mapping of IPEDS ID to uploaded image URLs"
    )
    errors: List[str] = Field(
        default_factory=list, description="List of error messages"
    )
    processing_time: float = Field(
        ..., description="Time taken to process batch in seconds"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "processed": 5,
                "failed": 0,
                "batch_id": "batch_20241215_001",
                "uploaded_urls": {
                    100654: {
                        "primary_url": "https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/primary/Alabama_A_M_University_q90_og_image.jpg",
                        "logo_url": "https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/logos/Alabama_A_M_University_q45_logo.jpg",
                        "quality_score": 90,
                    }
                },
                "errors": [],
                "processing_time": 45.2,
            }
        }


class ProcessingStats(BaseModel):
    """Schema for processing statistics"""

    total_institutions: int = Field(..., description="Total number of institutions")
    with_images: int = Field(..., description="Number of institutions with images")
    high_quality_images: int = Field(
        ..., description="Number with high quality images (80+ score)"
    )
    pending_processing: int = Field(..., description="Number pending processing")
    completion_rate: str = Field(..., description="Percentage completion rate")

    class Config:
        json_schema_extra = {
            "example": {
                "total_institutions": 6163,
                "with_images": 1250,
                "high_quality_images": 856,
                "pending_processing": 4913,
                "completion_rate": "20.3%",
            }
        }


class ImageQualityFilter(BaseModel):
    """Schema for filtering institutions by image quality"""

    min_quality_score: Optional[int] = Field(
        None, ge=0, le=100, description="Minimum quality score"
    )
    max_quality_score: Optional[int] = Field(
        None, ge=0, le=100, description="Maximum quality score"
    )
    has_primary_image: Optional[bool] = Field(
        None, description="Filter by primary image presence"
    )
    has_logo: Optional[bool] = Field(None, description="Filter by logo presence")
    extraction_status: Optional[str] = Field(
        None, description="Filter by extraction status"
    )


class ImageProcessingStatus(BaseModel):
    """Schema for individual institution processing status"""

    ipeds_id: int = Field(..., description="IPEDS ID")
    name: str = Field(..., description="Institution name")
    primary_image_url: Optional[str] = Field(None, description="Primary image URL")
    primary_image_quality_score: Optional[int] = Field(
        None, description="Quality score"
    )
    logo_image_url: Optional[str] = Field(None, description="Logo image URL")
    image_extraction_status: Optional[str] = Field(
        None, description="Processing status"
    )
    image_extraction_date: Optional[datetime] = Field(
        None, description="Last processing date"
    )

    class Config:
        from_attributes = True
