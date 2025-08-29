# app/services/scholarship.py
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc, text
from sqlalchemy.sql import text
from datetime import datetime, timedelta

from app.models.scholarship import (
    Scholarship,
    ScholarshipMatch,
    ScholarshipStatus,
    ScholarshipType,
)
from app.models.profile import UserProfile
from app.models.user import User
from app.schemas.scholarship import (
    ScholarshipCreate,
    ScholarshipUpdate,
    ScholarshipSearchFilter,
    ScholarshipMatchCreate,
    ScholarshipMatchUpdate,
    ScholarshipMatchSummary,
    BulkMatchingResponse,
)
import logging

logger = logging.getLogger(__name__)


class ScholarshipService:
    """Service class for handling scholarship operations and matching"""

    def __init__(self, db: Session):
        self.db = db

    # ===========================
    # BASIC CRUD OPERATIONS
    # ===========================

    def create_scholarship(
        self,
        scholarship_data: ScholarshipCreate,
        created_by_user_id: Optional[int] = None,
    ) -> Scholarship:
        """Create a new scholarship"""
        try:
            db_scholarship = Scholarship(
                **scholarship_data.model_dump(exclude_unset=True),
                created_by=created_by_user_id,
            )

            self.db.add(db_scholarship)
            self.db.commit()
            self.db.refresh(db_scholarship)

            logger.info(
                f"Created scholarship: {db_scholarship.id} - {db_scholarship.title}"
            )
            return db_scholarship

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating scholarship: {str(e)}")
            raise Exception(f"Failed to create scholarship: {str(e)}")

    def get_scholarship_by_id(self, scholarship_id: int) -> Optional[Scholarship]:
        """Get scholarship by ID"""
        return (
            self.db.query(Scholarship).filter(Scholarship.id == scholarship_id).first()
        )

    def get_scholarships_paginated(
        self, page: int = 1, limit: int = 50, active_only: bool = True
    ) -> Tuple[List[Scholarship], int]:
        """Get paginated list of scholarships"""
        try:
            query = self.db.query(Scholarship)

            if active_only:
                query = query.filter(Scholarship.status == ScholarshipStatus.ACTIVE)

            # Count total results
            total = query.count()

            # Apply pagination
            offset = (page - 1) * limit
            scholarships = query.offset(offset).limit(limit).all()

            return scholarships, total

        except Exception as e:
            logger.error(f"Error getting paginated scholarships: {str(e)}")
            raise Exception(f"Failed to get scholarships: {str(e)}")

    def update_scholarship(
        self, scholarship_id: int, scholarship_data: ScholarshipUpdate
    ) -> Optional[Scholarship]:
        """Update existing scholarship"""
        try:
            db_scholarship = self.get_scholarship_by_id(scholarship_id)
            if not db_scholarship:
                return None

            update_data = scholarship_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_scholarship, field, value)

            db_scholarship.updated_at = func.now()

            self.db.commit()
            self.db.refresh(db_scholarship)

            logger.info(f"Updated scholarship: {scholarship_id}")
            return db_scholarship

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating scholarship {scholarship_id}: {str(e)}")
            raise Exception(f"Failed to update scholarship: {str(e)}")

    def delete_scholarship(self, scholarship_id: int) -> bool:
        """Delete scholarship"""
        try:
            db_scholarship = self.get_scholarship_by_id(scholarship_id)
            if not db_scholarship:
                return False

            self.db.delete(db_scholarship)
            self.db.commit()

            logger.info(f"Deleted scholarship: {scholarship_id}")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting scholarship {scholarship_id}: {str(e)}")
            raise Exception(f"Failed to delete scholarship: {str(e)}")

    # ===========================
    # SEARCH AND FILTERING
    # ===========================

    def search_scholarships(
        self, filters: ScholarshipSearchFilter
    ) -> Tuple[List[Scholarship], int]:
        """Search scholarships with comprehensive filters"""
        try:
            query = self.db.query(Scholarship)

            # Basic status filters
            if filters.active_only:
                query = query.filter(Scholarship.status == ScholarshipStatus.ACTIVE)

            if filters.verified_only:
                query = query.filter(Scholarship.verified == True)

            if filters.featured_only:
                query = query.filter(Scholarship.featured == True)

            # Scholarship type filter
            if filters.scholarship_type:
                query = query.filter(
                    Scholarship.scholarship_type == filters.scholarship_type
                )

            # Text search
            if filters.search_query:
                search_term = f"%{filters.search_query}%"
                query = query.filter(
                    or_(
                        Scholarship.title.ilike(search_term),
                        Scholarship.description.ilike(search_term),
                        Scholarship.organization.ilike(search_term),
                    )
                )

            if filters.organization:
                org_term = f"%{filters.organization}%"
                query = query.filter(Scholarship.organization.ilike(org_term))

            # Financial filters
            if filters.min_amount:
                query = query.filter(
                    or_(
                        Scholarship.amount_exact >= filters.min_amount,
                        Scholarship.amount_min >= filters.min_amount,
                        Scholarship.amount_max >= filters.min_amount,
                    )
                )

            if filters.max_amount:
                query = query.filter(
                    or_(
                        Scholarship.amount_exact <= filters.max_amount,
                        Scholarship.amount_min <= filters.max_amount,
                        Scholarship.amount_max <= filters.max_amount,
                    )
                )

            if filters.renewable_only is not None:
                query = query.filter(Scholarship.is_renewable == filters.renewable_only)

            # Academic filters for student matching
            if filters.student_gpa:
                query = query.filter(
                    or_(
                        Scholarship.min_gpa.is_(None),
                        Scholarship.min_gpa <= filters.student_gpa,
                    )
                )

            if filters.student_sat_score:
                query = query.filter(
                    or_(
                        Scholarship.min_sat_score.is_(None),
                        Scholarship.min_sat_score <= filters.student_sat_score,
                    )
                )

            if filters.student_act_score:
                query = query.filter(
                    or_(
                        Scholarship.min_act_score.is_(None),
                        Scholarship.min_act_score <= filters.student_act_score,
                    )
                )

            if filters.student_major:
                query = query.filter(
                    or_(
                        Scholarship.required_majors.is_(None),
                        Scholarship.required_majors.contains([filters.student_major]),
                    )
                )

            # Geographic filters
            if filters.student_state:
                query = query.filter(
                    or_(
                        Scholarship.eligible_states.is_(None),
                        Scholarship.eligible_states.contains([filters.student_state]),
                    )
                )

            if filters.student_city:
                query = query.filter(
                    or_(
                        Scholarship.eligible_cities.is_(None),
                        Scholarship.eligible_cities.contains([filters.student_city]),
                    )
                )

            # Demographic filters
            if filters.is_first_generation is not None:
                query = query.filter(
                    or_(
                        Scholarship.first_generation_college_required.is_(None),
                        Scholarship.first_generation_college_required
                        == filters.is_first_generation,
                    )
                )

            # Application requirement filters
            if filters.requires_essay is not None:
                query = query.filter(
                    Scholarship.essay_required == filters.requires_essay
                )

            if filters.requires_leadership is not None:
                query = query.filter(
                    Scholarship.leadership_required == filters.requires_leadership
                )

            # Deadline filters
            if filters.deadline_after:
                query = query.filter(
                    or_(
                        Scholarship.deadline.is_(None),
                        Scholarship.deadline >= filters.deadline_after,
                    )
                )

            if filters.deadline_before:
                query = query.filter(
                    or_(
                        Scholarship.deadline.is_(None),
                        Scholarship.deadline <= filters.deadline_before,
                    )
                )

            if filters.rolling_deadline_only is not None:
                query = query.filter(
                    Scholarship.is_rolling_deadline == filters.rolling_deadline_only
                )

            # Difficulty filter
            if filters.max_difficulty:
                difficulty_order = {"easy": 1, "moderate": 2, "hard": 3, "very_hard": 4}
                max_level = difficulty_order.get(filters.max_difficulty, 4)

                difficulty_conditions = []
                for level, order in difficulty_order.items():
                    if order <= max_level:
                        difficulty_conditions.append(
                            Scholarship.difficulty_level == level
                        )

                if difficulty_conditions:
                    query = query.filter(or_(*difficulty_conditions))

            # Count total before pagination
            total = query.count()

            # Sorting
            sort_column = getattr(Scholarship, filters.sort_by, Scholarship.created_at)
            if filters.sort_order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))

            # Pagination
            offset = (filters.page - 1) * filters.limit
            scholarships = query.offset(offset).limit(filters.limit).all()

            return scholarships, total

        except Exception as e:
            logger.error(f"Error searching scholarships: {str(e)}")
            raise Exception(f"Failed to search scholarships: {str(e)}")

    # ===========================
    # MATCHING ALGORITHMS
    # ===========================

    def find_matches_for_user(
        self, user_id: int, min_score: float = 0.0, limit: int = 100
    ) -> List[Tuple[Scholarship, float]]:
        """Find scholarship matches for a specific user"""
        try:
            profile = (
                self.db.query(UserProfile)
                .filter(UserProfile.user_id == user_id)
                .first()
            )
            if not profile:
                logger.warning(f"No profile found for user {user_id}")
                return []

            # Get active scholarships with upcoming or no deadlines
            current_time = datetime.utcnow()
            scholarships = (
                self.db.query(Scholarship)
                .filter(
                    Scholarship.status == ScholarshipStatus.ACTIVE,
                    or_(
                        Scholarship.deadline.is_(None),
                        Scholarship.deadline > current_time,
                    ),
                )
                .all()
            )

            matches = []
            for scholarship in scholarships:
                if scholarship.matches_profile_basic(profile):
                    score = scholarship.calculate_match_score(profile)
                    if score >= min_score:
                        matches.append((scholarship, score))

            # Sort by score (highest first)
            matches.sort(key=lambda x: x[1], reverse=True)

            return matches[:limit]

        except Exception as e:
            logger.error(f"Error finding matches for user {user_id}: {str(e)}")
            raise Exception(f"Failed to find matches: {str(e)}")

    def calculate_and_store_matches(
        self, user_id: int, force_recalculate: bool = False, min_score: float = 30.0
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
                deleted_count = (
                    self.db.query(ScholarshipMatch)
                    .filter(ScholarshipMatch.user_id == user_id)
                    .delete()
                )
                logger.info(
                    f"Deleted {deleted_count} existing matches for user {user_id}"
                )

            # Get scholarships that don't already have matches for this user
            existing_match_subquery = (
                self.db.query(ScholarshipMatch.scholarship_id)
                .filter(ScholarshipMatch.user_id == user_id)
                .subquery()
            )

            current_time = datetime.utcnow()
            scholarships = (
                self.db.query(Scholarship)
                .filter(
                    Scholarship.status == ScholarshipStatus.ACTIVE,
                    or_(
                        Scholarship.deadline.is_(None),
                        Scholarship.deadline > current_time,
                    ),
                    ~Scholarship.id.in_(existing_match_subquery),
                )
                .all()
            )

            matches_created = 0
            for scholarship in scholarships:
                try:
                    if scholarship.matches_profile_basic(profile):
                        score = scholarship.calculate_match_score(profile)

                        # Only store matches above threshold
                        if score >= min_score:
                            match_reasons = self._get_match_reasons(
                                scholarship, profile
                            )
                            mismatch_reasons = self._get_mismatch_reasons(
                                scholarship, profile
                            )

                            db_match = ScholarshipMatch(
                                user_id=user_id,
                                scholarship_id=scholarship.id,
                                match_score=score,
                                match_reasons=match_reasons,
                                mismatch_reasons=mismatch_reasons,
                            )

                            self.db.add(db_match)
                            matches_created += 1

                except Exception as match_error:
                    logger.error(
                        f"Error calculating match for scholarship {scholarship.id} and user {user_id}: {str(match_error)}"
                    )
                    continue

            self.db.commit()
            logger.info(f"Created {matches_created} matches for user {user_id}")
            return matches_created

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error calculating matches for user {user_id}: {str(e)}")
            raise Exception(f"Failed to calculate matches: {str(e)}")

    def recalculate_all_matches(self) -> BulkMatchingResponse:
        """Recalculate matches for all users with completed profiles"""
        start_time = datetime.utcnow()

        try:
            profiles = (
                self.db.query(UserProfile)
                .filter(UserProfile.profile_completed == True)
                .all()
            )

            total_users = len(profiles)
            total_matches = 0
            errors = []

            logger.info(f"Starting bulk recalculation for {total_users} users")

            for profile in profiles:
                try:
                    matches = self.calculate_and_store_matches(
                        profile.user_id, force_recalculate=True
                    )
                    total_matches += matches
                except Exception as e:
                    error_msg = f"Failed to recalculate matches for user {profile.user_id}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)

            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds()

            return BulkMatchingResponse(
                users_processed=total_users,
                scholarships_processed=0,  # We process all scholarships for each user
                matches_created=total_matches,
                matches_updated=0,
                processing_time_seconds=processing_time,
                errors=errors,
            )

        except Exception as e:
            logger.error(f"Error in bulk recalculation: {str(e)}")
            raise Exception(f"Bulk recalculation failed: {str(e)}")

    # ===========================
    # MATCH MANAGEMENT
    # ===========================

    def get_user_matches(
        self, user_id: int, page: int = 1, limit: int = 50, min_score: float = 0.0
    ) -> Tuple[List[ScholarshipMatch], int]:
        """Get scholarship matches for a user with pagination"""
        try:
            query = (
                self.db.query(ScholarshipMatch)
                .filter(
                    ScholarshipMatch.user_id == user_id,
                    ScholarshipMatch.match_score >= min_score,
                )
                .order_by(desc(ScholarshipMatch.match_score))
            )

            total = query.count()
            offset = (page - 1) * limit
            matches = query.offset(offset).limit(limit).all()

            return matches, total

        except Exception as e:
            logger.error(f"Error getting matches for user {user_id}: {str(e)}")
            raise Exception(f"Failed to get user matches: {str(e)}")

    def update_match_status(
        self, user_id: int, scholarship_id: int, status_data: ScholarshipMatchUpdate
    ) -> Optional[ScholarshipMatch]:
        """Update user's interaction with a scholarship match"""
        try:
            db_match = (
                self.db.query(ScholarshipMatch)
                .filter(
                    ScholarshipMatch.user_id == user_id,
                    ScholarshipMatch.scholarship_id == scholarship_id,
                )
                .first()
            )

            if not db_match:
                return None

            update_data = status_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_match, field, value)

            # Update timestamps
            current_time = datetime.utcnow()
            if "viewed" in update_data and update_data["viewed"]:
                db_match.viewed_at = current_time

            if "applied" in update_data and update_data["applied"]:
                db_match.applied_at = current_time

            self.db.commit()
            self.db.refresh(db_match)

            logger.info(
                f"Updated match status for user {user_id}, scholarship {scholarship_id}"
            )
            return db_match

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating match status: {str(e)}")
            raise Exception(f"Failed to update match status: {str(e)}")

    def get_match_summary(self, user_id: int) -> ScholarshipMatchSummary:
        """Get summary statistics for a user's matches"""
        try:
            matches = (
                self.db.query(ScholarshipMatch)
                .filter(ScholarshipMatch.user_id == user_id)
                .all()
            )

            if not matches:
                return ScholarshipMatchSummary(
                    user_id=user_id,
                    total_matches=0,
                    high_matches=0,
                    medium_matches=0,
                    low_matches=0,
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
            high_matches = len([m for m in matches if m.match_score >= 80])
            medium_matches = len([m for m in matches if 60 <= m.match_score < 80])
            low_matches = len([m for m in matches if m.match_score < 60])

            viewed_count = len([m for m in matches if m.viewed])
            applied_count = len([m for m in matches if m.applied])
            bookmarked_count = len([m for m in matches if m.bookmarked])
            interested_count = len([m for m in matches if m.interested == True])

            scores = [m.match_score for m in matches]
            average_match_score = sum(scores) / len(scores) if scores else 0.0
            best_match_score = max(scores) if scores else 0.0

            # Matches created in the last 30 days
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            matches_this_month = len(
                [m for m in matches if m.match_date >= thirty_days_ago]
            )

            # Upcoming deadlines (next 30 days)
            thirty_days_later = datetime.utcnow() + timedelta(days=30)
            scholarship_ids = [m.scholarship_id for m in matches]
            upcoming_deadlines = (
                self.db.query(Scholarship)
                .filter(
                    Scholarship.id.in_(scholarship_ids),
                    Scholarship.deadline.between(datetime.utcnow(), thirty_days_later),
                )
                .count()
            )

            return ScholarshipMatchSummary(
                user_id=user_id,
                total_matches=total_matches,
                high_matches=high_matches,
                medium_matches=medium_matches,
                low_matches=low_matches,
                viewed_count=viewed_count,
                applied_count=applied_count,
                bookmarked_count=bookmarked_count,
                interested_count=interested_count,
                average_match_score=round(average_match_score, 1),
                best_match_score=round(best_match_score, 1),
                matches_this_month=matches_this_month,
                upcoming_deadlines=upcoming_deadlines,
            )

        except Exception as e:
            logger.error(f"Error getting match summary for user {user_id}: {str(e)}")
            raise Exception(f"Failed to get match summary: {str(e)}")

    # ===========================
    # UTILITY AND HELPER METHODS
    # ===========================

    def get_scholarship_statistics(self) -> Dict[str, Any]:
        """Get overall scholarship platform statistics"""
        try:
            total_scholarships = self.db.query(Scholarship).count()
            active_scholarships = (
                self.db.query(Scholarship)
                .filter(Scholarship.status == ScholarshipStatus.ACTIVE)
                .count()
            )
            verified_scholarships = (
                self.db.query(Scholarship).filter(Scholarship.verified == True).count()
            )

            # Total scholarship money available (approximate)
            amount_sum = (
                self.db.query(
                    func.coalesce(func.sum(Scholarship.amount_exact), 0)
                    + func.coalesce(func.sum(Scholarship.amount_max), 0)
                )
                .filter(Scholarship.status == ScholarshipStatus.ACTIVE)
                .scalar()
                or 0
            )

            # Scholarship types breakdown
            type_breakdown_result = (
                self.db.query(Scholarship.scholarship_type, func.count(Scholarship.id))
                .filter(Scholarship.status == ScholarshipStatus.ACTIVE)
                .group_by(Scholarship.scholarship_type)
                .all()
            )

            type_breakdown = {
                str(type_val): count for type_val, count in type_breakdown_result
            }

            return {
                "total_scholarships": total_scholarships,
                "active_scholarships": active_scholarships,
                "verified_scholarships": verified_scholarships,
                "total_amount_available": int(amount_sum),
                "scholarship_types": type_breakdown,
            }

        except Exception as e:
            logger.error(f"Error getting scholarship statistics: {str(e)}")
            raise Exception(f"Failed to get statistics: {str(e)}")

    def _get_match_reasons(
        self, scholarship: Scholarship, profile: UserProfile
    ) -> List[str]:
        """Get reasons why a scholarship matches a profile"""
        reasons = []

        try:
            # GPA match
            if (
                scholarship.min_gpa
                and profile.gpa
                and profile.gpa >= scholarship.min_gpa
            ):
                reasons.append(
                    f"Meets GPA requirement ({profile.gpa:.1f} >= {scholarship.min_gpa:.1f})"
                )

            # Test scores
            if (
                scholarship.min_sat_score
                and profile.sat_score
                and profile.sat_score >= scholarship.min_sat_score
            ):
                reasons.append(
                    f"Meets SAT requirement ({profile.sat_score} >= {scholarship.min_sat_score})"
                )

            if (
                scholarship.min_act_score
                and profile.act_score
                and profile.act_score >= scholarship.min_act_score
            ):
                reasons.append(
                    f"Meets ACT requirement ({profile.act_score} >= {scholarship.min_act_score})"
                )

            # Major match
            if scholarship.required_majors and profile.intended_major:
                if profile.intended_major in scholarship.required_majors:
                    reasons.append(f"Major matches ({profile.intended_major})")

            # Geographic match
            if scholarship.eligible_states and profile.state:
                if profile.state in scholarship.eligible_states:
                    reasons.append(f"State eligible ({profile.state})")

            # Demographics
            if scholarship.first_generation_college_required is not None:
                if (
                    profile.first_generation_college
                    == scholarship.first_generation_college_required
                ):
                    if profile.first_generation_college:
                        reasons.append("First-generation college student")

            # Activities
            if scholarship.required_activities and profile.extracurricular_activities:
                common = set(scholarship.required_activities) & set(
                    profile.extracurricular_activities
                )
                if common:
                    reasons.append(
                        f"Matching activities: {', '.join(list(common)[:3])}"
                    )

            # Volunteer hours
            if scholarship.volunteer_hours_min and profile.volunteer_hours:
                if profile.volunteer_hours >= scholarship.volunteer_hours_min:
                    reasons.append(
                        f"Meets volunteer requirement ({profile.volunteer_hours} >= {scholarship.volunteer_hours_min} hours)"
                    )

            # Special talents
            if scholarship.special_talents and profile.special_talents:
                common = set(scholarship.special_talents) & set(profile.special_talents)
                if common:
                    reasons.append(
                        f"Special talents match: {', '.join(list(common)[:2])}"
                    )

            # Language preferences
            if scholarship.languages_preferred and profile.languages_spoken:
                common = set(scholarship.languages_preferred) & set(
                    profile.languages_spoken
                )
                if common:
                    reasons.append(f"Language skills: {', '.join(list(common))}")

        except Exception as e:
            logger.error(f"Error generating match reasons: {str(e)}")
            reasons.append("Basic eligibility criteria met")

        return reasons

    def _get_mismatch_reasons(
        self, scholarship: Scholarship, profile: UserProfile
    ) -> List[str]:
        """Get reasons why a scholarship might not be a perfect match"""
        reasons = []

        try:
            # Missing test scores
            if scholarship.min_sat_score and not profile.sat_score:
                if scholarship.min_act_score and not profile.act_score:
                    reasons.append("No test scores provided (SAT or ACT required)")

            # Missing essays
            if scholarship.essay_required and not profile.has_personal_statement:
                reasons.append("Essay required but personal statement not completed")

            if (
                scholarship.leadership_essay_required
                and not profile.has_leadership_essay
            ):
                reasons.append("Leadership essay required but not completed")

            # Missing activities
            if (
                scholarship.required_activities
                and not profile.extracurricular_activities
            ):
                reasons.append("Specific activities required but none listed")

            # Volunteer hours gap
            if scholarship.volunteer_hours_min and (
                not profile.volunteer_hours
                or profile.volunteer_hours < scholarship.volunteer_hours_min
            ):
                reasons.append(
                    f"Minimum {scholarship.volunteer_hours_min} volunteer hours required"
                )

            # Portfolio/interview requirements
            if scholarship.portfolio_required:
                reasons.append("Portfolio submission required")

            if scholarship.interview_required:
                reasons.append("Interview process required")

            # High difficulty warning
            if scholarship.difficulty_level == "very_hard":
                reasons.append(
                    "Very competitive scholarship with extensive requirements"
                )
            elif scholarship.difficulty_level == "hard":
                reasons.append("Highly competitive scholarship")

            # Recommendation letters
            if scholarship.recommendation_letters_required > 0:
                reasons.append(
                    f"{scholarship.recommendation_letters_required} recommendation letters required"
                )

        except Exception as e:
            logger.error(f"Error generating mismatch reasons: {str(e)}")

        return reasons

    # ===========================
    # ADMIN & VERIFICATION METHODS
    # ===========================

    def verify_scholarship(
        self, scholarship_id: int, verified: bool, notes: Optional[str] = None
    ) -> Optional[Scholarship]:
        """Admin function to verify/unverify scholarships"""
        try:
            db_scholarship = self.get_scholarship_by_id(scholarship_id)
            if not db_scholarship:
                return None

            db_scholarship.verified = verified
            db_scholarship.last_verified_at = datetime.utcnow()

            if notes:
                db_scholarship.verification_notes = notes

            self.db.commit()
            self.db.refresh(db_scholarship)

            logger.info(
                f"{'Verified' if verified else 'Unverified'} scholarship {scholarship_id}"
            )
            return db_scholarship

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error verifying scholarship {scholarship_id}: {str(e)}")
            raise Exception(f"Failed to verify scholarship: {str(e)}")

    def increment_view_count(self, scholarship_id: int) -> bool:
        """Increment the view count for a scholarship"""
        try:
            db_scholarship = self.get_scholarship_by_id(scholarship_id)
            if not db_scholarship:
                return False

            db_scholarship.views_count = (db_scholarship.views_count or 0) + 1
            self.db.commit()

            return True

        except Exception as e:
            self.db.rollback()
            logger.error(
                f"Error incrementing view count for scholarship {scholarship_id}: {str(e)}"
            )
            return False

    def get_scholarships_by_organization(self, organization: str) -> List[Scholarship]:
        """Get all scholarships from a specific organization"""
        try:
            return (
                self.db.query(Scholarship)
                .filter(Scholarship.organization.ilike(f"%{organization}%"))
                .all()
            )
        except Exception as e:
            logger.error(
                f"Error getting scholarships by organization {organization}: {str(e)}"
            )
            raise Exception(f"Failed to get scholarships by organization: {str(e)}")

    def get_expiring_scholarships(self, days_ahead: int = 30) -> List[Scholarship]:
        """Get scholarships expiring within the specified number of days"""
        try:
            cutoff_date = datetime.utcnow() + timedelta(days=days_ahead)

            return (
                self.db.query(Scholarship)
                .filter(
                    Scholarship.status == ScholarshipStatus.ACTIVE,
                    Scholarship.deadline.is_not(None),
                    Scholarship.deadline <= cutoff_date,
                    Scholarship.deadline >= datetime.utcnow(),
                )
                .order_by(asc(Scholarship.deadline))
                .all()
            )

        except Exception as e:
            logger.error(f"Error getting expiring scholarships: {str(e)}")
            raise Exception(f"Failed to get expiring scholarships: {str(e)}")

    # ===========================
    # BULK OPERATIONS
    # ===========================

    def bulk_create_scholarships(
        self,
        scholarships_data: List[ScholarshipCreate],
        created_by_user_id: Optional[int] = None,
    ) -> Tuple[List[Scholarship], List[str]]:
        """Bulk create scholarships"""
        created_scholarships = []
        errors = []

        try:
            for i, scholarship_data in enumerate(scholarships_data):
                try:
                    scholarship = self.create_scholarship(
                        scholarship_data, created_by_user_id
                    )
                    created_scholarships.append(scholarship)
                except Exception as e:
                    error_msg = f"Error creating scholarship {i+1}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)

            return created_scholarships, errors

        except Exception as e:
            logger.error(f"Error in bulk create scholarships: {str(e)}")
            raise Exception(f"Bulk create failed: {str(e)}")

    def update_expired_scholarships(self) -> int:
        """Update scholarships that have passed their deadline to expired status"""
        try:
            current_time = datetime.utcnow()

            updated_count = (
                self.db.query(Scholarship)
                .filter(
                    Scholarship.status == ScholarshipStatus.ACTIVE,
                    Scholarship.deadline.is_not(None),
                    Scholarship.deadline < current_time,
                )
                .update(
                    {
                        "status": ScholarshipStatus.EXPIRED,
                        "updated_at": current_time,
                    },
                    synchronize_session=False,
                )
            )

            self.db.commit()
            logger.info(f"Updated {updated_count} scholarships to expired status")
            return updated_count

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating expired scholarships: {str(e)}")
            raise Exception(f"Failed to update expired scholarships: {str(e)}")
