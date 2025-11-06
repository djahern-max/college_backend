# app/models/scholarship_applications.py
"""
Database model for scholarship application tracking
"""

from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum as SQLEnum
from datetime import datetime

from app.core.database import Base
from app.schemas.scholarship_tracking import ApplicationStatus


class ScholarshipApplication(Base):
    """
    Tracks a user's scholarship application progress

    This is the join table between users and scholarships
    that adds status tracking and metadata
    """

    __tablename__ = "scholarship_applications"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scholarship_id = Column(Integer, ForeignKey("scholarships.id"), nullable=False)

    # Status Tracking
    status = Column(
        SQLEnum(ApplicationStatus),
        default=ApplicationStatus.INTERESTED,
        nullable=False,
        index=True,
    )

    # Timeline
    saved_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    decision_date = Column(DateTime, nullable=True)

    # User Data
    notes = Column(Text, nullable=True)
    essay_draft = Column(Text, nullable=True)
    documents_needed = Column(Text, nullable=True)

    # Reminders
    reminder_date = Column(DateTime, nullable=True)
    reminder_sent = Column(Boolean, default=False, nullable=False)

    # Award Info
    award_amount = Column(Integer, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow, nullable=True)

    # Relationships
    user = relationship("User", back_populates="scholarship_applications")
    scholarship = relationship("Scholarship")

    # Composite Indexes
    __table_args__ = (
        Index("idx_user_scholarship", "user_id", "scholarship_id", unique=True),
        Index("idx_user_status", "user_id", "status"),
    )

    def __repr__(self):
        return f"<ScholarshipApplication(user_id={self.user_id}, scholarship_id={self.scholarship_id}, status={self.status})>"
