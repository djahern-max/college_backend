# app/services/college.py - IMPROVED VERSION
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from datetime import datetime, timedelta
import logging

from app.models.college import (
    College,
    CollegeMatch,
    CollegeType,
    CollegeSize,
    AdmissionDifficulty,
)
from app.models.profile import UserProfile
from app.schemas.college import (
    CollegeCreate,
    CollegeUpdate,
    CollegeSearchFilter,
    CollegeMatchUpdate,
    CollegeMatchSummary,
)

logger = logging.getLogger(__name__)


class CollegeService:
    """Service class for handling college operations and matching"""

    def __init__(self, db: Session):
        self.db = db

    # ===========================
    # BASIC CRUD OPERATIONS
    # ===========================

    def create_college(self, college_data: CollegeCreate) -> College:
        """Create a new college"""
        try:
            # Convert enum values properly
            college_dict = college_data.model_dump(exclude_unset=True)

            # Handle college_size properly - derive from enrollment if not provided
            if not college_dict.get("college_size") and college_dict.get(
                "total_enrollment"
            ):
                enrollment = college_dict["total_enrollment"]
                if enrollment < 2000:
                    college_dict["college_size"] = CollegeSize.SMALL
                elif enrollment <= 15000:
                    college_dict["college_size"] = CollegeSize.MEDIUM
                else:
                    college_dict["college_size"] = CollegeSize.LARGE

            db_college = College(**college_dict)

            self.db.add(db_college)
            self.db.commit()
            self.db.refresh(db_college)

            logger.info(f"Created college: {db_college.name} (ID: {db_college.id})")
            return db_college

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating college: {str(e)}")
            raise

    def get_college_by_id(self, college_id: int) -> Optional[College]:
        """Get college by ID"""
        return (
            self.db.query(College)
            .filter(College.id == college_id, College.is_active == True)
            .first()
        )

    def update_college(
        self, college_id: int, college_data: CollegeUpdate
    ) -> Optional[College]:
        """Update existing college"""
        try:
            db_college = self.db.query(College).filter(College.id == college_id).first()
            if not db_college:
                return None

            update_data = college_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_college, field, value)

            # Update college_size if enrollment changed
            if "total_enrollment" in update_data and update_data["total_enrollment"]:
                enrollment = update_data["total_enrollment"]
                if enrollment < 2000:
                    db_college.college_size = CollegeSize.SMALL
                elif enrollment <= 15000:
                    db_college.college_size = CollegeSize.MEDIUM
                else:
                    db_college.college_size = CollegeSize.LARGE

            db_college.updated_at = func.now()

            self.db.commit()
            self.db.refresh(db_college)

            logger.info(f"Updated college: {db_college.name} (ID: {college_id})")
            return db_college

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating college {college_id}: {str(e)}")
            raise

    def delete_college(self, college_id: int) -> bool:
        """Delete college (soft delete by setting inactive)"""
        try:
            db_college = self.db.query(College).filter(College.id == college_id).first()
            if not db_college:
                return False

            db_college.is_active = False
            db_college.updated_at = func.now()

            self.db.commit()

            logger.info(f"Soft deleted college: {db_college.name} (ID: {college_id})")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting college {college_id}: {str(e)}")
            raise

    def batch_create_colleges(
        self, colleges_data: List[CollegeCreate]
    ) -> Dict[str, Any]:
        """Batch create multiple colleges"""
        created_count = 0
        error_count = 0
        errors = []
        created_ids = []

        for i, college_data in enumerate(colleges_data):
            try:
                college = self.create_college(college_data)
                created_ids.append(college.id)
                created_count += 1

            except Exception as e:
                error_count += 1
                errors.append(f"College {i}: {str(e)}")
                logger.error(f"Error creating college {i}: {str(e)}")

        return {
            "success_count": created_count,
            "error_count": error_count,
            "errors": errors if errors else None,
            "created_ids": created_ids if created_ids else None,
        }

    # ===========================
    # SEARCH AND FILTERING
    # ===========================

    def search_colleges(
        self, filters: CollegeSearchFilter
    ) -> Tuple[List[College], int]:
        """Search colleges with comprehensive filters"""
        try:
            query = self.db.query(College)

            # Apply filters systematically
            query = self._apply_basic_filters(query, filters)
            query = self._apply_academic_filters(query, filters)
            query = self._apply_financial_filters(query, filters)
            query = self._apply_location_filters(query, filters)
            query = self._apply_program_filters(query, filters)
            query = self._apply_diversity_filters(query, filters)

            # Count total before pagination
            total = query.count()

            # Apply sorting
            query = self._apply_sorting(query, filters)

            # Apply pagination
            colleges = (
                query.offset((filters.page - 1) * filters.limit)
                .limit(filters.limit)
                .all()
            )

            return colleges, total

        except Exception as e:
            logger.error(f"Error searching colleges: {str(e)}")
            raise

    def _apply_basic_filters(self, query, filters):
        """Apply basic filters"""
        if filters.active_only:
            query = query.filter(College.is_active == True)

        if filters.verified_only:
            query = query.filter(College.is_verified == True)

        # Text search
        if filters.search_query:
            search_term = f"%{filters.search_query}%"
            query = query.filter(
                or_(
                    College.name.ilike(search_term),
                    College.short_name.ilike(search_term),
                    College.city.ilike(search_term),
                    College.state.ilike(search_term),
                )
            )

        return query

    def _apply_academic_filters(self, query, filters):
        """Apply academic-related filters"""
        if filters.min_acceptance_rate is not None:
            query = query.filter(College.acceptance_rate >= filters.min_acceptance_rate)

        if filters.max_acceptance_rate is not None:
            query = query.filter(College.acceptance_rate <= filters.max_acceptance_rate)

        if filters.admission_difficulty:
            query = query.filter(
                College.admission_difficulty == filters.admission_difficulty
            )

        # Student profile matching
        if filters.student_gpa is not None:
            query = query.filter(
                or_(
                    College.min_gpa_recommended.is_(None),
                    College.min_gpa_recommended <= filters.student_gpa,
                )
            )

        if filters.student_sat_score is not None:
            query = query.filter(
                or_(
                    College.sat_total_25.is_(None),
                    College.sat_total_25 <= (filters.student_sat_score + 100),
                )
            )

        if filters.student_act_score is not None:
            query = query.filter(
                or_(
                    College.act_composite_25.is_(None),
                    College.act_composite_25 <= (filters.student_act_score + 3),
                )
            )

        return query

    def _apply_financial_filters(self, query, filters):
        """Apply financial filters"""
        if filters.max_tuition_in_state is not None:
            query = query.filter(
                or_(
                    College.tuition_in_state.is_(None),
                    College.tuition_in_state <= filters.max_tuition_in_state,
                )
            )

        if filters.max_tuition_out_of_state is not None:
            query = query.filter(
                or_(
                    College.tuition_out_of_state.is_(None),
                    College.tuition_out_of_state <= filters.max_tuition_out_of_state,
                )
            )

        if filters.max_total_cost is not None:
            if filters.student_state:
                # Use appropriate cost based on residency
                query = query.filter(
                    or_(
                        and_(
                            College.state == filters.student_state,
                            or_(
                                College.total_cost_in_state.is_(None),
                                College.total_cost_in_state <= filters.max_total_cost,
                            ),
                        ),
                        and_(
                            College.state != filters.student_state,
                            or_(
                                College.total_cost_out_of_state.is_(None),
                                College.total_cost_out_of_state
                                <= filters.max_total_cost,
                            ),
                        ),
                    )
                )
            else:
                # Default to out-of-state cost
                query = query.filter(
                    or_(
                        College.total_cost_out_of_state.is_(None),
                        College.total_cost_out_of_state <= filters.max_total_cost,
                    )
                )

        return query

    def _apply_location_filters(self, query, filters):
        """Apply location filters"""
        if filters.state:
            query = query.filter(College.state == filters.state)

        if filters.region:
            query = query.filter(College.region == filters.region)

        if filters.campus_setting:
            query = query.filter(College.campus_setting == filters.campus_setting)

        return query

    def _apply_program_filters(self, query, filters):
        """Apply program and major filters"""
        if filters.student_major:
            query = query.filter(
                or_(
                    College.available_majors.is_(None),
                    College.available_majors.contains([filters.student_major]),
                )
            )

        if filters.strong_programs_only:
            query = query.filter(College.strong_programs.is_not(None))

        # Size filters
        if filters.min_enrollment is not None:
            query = query.filter(
                or_(
                    College.total_enrollment.is_(None),
                    College.total_enrollment >= filters.min_enrollment,
                )
            )

        if filters.max_enrollment is not None:
            query = query.filter(
                or_(
                    College.total_enrollment.is_(None),
                    College.total_enrollment <= filters.max_enrollment,
                )
            )

        if filters.college_type:
            query = query.filter(College.college_type == filters.college_type)

        if filters.college_size:
            query = query.filter(College.college_size == filters.college_size)

        return query

    def _apply_diversity_filters(self, query, filters):
        """Apply diversity and athletics filters"""
        if filters.historically_black is not None:
            query = query.filter(
                College.is_historically_black == filters.historically_black
            )

        if filters.hispanic_serving is not None:
            query = query.filter(
                College.is_hispanic_serving == filters.hispanic_serving
            )

        if filters.athletic_division:
            query = query.filter(College.athletic_division == filters.athletic_division)

        # Outcomes filters
        if filters.min_graduation_rate is not None:
            query = query.filter(
                or_(
                    College.graduation_rate_6_year.is_(None),
                    College.graduation_rate_6_year >= filters.min_graduation_rate,
                )
            )

        if filters.min_retention_rate is not None:
            query = query.filter(
                or_(
                    College.retention_rate.is_(None),
                    College.retention_rate >= filters.min_retention_rate,
                )
            )

        return query

    def _apply_sorting(self, query, filters):
        """Apply sorting to query"""
        # Validate sort_by field exists on College model
        valid_sort_fields = [
            "name",
            "acceptance_rate",
            "tuition_in_state",
            "tuition_out_of_state",
            "total_enrollment",
            "graduation_rate_6_year",
            "us_news_ranking",
        ]

        sort_field = filters.sort_by if filters.sort_by in valid_sort_fields else "name"
        sort_column = getattr(College, sort_field, College.name)

        if filters.sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        return query

    def search_colleges_by_name(
        self, name_query: str, limit: int = 20
    ) -> List[College]:
        """Search colleges by name for autocomplete"""
        search_term = f"%{name_query}%"
        return (
            self.db.query(College)
            .filter(
                College.is_active == True,
                or_(
                    College.name.ilike(search_term),
                    College.short_name.ilike(search_term),
                ),
            )
            .order_by(College.name)
            .limit(limit)
            .all()
        )

    def get_colleges_by_state(self, state: str) -> List[College]:
        """Get all colleges in a specific state"""
        return (
            self.db.query(College)
            .filter(College.state == state, College.is_active == True)
            .order_by(College.name)
            .all()
        )

    def get_similar_colleges(self, college_id: int, limit: int = 10) -> List[College]:
        """Get colleges similar to a given college"""
        base_college = self.get_college_by_id(college_id)
        if not base_college:
            return []

        query = self.db.query(College).filter(
            College.id != college_id,
            College.is_active == True,
        )

        # Apply similarity filters
        if base_college.college_type:
            query = query.filter(College.college_type == base_college.college_type)

        if base_college.college_size:
            query = query.filter(College.college_size == base_college.college_size)

        if base_college.acceptance_rate:
            query = query.filter(
                College.acceptance_rate.between(
                    max(0, base_college.acceptance_rate - 0.2),
                    min(1, base_college.acceptance_rate + 0.2),
                )
            )

        if base_college.region:
            query = query.filter(College.region == base_college.region)

        return query.limit(limit).all()

    # ===========================
    # MATCHING ALGORITHMS
    # ===========================

    def calculate_and_store_matches(
        self, user_id: int, force_recalculate: bool = False
    ) -> int:
        """Calculate and store matches for a user"""
        try:
            profile = (
                self.db.query(UserProfile)
                .filter(UserProfile.user_id == user_id)
                .first()
            )
            if not profile:
                logger.warning(f"No profile found for user {user_id}")
                return 0

            # Clear existing matches if force recalculate
            if force_recalculate:
                self.db.query(CollegeMatch).filter(
                    CollegeMatch.user_id == user_id
                ).delete()
                self.db.commit()

            # Get colleges without existing matches
            existing_college_ids = (
                self.db.query(CollegeMatch.college_id)
                .filter(CollegeMatch.user_id == user_id)
                .subquery()
            )

            colleges = (
                self.db.query(College)
                .filter(
                    College.is_active == True,
                    ~College.id.in_(existing_college_ids),
                )
                .all()
            )

            matches_created = 0
            for college in colleges:
                if self._check_basic_eligibility(college, profile):
                    score = self._calculate_match_score_safe(college, profile)

                    if score >= 20.0:  # Minimum threshold
                        match_category = self._determine_match_category(
                            college, profile, score
                        )
                        match_reasons = self._get_match_reasons(college, profile)
                        concerns = self._get_concerns(college, profile)

                        db_match = CollegeMatch(
                            user_id=user_id,
                            college_id=college.id,
                            match_score=score,
                            match_category=match_category,
                            match_reasons=match_reasons,
                            concerns=concerns,
                        )

                        self.db.add(db_match)
                        matches_created += 1

            self.db.commit()
            logger.info(f"Created {matches_created} college matches for user {user_id}")
            return matches_created

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error calculating matches for user {user_id}: {str(e)}")
            raise

    def _check_basic_eligibility(self, college: College, profile) -> bool:
        """Check basic eligibility for a college"""
        try:
            # GPA requirement
            if college.min_gpa_recommended and profile.gpa:
                if profile.gpa < college.min_gpa_recommended:
                    return False

            # Test score requirements with flexibility
            if college.sat_total_25 and profile.sat_score:
                if profile.sat_score < (college.sat_total_25 - 50):
                    return False

            if college.act_composite_25 and profile.act_score:
                if profile.act_score < (college.act_composite_25 - 2):
                    return False

            # Major availability
            if college.available_majors and profile.intended_major:
                if profile.intended_major not in college.available_majors:
                    return False

            return True

        except Exception as e:
            logger.error(
                f"Error checking eligibility for college {college.id}: {str(e)}"
            )
            return False

    def _calculate_match_score_safe(self, college: College, profile) -> float:
        """Safe match score calculation with error handling"""
        try:
            score = 0.0
            max_possible_score = 100.0

            # Academic fit (40% weight)
            academic_score = self._calculate_academic_score(college, profile)
            score += academic_score

            # Financial fit (20% weight)
            financial_score = self._calculate_financial_score(college, profile)
            score += financial_score

            # Location fit (15% weight)
            location_score = self._calculate_location_score(college, profile)
            score += location_score

            # Size and environment (15% weight)
            environment_score = self._calculate_environment_score(college, profile)
            score += environment_score

            # Program strength (10% weight)
            program_score = self._calculate_program_score(college, profile)
            score += program_score

            return round(min(score, max_possible_score), 1)

        except Exception as e:
            logger.error(
                f"Error calculating match score for college {college.id}: {str(e)}"
            )
            return 0.0

    def _calculate_academic_score(self, college: College, profile) -> float:
        """Calculate academic fit score (max 40 points)"""
        score = 0.0

        # GPA fit (15 points)
        if college.avg_gpa and profile.gpa:
            gpa_diff = abs(profile.gpa - college.avg_gpa)
            if gpa_diff <= 0.2:
                score += 15
            elif gpa_diff <= 0.5:
                score += 12
            elif gpa_diff <= 0.8:
                score += 8
            else:
                score += 3

        # Test score fit (15 points)
        if profile.sat_score and college.sat_total_25 and college.sat_total_75:
            if college.sat_total_25 <= profile.sat_score <= college.sat_total_75:
                score += 15
            elif profile.sat_score >= college.sat_total_75:
                score += 12
            elif profile.sat_score >= (college.sat_total_25 - 100):
                score += 8
            else:
                score += 2
        elif (
            profile.act_score and college.act_composite_25 and college.act_composite_75
        ):
            if (
                college.act_composite_25
                <= profile.act_score
                <= college.act_composite_75
            ):
                score += 15
            elif profile.act_score >= college.act_composite_75:
                score += 12
            elif profile.act_score >= (college.act_composite_25 - 3):
                score += 8
            else:
                score += 2

        # Acceptance rate consideration (10 points)
        if college.acceptance_rate:
            if college.acceptance_rate >= 0.7:
                score += 8
            elif college.acceptance_rate >= 0.5:
                score += 10
            elif college.acceptance_rate >= 0.3:
                score += 6
            else:
                score += 4

        return score

    def _calculate_financial_score(self, college: College, profile) -> float:
        """Calculate financial fit score (max 20 points)"""
        score = 0.0

        if (
            not hasattr(profile, "household_income_range")
            or not profile.household_income_range
        ):
            return 10.0  # Neutral score if no income data

        # Income mapping for affordability calculation
        income_mapping = {
            "Under $25,000": 15000,
            "$25,000 - $50,000": 37500,
            "$50,000 - $75,000": 62500,
            "$75,000 - $100,000": 87500,
            "$100,000 - $150,000": 125000,
            "Over $150,000": 200000,
        }

        estimated_income = income_mapping.get(profile.household_income_range, 50000)

        # Determine relevant cost
        if (
            hasattr(profile, "state")
            and profile.state == college.state
            and college.total_cost_in_state
        ):
            total_cost = college.total_cost_in_state
        elif college.total_cost_out_of_state:
            total_cost = college.total_cost_out_of_state
        else:
            return 10.0  # Neutral score if no cost data

        # Use net price if available (more accurate)
        if college.avg_net_price:
            net_cost = college.avg_net_price
        else:
            net_cost = total_cost

        # Score based on affordability (30% of income rule)
        affordable_threshold = estimated_income * 0.3
        if net_cost <= affordable_threshold:
            score = 20
        elif net_cost <= affordable_threshold * 1.5:
            score = 15
        elif net_cost <= affordable_threshold * 2:
            score = 10
        else:
            score = 5

        return score

    def _calculate_location_score(self, college: College, profile) -> float:
        """Calculate location preference score (max 15 points)"""
        score = 0.0

        # In-state preference (10 points)
        if hasattr(profile, "state") and profile.state == college.state:
            score += 10
        elif (
            hasattr(profile, "preferred_college_location")
            and profile.preferred_college_location
        ):
            if (
                college.region
                and profile.preferred_college_location.lower() in college.region.lower()
            ):
                score += 6
            else:
                score += 2
        else:
            score += 5  # Neutral

        # Campus setting preference (5 points)
        if (
            hasattr(profile, "preferred_college_location")
            and profile.preferred_college_location
        ):
            location_pref = profile.preferred_college_location.lower()
            if (
                ("urban" in location_pref and college.campus_setting == "Urban")
                or (
                    "suburban" in location_pref and college.campus_setting == "Suburban"
                )
                or ("rural" in location_pref and college.campus_setting == "Rural")
            ):
                score += 5
            else:
                score += 2
        else:
            score += 3  # Neutral

        return score

    def _calculate_environment_score(self, college: College, profile) -> float:
        """Calculate campus environment fit score (max 15 points)"""
        score = 0.0

        # Size preference (10 points)
        if (
            hasattr(profile, "preferred_college_size")
            and profile.preferred_college_size
        ):
            if (
                college.college_size
                and profile.preferred_college_size.lower() == college.college_size.value
            ):
                score += 10
            else:
                score += 2
        else:
            score += 6  # Neutral

        # Diversity considerations (5 points)
        if hasattr(profile, "ethnicity") and profile.ethnicity:
            if (
                college.is_historically_black
                and "Black or African American" in profile.ethnicity
            ):
                score += 5
            elif college.is_hispanic_serving and any(
                "Hispanic" in eth or "Latino" in eth for eth in profile.ethnicity
            ):
                score += 5
            elif college.percent_white and college.percent_white < 0.7:
                score += 4
            else:
                score += 3
        else:
            score += 3

        return score

    def _calculate_program_score(self, college: College, profile) -> float:
        """Calculate academic program strength score (max 10 points)"""
        score = 0.0

        if not hasattr(profile, "intended_major") or not profile.intended_major:
            return 5.0  # Neutral score

        # Major availability and strength
        if (
            college.available_majors
            and profile.intended_major in college.available_majors
        ):
            score += 5

            # Program strength bonus
            if (
                college.strong_programs
                and profile.intended_major in college.strong_programs
            ):
                score += 3
            elif (
                college.popular_majors
                and profile.intended_major in college.popular_majors
            ):
                score += 2
            else:
                score += 1
        else:
            score += 1  # May have similar programs

        return score

    def _determine_match_category(self, college: College, profile, score: float) -> str:
        """Determine if college is safety, match, or reach"""
        try:
            if not college.acceptance_rate:
                return "match"

            # Consider student competitiveness
            student_competitive = False

            # Check GPA competitiveness
            if college.avg_gpa and hasattr(profile, "gpa") and profile.gpa:
                if profile.gpa >= college.avg_gpa + 0.3:
                    student_competitive = True

            # Check test score competitiveness
            if (
                college.sat_total_75
                and hasattr(profile, "sat_score")
                and profile.sat_score
            ):
                if profile.sat_score >= college.sat_total_75:
                    student_competitive = True
            elif (
                college.act_composite_75
                and hasattr(profile, "act_score")
                and profile.act_score
            ):
                if profile.act_score >= college.act_composite_75:
                    student_competitive = True

            # Categorize
            if college.acceptance_rate >= 0.7 or student_competitive:
                return "safety"
            elif college.acceptance_rate >= 0.3 and score >= 70:
                return "match"
            else:
                return "reach"

        except Exception as e:
            logger.error(f"Error determining match category: {str(e)}")
            return "match"

    def _get_match_reasons(self, college: College, profile) -> List[str]:
        """Get concise match reasons"""
        reasons = []

        try:
            # Academic fit
            if college.avg_gpa and hasattr(profile, "gpa") and profile.gpa:
                gpa_diff = abs(profile.gpa - college.avg_gpa)
                if gpa_diff <= 0.3:
                    reasons.append(
                        f"Good GPA fit ({profile.gpa:.1f} vs {college.avg_gpa:.1f} avg)"
                    )

            # Test scores
            if (
                hasattr(profile, "sat_score")
                and profile.sat_score
                and college.sat_total_25
                and college.sat_total_75
            ):
                if college.sat_total_25 <= profile.sat_score <= college.sat_total_75:
                    reasons.append("SAT score in target range")

            # Location
            if hasattr(profile, "state") and profile.state == college.state:
                reasons.append("In-state tuition savings")

            # Major
            if (
                college.available_majors
                and hasattr(profile, "intended_major")
                and profile.intended_major
                and profile.intended_major in college.available_majors
            ):
                reasons.append(f"Offers {profile.intended_major}")

            return reasons[:3]  # Limit to top 3

        except Exception as e:
            logger.error(f"Error getting match reasons: {str(e)}")
            return []

    def _get_concerns(self, college: College, profile) -> List[str]:
        """Get potential concerns"""
        concerns = []

        try:
            # Competitive admission
            if college.acceptance_rate and college.acceptance_rate < 0.2:
                concerns.append(
                    f"Highly competitive ({college.acceptance_rate:.1%} acceptance)"
                )

            # Academic stretch
            if (
                college.avg_gpa
                and hasattr(profile, "gpa")
                and profile.gpa
                and profile.gpa < college.avg_gpa - 0.4
            ):
                concerns.append("GPA below average")

            # Cost concerns (simplified)
            if (
                college.total_cost_out_of_state
                and college.total_cost_out_of_state > 60000
            ):
                concerns.append("High cost")

            return concerns[:2]  # Limit to top 2

        except Exception as e:
            logger.error(f"Error getting concerns: {str(e)}")
            return []

    # ===========================
    # MATCH MANAGEMENT
    # ===========================

    def get_user_matches(
        self, user_id: int, limit: int = 50, min_score: float = 0.0
    ) -> List[CollegeMatch]:
        """Get college matches for a user"""
        return (
            self.db.query(CollegeMatch)
            .filter(
                CollegeMatch.user_id == user_id,
                CollegeMatch.match_score >= min_score,
            )
            .order_by(desc(CollegeMatch.match_score))
            .limit(limit)
            .all()
        )

    def update_match_status(
        self, user_id: int, college_id: int, status_data: CollegeMatchUpdate
    ) -> Optional[CollegeMatch]:
        """Update user's interaction with a college match"""
        try:
            db_match = (
                self.db.query(CollegeMatch)
                .filter(
                    CollegeMatch.user_id == user_id,
                    CollegeMatch.college_id == college_id,
                )
                .first()
            )

            if not db_match:
                return None

            update_data = status_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_match, field, value)

            # Update timestamps appropriately
            if update_data.get("viewed"):
                db_match.viewed_at = datetime.utcnow()

            if update_data.get("applied"):
                db_match.applied_at = datetime.utcnow()

            db_match.updated_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(db_match)
            return db_match

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating match status: {str(e)}")
            raise

    def get_match_summary(self, user_id: int) -> CollegeMatchSummary:
        """Get summary statistics for user's college matches"""
        try:
            matches = (
                self.db.query(CollegeMatch)
                .filter(CollegeMatch.user_id == user_id)
                .all()
            )

            if not matches:
                return CollegeMatchSummary(
                    user_id=user_id,
                    total_matches=0,
                    safety_schools=0,
                    match_schools=0,
                    reach_schools=0,
                    viewed_count=0,
                    applied_count=0,
                    bookmarked_count=0,
                    interested_count=0,
                    average_match_score=0.0,
                    best_match_score=0.0,
                    matches_this_month=0,
                    upcoming_deadlines=0,
                )

            # Calculate basic stats
            total_matches = len(matches)
            safety_schools = sum(1 for m in matches if m.match_category == "safety")
            match_schools = sum(1 for m in matches if m.match_category == "match")
            reach_schools = sum(1 for m in matches if m.match_category == "reach")

            viewed_count = sum(1 for m in matches if m.viewed)
            applied_count = sum(1 for m in matches if m.applied)
            bookmarked_count = sum(1 for m in matches if m.bookmarked)
            interested_count = sum(1 for m in matches if m.interested is True)

            scores = [m.match_score for m in matches if m.match_score]
            average_match_score = sum(scores) / len(scores) if scores else 0.0
            best_match_score = max(scores) if scores else 0.0

            # Recent activity
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            matches_this_month = sum(
                1 for m in matches if m.match_date and m.match_date >= thirty_days_ago
            )

            # Upcoming deadlines
            sixty_days_later = datetime.utcnow() + timedelta(days=60)
            upcoming_deadlines = sum(
                1
                for m in matches
                if m.application_deadline and m.application_deadline <= sixty_days_later
            )

            # Get financial summary
            college_ids = [m.college_id for m in matches]
            colleges = (
                (self.db.query(College).filter(College.id.in_(college_ids)).all())
                if college_ids
                else []
            )

            # Calculate cost averages
            in_state_costs = [
                c.total_cost_in_state for c in colleges if c.total_cost_in_state
            ]
            out_of_state_costs = [
                c.total_cost_out_of_state for c in colleges if c.total_cost_out_of_state
            ]

            avg_cost_in_state = (
                int(sum(in_state_costs) / len(in_state_costs))
                if in_state_costs
                else None
            )
            avg_cost_out_of_state = (
                int(sum(out_of_state_costs) / len(out_of_state_costs))
                if out_of_state_costs
                else None
            )

            # Find most affordable
            most_affordable_match = None
            if colleges:

                def get_min_cost(college):
                    costs = [
                        c
                        for c in [
                            college.total_cost_in_state,
                            college.total_cost_out_of_state,
                        ]
                        if c
                    ]
                    return min(costs) if costs else float("inf")

                affordable_college = min(colleges, key=get_min_cost)
                if get_min_cost(affordable_college) != float("inf"):
                    most_affordable_match = affordable_college.name

            # Academic summary
            acceptance_rates = [
                c.acceptance_rate for c in colleges if c.acceptance_rate
            ]
            avg_acceptance_rate = (
                sum(acceptance_rates) / len(acceptance_rates)
                if acceptance_rates
                else None
            )

            # Most competitive
            most_competitive_match = None
            if colleges:
                competitive_colleges = [c for c in colleges if c.acceptance_rate]
                if competitive_colleges:
                    competitive_college = min(
                        competitive_colleges, key=lambda c: c.acceptance_rate
                    )
                    most_competitive_match = competitive_college.name

            return CollegeMatchSummary(
                user_id=user_id,
                total_matches=total_matches,
                safety_schools=safety_schools,
                match_schools=match_schools,
                reach_schools=reach_schools,
                viewed_count=viewed_count,
                applied_count=applied_count,
                bookmarked_count=bookmarked_count,
                interested_count=interested_count,
                average_match_score=round(average_match_score, 1),
                best_match_score=best_match_score,
                matches_this_month=matches_this_month,
                upcoming_deadlines=upcoming_deadlines,
                avg_cost_in_state=avg_cost_in_state,
                avg_cost_out_of_state=avg_cost_out_of_state,
                most_affordable_match=most_affordable_match,
                avg_acceptance_rate=(
                    round(avg_acceptance_rate, 3) if avg_acceptance_rate else None
                ),
                most_competitive_match=most_competitive_match,
            )

        except Exception as e:
            logger.error(f"Error generating match summary: {str(e)}")
            raise

    def recalculate_all_matches(self) -> Dict[str, int]:
        """Recalculate matches for all users with completed profiles"""
        try:
            profiles = (
                self.db.query(UserProfile)
                .filter(UserProfile.profile_completed == True)
                .all()
            )

            total_users = len(profiles)
            total_matches = 0

            for profile in profiles:
                try:
                    matches = self.calculate_and_store_matches(
                        profile.user_id, force_recalculate=True
                    )
                    total_matches += matches
                except Exception as e:
                    logger.error(
                        f"Error recalculating matches for user {profile.user_id}: {str(e)}"
                    )

            return {
                "users_processed": total_users,
                "total_matches_created": total_matches,
            }

        except Exception as e:
            logger.error(f"Error in recalculate_all_matches: {str(e)}")
            raise

    # ===========================
    # STATISTICS AND UTILITIES
    # ===========================

    def get_college_statistics(self) -> Dict[str, Any]:
        """Get overall college platform statistics"""
        try:
            total_colleges = self.db.query(College).count()
            active_colleges = (
                self.db.query(College).filter(College.is_active == True).count()
            )
            verified_colleges = (
                self.db.query(College).filter(College.is_verified == True).count()
            )

            # Type breakdown
            type_breakdown = (
                self.db.query(College.college_type, func.count(College.id))
                .filter(College.is_active == True)
                .group_by(College.college_type)
                .all()
            )

            # Size breakdown
            size_breakdown = (
                self.db.query(College.college_size, func.count(College.id))
                .filter(College.is_active == True)
                .group_by(College.college_size)
                .all()
            )

            # State breakdown (top 10)
            state_breakdown = (
                self.db.query(College.state, func.count(College.id))
                .filter(College.is_active == True)
                .group_by(College.state)
                .order_by(desc(func.count(College.id)))
                .limit(10)
                .all()
            )

            # Calculate averages safely
            avg_acceptance_rate = (
                self.db.query(func.avg(College.acceptance_rate))
                .filter(College.acceptance_rate.is_not(None), College.is_active == True)
                .scalar()
            )

            avg_tuition_public = (
                self.db.query(func.avg(College.tuition_in_state))
                .filter(
                    College.college_type == CollegeType.PUBLIC,
                    College.tuition_in_state.is_not(None),
                    College.is_active == True,
                )
                .scalar()
            )

            avg_tuition_private = (
                self.db.query(func.avg(College.tuition_out_of_state))
                .filter(
                    College.college_type.in_(
                        [CollegeType.PRIVATE_NONPROFIT, CollegeType.PRIVATE_FOR_PROFIT]
                    ),
                    College.tuition_out_of_state.is_not(None),
                    College.is_active == True,
                )
                .scalar()
            )

            return {
                "total_colleges": total_colleges,
                "active_colleges": active_colleges,
                "verified_colleges": verified_colleges,
                "colleges_by_type": {str(k): v for k, v in type_breakdown},
                "colleges_by_size": {str(k): v for k, v in size_breakdown},
                "colleges_by_state": dict(state_breakdown),
                "avg_acceptance_rate": (
                    round(avg_acceptance_rate, 3) if avg_acceptance_rate else None
                ),
                "avg_tuition_public": (
                    int(avg_tuition_public) if avg_tuition_public else None
                ),
                "avg_tuition_private": (
                    int(avg_tuition_private) if avg_tuition_private else None
                ),
            }

        except Exception as e:
            logger.error(f"Error generating college statistics: {str(e)}")
            raise

    def get_filter_options(self) -> Dict[str, Any]:
        """Get available filter options for UI"""
        try:
            # Get distinct values from active colleges
            states = (
                self.db.query(College.state)
                .filter(College.is_active == True)
                .distinct()
                .all()
            )

            regions = (
                self.db.query(College.region)
                .filter(College.is_active == True, College.region.is_not(None))
                .distinct()
                .all()
            )

            campus_settings = (
                self.db.query(College.campus_setting)
                .filter(College.is_active == True, College.campus_setting.is_not(None))
                .distinct()
                .all()
            )

            athletic_divisions = (
                self.db.query(College.athletic_division)
                .filter(
                    College.is_active == True, College.athletic_division.is_not(None)
                )
                .distinct()
                .all()
            )

            return {
                "college_types": [e.value for e in CollegeType],
                "college_sizes": [e.value for e in CollegeSize],
                "admission_difficulties": [e.value for e in AdmissionDifficulty],
                "states": sorted([s[0] for s in states if s[0]]),
                "regions": sorted([r[0] for r in regions if r[0]]),
                "campus_settings": sorted([c[0] for c in campus_settings if c[0]]),
                "athletic_divisions": sorted(
                    [a[0] for a in athletic_divisions if a[0]]
                ),
                "sort_options": [
                    "name",
                    "acceptance_rate",
                    "tuition_in_state",
                    "tuition_out_of_state",
                    "total_enrollment",
                    "graduation_rate_6_year",
                    "us_news_ranking",
                ],
            }

        except Exception as e:
            logger.error(f"Error getting filter options: {str(e)}")
            raise

    # ===========================
    # HELPER METHODS
    # ===========================

    def validate_college_data(self, college_data: dict) -> List[str]:
        """Validate college data and return validation errors"""
        errors = []

        # Required fields
        required_fields = ["name", "city", "state", "college_type"]
        for field in required_fields:
            if not college_data.get(field):
                errors.append(f"Missing required field: {field}")

        # Validate ranges
        acceptance_rate = college_data.get("acceptance_rate")
        if acceptance_rate is not None and not (0 <= acceptance_rate <= 1):
            errors.append("Acceptance rate must be between 0 and 1")

        avg_gpa = college_data.get("avg_gpa")
        if avg_gpa is not None and not (0 <= avg_gpa <= 5):
            errors.append("GPA must be between 0 and 5")

        # Validate SAT score ranges
        sat_25 = college_data.get("sat_total_25")
        sat_75 = college_data.get("sat_total_75")
        if sat_25 is not None and sat_75 is not None and sat_25 > sat_75:
            errors.append("SAT 25th percentile cannot be higher than 75th percentile")

        # Validate ACT score ranges
        act_25 = college_data.get("act_composite_25")
        act_75 = college_data.get("act_composite_75")
        if act_25 is not None and act_75 is not None and act_25 > act_75:
            errors.append("ACT 25th percentile cannot be higher than 75th percentile")

        return errors

    def get_popular_majors(self, limit: int = 20) -> List[str]:
        """Get most popular majors across colleges"""
        # This would require complex aggregation in real implementation
        # For now, return common majors
        popular_majors = [
            "Business",
            "Psychology",
            "Computer Science",
            "Biology",
            "Engineering",
            "English",
            "Economics",
            "Political Science",
            "Communications",
            "History",
            "Mathematics",
            "Chemistry",
            "Nursing",
            "Education",
            "Art",
            "Sociology",
            "Philosophy",
            "Criminal Justice",
            "International Studies",
            "Environmental Studies",
        ]
        return popular_majors[:limit]

    def get_affordable_colleges(
        self, max_cost: int, student_state: str = None, limit: int = 50
    ) -> List[College]:
        """Get affordable colleges based on cost threshold"""
        query = self.db.query(College).filter(College.is_active == True)

        if student_state:
            # Prefer in-state options
            query = query.filter(
                or_(
                    and_(
                        College.state == student_state,
                        College.total_cost_in_state <= max_cost,
                    ),
                    College.total_cost_out_of_state <= max_cost,
                )
            )
        else:
            query = query.filter(
                or_(
                    College.total_cost_in_state <= max_cost,
                    College.total_cost_out_of_state <= max_cost,
                )
            )

        return (
            query.order_by(College.total_cost_in_state.nullslast()).limit(limit).all()
        )

    def get_college_comparison(self, college_ids: List[int]) -> Dict[str, Any]:
        """Compare multiple colleges side by side"""
        try:
            colleges = (
                self.db.query(College)
                .filter(College.id.in_(college_ids), College.is_active == True)
                .all()
            )

            if not colleges:
                return {"error": "No colleges found"}

            comparison_data = {
                "colleges": colleges,
                "comparison_metrics": {
                    "acceptance_rates": {
                        c.name: c.acceptance_rate for c in colleges if c.acceptance_rate
                    },
                    "tuition_costs": {
                        c.name: c.tuition_out_of_state or c.tuition_in_state
                        for c in colleges
                        if (c.tuition_out_of_state or c.tuition_in_state)
                    },
                    "enrollments": {
                        c.name: c.total_enrollment
                        for c in colleges
                        if c.total_enrollment
                    },
                    "graduation_rates": {
                        c.name: c.graduation_rate_6_year
                        for c in colleges
                        if c.graduation_rate_6_year
                    },
                    "rankings": {
                        c.name: c.us_news_ranking for c in colleges if c.us_news_ranking
                    },
                },
                "common_majors": list(
                    set().union(*[c.available_majors or [] for c in colleges])
                ),
            }

            return comparison_data

        except Exception as e:
            logger.error(f"Error creating college comparison: {str(e)}")
            raise
