# app/models/institution_match.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Float,
    DateTime,
    Text,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class InstitutionMatch(Base):
    """
    User-Institution matching results with tracking
    Similar to ScholarshipMatch but for college/university matches
    """

    __tablename__ = "institution_matches"

    # Primary key and relationships
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    institution_id = Column(
        Integer, ForeignKey("institutions.id"), nullable=False, index=True
    )

    # Match scoring
    match_score = Column(Float, nullable=False)  # 0-100 score
    match_reasons = Column(JSON, nullable=True)  # Why it's a good match
    mismatch_reasons = Column(JSON, nullable=True)  # Potential concerns

    # User interaction tracking
    interested = Column(Boolean, nullable=True)  # True/False/None for unsure
    applied = Column(Boolean, default=False)
    admitted = Column(Boolean, default=False)
    enrolled = Column(Boolean, default=False)
    visited = Column(Boolean, default=False)  # Campus visit

    # Status tracking
    application_status = Column(
        String(50), nullable=True
    )  # "researching", "preparing", "submitted", "deferred", "waitlisted", "accepted", "rejected", "enrolled"
    notes = Column(Text, nullable=True)  # User notes

    # Timestamps
    match_date = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    user = relationship("User", back_populates="institution_matches")
    institution = relationship("Institution", back_populates="matches")

    def __repr__(self):
        return f"<InstitutionMatch(user_id={self.user_id}, institution_id={self.institution_id}, score={self.match_score})>"
