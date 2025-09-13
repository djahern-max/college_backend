# app/models/scholarship.py
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
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from enum import Enum
from typing import List, Optional
from datetime import datetime
import logging
from app.models.institution import ImageExtractionStatus

logger = logging.getLogger(__name__)


class ScholarshipType(str, Enum):
    """Types of scholarships available"""

    ACADEMIC_MERIT = "academic_merit"
    NEED_BASED = "need_based"
    ATHLETIC = "athletic"
    STEM = "stem"
    ARTS = "arts"
    DIVERSITY = "diversity"
    FIRST_GENERATION = "first_generation"
    COMMUNITY_SERVICE = "community_service"
    LEADERSHIP = "leadership"
    LOCAL_COMMUNITY = "local_community"
    EMPLOYER_SPONSORED = "employer_sponsored"
    MILITARY = "military"
    RELIGIOUS = "religious"
    CAREER_SPECIFIC = "career_specific"
    ESSAY_BASED = "essay_based"
    RENEWABLE = "renewable"


class ScholarshipStatus(str, Enum):
    """Status of scholarship listings"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"


class DifficultyLevel(str, Enum):
    """Application difficulty levels"""

    EASY = "easy"  # Basic info only
    MODERATE = "moderate"  # Essays + transcripts
    HARD = "hard"  # Multiple essays, interviews
    VERY_HARD = "very_hard"  # Extensive requirements


class Scholarship(Base):
    """
    Scholarship model with comprehensive matching criteria
    """

    __tablename__ = "scholarships"

    # ===========================
    # PRIMARY KEY & BASIC INFO
    # ===========================
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    organization = Column(String(255), nullable=False, index=True)
    website_url = Column(String(500), nullable=True)
    application_url = Column(String(500), nullable=True)

    # ===========================
    # SCHOLARSHIP CLASSIFICATION
    # ===========================
    scholarship_type = Column(SQLEnum(ScholarshipType), nullable=False, index=True)
    categories = Column(ARRAY(String), nullable=True)  # Additional tags
    status = Column(
        SQLEnum(ScholarshipStatus), default=ScholarshipStatus.ACTIVE, nullable=False
    )
    difficulty_level = Column(
        SQLEnum(DifficultyLevel), default=DifficultyLevel.MODERATE, nullable=False
    )

    # ===========================
    # FINANCIAL INFORMATION
    # ===========================
    amount_min = Column(Integer, nullable=True)  # Minimum award amount
    amount_max = Column(Integer, nullable=True)  # Maximum award amount
    amount_exact = Column(Integer, nullable=True)  # Exact amount if fixed
    is_renewable = Column(Boolean, default=False)
    renewal_years = Column(Integer, nullable=True)  # How many years renewable
    number_of_awards = Column(Integer, nullable=True)  # How many recipients

    # ===========================
    # ACADEMIC REQUIREMENTS
    # ===========================
    min_gpa = Column(Float, nullable=True)
    max_gpa = Column(Float, nullable=True)  # Some scholarships have GPA caps
    min_sat_score = Column(Integer, nullable=True)
    min_act_score = Column(Integer, nullable=True)
    required_majors = Column(ARRAY(String), nullable=True)
    excluded_majors = Column(ARRAY(String), nullable=True)
    academic_level = Column(
        ARRAY(String), nullable=True
    )  # ["undergraduate", "graduate", "phd"]

    # ===========================
    # DEMOGRAPHIC REQUIREMENTS
    # ===========================
    eligible_ethnicities = Column(ARRAY(String), nullable=True)
    gender_requirements = Column(
        ARRAY(String), nullable=True
    )  # ["female", "male", "non-binary", "any"]
    first_generation_college_required = Column(Boolean, nullable=True)

    # ===========================
    # FINANCIAL NEED REQUIREMENTS
    # ===========================
    income_max = Column(Integer, nullable=True)  # Max household income
    income_min = Column(Integer, nullable=True)  # Min household income (rare)
    need_based_required = Column(Boolean, default=False)

    # ===========================
    # GEOGRAPHIC REQUIREMENTS
    # ===========================
    eligible_states = Column(ARRAY(String), nullable=True)
    eligible_cities = Column(ARRAY(String), nullable=True)
    eligible_counties = Column(ARRAY(String), nullable=True)
    zip_codes = Column(ARRAY(String), nullable=True)
    international_students_eligible = Column(Boolean, default=False)

    # ===========================
    # SCHOOL & EDUCATION REQUIREMENTS
    # ===========================
    eligible_schools = Column(ARRAY(String), nullable=True)  # Specific colleges
    high_school_names = Column(ARRAY(String), nullable=True)  # Specific high schools
    graduation_year_min = Column(Integer, nullable=True)
    graduation_year_max = Column(Integer, nullable=True)

    # ===========================
    # ACTIVITY & EXPERIENCE REQUIREMENTS
    # ===========================
    required_activities = Column(ARRAY(String), nullable=True)
    volunteer_hours_min = Column(Integer, nullable=True)
    leadership_required = Column(Boolean, default=False)
    work_experience_required = Column(Boolean, default=False)
    special_talents = Column(ARRAY(String), nullable=True)

    # ===========================
    # APPLICATION REQUIREMENTS
    # ===========================
    essay_required = Column(Boolean, default=False)
    essay_topics = Column(ARRAY(String), nullable=True)
    essay_word_limit = Column(Integer, nullable=True)
    transcript_required = Column(Boolean, default=True)
    recommendation_letters_required = Column(Integer, default=0)
    portfolio_required = Column(Boolean, default=False)
    interview_required = Column(Boolean, default=False)

    # Essay-specific requirements
    personal_statement_required = Column(Boolean, default=False)
    leadership_essay_required = Column(Boolean, default=False)
    community_service_essay_required = Column(Boolean, default=False)

    # ===========================
    # DATES & DEADLINES
    # ===========================
    application_opens = Column(DateTime(timezone=True), nullable=True)
    deadline = Column(DateTime(timezone=True), nullable=True)
    award_date = Column(DateTime(timezone=True), nullable=True)
    is_rolling_deadline = Column(Boolean, default=False)

    # ===========================
    # ADDITIONAL PREFERENCES
    # ===========================
    languages_preferred = Column(ARRAY(String), nullable=True)
    military_affiliation_required = Column(Boolean, default=False)
    employer_affiliation = Column(String(255), nullable=True)

    # ===========================
    # IMAGE INFORMATION
    # ===========================
    primary_image_url = Column(
        String(500),
        nullable=True,
        comment="CDN URL to standardized scholarship card image",
    )
    primary_image_quality_score = Column(
        Integer,
        nullable=True,
        comment="Quality score 0-100 for ranking scholarships by image quality",
        index=True,
    )
    logo_image_url = Column(
        String(500), nullable=True, comment="CDN URL to organization logo"
    )
    image_extraction_status = Column(
        SQLEnum(ImageExtractionStatus),
        default=ImageExtractionStatus.PENDING,
        index=True,
        comment="Status of image extraction process",
    )
    image_extraction_date = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When images were last extracted/updated",
    )

    # ===========================
    # METADATA & ADMINISTRATION
    # ===========================
    verified = Column(Boolean, default=False)  # Admin-verified scholarship
    featured = Column(Boolean, default=False)  # Featured on homepage
    views_count = Column(Integer, default=0)
    applications_count = Column(Integer, default=0)

    # AI-generated fields
    ai_generated_summary = Column(Text, nullable=True)
    matching_keywords = Column(ARRAY(String), nullable=True)

    # Admin fields
    created_by = Column(
        Integer, ForeignKey("users.id"), nullable=True
    )  # Admin who added
    last_verified_at = Column(DateTime(timezone=True), nullable=True)
    verification_notes = Column(Text, nullable=True)

    # ===========================
    # TIMESTAMPS
    # ===========================
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # ===========================
    # RELATIONSHIPS
    # ===========================
    matches = relationship(
        "ScholarshipMatch", back_populates="scholarship", cascade="all, delete-orphan"
    )
    created_by_user = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<Scholarship(id={self.id}, title='{self.title}', organization='{self.organization}')>"

    # ===========================
    # IMAGE PROPERTIES & METHODS
    # ===========================

    @property
    def display_image_url(self) -> Optional[str]:
        """Return the best available image URL for display"""
        if self.primary_image_url:
            return self.primary_image_url
        elif self.logo_image_url:
            return self.logo_image_url
        else:
            return self._get_fallback_image_url()

    def _get_fallback_image_url(self) -> str:
        """Get fallback image based on scholarship characteristics"""
        base_url = "https://magicscholar-images.nyc3.digitaloceanspaces.com/fallbacks/"

        if self.scholarship_type == ScholarshipType.STEM:
            return f"{base_url}stem_scholarship.jpg"
        elif self.scholarship_type == ScholarshipType.ARTS:
            return f"{base_url}arts_scholarship.jpg"
        elif self.scholarship_type == ScholarshipType.ATHLETIC:
            return f"{base_url}athletic_scholarship.jpg"
        elif self.scholarship_type == ScholarshipType.DIVERSITY:
            return f"{base_url}diversity_scholarship.jpg"
        elif self.scholarship_type == ScholarshipType.NEED_BASED:
            return f"{base_url}need_based_scholarship.jpg"
        else:
            return f"{base_url}general_scholarship.jpg"

    @property
    def has_high_quality_image(self) -> bool:
        """Check if scholarship has a high-quality image (score 80+)"""
        return (
            self.primary_image_quality_score is not None
            and self.primary_image_quality_score >= 80
        )

    @property
    def has_good_image(self) -> bool:
        """Check if scholarship has a good quality image (score 60+)"""
        return (
            self.primary_image_quality_score is not None
            and self.primary_image_quality_score >= 60
        )

    def update_image_info(
        self,
        image_url: str,
        quality_score: int,
        logo_url: Optional[str] = None,
        status: ImageExtractionStatus = ImageExtractionStatus.SUCCESS,
    ):
        """Update image information for the scholarship"""
        self.primary_image_url = image_url
        self.primary_image_quality_score = quality_score
        if logo_url:
            self.logo_image_url = logo_url
        self.image_extraction_status = status
        self.image_extraction_date = datetime.utcnow()

    # ===========================
    # MATCHING LOGIC METHODS
    # ===========================

    def matches_profile_basic(self, profile) -> bool:
        """
        Basic eligibility check - hard requirements only
        Returns True if profile meets all hard requirements
        """
        # GPA requirements
        if self.min_gpa and (not profile.gpa or profile.gpa < self.min_gpa):
            return False
        if self.max_gpa and profile.gpa and profile.gpa > self.max_gpa:
            return False

        # Test score requirements (either SAT OR ACT acceptable)
        test_score_required = bool(self.min_sat_score or self.min_act_score)
        if test_score_required:
            sat_qualifies = (
                self.min_sat_score
                and profile.sat_score
                and profile.sat_score >= self.min_sat_score
            )
            act_qualifies = (
                self.min_act_score
                and profile.act_score
                and profile.act_score >= self.min_act_score
            )
            if not (sat_qualifies or act_qualifies):
                return False

        # Geographic eligibility
        if self.eligible_states and profile.state:
            if profile.state not in self.eligible_states:
                return False

        # Major requirements
        if self.required_majors and profile.intended_major:
            if profile.intended_major not in self.required_majors:
                return False

        # Excluded majors
        if self.excluded_majors and profile.intended_major:
            if profile.intended_major in self.excluded_majors:
                return False

        # Demographic requirements
        if self.first_generation_college_required is not None:
            if (
                profile.first_generation_college
                != self.first_generation_college_required
            ):
                return False

        return True

    def calculate_match_score(self, profile) -> float:
        """
        Calculate detailed match score (0-100)
        Higher score = better match
        """
        if not self.matches_profile_basic(profile):
            return 0.0

        score = 0.0
        max_possible_score = 0.0

        # Academic alignment (40% of score)
        academic_score, academic_max = self._calculate_academic_score(profile)
        score += academic_score
        max_possible_score += academic_max

        # Activity alignment (25% of score)
        activity_score, activity_max = self._calculate_activity_score(profile)
        score += activity_score
        max_possible_score += activity_max

        # Demographic bonus (15% of score)
        demo_score, demo_max = self._calculate_demographic_score(profile)
        score += demo_score
        max_possible_score += demo_max

        # Essay readiness (10% of score)
        essay_score, essay_max = self._calculate_essay_score(profile)
        score += essay_score
        max_possible_score += essay_max

        # Special alignment (10% of score)
        special_score, special_max = self._calculate_special_score(profile)
        score += special_score
        max_possible_score += special_max

        if max_possible_score == 0:
            return 50.0  # Neutral score if no criteria to evaluate

        return min(100.0, (score / max_possible_score) * 100)

    def _calculate_academic_score(self, profile) -> tuple:
        """Calculate academic alignment score"""
        score = 0.0
        max_score = 40.0

        # GPA excellence bonus
        if profile.gpa:
            if profile.gpa >= 3.8:
                score += 15.0
            elif profile.gpa >= 3.5:
                score += 12.0
            elif profile.gpa >= 3.0:
                score += 8.0
            else:
                score += 5.0
        else:
            max_score -= 15.0

        # Test score excellence
        if profile.sat_score:
            if profile.sat_score >= 1450:
                score += 15.0
            elif profile.sat_score >= 1350:
                score += 12.0
            elif profile.sat_score >= 1200:
                score += 8.0
            else:
                score += 5.0
        elif profile.act_score:
            if profile.act_score >= 32:
                score += 15.0
            elif profile.act_score >= 28:
                score += 12.0
            elif profile.act_score >= 24:
                score += 8.0
            else:
                score += 5.0
        else:
            max_score -= 15.0

        # Academic interests alignment
        if self.required_majors and profile.academic_interests:
            interest_matches = len(
                set(self.required_majors) & set(profile.academic_interests)
            )
            score += min(10.0, interest_matches * 3.0)
        else:
            max_score -= 10.0

        return score, max_score

    def _calculate_activity_score(self, profile) -> tuple:
        """Calculate activity alignment score"""
        score = 0.0
        max_score = 25.0

        # Required activities match
        if self.required_activities and profile.extracurricular_activities:
            matches = len(
                set(self.required_activities) & set(profile.extracurricular_activities)
            )
            score += min(10.0, matches * 5.0)
        else:
            max_score -= 10.0

        # Volunteer hours
        if self.volunteer_hours_min and profile.volunteer_hours:
            if profile.volunteer_hours >= self.volunteer_hours_min * 2:
                score += 10.0
            elif profile.volunteer_hours >= self.volunteer_hours_min:
                score += 8.0
            else:
                score += 3.0
        elif profile.volunteer_hours and profile.volunteer_hours > 0:
            score += 5.0  # General volunteer bonus
        else:
            max_score -= 10.0

        # Leadership activities
        if self.leadership_required and profile.extracurricular_activities:
            leadership_keywords = ["president", "captain", "leader", "chair", "head"]
            has_leadership = any(
                any(keyword in activity.lower() for keyword in leadership_keywords)
                for activity in profile.extracurricular_activities
            )
            if has_leadership:
                score += 5.0
        else:
            max_score -= 5.0

        return score, max_score

    def _calculate_demographic_score(self, profile) -> tuple:
        """Calculate demographic bonus score"""
        score = 0.0
        max_score = 15.0

        # Ethnicity match bonus
        if self.eligible_ethnicities and profile.ethnicity:
            if any(eth in self.eligible_ethnicities for eth in profile.ethnicity):
                score += 8.0
        else:
            max_score -= 8.0

        # First-generation bonus
        if self.first_generation_college_required and profile.first_generation_college:
            score += 7.0
        else:
            max_score -= 7.0

        return score, max_score

    def _calculate_essay_score(self, profile) -> tuple:
        """Calculate essay readiness score"""
        score = 0.0
        max_score = 10.0

        if self.essay_required:
            if profile.has_personal_statement:
                score += 5.0
            if self.leadership_essay_required and profile.has_leadership_essay:
                score += 5.0
            elif not self.leadership_essay_required:
                max_score -= 5.0
        else:
            max_score = 0.0

        return score, max_score

    def _calculate_special_score(self, profile) -> tuple:
        """Calculate special talents/languages bonus"""
        score = 0.0
        max_score = 10.0

        # Special talents match
        if self.special_talents and profile.special_talents:
            matches = len(set(self.special_talents) & set(profile.special_talents))
            score += min(5.0, matches * 2.0)
        else:
            max_score -= 5.0

        # Language match
        if self.languages_preferred and profile.languages_spoken:
            matches = len(set(self.languages_preferred) & set(profile.languages_spoken))
            score += min(5.0, matches * 2.0)
        else:
            max_score -= 5.0

        return score, max_score


class ScholarshipMatch(Base):
    """
    User-Scholarship matching results with tracking
    """

    __tablename__ = "scholarship_matches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    scholarship_id = Column(
        Integer, ForeignKey("scholarships.id"), nullable=False, index=True
    )

    # Match scoring
    match_score = Column(Float, nullable=False)  # 0-100 score
    match_reasons = Column(JSON, nullable=True)  # Why it's a good match
    mismatch_reasons = Column(JSON, nullable=True)  # Potential concerns

    # User interaction tracking
    viewed = Column(Boolean, default=False)
    interested = Column(Boolean, nullable=True)  # True/False/None
    applied = Column(Boolean, default=False)
    bookmarked = Column(Boolean, default=False)

    # Status tracking
    application_status = Column(
        String(50), nullable=True
    )  # "planning", "in_progress", "submitted", "rejected", "awarded"
    notes = Column(Text, nullable=True)  # User notes

    # Timestamps
    match_date = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    viewed_at = Column(DateTime(timezone=True), nullable=True)
    applied_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User")
    scholarship = relationship("Scholarship", back_populates="matches")

    def __repr__(self):
        return f"<ScholarshipMatch(user_id={self.user_id}, scholarship_id={self.scholarship_id}, score={self.match_score})>"
