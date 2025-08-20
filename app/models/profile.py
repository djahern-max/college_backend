from sqlalchemy import Boolean, Column, Integer, String, DateTime, Text, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

from app.core.database import Base


class UserProfile(Base):
    """
    User Profile model - stores comprehensive student information for scholarship matching.
    This is the core model that drives scholarship recommendations.
    """
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # === BASIC INFORMATION ===
    date_of_birth = Column(String, nullable=True)  # Format: YYYY-MM-DD
    phone_number = Column(String, nullable=True)
    high_school_name = Column(String, nullable=True)
    graduation_year = Column(Integer, nullable=True)
    gpa = Column(Float, nullable=True)
    
    # === TEST SCORES ===
    sat_score = Column(Integer, nullable=True)
    act_score = Column(Integer, nullable=True)
    
    # === ACADEMIC INTERESTS ===
    intended_major = Column(String, nullable=True)
    academic_interests = Column(JSON, nullable=True)  # Array of strings
    career_goals = Column(JSON, nullable=True)  # Array of strings
    
    # === ACTIVITIES & EXPERIENCE ===
    extracurricular_activities = Column(JSON, nullable=True)  # Array of strings
    volunteer_experience = Column(JSON, nullable=True)  # Array of strings
    volunteer_hours = Column(Integer, nullable=True)
    work_experience = Column(JSON, nullable=True)  # Array of objects with job details
    
    # === BACKGROUND & DEMOGRAPHICS ===
    ethnicity = Column(JSON, nullable=True)  # Array of strings
    first_generation_college = Column(Boolean, nullable=True)
    household_income_range = Column(String, nullable=True)  # e.g., "$30,000-$50,000"
    
    # === LOCATION ===
    state = Column(String, nullable=True)
    city = Column(String, nullable=True)
    zip_code = Column(String, nullable=True)
    
    # === COLLEGE PLANS ===
    preferred_college_size = Column(String, nullable=True)  # Small, Medium, Large
    preferred_college_location = Column(String, nullable=True)  # In-state, Out-of-state, etc.
    college_application_status = Column(String, nullable=True)  # Not started, In progress, etc.
    
    # === ESSAYS & PERSONAL STATEMENTS ===
    personal_statement = Column(Text, nullable=True)
    leadership_experience = Column(Text, nullable=True)
    challenges_overcome = Column(Text, nullable=True)
    
    # === SCHOLARSHIP PREFERENCES ===
    scholarship_types_interested = Column(JSON, nullable=True)  # Merit, Need-based, etc.
    application_deadline_preference = Column(String, nullable=True)  # Early, Regular, etc.
    
    # === ADDITIONAL INFORMATION ===
    languages_spoken = Column(JSON, nullable=True)  # Array of strings
    special_talents = Column(JSON, nullable=True)  # Music, Sports, Art, etc.
    additional_info = Column(Text, nullable=True)  # Free-form additional information
    
    # === PROFILE STATUS ===
    profile_completed = Column(Boolean, default=False)
    completion_percentage = Column(Integer, default=0)
    
    # === TIMESTAMPS ===
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # === RELATIONSHIPS ===
    user = relationship("User", back_populates="profile")
    
    def calculate_completion_percentage(self):
        """
        Calculate profile completion percentage based on filled fields.
        This helps users understand how complete their profile is.
        """
        # Core fields that are most important for scholarship matching
        core_fields = [
            self.high_school_name,
            self.graduation_year,
            self.gpa,
            self.intended_major,
            self.academic_interests,
            self.extracurricular_activities,
            self.state,
            self.city,
            self.ethnicity,
            self.household_income_range
        ]
        
        completed_fields = sum(1 for field in core_fields if field is not None)
        percentage = int((completed_fields / len(core_fields)) * 100)
        
        # Update the stored percentage
        self.completion_percentage = percentage
        return percentage
    
    def __repr__(self):
        return f"<UserProfile(user_id={self.user_id}, completed={self.profile_completed})>"
