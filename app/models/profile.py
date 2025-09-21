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
    Text,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from enum import Enum
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class IncomeRange(str, Enum):
    """Standardized income ranges for need-based matching"""

    UNDER_30K = "under_30k"
    RANGE_30K_50K = "30k_50k"
    RANGE_50K_75K = "50k_75k"
    RANGE_75K_100K = "75k_100k"
    RANGE_100K_150K = "100k_150k"
    OVER_150K = "over_150k"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class ProfileTier(str, Enum):
    """Profile completion tiers"""

    BASIC = "basic"  # Core fields only
    ENHANCED = "enhanced"  # + activities and demographics
    COMPLETE = "complete"  # + preferences and advanced
    OPTIMIZED = "optimized"  # + all optional fields


class CollegeSize(str, Enum):
    """College size preferences"""

    VERY_SMALL = "very_small"  # <1,000
    SMALL = "small"  # 1,000-2,999
    MEDIUM = "medium"  # 3,000-9,999
    LARGE = "large"  # 10,000-19,999
    VERY_LARGE = "very_large"  # 20,000+
    NO_PREFERENCE = "no_preference"


class UserProfile(Base):
    """
    User Profile model - Progressive onboarding compatible
    """

    __tablename__ = "user_profiles"

    # Primary key and foreign key
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True
    )

    # =========================
    # BASIC INFORMATION (PHASE 1)
    # =========================
    high_school_name = Column(String(255), nullable=True, index=True)
    graduation_year = Column(Integer, nullable=True, index=True)
    gpa = Column(Float, nullable=True, index=True)
    gpa_scale = Column(String(10), default="4.0", nullable=True)
    intended_major = Column(String(255), nullable=True, index=True)
    state = Column(String(50), nullable=True, index=True)

    # Test scores (either/or acceptable)
    sat_score = Column(Integer, nullable=True, index=True)
    act_score = Column(Integer, nullable=True, index=True)

    # Quick academic interests (Phase 1 optional)
    academic_interests = Column(ARRAY(String), nullable=True)

    # =========================
    # CONTACT & PERSONAL INFO
    # =========================
    date_of_birth = Column(String, nullable=True)
    phone_number = Column(String(20), nullable=True)
    city = Column(String(100), nullable=True, index=True)
    zip_code = Column(String(10), nullable=True, index=True)

    # =========================
    # ENHANCED ACADEMIC (PHASE 2A)
    # =========================
    sat_math = Column(Integer, nullable=True)
    sat_verbal = Column(Integer, nullable=True)
    act_math = Column(Integer, nullable=True)
    act_english = Column(Integer, nullable=True)
    act_science = Column(Integer, nullable=True)
    act_reading = Column(Integer, nullable=True)

    secondary_major = Column(String(255), nullable=True)
    minor_interests = Column(ARRAY(String), nullable=True)
    career_goals = Column(ARRAY(String), nullable=True)

    ap_courses = Column(ARRAY(String), nullable=True)
    honors_courses = Column(ARRAY(String), nullable=True)
    dual_enrollment = Column(Boolean, default=False)
    class_rank = Column(Integer, nullable=True)
    class_size = Column(Integer, nullable=True)

    # =========================
    # ACTIVITIES & EXPERIENCE (PHASE 2B)
    # =========================
    extracurricular_activities = Column(JSON, nullable=True)
    volunteer_experience = Column(JSON, nullable=True)
    volunteer_hours = Column(Integer, nullable=True)
    work_experience = Column(JSON, nullable=True)

    leadership_positions = Column(JSON, nullable=True)
    awards_honors = Column(ARRAY(String), nullable=True)
    competitions = Column(JSON, nullable=True)

    sports_activities = Column(JSON, nullable=True)
    arts_activities = Column(JSON, nullable=True)
    musical_instruments = Column(ARRAY(String), nullable=True)

    # =========================
    # DEMOGRAPHICS (PHASE 2C)
    # =========================
    ethnicity = Column(ARRAY(String), nullable=True)
    gender = Column(String(50), nullable=True)
    first_generation_college = Column(Boolean, nullable=True, index=True)
    household_income_range = Column(SQLEnum(IncomeRange), nullable=True, index=True)
    family_size = Column(Integer, nullable=True)

    military_connection = Column(Boolean, default=False)
    disability_status = Column(Boolean, nullable=True)
    lgbtq_identification = Column(Boolean, nullable=True)
    rural_background = Column(Boolean, nullable=True)

    # =========================
    # COLLEGE PREFERENCES (PHASE 3)
    # =========================
    preferred_college_size = Column(SQLEnum(CollegeSize), nullable=True)
    preferred_states = Column(ARRAY(String), nullable=True)
    college_application_status = Column(String(50), nullable=True)

    max_tuition_budget = Column(Integer, nullable=True)
    financial_aid_needed = Column(Boolean, nullable=True)
    work_study_interest = Column(Boolean, default=False)

    campus_setting = Column(
        ARRAY(String), nullable=True
    )  # ["urban", "suburban", "rural"]
    religious_affiliation = Column(String(100), nullable=True)
    greek_life_interest = Column(Boolean, nullable=True)
    research_opportunities_important = Column(Boolean, default=False)
    study_abroad_interest = Column(Boolean, default=False)

    # =========================
    # ESSAY STATUS
    # =========================
    has_personal_statement = Column(Boolean, default=False)
    has_leadership_essay = Column(Boolean, default=False)
    has_challenges_essay = Column(Boolean, default=False)
    has_diversity_essay = Column(Boolean, default=False)
    has_community_service_essay = Column(Boolean, default=False)
    has_academic_interest_essay = Column(Boolean, default=False)

    # =========================
    # SCHOLARSHIP PREFERENCES
    # =========================
    scholarship_types_interested = Column(ARRAY(String), nullable=True)
    application_deadline_preference = Column(String(50), nullable=True)
    min_scholarship_amount = Column(Integer, nullable=True)
    renewable_scholarships_only = Column(Boolean, default=False)
    local_scholarships_priority = Column(Boolean, default=True)

    # =========================
    # ADDITIONAL INFORMATION
    # =========================
    languages_spoken = Column(ARRAY(String), nullable=True)
    special_talents = Column(ARRAY(String), nullable=True)
    certifications = Column(ARRAY(String), nullable=True)
    additional_notes = Column(Text, nullable=True)

    # =========================
    # PARENT/GUARDIAN INFORMATION
    # =========================
    parent_education_level = Column(String(100), nullable=True)
    parent_occupation = Column(String(100), nullable=True)
    parent_employer = Column(String(255), nullable=True)

    # =========================
    # PROFILE TRACKING
    # =========================
    profile_tier = Column(
        SQLEnum(ProfileTier), default=ProfileTier.BASIC, nullable=False
    )
    profile_completed = Column(Boolean, default=False, nullable=False)
    completion_percentage = Column(Integer, default=0, nullable=False)
    last_matching_update = Column(DateTime(timezone=True), nullable=True)

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
        return f"<UserProfile(id={self.id}, user_id={self.user_id}, tier={self.profile_tier})>"

    def calculate_completion_percentage(self) -> int:
        """Calculate profile completion percentage with tier-based weighting"""
        try:
            # Basic tier fields (required for initial functionality)
            basic_fields = [
                self.high_school_name,
                self.graduation_year,
                self.gpa,
                self.intended_major,
                self.state,
                bool(self.sat_score or self.act_score),
            ]

            basic_completed = sum(
                1 for field in basic_fields if self._is_field_completed(field)
            )
            basic_percentage = (basic_completed / len(basic_fields)) * 100

            # If still in basic tier, just return basic percentage
            if self.profile_tier == ProfileTier.BASIC:
                return int(basic_percentage)

            # Enhanced tier adds activities and demographics
            enhanced_fields = [
                self.extracurricular_activities,
                self.volunteer_experience,
                self.leadership_positions,
                self.ethnicity,
                self.first_generation_college,
            ]

            enhanced_completed = sum(
                1 for field in enhanced_fields if self._is_field_completed(field)
            )
            enhanced_percentage = (enhanced_completed / len(enhanced_fields)) * 100

            if self.profile_tier == ProfileTier.ENHANCED:
                return int((basic_percentage * 0.7) + (enhanced_percentage * 0.3))

            # Complete tier adds preferences and essays
            complete_fields = [
                self.has_personal_statement,
                self.preferred_college_size,
                self.career_goals,
                self.scholarship_types_interested,
            ]

            complete_completed = sum(
                1 for field in complete_fields if self._is_field_completed(field)
            )
            complete_percentage = (complete_completed / len(complete_fields)) * 100

            # Weighted average across all tiers
            return int(
                (basic_percentage * 0.5)
                + (enhanced_percentage * 0.3)
                + (complete_percentage * 0.2)
            )

        except Exception as e:
            logger.error(f"Error calculating completion percentage: {str(e)}")
            return 0

    def _is_field_completed(self, field) -> bool:
        """Check if a field is meaningfully completed"""
        if field is None:
            return False

        if isinstance(field, bool):
            return field is not None

        if isinstance(field, (list, dict)):
            return len(field) > 0

        if isinstance(field, str):
            return bool(field.strip())

        return bool(field)

    def get_missing_basic_fields(self) -> List[str]:
        """Get list of missing basic fields for onboarding prompts"""
        missing = []
        basic_fields = {
            "high_school_name": self.high_school_name,
            "graduation_year": self.graduation_year,
            "gpa": self.gpa,
            "intended_major": self.intended_major,
            "state": self.state,
        }

        for field_name, value in basic_fields.items():
            if not self._is_field_completed(value):
                missing.append(field_name)

        if not (self.sat_score or self.act_score):
            missing.append("test_scores")

        return missing

    def can_advance_to_enhanced(self) -> bool:
        """Check if profile can advance to enhanced tier"""
        basic_required = [
            self.high_school_name,
            self.graduation_year,
            self.gpa,
            self.intended_major,
            self.state,
            bool(self.sat_score or self.act_score),
        ]
        return all(self._is_field_completed(field) for field in basic_required)

    def update_completion_status(self):
        """Update completion percentage and status"""
        try:
            self.completion_percentage = self.calculate_completion_percentage()

            # Auto-advance tiers based on content
            if (
                self.profile_tier == ProfileTier.BASIC
                and self.can_advance_to_enhanced()
            ):
                if (
                    self.extracurricular_activities
                    or self.volunteer_experience
                    or self.ethnicity is not None
                    or self.first_generation_college is not None
                ):
                    self.profile_tier = ProfileTier.ENHANCED

            # Mark as completed based on tier and percentage
            tier_completion_thresholds = {
                ProfileTier.BASIC: 80,
                ProfileTier.ENHANCED: 70,
                ProfileTier.COMPLETE: 75,
                ProfileTier.OPTIMIZED: 80,
            }

            threshold = tier_completion_thresholds.get(self.profile_tier, 80)
            minimum_required = self.can_advance_to_enhanced()

            self.profile_completed = (
                self.completion_percentage >= threshold and minimum_required
            )

            if self.profile_completed and not self.completed_at:
                self.completed_at = func.now()

        except Exception as e:
            logger.error(f"Error updating completion status: {str(e)}")
            self.completion_percentage = 0
            self.profile_completed = False

    def get_scholarship_matching_profile(self) -> Dict[str, Any]:
        """Return profile data formatted for scholarship matching"""
        return {
            # Academic info
            "gpa": self.gpa,
            "gpa_scale": self.gpa_scale,
            "sat_score": self.sat_score,
            "act_score": self.act_score,
            "intended_major": self.intended_major,
            "academic_interests": self.academic_interests or [],
            "career_goals": self.career_goals or [],
            "ap_courses": self.ap_courses or [],
            "class_rank": self.class_rank,
            "class_size": self.class_size,
            # Demographics
            "ethnicity": self.ethnicity or [],
            "gender": self.gender,
            "first_generation_college": self.first_generation_college,
            "household_income_range": self.household_income_range,
            "military_connection": self.military_connection,
            "disability_status": self.disability_status,
            # Location
            "state": self.state,
            "city": self.city,
            "zip_code": self.zip_code,
            # Activities
            "extracurricular_activities": self.extracurricular_activities or {},
            "volunteer_experience": self.volunteer_experience or {},
            "volunteer_hours": self.volunteer_hours,
            "leadership_positions": self.leadership_positions or {},
            "sports_activities": self.sports_activities or {},
            "arts_activities": self.arts_activities or {},
            # Special info
            "languages_spoken": self.languages_spoken or [],
            "special_talents": self.special_talents or [],
            "awards_honors": self.awards_honors or [],
            # Essays
            "essay_status": {
                "personal_statement": self.has_personal_statement,
                "leadership": self.has_leadership_essay,
                "challenges": self.has_challenges_essay,
                "diversity": self.has_diversity_essay,
                "community_service": self.has_community_service_essay,
            },
            # Parent info
            "parent_education_level": self.parent_education_level,
            "parent_employer": self.parent_employer,
        }
