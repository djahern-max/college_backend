# app/models/profile.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    Float,
    DateTime,
    ForeignKey,
    JSON,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class UserProfile(Base):
    """
    User Profile model matching the frontend ProfileBuilder and ProfileView requirements
    """

    __tablename__ = "user_profiles"

    # Primary key and foreign key
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True
    )

    # =========================
    # BASIC INFORMATION SECTION
    # =========================
    date_of_birth = Column(String, nullable=True)  # Format: YYYY-MM-DD
    phone_number = Column(String(20), nullable=True)
    high_school_name = Column(String(255), nullable=True)
    graduation_year = Column(Integer, nullable=True)
    gpa = Column(Float, nullable=True)  # Scale of 4.0

    # =========================
    # ACADEMIC INFORMATION
    # =========================
    # Test Scores
    sat_score = Column(Integer, nullable=True)  # Total SAT score (out of 1600)
    act_score = Column(Integer, nullable=True)  # ACT composite score (out of 36)

    # Academic Interests & Goals
    intended_major = Column(String(255), nullable=True)
    academic_interests = Column(ARRAY(String), nullable=True)  # Array of interests
    career_goals = Column(ARRAY(String), nullable=True)  # Array of career goals

    # =========================
    # ACTIVITIES & EXPERIENCE
    # =========================
    extracurricular_activities = Column(ARRAY(String), nullable=True)
    volunteer_experience = Column(ARRAY(String), nullable=True)
    volunteer_hours = Column(Integer, nullable=True)
    work_experience = Column(JSON, nullable=True)  # Array of objects with job details

    # =========================
    # BACKGROUND & DEMOGRAPHICS
    # =========================
    ethnicity = Column(ARRAY(String), nullable=True)
    first_generation_college = Column(Boolean, nullable=True)
    household_income_range = Column(
        String(50), nullable=True
    )  # e.g., "$50,000-$75,000"

    # =========================
    # LOCATION INFORMATION
    # =========================
    state = Column(String(50), nullable=True)
    city = Column(String(100), nullable=True)
    zip_code = Column(String(10), nullable=True)

    # =========================
    # COLLEGE PLANS
    # =========================
    preferred_college_size = Column(
        String(50), nullable=True
    )  # e.g., "Small", "Medium", "Large"
    preferred_college_location = Column(String(100), nullable=True)
    college_application_status = Column(String(50), nullable=True)

    # =========================
    # ESSAYS & PERSONAL STATEMENTS
    # =========================
    personal_statement = Column(Text, nullable=True)
    leadership_experience = Column(Text, nullable=True)
    challenges_overcome = Column(Text, nullable=True)

    # =========================
    # SCHOLARSHIP PREFERENCES
    # =========================
    scholarship_types_interested = Column(ARRAY(String), nullable=True)
    application_deadline_preference = Column(String(50), nullable=True)

    # =========================
    # ADDITIONAL INFORMATION
    # =========================
    languages_spoken = Column(ARRAY(String), nullable=True)
    special_talents = Column(ARRAY(String), nullable=True)
    additional_info = Column(Text, nullable=True)

    # =========================
    # PROFILE STATUS & METADATA
    # =========================
    profile_completed = Column(Boolean, default=False, nullable=False)
    completion_percentage = Column(Integer, default=0, nullable=False)

    # =========================
    # TIMESTAMPS
    # =========================
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # =========================
    # RELATIONSHIPS
    # =========================
    user = relationship("User", back_populates="profile")

    def __repr__(self):
        return f"<UserProfile(id={self.id}, user_id={self.user_id}, completed={self.profile_completed})>"

    @property
    def is_basic_info_complete(self) -> bool:
        """Check if basic information section is complete"""
        return bool(
            self.high_school_name and self.graduation_year and self.gpa is not None
        )

    @property
    def is_academic_info_complete(self) -> bool:
        """Check if academic information section is complete"""
        return bool(
            self.intended_major
            and (self.sat_score or self.act_score)
            and self.academic_interests
        )

    @property
    def is_personal_info_complete(self) -> bool:
        """Check if personal information section is complete"""
        return bool(
            self.personal_statement
            and self.extracurricular_activities
            and self.volunteer_experience
        )

    def calculate_completion_percentage(self) -> int:
        """
        Calculate profile completion percentage based on filled fields
        Matches the logic expected by ProfileBuilder and ProfileView
        """
        total_fields = 0
        completed_fields = 0

        # Define weighted sections based on ProfileBuilder sections
        basic_fields = [
            self.high_school_name,
            self.graduation_year,
            self.gpa,
            self.date_of_birth,
            self.phone_number,
        ]

        academic_fields = [
            self.intended_major,
            self.academic_interests,
            self.career_goals,
            self.sat_score or self.act_score,  # Either SAT or ACT counts
        ]

        activities_fields = [
            self.extracurricular_activities,
            self.volunteer_experience,
            self.volunteer_hours,
            self.work_experience,
        ]

        background_fields = [
            self.ethnicity,
            self.household_income_range,
            self.state,
            self.city,
        ]

        essays_fields = [
            self.personal_statement,
            self.leadership_experience,
            self.challenges_overcome,
        ]

        preferences_fields = [
            self.scholarship_types_interested,
            self.preferred_college_size,
            self.languages_spoken,
        ]

        # Count all fields
        all_sections = [
            basic_fields,
            academic_fields,
            activities_fields,
            background_fields,
            essays_fields,
            preferences_fields,
        ]

        for section in all_sections:
            for field in section:
                total_fields += 1
                if field:
                    if isinstance(field, list) and len(field) > 0:
                        completed_fields += 1
                    elif not isinstance(field, list):
                        completed_fields += 1

        if total_fields == 0:
            return 0

        return int((completed_fields / total_fields) * 100)

    def update_completion_status(self):
        """Update completion percentage and status"""
        self.completion_percentage = self.calculate_completion_percentage()

        # Mark as completed if >= 80% complete and has minimum required fields
        minimum_required = (
            self.high_school_name
            and self.graduation_year
            and self.intended_major
            and self.personal_statement
        )

        self.profile_completed = self.completion_percentage >= 80 and minimum_required

        if self.profile_completed and not self.completed_at:
            self.completed_at = func.now()

    def get_missing_fields(self) -> list:
        """Get list of missing required fields for ProfileView display"""
        missing = []

        if not self.high_school_name:
            missing.append("High School Name")
        if not self.graduation_year:
            missing.append("Graduation Year")
        if not self.gpa:
            missing.append("GPA")
        if not self.intended_major:
            missing.append("Intended Major")
        if not self.personal_statement:
            missing.append("Personal Statement")
        if not (self.sat_score or self.act_score):
            missing.append("SAT or ACT Score")
        if not self.academic_interests:
            missing.append("Academic Interests")
        if not self.extracurricular_activities:
            missing.append("Extracurricular Activities")

        return missing
