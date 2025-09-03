# app/models/college.py
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
import logging

logger = logging.getLogger(__name__)


class CollegeType(str, Enum):
    """Types of colleges and universities"""

    PUBLIC = "public"
    PRIVATE_NONPROFIT = "private_nonprofit"
    PRIVATE_FOR_PROFIT = "private_for_profit"
    COMMUNITY_COLLEGE = "community_college"


class CollegeSize(str, Enum):
    """College size categories"""

    SMALL = "small"  # Under 2,000
    MEDIUM = "medium"  # 2,000 - 15,000
    LARGE = "large"  # Over 15,000


class AdmissionDifficulty(str, Enum):
    """Admission difficulty levels"""

    MOST_DIFFICULT = "most_difficult"  # <25% acceptance
    VERY_DIFFICULT = "very_difficult"  # 25-49% acceptance
    MODERATELY_DIFFICULT = "moderately_difficult"  # 50-74% acceptance
    MINIMALLY_DIFFICULT = "minimally_difficult"  # 75-89% acceptance
    NONCOMPETITIVE = "noncompetitive"  # >90% acceptance


class College(Base):
    """
    College/University model with comprehensive data for matching
    """

    __tablename__ = "colleges"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Basic Information
    name = Column(String(255), nullable=False, index=True)
    short_name = Column(String(100), nullable=True)  # Common abbreviation
    website = Column(String(255), nullable=True)

    # Location
    city = Column(String(100), nullable=False)
    state = Column(String(50), nullable=False, index=True)
    zip_code = Column(String(10), nullable=True)
    region = Column(String(50), nullable=True)  # Northeast, Southeast, etc.

    # Institution Type
    college_type = Column(SQLEnum(CollegeType), nullable=False, index=True)
    is_historically_black = Column(Boolean, default=False)
    is_hispanic_serving = Column(Boolean, default=False)
    is_tribal_college = Column(Boolean, default=False)
    is_women_only = Column(Boolean, default=False)
    is_men_only = Column(Boolean, default=False)

    # Size and Demographics
    total_enrollment = Column(Integer, nullable=True)
    undergraduate_enrollment = Column(Integer, nullable=True)
    graduate_enrollment = Column(Integer, nullable=True)
    college_size = Column(SQLEnum(CollegeSize), nullable=True, index=True)

    # Academic Information
    acceptance_rate = Column(Float, nullable=True)  # 0.0 to 1.0
    admission_difficulty = Column(
        SQLEnum(AdmissionDifficulty), nullable=True, index=True
    )

    # Test Score Ranges (25th-75th percentile)
    sat_math_25 = Column(Integer, nullable=True)
    sat_math_75 = Column(Integer, nullable=True)
    sat_reading_25 = Column(Integer, nullable=True)
    sat_reading_75 = Column(Integer, nullable=True)
    sat_total_25 = Column(Integer, nullable=True)
    sat_total_75 = Column(Integer, nullable=True)

    act_composite_25 = Column(Integer, nullable=True)
    act_composite_75 = Column(Integer, nullable=True)

    # GPA Requirements
    avg_gpa = Column(Float, nullable=True)
    min_gpa_recommended = Column(Float, nullable=True)

    # Financial Information
    tuition_in_state = Column(Integer, nullable=True)
    tuition_out_of_state = Column(Integer, nullable=True)
    room_and_board = Column(Integer, nullable=True)
    total_cost_in_state = Column(Integer, nullable=True)
    total_cost_out_of_state = Column(Integer, nullable=True)

    # Financial Aid
    avg_financial_aid = Column(Integer, nullable=True)
    percent_receiving_aid = Column(Float, nullable=True)
    avg_net_price = Column(Integer, nullable=True)

    # Academic Programs
    available_majors = Column(ARRAY(String), nullable=True)
    popular_majors = Column(ARRAY(String), nullable=True)
    strong_programs = Column(
        ARRAY(String), nullable=True
    )  # Nationally recognized programs

    # Campus Life
    campus_setting = Column(String(50), nullable=True)  # Urban, Suburban, Rural
    housing_guaranteed = Column(Boolean, default=False)
    greek_life_available = Column(Boolean, default=False)

    # Athletics
    athletic_division = Column(String(20), nullable=True)  # D1, D2, D3, NAIA, etc.
    athletic_conferences = Column(ARRAY(String), nullable=True)

    # Rankings and Recognition
    us_news_ranking = Column(Integer, nullable=True)
    forbes_ranking = Column(Integer, nullable=True)
    other_rankings = Column(JSON, nullable=True)

    # Outcomes
    graduation_rate_4_year = Column(Float, nullable=True)
    graduation_rate_6_year = Column(Float, nullable=True)
    retention_rate = Column(Float, nullable=True)
    employment_rate = Column(Float, nullable=True)
    avg_starting_salary = Column(Integer, nullable=True)

    # Diversity
    percent_white = Column(Float, nullable=True)
    percent_black = Column(Float, nullable=True)
    percent_hispanic = Column(Float, nullable=True)
    percent_asian = Column(Float, nullable=True)
    percent_international = Column(Float, nullable=True)

    # Application Information
    application_deadline = Column(String(50), nullable=True)
    early_decision_deadline = Column(String(50), nullable=True)
    early_action_deadline = Column(String(50), nullable=True)
    application_fee = Column(Integer, nullable=True)
    common_app_accepted = Column(Boolean, default=False)

    # Requirements
    essays_required = Column(Boolean, default=False)
    letters_of_recommendation = Column(Integer, nullable=True)
    interview_required = Column(Boolean, default=False)

    # Status and Verification
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    data_source = Column(String(100), nullable=True)  # Where data came from

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    college_matches = relationship(
        "CollegeMatch", back_populates="college", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<College(id={self.id}, name='{self.name}', state='{self.state}')>"

    def matches_profile_basic(self, profile) -> bool:
        """Basic eligibility check for a student profile"""
        try:
            # GPA requirement
            if self.min_gpa_recommended and profile.gpa:
                if profile.gpa < self.min_gpa_recommended:
                    return False

            # Test score requirements (if college requires them)
            if self.sat_total_25 and profile.sat_score:
                if profile.sat_score < (
                    self.sat_total_25 - 50
                ):  # Allow some flexibility
                    return False

            if self.act_composite_25 and profile.act_score:
                if profile.act_score < (
                    self.act_composite_25 - 2
                ):  # Allow some flexibility
                    return False

            # Major availability
            if self.available_majors and profile.intended_major:
                if profile.intended_major not in self.available_majors:
                    return False

            return True

        except Exception as e:
            logger.error(f"Error in basic matching for college {self.id}: {str(e)}")
            return False

    def calculate_match_score(self, profile) -> float:
        """Calculate compatibility score (0-100) between college and student profile"""
        try:
            score = 0.0
            max_score = 0.0

            # Academic Fit (40% of total score)
            academic_score, academic_max = self._calculate_academic_score(profile)
            score += academic_score
            max_score += academic_max

            # Financial Fit (20% of total score)
            financial_score, financial_max = self._calculate_financial_score(profile)
            score += financial_score
            max_score += financial_max

            # Location Preference (15% of total score)
            location_score, location_max = self._calculate_location_score(profile)
            score += location_score
            max_score += location_max

            # Size and Environment (15% of total score)
            environment_score, environment_max = self._calculate_environment_score(
                profile
            )
            score += environment_score
            max_score += environment_max

            # Program Strength (10% of total score)
            program_score, program_max = self._calculate_program_score(profile)
            score += program_score
            max_score += program_max

            if max_score == 0:
                return 0.0

            return round((score / max_score) * 100, 1)

        except Exception as e:
            logger.error(
                f"Error calculating match score for college {self.id}: {str(e)}"
            )
            return 0.0

    def _calculate_academic_score(self, profile) -> tuple:
        """Calculate academic fit score"""
        score = 0.0
        max_score = 40.0

        # GPA fit (15 points)
        if self.avg_gpa and profile.gpa:
            gpa_diff = abs(profile.gpa - self.avg_gpa)
            if gpa_diff <= 0.2:
                score += 15  # Perfect match
            elif gpa_diff <= 0.5:
                score += 12  # Good match
            elif gpa_diff <= 0.8:
                score += 8  # Acceptable match
            else:
                score += 3  # Reach/safety school

        # Test score fit (15 points)
        if profile.sat_score and self.sat_total_25 and self.sat_total_75:
            if self.sat_total_25 <= profile.sat_score <= self.sat_total_75:
                score += 15  # In range
            elif profile.sat_score >= self.sat_total_75:
                score += 12  # Above range (safety)
            elif profile.sat_score >= (self.sat_total_25 - 100):
                score += 8  # Slightly below (reach)
            else:
                score += 2  # Well below (high reach)
        elif profile.act_score and self.act_composite_25 and self.act_composite_75:
            if self.act_composite_25 <= profile.act_score <= self.act_composite_75:
                score += 15
            elif profile.act_score >= self.act_composite_75:
                score += 12
            elif profile.act_score >= (self.act_composite_25 - 3):
                score += 8
            else:
                score += 2

        # Admission difficulty vs. profile strength (10 points)
        if self.acceptance_rate:
            if self.acceptance_rate >= 0.7:  # Less competitive
                score += 8
            elif self.acceptance_rate >= 0.5:  # Moderately competitive
                score += 10
            elif self.acceptance_rate >= 0.3:  # Very competitive
                score += 6
            else:  # Highly competitive
                score += 4

        return score, max_score

    def _calculate_financial_score(self, profile) -> tuple:
        """Calculate financial fit score"""
        score = 0.0
        max_score = 20.0

        if not profile.household_income_range:
            return score, max_score

        # Estimate financial capacity based on income range
        income_mapping = {
            "Under $25,000": 15000,
            "$25,000 - $50,000": 37500,
            "$50,000 - $75,000": 62500,
            "$75,000 - $100,000": 87500,
            "$100,000 - $150,000": 125000,
            "Over $150,000": 200000,
        }

        estimated_income = income_mapping.get(profile.household_income_range, 50000)

        # Calculate affordability
        if profile.state == self.state and self.total_cost_in_state:
            total_cost = self.total_cost_in_state
        elif self.total_cost_out_of_state:
            total_cost = self.total_cost_out_of_state
        else:
            return score, max_score

        # Consider financial aid
        net_cost = total_cost
        if self.avg_net_price:
            net_cost = self.avg_net_price

        # Score based on affordability
        affordable_threshold = estimated_income * 0.3  # 30% of income
        if net_cost <= affordable_threshold:
            score += 20  # Very affordable
        elif net_cost <= affordable_threshold * 1.5:
            score += 15  # Affordable with some stretch
        elif net_cost <= affordable_threshold * 2:
            score += 10  # Challenging but possible
        else:
            score += 5  # Financial reach

        return score, max_score

    def _calculate_location_score(self, profile) -> tuple:
        """Calculate location preference score"""
        score = 0.0
        max_score = 15.0

        # In-state preference (10 points)
        if profile.state == self.state:
            score += 10
        elif profile.preferred_college_location:
            if profile.preferred_college_location.lower() in self.region.lower():
                score += 6
            else:
                score += 2
        else:
            score += 5  # Neutral if no preference

        # Campus setting preference (5 points)
        if profile.preferred_college_location:
            if (
                "urban" in profile.preferred_college_location.lower()
                and self.campus_setting == "Urban"
            ):
                score += 5
            elif (
                "suburban" in profile.preferred_college_location.lower()
                and self.campus_setting == "Suburban"
            ):
                score += 5
            elif (
                "rural" in profile.preferred_college_location.lower()
                and self.campus_setting == "Rural"
            ):
                score += 5
            else:
                score += 2
        else:
            score += 3  # Neutral

        return score, max_score

    def _calculate_environment_score(self, profile) -> tuple:
        """Calculate campus environment fit score"""
        score = 0.0
        max_score = 15.0

        # Size preference (10 points)
        if profile.preferred_college_size:
            if profile.preferred_college_size.lower() == self.college_size.value:
                score += 10
            elif (
                abs(
                    CollegeSize.__members__[
                        profile.preferred_college_size.upper()
                    ].value
                    - self.college_size.value
                )
                == 1
            ):
                score += 6  # Adjacent size category
            else:
                score += 2
        else:
            score += 6  # Neutral if no preference

        # Diversity considerations (5 points)
        if profile.ethnicity:
            # Bonus for diverse campuses or those serving specific populations
            if (
                self.is_historically_black
                and "Black or African American" in profile.ethnicity
            ):
                score += 5
            elif self.is_hispanic_serving and any(
                "Hispanic" in eth or "Latino" in eth for eth in profile.ethnicity
            ):
                score += 5
            elif self.percent_white and self.percent_white < 0.7:  # Diverse campus
                score += 4
            else:
                score += 3
        else:
            score += 3

        return score, max_score

    def _calculate_program_score(self, profile) -> tuple:
        """Calculate academic program strength score"""
        score = 0.0
        max_score = 10.0

        if not profile.intended_major:
            return score, max_score

        # Major availability and strength
        if self.available_majors and profile.intended_major in self.available_majors:
            score += 5  # Major available

            # Bonus for program strength
            if self.strong_programs and profile.intended_major in self.strong_programs:
                score += 3  # Nationally recognized program
            elif self.popular_majors and profile.intended_major in self.popular_majors:
                score += 2  # Popular program
            else:
                score += 1
        else:
            score += 1  # May have similar programs

        return score, max_score


class CollegeMatch(Base):
    """
    Student-College match results and tracking
    """

    __tablename__ = "college_matches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    college_id = Column(Integer, ForeignKey("colleges.id"), nullable=False, index=True)

    # Match scoring
    match_score = Column(Float, nullable=False)  # 0-100
    match_category = Column(String(20), nullable=True)  # "safety", "match", "reach"
    match_reasons = Column(ARRAY(String), nullable=True)
    concerns = Column(ARRAY(String), nullable=True)

    # User interaction tracking
    viewed = Column(Boolean, default=False)
    interested = Column(
        Boolean, nullable=True
    )  # True/False/None for interested/not/neutral
    applied = Column(Boolean, default=False)
    bookmarked = Column(Boolean, default=False)

    # Application status
    application_status = Column(
        String(50), nullable=True
    )  # "planning", "started", "submitted", "accepted", etc.
    application_deadline = Column(DateTime(timezone=True), nullable=True)

    # Notes
    user_notes = Column(Text, nullable=True)

    # Timestamps
    match_date = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    viewed_at = Column(DateTime(timezone=True), nullable=True)
    applied_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    college = relationship("College", back_populates="college_matches")

    def __repr__(self):
        return f"<CollegeMatch(user_id={self.user_id}, college_id={self.college_id}, score={self.match_score})>"
