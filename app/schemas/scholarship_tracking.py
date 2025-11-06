# app/schemas/scholarship_tracking.py
"""
Schemas for scholarship application tracking
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ===========================
# ENUMS
# ===========================


class ApplicationStatus(str, Enum):
    """Status of a scholarship application"""

    INTERESTED = "interested"
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    NOT_PURSUING = "not_pursuing"


# ===========================
# REQUEST SCHEMAS
# ===========================


class ScholarshipApplicationCreate(BaseModel):
    """Schema for creating a new scholarship application tracking entry"""

    scholarship_id: int
    status: ApplicationStatus = ApplicationStatus.INTERESTED
    notes: Optional[str] = None


class ScholarshipApplicationUpdate(BaseModel):
    """Schema for updating a scholarship application"""

    status: Optional[ApplicationStatus] = None
    notes: Optional[str] = None
    essay_draft: Optional[str] = None
    documents_needed: Optional[str] = None
    award_amount: Optional[int] = None


# ===========================
# RESPONSE SCHEMAS
# ===========================


class ScholarshipBasicInfo(BaseModel):
    """Basic scholarship info for nested responses"""

    id: int
    title: str
    organization: str
    amount_min: Optional[int]
    amount_max: Optional[int]
    deadline: Optional[str]

    class Config:
        from_attributes = True


class ScholarshipApplicationResponse(BaseModel):
    """Schema for scholarship application responses"""

    id: int
    user_id: int
    scholarship_id: int
    status: ApplicationStatus
    saved_at: datetime
    started_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    decision_date: Optional[datetime] = None
    notes: Optional[str] = None
    essay_draft: Optional[str] = None
    documents_needed: Optional[str] = None
    award_amount: Optional[int] = None

    # Nested scholarship data
    scholarship: Optional[ScholarshipBasicInfo] = None

    class Config:
        from_attributes = True


class DashboardSummary(BaseModel):
    """Summary statistics for dashboard"""

    total_applications: int
    submitted: int
    in_progress: int
    accepted: int
    total_potential_value: int
    total_awarded_value: int


class ScholarshipDashboardResponse(BaseModel):
    """Complete dashboard data"""

    summary: DashboardSummary
    upcoming_deadlines: List[ScholarshipApplicationResponse]
    overdue: List[ScholarshipApplicationResponse]
    applications: List[ScholarshipApplicationResponse]
