# app/models/scholarship.py
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
    Enum,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import Index
from app.core.database import Base
import enum
from typing import Dict, Any, List


class ScholarshipStatus(str, enum.Enum):
    """Scholarship status enumeration"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    EXPIRED = "expired"


class ScholarshipType(str, enum.Enum):
    """Types of scholarships for categorization"""

    MERIT = "merit"
    NEED_BASED = "need_based"
    ACADEMIC = "academic"
    ATHLETIC = "athletic"
    CREATIVE_ARTS = "creative_arts"
    STEM = "stem"
    COMMUNITY_SERVICE = "community_service"
    LEADERSHIP = "leadership"
    MINORITY = "minority"
    FIRST_GENERATION = "first_generation"
    MAJOR_SPECIFIC = "major_specific"
    STATE_SPECIFIC = "state_specific"
    EMPLOYER = "employer"
    MILITARY = "military"
    RELIGIOUS = "religious"
    OTHER = "other"


class Scholarship(Base):
    """
    Scholarship model for storing scholarship opportunities that can be matched to student profiles
    """

    __tablename__ = "scholarships"

    # Primary Information
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    provider = Column(
        String(255), nullable=False, index=True
    )  # Organization offering scholarship
    description = Column(Text, nullable=True)

    # Financial Information
    amount_min = Column(Float, nullable=True)  # Minimum award amount
    amount_max = Column(Float, nullable=True)  # Maximum award amount
    amount_exact = Column(Float, nullable=True)  # Exact amount (if not a range)
    renewable = Column(Boolean, default=False, nullable=False)  # Can be renewed
    renewable_years = Column(Integer, nullable=True)  # How many years renewable

    # Application Information
    deadline = Column(DateTime(timezone=True), nullable=True, index=True)
    application_url = Column(String(1000), nullable=True)
    contact_email = Column(String(255), nullable=True)
    application_fee = Column(Float, default=0.0, nullable=False)

    # Status and Verification
    status = Column(
        Enum(ScholarshipStatus),
        default=ScholarshipStatus.ACTIVE,
        nullable=False,
        index=True,
    )
    verified = Column(Boolean, default=False, nullable=False, index=True)

    # Categorization
    scholarship_type = Column(Enum(ScholarshipType), nullable=False, index=True)
    categories = Column(ARRAY(String), nullable=True)  # Additional tags/categories

    # ===========================
    # MATCHING CRITERIA FIELDS
    # These map directly to UserProfile fields for matching
    # ===========================

    # Academic Requirements
    min_gpa = Column(Float, nullable=True)
    max_gpa = Column(Float, nullable=True)  # Some scholarships have GPA caps
    min_sat_score = Column(Integer, nullable=True)
    min_act_score = Column(Integer, nullable=True)
    required_majors = Column(ARRAY(String), nullable=True)  # List of eligible majors
    academic_interests = Column(
        ARRAY(String), nullable=True
    )  # Matching academic interests

    # Geographic Requirements
    eligible_states = Column(
        ARRAY(String), nullable=True
    )  # US states where students must reside
    eligible_cities = Column(
        ARRAY(String), nullable=True
    )  # Specific cities if applicable
    zip_codes = Column(ARRAY(String), nullable=True)  # Specific zip codes

    # Demographic Requirements
    eligible_ethnicities = Column(ARRAY(String), nullable=True)
    first_generation_college_required = Column(Boolean, nullable=True)
    income_max = Column(Float, nullable=True)  # Maximum household income
    income_min = Column(
        Float, nullable=True
    )  # Minimum household income (rare but exists)

    # High School Requirements
    high_school_names = Column(ARRAY(String), nullable=True)  # Specific high schools
    graduation_year_min = Column(Integer, nullable=True)
    graduation_year_max = Column(Integer, nullable=True)

    # Activity Requirements
    required_activities = Column(
        ARRAY(String), nullable=True
    )  # Required extracurriculars
    volunteer_hours_min = Column(Integer, nullable=True)  # Minimum volunteer hours
    leadership_required = Column(Boolean, default=False, nullable=False)

    # Essay Requirements
    essay_required = Column(Boolean, default=False, nullable=False)
    personal_statement_required = Column(Boolean, default=False, nullable=False)
    leadership_essay_required = Column(Boolean, default=False, nullable=False)

    # Additional Requirements
    languages_preferred = Column(ARRAY(String), nullable=True)  # Preferred languages
    special_talents = Column(ARRAY(String), nullable=True)  # Special talents/skills

    # College Plans Requirements
    college_size_preference = Column(
        ARRAY(String), nullable=True
    )  # Preferred college sizes
    college_location_preference = Column(
        ARRAY(String), nullable=True
    )  # Preferred locations

    # Application Requirements (stored as JSON for flexibility)
    required_documents = Column(
        ARRAY(String), nullable=True
    )  # List of required documents
    additional_requirements = Column(
        JSON, nullable=True
    )  # Flexible additional requirements

    # ===========================
    # METADATA AND TRACKING
    # ===========================

    # Source Information
    source_url = Column(String(1000), nullable=True)  # Where scholarship was found
    data_source = Column(String(100), nullable=True)  # Internal tracking
    external_id = Column(String(255), nullable=True)  # ID from external system

    # Performance Tracking
    view_count = Column(Integer, default=0, nullable=False)
    application_count = Column(
        Integer, default=0, nullable=False
    )  # Estimated applications
    match_count = Column(
        Integer, default=0, nullable=False
    )  # How many students matched

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    deadline_reminder_sent = Column(DateTime(timezone=True), nullable=True)

    # Admin Information
    created_by = Column(
        Integer, ForeignKey("users.id"), nullable=True
    )  # Admin who added it
    notes = Column(Text, nullable=True)  # Internal admin notes

    # ===========================
    # RELATIONSHIPS
    # ===========================

    # Relationship to user who created it (admin)
    creator = relationship(
        "User", back_populates="created_scholarships", foreign_keys=[created_by]
    )

    # Relationship to scholarship matches
    matches = relationship(
        "ScholarshipMatch", back_populates="scholarship", cascade="all, delete-orphan"
    )

    # ===========================
    # INDEXES FOR PERFORMANCE
    # ===========================

    __table_args__ = (
        Index("idx_scholarship_deadline", "deadline"),
        Index("idx_scholarship_status_verified", "status", "verified"),
        Index("idx_scholarship_type_status", "scholarship_type", "status"),
        Index("idx_scholarship_gpa_range", "min_gpa", "max_gpa"),
        Index("idx_scholarship_amount_range", "amount_min", "amount_max"),
    )

    def __repr__(self):
        return f"<Scholarship(id={self.id}, title='{self.title}', provider='{self.provider}')>"

    # ===========================
    # BUSINESS LOGIC METHODS
    # ===========================

    def is_active(self) -> bool:
        """Check if scholarship is currently active and not expired"""
        if self.status != ScholarshipStatus.ACTIVE:
            return False
        if self.deadline and self.deadline < func.now():
            return False
        return True

    def get_amount_display(self) -> str:
        """Get formatted amount string for display"""
        if self.amount_exact:
            return f"${self.amount_exact:,.0f}"
        elif self.amount_min and self.amount_max:
            return f"${self.amount_min:,.0f} - ${self.amount_max:,.0f}"
        elif self.amount_min:
            return f"Up to ${self.amount_min:,.0f}"
        elif self.amount_max:
            return f"${self.amount_max:,.0f}"
        else:
            return "Amount varies"

    def matches_profile_basic(self, profile) -> bool:
        """
        Basic matching logic to check if a profile meets scholarship requirements.
        This is a simple version - you might want more sophisticated matching algorithms.
        """
        # GPA requirements
        if self.min_gpa and (not profile.gpa or profile.gpa < self.min_gpa):
            return False
        if self.max_gpa and profile.gpa and profile.gpa > self.max_gpa:
            return False

        # Test score requirements
        if self.min_sat_score and (
            not profile.sat_score or profile.sat_score < self.min_sat_score
        ):
            if not (
                self.min_act_score
                and profile.act_score
                and profile.act_score >= self.min_act_score
            ):
                return False

        # Geographic requirements
        if self.eligible_states and profile.state:
            if profile.state not in self.eligible_states:
                return False

        # Major requirements
        if self.required_majors and profile.intended_major:
            if profile.intended_major not in self.required_majors:
                return False

        # Demographic requirements
        if self.first_generation_college_required is not None:
            if (
                profile.first_generation_college
                != self.first_generation_college_required
            ):
                return False

        # Income requirements
        if self.income_max and profile.household_income_range:
            # This would need more sophisticated parsing of income ranges
            pass

        return True

    def calculate_match_score(self, profile) -> float:
        """
        Calculate a match score (0-100) based on how well the profile matches.
        Higher scores indicate better matches.
        """
        score = 0.0
        total_criteria = 0

        # GPA matching (weighted heavily)
        if self.min_gpa and profile.gpa:
            total_criteria += 3
            if profile.gpa >= self.min_gpa:
                score += 3
                # Bonus for exceeding minimum
                if profile.gpa > self.min_gpa:
                    score += min(1.0, (profile.gpa - self.min_gpa) * 2)

        # Major matching
        if self.required_majors and profile.intended_major:
            total_criteria += 2
            if profile.intended_major in self.required_majors:
                score += 2

        # Geographic matching
        if self.eligible_states and profile.state:
            total_criteria += 1
            if profile.state in self.eligible_states:
                score += 1

        # Academic interests alignment
        if self.academic_interests and profile.academic_interests:
            total_criteria += 2
            common_interests = set(self.academic_interests) & set(
                profile.academic_interests
            )
            if common_interests:
                score += 2 * (len(common_interests) / len(self.academic_interests))

        # Activity matching
        if self.required_activities and profile.extracurricular_activities:
            total_criteria += 1
            common_activities = set(self.required_activities) & set(
                profile.extracurricular_activities
            )
            if common_activities:
                score += 1

        # Convert to percentage
        if total_criteria == 0:
            return 50.0  # Neutral score if no criteria to match

        return min(100.0, (score / total_criteria) * 100)


class ScholarshipMatch(Base):
    """
    Junction table to store calculated matches between users and scholarships
    with match scores and status tracking
    """

    __tablename__ = "scholarship_matches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    scholarship_id = Column(
        Integer, ForeignKey("scholarships.id"), nullable=False, index=True
    )

    # Match Information
    match_score = Column(Float, nullable=False, index=True)  # 0-100 compatibility score
    match_reasons = Column(ARRAY(String), nullable=True)  # Why it matched
    mismatch_reasons = Column(
        ARRAY(String), nullable=True
    )  # Why it didn't match perfectly

    # User Interaction Tracking
    viewed = Column(Boolean, default=False, nullable=False)
    interested = Column(
        Boolean, nullable=True
    )  # True=interested, False=not interested, None=not set
    applied = Column(Boolean, default=False, nullable=False)
    bookmarked = Column(Boolean, default=False, nullable=False)

    # Status and Tracking
    match_date = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    viewed_at = Column(DateTime(timezone=True), nullable=True)
    applied_at = Column(DateTime(timezone=True), nullable=True)
    deadline_reminder_sent = Column(Boolean, default=False, nullable=False)

    # Relationships
    user = relationship("User", back_populates="scholarship_matches")
    scholarship = relationship("Scholarship", back_populates="matches")

    # Composite index for efficient queries
    __table_args__ = (
        Index("idx_user_scholarship_match", "user_id", "scholarship_id"),
        Index("idx_user_match_score", "user_id", "match_score"),
    )

    def __repr__(self):
        return f"<ScholarshipMatch(user_id={self.user_id}, scholarship_id={self.scholarship_id}, score={self.match_score})>"
