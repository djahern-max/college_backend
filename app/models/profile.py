"""
User Profile database model for scholarship applications.
"""
from __future__ import annotations
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Text, JSON, ForeignKey, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class UserProfile(Base):
    """User profile model for scholarship application data."""
    
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Privacy and Settings
    profile_visibility = Column(String(20), nullable=False, default="private")  # "public", "private", "friends", "scholarship_only"
    allow_scholarship_matching = Column(Boolean, nullable=False, default=True)
    field_privacy_settings = Column(JSON, nullable=True)  # Field-level privacy settings
    
    # Personal Information
    middle_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    
    # Profile Photo
    profile_photo_url = Column(String(500), nullable=True)  # URL to stored photo
    profile_photo_filename = Column(String(255), nullable=True)  # Original filename
    profile_photo_uploaded_at = Column(DateTime(timezone=True), nullable=True)
    
    # Address Information
    street_address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(50), nullable=True)
    zip_code = Column(String(10), nullable=True)
    country = Column(String(100), default="United States")
    
    # Academic Information
    high_school_name = Column(String(255), nullable=True)
    graduation_year = Column(Integer, nullable=True)
    gpa = Column(Numeric(3, 2), nullable=True)  # e.g., 3.85
    class_rank = Column(Integer, nullable=True)
    class_size = Column(Integer, nullable=True)
    sat_score = Column(Integer, nullable=True)
    act_score = Column(Integer, nullable=True)
    
    # Athletic Information
    sports_played = Column(JSON, nullable=True)  # ["volleyball", "track and field"]
    athletic_positions = Column(JSON, nullable=True)  # {"volleyball": "setter", "track": "sprinter"}
    years_participated = Column(JSON, nullable=True)  # {"volleyball": 4, "track": 3}
    team_captain = Column(JSON, nullable=True)  # ["volleyball_senior_year"]
    athletic_awards = Column(JSON, nullable=True)  # List of awards/honors
    
    # Community Service & Activities
    volunteer_hours = Column(Integer, nullable=True)
    volunteer_organizations = Column(JSON, nullable=True)  # List of organizations
    leadership_positions = Column(JSON, nullable=True)  # List of leadership roles
    extracurricular_activities = Column(JSON, nullable=True)  # Clubs, organizations, etc.
    work_experience = Column(JSON, nullable=True)  # Job history including lifeguarding
    
    # Academic Achievements
    honors_courses = Column(JSON, nullable=True)  # List of AP, honors, etc.
    academic_awards = Column(JSON, nullable=True)  # Honor roll, dean's list, etc.
    
    # College Plans
    intended_major = Column(String(255), nullable=True)
    college_preferences = Column(JSON, nullable=True)  # List of preferred colleges
    career_goals = Column(Text, nullable=True)
    
    # Essays/Personal Statements
    personal_statement = Column(Text, nullable=True)
    career_essay = Column(Text, nullable=True)
    athletic_impact_essay = Column(Text, nullable=True)
    
    # References
    references = Column(JSON, nullable=True)  # List of reference objects
    
    # Profile Completion Tracking
    profile_completed = Column(Boolean, nullable=False, default=False)
    completion_percentage = Column(Integer, nullable=False, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="profile")
    
    def __repr__(self):
        return f"<UserProfile(id={self.id}, user_id={self.user_id}, completed={self.profile_completed})>"