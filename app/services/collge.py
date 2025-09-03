# app/services/college.py - COMPLETE FILE
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc, text
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
    CollegeMatchCreate,
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
            db_college = College(**college_data.model_dump(exclude_unset=True))

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
        return self.db.query(College).filter(College.id == college_id).first()

    def get_colleges_paginated(
        self, page: int = 1, limit: int = 50, active_only: bool = True
    ) -> Tuple[List[College], int]:
        """Get paginated list of colleges"""
        query = self.db.query(College)

        if active_only:
            query = query.filter(College.is_active == True)

        total = query.count()
        colleges = query.offset((page - 1) * limit).limit(limit).all()

        return colleges, total

    def update_college(
        self, college_id: int, college_data: CollegeUpdate
    ) -> Optional[College]:
        """Update existing college"""
        try:
            db_college = self.get_college_by_id(college_id)
            if not db_college:
                return None

            update_data = college_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_college, field, value)

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
            db_college = self.get_college_by_id(college_id)
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
        query = self.db.query(College)

        # Basic filters
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

        # Location filters
        if filters.state:
            query = query.filter(College.state == filters.state)

        if filters.region:
            query = query.filter(College.region == filters.region)

        if filters.campus_setting:
            query = query.filter(College.campus_setting == filters.campus_setting)

        # Institution type filters
        if filters.college_type:
            query = query.filter(College.college_type == filters.college_type)

        if filters.college_size:
            query = query.filter(College.college_size == filters.college_size)

        # Academic filters
        if filters.min_acceptance_rate:
            query = query.filter(College.acceptance_rate >= filters.min_acceptance_rate)

        if filters.max_acceptance_rate:
            query = query.filter(College.acceptance_rate <= filters.max_acceptance_rate)

        if filters.admission_difficulty:
            query = query.filter(
                College.admission_difficulty == filters.admission_difficulty
            )

        # Student profile matching filters
        if filters.student_gpa:
            query = query.filter(
                or_(
                    College.min_gpa_recommended.is_(None),
                    College.min_gpa_recommended <= filters.student_gpa,
                )
            )

        if filters.student_sat_score:
            query = query.filter(
                or_(
                    College.sat_total_25.is_(None),
                    College.sat_total_25
                    <= (filters.student_sat_score + 100),  # Allow some flexibility
                )
            )

        if filters.student_act_score:
            query = query.filter(
                or_(
                    College.act_composite_25.is_(None),
                    College.act_composite_25
                    <= (filters.student_act_score + 3),  # Allow some flexibility
                )
            )

        if filters.student_major:
            query = query.filter(
                or_(
                    College.available_majors.is_(None),
                    College.available_majors.contains([filters.student_major]),
                )
            )

        # Financial filters
        if filters.max_tuition_in_state:
            query = query.filter(
                or_(
                    College.tuition_in_state.is_(None),
                    College.tuition_in_state <= filters.max_tuition_in_state,
                )
            )

        if filters.max_tuition_out_of_state:
            query = query.filter(
                or_(
                    College.tuition_out_of_state.is_(None),
                    College.tuition_out_of_state <= filters.max_tuition_out_of_state,
                )
            )

        if filters.max_total_cost:
            if filters.student_state:
                # Use in-state cost if student is from the same state
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
                # Use out-of-state cost as default
                query = query.filter(
                    or_(
                        College.total_cost_out_of_state.is_(None),
                        College.total_cost_out_of_state <= filters.max_total_cost,
                    )
                )

        # Program filters
        if filters.required_majors:
            for major in filters.required_majors:
                query = query.filter(College.available_majors.contains([major]))

        if filters.strong_programs_only:
            query = query.filter(College.strong_programs.is_not(None))

        # Size filters
        if filters.min_enrollment:
            query = query.filter(
                or_(
                    College.total_enrollment.is_(None),
                    College.total_enrollment >= filters.min_enrollment,
                )
            )

        if filters.max_enrollment:
            query = query.filter(
                or_(
                    College.total_enrollment.is_(None),
                    College.total_enrollment <= filters.max_enrollment,
                )
            )

        # Diversity filters
        if filters.historically_black is not None:
            query = query.filter(
                College.is_historically_black == filters.historically_black
            )

        if filters.hispanic_serving is not None:
            query = query.filter(
                College.is_hispanic_serving == filters.hispanic_serving
            )

        if filters.tribal_college is not None:
            query = query.filter(College.is_tribal_college == filters.tribal_college)

        if filters.women_only is not None:
            query = query.filter(College.is_women_only == filters.women_only)

        if filters.men_only is not None:
            query = query.filter(College.is_men_only == filters.men_only)

        # Athletics
        if filters.athletic_division:
            query = query.filter(College.athletic_division == filters.athletic_division)

        # Outcomes filters
        if filters.min_graduation_rate:
            query = query.filter(
                or_(
                    College.graduation_rate_6_year.is_(None),
                    College.graduation_rate_6_year >= filters.min_graduation_rate,
                )
            )

        if filters.min_retention_rate:
            query = query.filter(
                or_(
                    College.retention_rate.is_(None),
                    College.retention_rate >= filters.min_retention_rate,
                )
            )

        # Count total before pagination
        total = query.count()

        # Sorting
        if filters.sort_by == "match_score":
            # Special handling for match score sorting would require joining with matches
            # For now, default to name sorting
            sort_column = College.name
        else:
            sort_column = getattr(College, filters.sort_by, College.name)

        if filters.sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        # Pagination
        colleges = (
            query.offset((filters.page - 1) * filters.limit).limit(filters.limit).all()
        )

        return colleges, total

    # ===========================
    # MATCHING ALGORITHMS
    # ===========================

    def find_matches_for_user(
        self, user_id: int, min_score: float = 0.0, limit: int = 100
    ) -> List[College]:
        """Find college matches for a specific user"""
        profile = (
            self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        )
        if not profile:
            logger.warning(f"No profile found for user {user_id}")
            return []

        # Get active colleges
        colleges = self.db.query(College).filter(College.is_active == True).all()

        matches = []
        for college in colleges:
            if college.matches_profile_basic(profile):
                score = college.calculate_match_score(profile)
                if score >= min_score:
                    matches.append((college, score))

        # Sort by score (highest first)
        matches.sort(key=lambda x: x[1], reverse=True)

        return [match[0] for match in matches[:limit]]

    def calculate_and_store_matches(
        self, user_id: int, force_recalculate: bool = False
    ) -> int:
        """Calculate and store matches for a user in the database"""
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

            # Get colleges that don't already have matches for this user
            existing_match_ids = (
                self.db.query(CollegeMatch.college_id)
                .filter(CollegeMatch.user_id == user_id)
                .subquery()
            )

            colleges = (
                self.db.query(College)
                .filter(
                    College.is_active == True,
                    ~College.id.in_(existing_match_ids),
                )
                .all()
            )

            matches_created = 0
            for college in colleges:
                if college.matches_profile_basic(profile):
                    score = college.calculate_match_score(profile)

                    # Only store matches above a threshold
                    if score >= 20.0:  # Lower threshold than scholarships
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

    def recalculate_all_matches(self) -> Dict[str, int]:
        """Recalculate matches for all users with completed profiles"""
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

        return {"users_processed": total_users, "total_matches_created": total_matches}

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

            # Update timestamps
            if "viewed" in update_data and update_data["viewed"]:
                db_match.viewed_at = func.now()

            if "applied" in update_data and update_data["applied"]:
                db_match.applied_at = func.now()

            db_match.updated_at = func.now()

            self.db.commit()
            self.db.refresh(db_match)
            return db_match

        except Exception as e:
            self.db.rollback()
            logger.error(
                f"Error updating match status for user {user_id}, college {college_id}: {str(e)}"
            )
            raise

    def get_match_summary(self, user_id: int) -> CollegeMatchSummary:
        """Get summary statistics for a user's college matches"""
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

            total_matches = len(matches)
            safety_schools = len([m for m in matches if m.match_category == "safety"])
            match_schools = len([m for m in matches if m.match_category == "match"])
            reach_schools = len([m for m in matches if m.match_category == "reach"])

            viewed_count = len([m for m in matches if m.viewed])
            applied_count = len([m for m in matches if m.applied])
            bookmarked_count = len([m for m in matches if m.bookmarked])
            interested_count = len([m for m in matches if m.interested == True])

            scores = [m.match_score for m in matches]
            average_match_score = sum(scores) / len(scores) if scores else 0.0
            best_match_score = max(scores) if scores else 0.0

            # Matches created in the last 30 days
            thirty_days_ago = datetime.now() - timedelta(days=30)
            matches_this_month = len(
                [m for m in matches if m.match_date >= thirty_days_ago]
            )

            # Upcoming deadlines (next 60 days for college applications)
            sixty_days_later = datetime.now() + timedelta(days=60)
            upcoming_deadlines = len(
                [
                    m
                    for m in matches
                    if m.application_deadline
                    and m.application_deadline <= sixty_days_later
                ]
            )

            # Financial summary
            college_ids = [m.college_id for m in matches]
            colleges = self.db.query(College).filter(College.id.in_(college_ids)).all()

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

            # Find most affordable match
            most_affordable_match = None
            if colleges:
                affordable_college = min(
                    colleges,
                    key=lambda c: c.total_cost_in_state
                    or c.total_cost_out_of_state
                    or float("inf"),
                )
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

            # Most competitive match
            most_competitive_match = None
            if colleges:
                competitive_college = min(
                    colleges, key=lambda c: c.acceptance_rate or 1.0
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
            logger.error(f"Error generating match summary for user {user_id}: {str(e)}")
            raise

    # ===========================
    # UTILITY AND HELPER METHODS
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
                .group_by(College.college_type)
                .all()
            )

            # Size breakdown
            size_breakdown = (
                self.db.query(College.college_size, func.count(College.id))
                .group_by(College.college_size)
                .all()
            )

            # State breakdown (top 10)
            state_breakdown = (
                self.db.query(College.state, func.count(College.id))
                .group_by(College.state)
                .order_by(desc(func.count(College.id)))
                .limit(10)
                .all()
            )

            # Average acceptance rate
            avg_acceptance_rate = (
                self.db.query(func.avg(College.acceptance_rate))
                .filter(College.acceptance_rate.is_not(None))
                .scalar()
            )

            # Average tuition
            avg_tuition_public = (
                self.db.query(func.avg(College.tuition_in_state))
                .filter(
                    College.college_type == CollegeType.PUBLIC,
                    College.tuition_in_state.is_not(None),
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
                )
                .scalar()
            )

            return {
                "total_colleges": total_colleges,
                "active_colleges": active_colleges,
                "verified_colleges": verified_colleges,
                "colleges_by_type": dict(type_breakdown),
                "colleges_by_size": dict(size_breakdown),
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

    def _determine_match_category(self, college: College, profile, score: float) -> str:
        """Determine if college is safety, match, or reach for student"""
        try:
            # Base categorization on acceptance rate and student stats
            if not college.acceptance_rate:
                return "match"  # Default if no acceptance rate data

            # Consider student's academic profile relative to college
            student_competitive = False

            # GPA comparison
            if college.avg_gpa and profile.gpa:
                if profile.gpa >= college.avg_gpa + 0.3:
                    student_competitive = True

            # Test score comparison
            if college.sat_total_75 and profile.sat_score:
                if profile.sat_score >= college.sat_total_75:
                    student_competitive = True
            elif college.act_composite_75 and profile.act_score:
                if profile.act_score >= college.act_composite_75:
                    student_competitive = True

            # Categorize based on acceptance rate and competitiveness
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
        """Get reasons why a college matches a profile"""
        reasons = []

        try:
            # Academic fit
            if college.avg_gpa and profile.gpa:
                gpa_diff = abs(profile.gpa - college.avg_gpa)
                if gpa_diff <= 0.2:
                    reasons.append(
                        f"GPA is excellent fit ({profile.gpa} vs {college.avg_gpa} average)"
                    )
                elif gpa_diff <= 0.5:
                    reasons.append(
                        f"GPA is good fit ({profile.gpa} vs {college.avg_gpa} average)"
                    )

            # Test scores
            if college.sat_total_25 and college.sat_total_75 and profile.sat_score:
                if college.sat_total_25 <= profile.sat_score <= college.sat_total_75:
                    reasons.append(
                        f"SAT score in middle 50% range ({profile.sat_score})"
                    )
                elif profile.sat_score > college.sat_total_75:
                    reasons.append(f"SAT score above average ({profile.sat_score})")

            if (
                college.act_composite_25
                and college.act_composite_75
                and profile.act_score
            ):
                if (
                    college.act_composite_25
                    <= profile.act_score
                    <= college.act_composite_75
                ):
                    reasons.append(
                        f"ACT score in middle 50% range ({profile.act_score})"
                    )
                elif profile.act_score > college.act_composite_75:
                    reasons.append(f"ACT score above average ({profile.act_score})")

            # Major availability
            if college.available_majors and profile.intended_major:
                if profile.intended_major in college.available_majors:
                    reasons.append(f"Offers intended major: {profile.intended_major}")

                    # Strong program bonus
                    if (
                        college.strong_programs
                        and profile.intended_major in college.strong_programs
                    ):
                        reasons.append(
                            f"Nationally recognized program in {profile.intended_major}"
                        )

            # Location match
            if profile.state == college.state:
                reasons.append("In-state tuition savings")

            # Size preference
            if profile.preferred_college_size and college.college_size:
                if profile.preferred_college_size.lower() == college.college_size.value:
                    reasons.append(
                        f"Preferred college size: {college.college_size.value}"
                    )

            # Financial fit
            if profile.household_income_range and college.avg_net_price:
                income_mapping = {
                    "Under $25,000": 25000,
                    "$25,000 - $50,000": 50000,
                    "$50,000 - $75,000": 75000,
                    "$75,000 - $100,000": 100000,
                }

                estimated_income = income_mapping.get(
                    profile.household_income_range, 100000
                )
                if college.avg_net_price <= estimated_income * 0.3:
                    reasons.append("Financially affordable based on average net price")

            # Diversity considerations
            if profile.ethnicity:
                if (
                    college.is_historically_black
                    and "Black or African American" in profile.ethnicity
                ):
                    reasons.append("Historically Black College/University")
                elif college.is_hispanic_serving and any(
                    "Hispanic" in eth for eth in profile.ethnicity
                ):
                    reasons.append("Hispanic Serving Institution")

            return reasons

        except Exception as e:
            logger.error(f"Error getting match reasons: {str(e)}")
            return []

    def _get_concerns(self, college: College, profile) -> List[str]:
        """Get potential concerns about a college match"""
        concerns = []

        try:
            # Academic concerns
            if college.avg_gpa and profile.gpa:
                if profile.gpa < college.avg_gpa - 0.5:
                    concerns.append(
                        f"GPA below average (your {profile.gpa} vs {college.avg_gpa} average)"
                    )

            # Test score concerns
            if college.sat_total_25 and profile.sat_score:
                if profile.sat_score < college.sat_total_25 - 50:
                    concerns.append(
                        f"SAT score below typical range (your {profile.sat_score} vs {college.sat_total_25}-{college.sat_total_75 or 'unknown'} range)"
                    )

            if college.act_composite_25 and profile.act_score:
                if profile.act_score < college.act_composite_25 - 2:
                    concerns.append(
                        f"ACT score below typical range (your {profile.act_score} vs {college.act_composite_25}-{college.act_composite_75 or 'unknown'} range)"
                    )

            # Acceptance rate concerns
            if college.acceptance_rate and college.acceptance_rate < 0.2:
                concerns.append(
                    f"Highly competitive admission ({college.acceptance_rate:.1%} acceptance rate)"
                )

            # Financial concerns
            cost = None
            if profile.state == college.state and college.total_cost_in_state:
                cost = college.total_cost_in_state
                cost_type = "in-state"
            elif college.total_cost_out_of_state:
                cost = college.total_cost_out_of_state
                cost_type = "out-of-state"

            if cost and profile.household_income_range:
                income_mapping = {
                    "Under $25,000": 25000,
                    "$25,000 - $50,000": 50000,
                    "$50,000 - $75,000": 75000,
                    "$75,000 - $100,000": 100000,
                }

                estimated_income = income_mapping.get(
                    profile.household_income_range, 100000
                )
                if cost > estimated_income * 0.4:
                    concerns.append(
                        f"High cost relative to income (${cost:,} {cost_type} total cost)"
                    )

            # Major concerns
            if college.available_majors and profile.intended_major:
                if profile.intended_major not in college.available_majors:
                    concerns.append(
                        f"Intended major ({profile.intended_major}) may not be available"
                    )

            # Application requirements
            if (
                college.essays_required
                and not hasattr(profile, "has_personal_statement")
                or not profile.has_personal_statement
            ):
                concerns.append("Essays required for application")

            if (
                college.letters_of_recommendation
                and college.letters_of_recommendation > 0
            ):
                concerns.append(
                    f"Requires {college.letters_of_recommendation} letters of recommendation"
                )

            return concerns

        except Exception as e:
            logger.error(f"Error getting concerns: {str(e)}")
            return []

    def get_colleges_by_state(self, state: str) -> List[College]:
        """Get all colleges in a specific state"""
        return (
            self.db.query(College)
            .filter(College.state == state, College.is_active == True)
            .order_by(College.name)
            .all()
        )

    def search_colleges_by_name(
        self, name_query: str, limit: int = 20
    ) -> List[College]:
        """Search colleges by name (for autocomplete/suggestions)"""
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

    def get_similar_colleges(self, college_id: int, limit: int = 10) -> List[College]:
        """Get colleges similar to a given college"""
        base_college = self.get_college_by_id(college_id)
        if not base_college:
            return []

        # Find colleges with similar characteristics
        query = self.db.query(College).filter(
            College.id != college_id,
            College.is_active == True,
        )

        # Similar type and size
        if base_college.college_type:
            query = query.filter(College.college_type == base_college.college_type)

        if base_college.college_size:
            query = query.filter(College.college_size == base_college.college_size)

        # Similar academic level (acceptance rate within 20%)
        if base_college.acceptance_rate:
            query = query.filter(
                College.acceptance_rate.between(
                    max(0, base_college.acceptance_rate - 0.2),
                    min(1, base_college.acceptance_rate + 0.2),
                )
            )

        # Same region or nearby states
        if base_college.region:
            query = query.filter(College.region == base_college.region)

        return query.limit(limit).all()

    def get_colleges_by_criteria(self, **criteria) -> List[College]:
        """Get colleges matching specific criteria (helper method)"""
        query = self.db.query(College).filter(College.is_active == True)

        for key, value in criteria.items():
            if hasattr(College, key) and value is not None:
                query = query.filter(getattr(College, key) == value)

        return query.all()

    def get_popular_majors(self, limit: int = 20) -> List[str]:
        """Get most popular majors across all colleges"""
        try:
            # This would require more complex aggregation in a real implementation
            # For now, return a static list of popular majors
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
        except Exception as e:
            logger.error(f"Error getting popular majors: {str(e)}")
            return []

    def get_college_recommendations_for_major(
        self, major: str, limit: int = 20
    ) -> List[College]:
        """Get colleges with strong programs in a specific major"""
        return (
            self.db.query(College)
            .filter(
                College.is_active == True, College.strong_programs.contains([major])
            )
            .order_by(desc(College.us_news_ranking))
            .limit(limit)
            .all()
        )

    def get_affordable_colleges(
        self, max_cost: int, student_state: str = None, limit: int = 50
    ) -> List[College]:
        """Get affordable colleges based on cost threshold"""
        query = self.db.query(College).filter(College.is_active == True)

        if student_state:
            # Prefer in-state options first
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

    def validate_college_data(self, college_data: dict) -> List[str]:
        """Validate college data and return list of validation errors"""
        errors = []

        # Required fields
        required_fields = ["name", "city", "state", "college_type"]
        for field in required_fields:
            if not college_data.get(field):
                errors.append(f"Missing required field: {field}")

        # Validate ranges
        if college_data.get("acceptance_rate"):
            if not 0 <= college_data["acceptance_rate"] <= 1:
                errors.append("Acceptance rate must be between 0 and 1")

        if college_data.get("gpa"):
            if not 0 <= college_data["gpa"] <= 5:
                errors.append("GPA must be between 0 and 5")

        # Validate SAT scores
        sat_total_25 = college_data.get("sat_total_25")
        sat_total_75 = college_data.get("sat_total_75")

        if sat_total_25 and sat_total_75:
            if sat_total_25 > sat_total_75:
                errors.append(
                    "SAT 25th percentile cannot be higher than 75th percentile"
                )

        # Validate ACT scores
        act_25 = college_data.get("act_composite_25")
        act_75 = college_data.get("act_composite_75")

        if act_25 and act_75:
            if act_25 > act_75:
                errors.append(
                    "ACT 25th percentile cannot be higher than 75th percentile"
                )

        return errors

    def update_college_rankings(
        self, rankings_data: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Batch update college rankings from external data source"""
        updated_count = 0
        error_count = 0

        try:
            for ranking_data in rankings_data:
                college_name = ranking_data.get("name")
                us_news_rank = ranking_data.get("us_news_ranking")
                forbes_rank = ranking_data.get("forbes_ranking")

                if not college_name:
                    error_count += 1
                    continue

                college = (
                    self.db.query(College)
                    .filter(College.name.ilike(f"%{college_name}%"))
                    .first()
                )

                if college:
                    if us_news_rank:
                        college.us_news_ranking = us_news_rank
                    if forbes_rank:
                        college.forbes_ranking = forbes_rank

                    college.updated_at = func.now()
                    updated_count += 1
                else:
                    error_count += 1

            self.db.commit()
            logger.info(f"Updated rankings for {updated_count} colleges")

            return {"updated_count": updated_count, "error_count": error_count}

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating college rankings: {str(e)}")
            raise

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
                "colleges": [
                    CollegeResponse.model_validate(college) for college in colleges
                ],
                "comparison_metrics": {
                    "acceptance_rates": {
                        c.name: c.acceptance_rate for c in colleges if c.acceptance_rate
                    },
                    "tuition_costs": {
                        c.name: c.tuition_out_of_state or c.tuition_in_state
                        for c in colleges
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
