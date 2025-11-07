# app/schemas/college_tracking.py
"""
Schemas for college application tracking
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


# ===========================
# ENUMS
# ===========================


class ApplicationStatus(str, Enum):
    """Status of a college application"""

    RESEARCHING = "researching"
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    WAITLISTED = "waitlisted"
    REJECTED = "rejected"
    DECLINED = "declined"
    ENROLLED = "enrolled"


class ApplicationType(str, Enum):
    """Type of college application"""

    EARLY_DECISION = "early_decision"
    EARLY_ACTION = "early_action"
    REGULAR_DECISION = "regular_decision"
    ROLLING = "rolling"


# ===========================
# REQUEST SCHEMAS
# ===========================


class CollegeApplicationCreate(BaseModel):
    """Schema for creating a new college application tracking entry"""

    institution_id: int
    status: ApplicationStatus = ApplicationStatus.RESEARCHING
    application_type: Optional[ApplicationType] = None
    deadline: Optional[date] = None
    notes: Optional[str] = None


class CollegeApplicationUpdate(BaseModel):
    """Schema for updating a college application"""

    status: Optional[ApplicationStatus] = None
    application_type: Optional[ApplicationType] = None
    deadline: Optional[date] = None
    decision_date: Optional[date] = None
    actual_decision_date: Optional[date] = None
    notes: Optional[str] = None
    application_fee: Optional[int] = None
    fee_waiver_obtained: Optional[bool] = None
    application_portal: Optional[str] = None
    portal_url: Optional[str] = None
    portal_username: Optional[str] = None


# ===========================
# RESPONSE SCHEMAS
# ===========================


class InstitutionBasicInfo(BaseModel):
    """Basic institution info for nested responses"""

    id: int
    ipeds_id: int
    name: str
    city: str
    state: str
    control_type: str
    primary_image_url: Optional[str]

    class Config:
        from_attributes = True


class CollegeApplicationResponse(BaseModel):
    """Schema for college application responses"""

    id: int
    user_id: int
    institution_id: int
    status: ApplicationStatus
    application_type: Optional[ApplicationType]
    deadline: Optional[date]
    decision_date: Optional[date]
    actual_decision_date: Optional[date]

    saved_at: datetime
    started_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    decided_at: Optional[datetime] = None

    notes: Optional[str] = None
    application_fee: Optional[int] = None
    fee_waiver_obtained: bool
    application_portal: Optional[str] = None
    portal_url: Optional[str] = None
    portal_username: Optional[str] = None

    # Nested institution data
    institution: Optional[InstitutionBasicInfo] = None

    class Config:
        from_attributes = True


class CollegeDashboardSummary(BaseModel):
    """Summary statistics for college dashboard"""

    total_applications: int
    submitted: int
    in_progress: int
    accepted: int
    waitlisted: int
    rejected: int
    awaiting_decision: int  # submitted but no decision yet


class CollegeDashboardResponse(BaseModel):
    """Complete college dashboard data"""

    summary: CollegeDashboardSummary
    upcoming_deadlines: List[CollegeApplicationResponse]  # Next 30 days
    overdue: List[CollegeApplicationResponse]
    applications: List[CollegeApplicationResponse]
