# app/models/college_applications.py
"""
Database model for college application tracking
FIXED: Added explicit enum names to avoid conflicts with scholarship tracking
"""

from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text, Boolean, Date, Index
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum as SQLEnum
from datetime import datetime

from app.core.database import Base
from enum import Enum as PyEnum


class ApplicationStatus(str, PyEnum):
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


class ApplicationType(str, PyEnum):
    """Type of college application"""

    EARLY_DECISION = "early_decision"
    EARLY_ACTION = "early_action"
    REGULAR_DECISION = "regular_decision"
    ROLLING = "rolling"


class CollegeApplication(Base):
    """
    Tracks a user's college application progress

    This is the join table between users and institutions
    that adds status tracking and metadata
    """

    __tablename__ = "college_applications"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)

    # Application Details
    status = Column(
        SQLEnum(
            ApplicationStatus, name="applicationstatus_college"
        ),  # ← FIXED: Added explicit name
        default=ApplicationStatus.RESEARCHING,
        nullable=False,
        index=True,
    )

    application_type = Column(
        SQLEnum(
            ApplicationType, name="applicationtype_college"
        ),  # ← FIXED: Added explicit name
        nullable=True,
    )

    # Dates
    deadline = Column(Date, nullable=True, index=True)
    decision_date = Column(Date, nullable=True)
    actual_decision_date = Column(Date, nullable=True)

    # Timeline tracking
    saved_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    decided_at = Column(DateTime, nullable=True)

    # User Data
    notes = Column(Text, nullable=True)

    # Application logistics
    application_fee = Column(Integer, nullable=True)
    fee_waiver_obtained = Column(Boolean, default=False, nullable=False)
    application_portal = Column(Text, nullable=True)
    portal_url = Column(Text, nullable=True)
    portal_username = Column(Text, nullable=True)

    # Reminders
    reminder_date = Column(DateTime, nullable=True)
    reminder_sent = Column(Boolean, default=False, nullable=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow, nullable=True)

    # Relationships
    user = relationship("User", back_populates="college_applications")
    institution = relationship("Institution")

    # Composite Indexes
    __table_args__ = (
        Index("idx_user_institution", "user_id", "institution_id", unique=True),
        Index("idx_user_college_status", "user_id", "status"),
        Index("idx_deadline", "deadline"),
    )

    def __repr__(self):
        return f"<CollegeApplication(user_id={self.user_id}, institution_id={self.institution_id}, status={self.status})>"
