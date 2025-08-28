# app/models/profile.py - UPDATED VERSION
from sqlalchemy import (
    Column,
    Integer,
    String,
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
import logging

logger = logging.getLogger(__name__)


class UserProfile(Base):
    """
    User Profile model - essays moved to separate Essay table
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
    date_of_birth = Column(String, nullable=True)
    phone_number = Column(String(20), nullable=True)
    high_school_name = Column(String(255), nullable=True)
    graduation_year = Column(Integer, nullable=True)
    gpa = Column(Float, nullable=True)

    # =========================
    # ACADEMIC INFORMATION
    # =========================
    sat_score = Column(Integer, nullable=True)
    act_score = Column(Integer, nullable=True)
    intended_major = Column(String(255), nullable=True)
    academic_interests = Column(ARRAY(String), nullable=True)
    career_goals = Column(ARRAY(String), nullable=True)

    # =========================
    # ACTIVITIES & EXPERIENCE
    # =========================
    extracurricular_activities = Column(ARRAY(String), nullable=True)
    volunteer_experience = Column(ARRAY(String), nullable=True)
    volunteer_hours = Column(Integer, nullable=True)
    work_experience = Column(JSON, nullable=True)

    # =========================
    # BACKGROUND & DEMOGRAPHICS
    # =========================
    ethnicity = Column(ARRAY(String), nullable=True)
    first_generation_college = Column(Boolean, nullable=True)
    household_income_range = Column(String(50), nullable=True)

    # =========================
    # LOCATION INFORMATION
    # =========================
    state = Column(String(50), nullable=True)
    city = Column(String(100), nullable=True)
    zip_code = Column(String(10), nullable=True)

    # =========================
    # COLLEGE PLANS
    # =========================
    preferred_college_size = Column(String(50), nullable=True)
    preferred_college_location = Column(String(100), nullable=True)
    college_application_status = Column(String(50), nullable=True)

    # =========================
    # ESSAY STATUS (BOOLEAN FLAGS)
    # =========================
    has_personal_statement = Column(Boolean, default=False)
    has_leadership_essay = Column(Boolean, default=False)
    has_challenges_essay = Column(Boolean, default=False)
    has_diversity_essay = Column(Boolean, default=False)

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
    additional_notes = Column(String(500), nullable=True)  # Short notes only

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
    essays = relationship(
        "Essay", back_populates="profile", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<UserProfile(id={self.id}, user_id={self.user_id}, completed={self.profile_completed})>"

    def calculate_completion_percentage(self) -> int:
        """Calculate profile completion percentage"""
        try:
            total_fields = 0
            completed_fields = 0

            # Core required fields
            core_fields = [
                self.high_school_name,
                self.graduation_year,
                self.gpa,
                self.intended_major,
                self.state,
            ]

            # Academic fields
            academic_fields = [
                self.academic_interests,
                self.career_goals,
                bool(self.sat_score or self.act_score),  # Either test score
            ]

            # Activity fields
            activity_fields = [
                self.extracurricular_activities,
                self.volunteer_experience,
                self.volunteer_hours,
            ]

            # Personal fields
            personal_fields = [
                self.scholarship_types_interested,
                self.languages_spoken,
                self.special_talents,
            ]

            # Essay completion (check if essays exist)
            essay_completion = [
                self.has_personal_statement,
                self.has_leadership_essay,
            ]

            # Count all fields
            all_sections = [
                core_fields,
                academic_fields,
                activity_fields,
                personal_fields,
                essay_completion,
            ]

            for section in all_sections:
                for field in section:
                    total_fields += 1
                    if field:
                        if isinstance(field, list) and len(field) > 0:
                            completed_fields += 1
                        elif not isinstance(field, list) and field:
                            completed_fields += 1

            if total_fields == 0:
                return 0

            return int((completed_fields / total_fields) * 100)
        except Exception as e:
            logger.error(f"Error calculating completion percentage: {str(e)}")
            return 0

    def update_completion_status(self):
        """Update completion percentage and status"""
        try:
            self.completion_percentage = self.calculate_completion_percentage()

            # Update essay flags based on actual essays
            # This would be updated when essays are created/deleted

            # Mark as completed if >= 80% complete and has minimum required fields
            minimum_required = (
                self.high_school_name
                and self.graduation_year
                and self.intended_major
                and self.has_personal_statement  # Requires at least personal statement essay
            )

            self.profile_completed = (
                self.completion_percentage >= 80 and minimum_required
            )

            if self.profile_completed and not self.completed_at:
                self.completed_at = func.now()

        except Exception as e:
            logger.error(f"Error updating completion status: {str(e)}")
            self.completion_percentage = 0
            self.profile_completed = False

    def update_essay_flags(self):
        """Update essay boolean flags based on actual essays (called from essay service)"""
        # This method would be called whenever essays are created/updated/deleted
        # For now, this is a placeholder - the actual logic would query the essays table
        pass
