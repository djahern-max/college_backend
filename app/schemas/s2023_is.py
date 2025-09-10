# app/schemas/s2023_is.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from enum import Enum


class DiversityCategory(str, Enum):
    HIGH = "High"
    MODERATE = "Moderate"
    LOW = "Low"


class FacultySizeCategory(str, Enum):
    VERY_SMALL = "Very Small"
    SMALL = "Small"
    MEDIUM = "Medium"
    LARGE = "Large"
    VERY_LARGE = "Very Large"


class S2023_ISBase(BaseModel):
    """Base schema for S2023_IS faculty metrics"""

    unitid: str = Field(..., description="Institution UNITID")
    total_faculty: int = Field(..., ge=0, description="Total faculty count")
    female_faculty_percent: float = Field(
        ..., ge=0, le=100, description="Percentage of female faculty"
    )
    male_faculty_percent: float = Field(
        ..., ge=0, le=100, description="Percentage of male faculty"
    )
    diversity_category: DiversityCategory = Field(
        ..., description="Faculty diversity category"
    )
    faculty_size_category: FacultySizeCategory = Field(
        ..., description="Faculty size category"
    )
    faculty_description: str = Field(
        ..., description="Human-readable faculty description"
    )
    diversity_index: float = Field(..., ge=0, le=1, description="Diversity index (0-1)")
    asian_faculty_percent: float = Field(
        ..., ge=0, le=100, description="Percentage of Asian faculty"
    )
    black_faculty_percent: float = Field(
        ..., ge=0, le=100, description="Percentage of Black faculty"
    )
    hispanic_faculty_percent: float = Field(
        ..., ge=0, le=100, description="Percentage of Hispanic faculty"
    )
    white_faculty_percent: float = Field(
        ..., ge=0, le=100, description="Percentage of White faculty"
    )

    @validator("female_faculty_percent", "male_faculty_percent")
    def validate_gender_percentages(cls, v, values):
        """Ensure gender percentages are reasonable"""
        if "female_faculty_percent" in values and "male_faculty_percent" in values:
            total = values.get("female_faculty_percent", 0) + v
            if abs(total - 100) > 1:  # Allow 1% tolerance for rounding
                raise ValueError(
                    "Female and male percentages should sum to approximately 100%"
                )
        return v

    @validator(
        "asian_faculty_percent",
        "black_faculty_percent",
        "hispanic_faculty_percent",
        "white_faculty_percent",
    )
    def validate_demographic_percentages(cls, v):
        """Ensure demographic percentages are valid"""
        if v < 0 or v > 100:
            raise ValueError("Demographic percentages must be between 0 and 100")
        return v


class S2023_ISCreate(S2023_ISBase):
    """Schema for creating new S2023_IS records"""

    pass


class S2023_ISUpdate(BaseModel):
    """Schema for updating S2023_IS records"""

    total_faculty: Optional[int] = Field(None, ge=0)
    female_faculty_percent: Optional[float] = Field(None, ge=0, le=100)
    male_faculty_percent: Optional[float] = Field(None, ge=0, le=100)
    diversity_category: Optional[DiversityCategory] = None
    faculty_size_category: Optional[FacultySizeCategory] = None
    faculty_description: Optional[str] = None
    diversity_index: Optional[float] = Field(None, ge=0, le=1)
    asian_faculty_percent: Optional[float] = Field(None, ge=0, le=100)
    black_faculty_percent: Optional[float] = Field(None, ge=0, le=100)
    hispanic_faculty_percent: Optional[float] = Field(None, ge=0, le=100)
    white_faculty_percent: Optional[float] = Field(None, ge=0, le=100)


class S2023_ISResponse(S2023_ISBase):
    """Schema for S2023_IS API responses"""

    id: int = Field(..., description="Database record ID")
    faculty_highlights: List[str] = Field(
        ..., description="4-6 bullet points about faculty"
    )
    demographics: Dict[str, float] = Field(..., description="Demographic breakdown")

    class Config:
        from_attributes = True


class S2023_ISHighlights(BaseModel):
    """Schema for faculty highlights only"""

    unitid: str = Field(..., description="Institution UNITID")
    faculty_highlights: List[str] = Field(..., description="4-6 faculty bullet points")


class S2023_ISSearch(BaseModel):
    """Schema for searching S2023_IS records"""

    min_faculty: Optional[int] = Field(None, ge=0, description="Minimum faculty count")
    max_faculty: Optional[int] = Field(None, ge=0, description="Maximum faculty count")
    diversity_categories: Optional[List[DiversityCategory]] = Field(
        None, description="Diversity categories to include"
    )
    size_categories: Optional[List[FacultySizeCategory]] = Field(
        None, description="Size categories to include"
    )
    min_female_percent: Optional[float] = Field(
        None, ge=0, le=100, description="Minimum female faculty percentage"
    )
    max_female_percent: Optional[float] = Field(
        None, ge=0, le=100, description="Maximum female faculty percentage"
    )
    min_diversity_index: Optional[float] = Field(
        None, ge=0, le=1, description="Minimum diversity index"
    )
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=1000, description="Number of records to return")


class S2023_ISStats(BaseModel):
    """Schema for aggregate statistics"""

    total_institutions: int = Field(..., description="Total number of institutions")
    average_faculty_size: float = Field(..., description="Average faculty size")
    median_faculty_size: float = Field(..., description="Median faculty size")
    diversity_breakdown: Dict[str, int] = Field(
        ..., description="Count by diversity category"
    )
    size_breakdown: Dict[str, int] = Field(..., description="Count by size category")
    gender_stats: Dict[str, float] = Field(..., description="Gender statistics")


class S2023_ISList(BaseModel):
    """Schema for paginated list of S2023_IS records"""

    items: List[S2023_ISResponse] = Field(..., description="List of faculty metrics")
    total: int = Field(..., description="Total number of records")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Records per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_prev: bool = Field(..., description="Whether there are previous pages")


class S2023_ISImportResponse(BaseModel):
    """Schema for CSV import response"""

    message: str = Field(..., description="Import status message")
    records_imported: int = Field(..., description="Number of records imported")
    records_failed: int = Field(0, description="Number of records that failed")
    errors: Optional[List[str]] = Field(None, description="List of import errors")


class InstitutionWithFacultyMetrics(BaseModel):
    """Schema for institution data combined with faculty metrics"""

    # Institution basic info
    unitid: str = Field(..., description="Institution UNITID")
    name: str = Field(..., description="Institution name")
    city: str = Field(..., description="City")
    state: str = Field(..., description="State")
    control_type: str = Field(..., description="Public/Private control type")

    # Faculty metrics (optional - may not exist for all institutions)
    faculty_metrics: Optional[S2023_ISResponse] = Field(
        None, description="Faculty metrics if available"
    )

    # Combined display data
    has_faculty_data: bool = Field(
        ..., description="Whether faculty metrics are available"
    )
    faculty_summary: Optional[str] = Field(None, description="Brief faculty summary")


class S2023_ISBulkCreate(BaseModel):
    """Schema for bulk creating S2023_IS records"""

    records: List[S2023_ISCreate] = Field(..., description="List of records to create")
    replace_existing: bool = Field(
        False, description="Whether to replace existing records"
    )
