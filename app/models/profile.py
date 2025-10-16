# app/models/profile.py - MINIMAL VERSION
"""
Ultra-simplified profile model - only core essentials
Reduced from 84 fields to 13 fields (85% reduction)
No demographics - just academic basics
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class UserProfile(Base):
    """Minimal user profile - just the essentials"""

    __tablename__ = "user_profiles"

    # ===========================
    # CORE IDENTITY
    # ===========================
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True
    )

    # ===========================
    # LOCATION (3 fields)
    # ===========================
    state = Column(String(2), nullable=True, index=True)
    city = Column(String(100), nullable=True)
    zip_code = Column(String(10), nullable=True)

    # ===========================
    # ACADEMIC INFO (6 fields)
    # ===========================
    high_school_name = Column(String(255), nullable=True)
    graduation_year = Column(Integer, nullable=True, index=True)
    gpa = Column(Float, nullable=True)
    gpa_scale = Column(String(10), nullable=True)  # "4.0", "5.0", "100"
    sat_score = Column(Integer, nullable=True)
    act_score = Column(Integer, nullable=True)
    intended_major = Column(String(255), nullable=True)

    # ===========================
    # MATCHING CRITERIA (1 field)
    # ===========================
    location_preference = Column(
        String(2), nullable=True, index=True
    )  # State code: NH, CO, CA, etc.

    # ===========================
    # TIMESTAMPS (2 fields)
    # ===========================
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # ===========================
    # RELATIONSHIPS
    # ===========================
    user = relationship("User", back_populates="profile")

    def __repr__(self):
        return (
            f"<UserProfile(id={self.id}, user_id={self.user_id}, state='{self.state}')>"
        )

    @property
    def is_complete(self) -> bool:
        """Check if profile has minimum required info"""
        return bool(self.state and self.graduation_year and self.gpa)

    @property
    def completion_percentage(self) -> int:
        """Calculate profile completion percentage"""
        total_fields = 10  # Core fields we care about
        filled_fields = sum(
            [
                bool(self.state),
                bool(self.city),
                bool(self.high_school_name),
                bool(self.graduation_year),
                bool(self.gpa),
                bool(self.gpa_scale),
                bool(self.sat_score or self.act_score),
                bool(self.intended_major),
            ]
        )
        return int((filled_fields / total_fields) * 100)
