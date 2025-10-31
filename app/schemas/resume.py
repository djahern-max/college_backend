# app/schemas/resume.py
"""
Pydantic schemas for resume parsing
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ExtracurricularActivity(BaseModel):
    """Schema for extracurricular activity"""

    name: str
    role: Optional[str] = None
    description: Optional[str] = None
    years_active: Optional[str] = None


class WorkExperience(BaseModel):
    """Schema for work experience"""

    title: str
    organization: str
    dates: str
    description: Optional[str] = None


class ParsedResumeData(BaseModel):
    """Schema for parsed resume data"""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    high_school_name: Optional[str] = None
    graduation_year: Optional[int] = None
    gpa: Optional[float] = None
    gpa_scale: Optional[str] = None
    sat_score: Optional[int] = None
    act_score: Optional[int] = None
    intended_major: Optional[str] = None
    career_goals: Optional[str] = None
    extracurriculars: List[ExtracurricularActivity] = []
    work_experience: List[WorkExperience] = []
    honors_awards: List[str] = []
    skills: List[str] = []
    volunteer_hours: Optional[int] = None


class ResumeParsingMetadata(BaseModel):
    """Metadata about the resume parsing operation"""

    confidence_score: float = Field(
        ..., ge=0, le=1, description="Confidence score between 0 and 1"
    )
    fields_extracted: int = Field(
        ..., ge=0, description="Number of fields successfully extracted"
    )
    extraction_notes: List[str] = Field(
        default_factory=list, description="Notes about the extraction"
    )


class ResumeUploadResponse(BaseModel):
    """Response after uploading and parsing a resume"""

    status: str = "success"
    resume_url: str = Field(..., description="CDN URL of the uploaded resume")
    parsed_data: ParsedResumeData
    metadata: ResumeParsingMetadata
    message: str = "Resume uploaded and parsed successfully"


class ResumeParsingError(BaseModel):
    """Error response for resume parsing"""

    status: str = "error"
    error: str
    message: str
