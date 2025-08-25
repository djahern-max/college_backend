# app/services/scholarship.py
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from sqlalchemy.sql import text
from datetime import datetime, timedelta

from app.models.scholarship import (
    Scholarship,
    ScholarshipMatch,
    ScholarshipStatus,
    ScholarshipType,
)
from app.models.profile import UserProfile
from app.schemas.scholarship import (
    ScholarshipCreate,
    ScholarshipUpdate,
    ScholarshipSearchFilter,
    ScholarshipMatchCreate,
    ScholarshipMatchUpdate,
    ScholarshipMatchSummary,
)


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
        db_scholarship = Scholarship(
            **scholarship_data.model_dump(exclude_unset=True),
            created_by=created_by_user_id,
        )

        self.db.add(db_scholarship)
        self.db.commit()
        self.db.refresh(db_scholarship)
        return db_scholarship

    def get_scholarship_by_id(self, scholarship_id: int) -> Optional[Scholarship]:
        """Get scholarship by ID"""
        return (
            self.db.query(Scholarship).filter(Scholarship.id == scholarship_id).first()
        )

    def get_scholarships_paginated(
        self, page: int = 1, limit: int = 50, active_only: bool = True
    ) -> Tuple[List[Scholarship], int]:
        """Get paginated list of scholarships"""
        query = self.db.query(Scholarship)

        if active_only:
            query = query.filter(Scholarship.status == ScholarshipStatus.ACTIVE)

        total = query.count()

        scholarships = query.offset((page - 1) * limit).limit(limit).all()

        return scholarships, total

    def update_scholarship(
        self, scholarship_id: int, scholarship_data: ScholarshipUpdate
    ) -> Optional[Scholarship]:
        """Update existing scholarship"""
        db_scholarship = self.get_scholarship_by_id(scholarship_id)
        if not db_scholarship:
            return None

        update_data = scholarship_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_scholarship, field, value)

        db_scholarship.updated_at = func.now()

        self.db.commit()
        self.db.refresh(db_scholarship)
        return db_scholarship

    def delete_scholarship(self, scholarship_id: int) -> bool:
        """Delete scholarship"""
        db_scholarship = self.get_scholarship_by_id(scholarship_id)
        if not db_scholarship:
            return False

        self.db.delete(db_scholarship)
        self.db.commit()
        return True

    # ===========================
    # SEARCH AND FILTERING
    # ===========================

    def search_scholarships(
        self, filters: ScholarshipSearchFilter
    ) -> Tuple[List[Scholarship], int]:
        """Search scholarships with filters"""
        query = self.db.query(Scholarship)

        # Basic filters
        if filters.active_only:
            query = query.filter(Scholarship.status == ScholarshipStatus.ACTIVE)

        if filters.verified_only:
            query = query.filter(Scholarship.verified == True)

        if filters.scholarship_type:
            query = query.filter(
                Scholarship.scholarship_type == filters.scholarship_type
            )

        # Amount filters
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

        # Academic filters
        if filters.student_gpa:
            query = query.filter(
                or_(
                    Scholarship.min_gpa.is_(None),
                    Scholarship.min_gpa <= filters.student_gpa,
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

        # Demographic filters
        if filters.is_first_generation is not None:
            query = query.filter(
                or_(
                    Scholarship.first_generation_college_required.is_(None),
                    Scholarship.first_generation_college_required
                    == filters.is_first_generation,
                )
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

        # Essay/Leadership requirements
        if filters.requires_essay is not None:
            if filters.requires_essay:
                query = query.filter(Scholarship.essay_required == True)
            else:
                query = query.filter(Scholarship.essay_required == False)

        if filters.requires_leadership is not None:
            if filters.requires_leadership:
                query = query.filter(Scholarship.leadership_required == True)
            else:
                query = query.filter(Scholarship.leadership_required == False)

        # Count total before pagination
        total = query.count()

        # Sorting
        sort_column = getattr(Scholarship, filters.sort_by, Scholarship.created_at)
        if filters.sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        # Pagination
        scholarships = (
            query.offset((filters.page - 1) * filters.limit).limit(filters.limit).all()
        )

        return scholarships, total

    # ===========================
    # MATCHING ALGORITHMS
    # ===========================

    def find_matches_for_user(
        self, user_id: int, min_score: float = 0.0, limit: int = 100
    ) -> List[Scholarship]:
        """Find scholarship matches for a specific user"""
        profile = (
            self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        )
        if not profile:
            return []

        # Get active scholarships
        scholarships = (
            self.db.query(Scholarship)
            .filter(
                Scholarship.status == ScholarshipStatus.ACTIVE,
                or_(Scholarship.deadline.is_(None), Scholarship.deadline > func.now()),
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

        return [match[0] for match in matches[:limit]]

    def calculate_and_store_matches(
        self, user_id: int, force_recalculate: bool = False
    ) -> int:
        """Calculate and store matches for a user in the database"""
        profile = (
            self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        )
        if not profile:
            return 0

        # Clear existing matches if force recalculate
        if force_recalculate:
            self.db.query(ScholarshipMatch).filter(
                ScholarshipMatch.user_id == user_id
            ).delete()

        # Get scholarships that don't already have matches for this user
        existing_match_ids = (
            self.db.query(ScholarshipMatch.scholarship_id)
            .filter(ScholarshipMatch.user_id == user_id)
            .subquery()
        )

        scholarships = (
            self.db.query(Scholarship)
            .filter(
                Scholarship.status == ScholarshipStatus.ACTIVE,
                or_(Scholarship.deadline.is_(None), Scholarship.deadline > func.now()),
                ~Scholarship.id.in_(existing_match_ids),
            )
            .all()
        )

        matches_created = 0
        for scholarship in scholarships:
            if scholarship.matches_profile_basic(profile):
                score = scholarship.calculate_match_score(profile)

                # Only store matches above a threshold
                if score >= 30.0:
                    match_reasons = self._get_match_reasons(scholarship, profile)
                    mismatch_reasons = self._get_mismatch_reasons(scholarship, profile)

                    db_match = ScholarshipMatch(
                        user_id=user_id,
                        scholarship_id=scholarship.id,
                        match_score=score,
                        match_reasons=match_reasons,
                        mismatch_reasons=mismatch_reasons,
                    )

                    self.db.add(db_match)
                    matches_created += 1

        self.db.commit()
        return matches_created

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
            matches = self.calculate_and_store_matches(
                profile.user_id, force_recalculate=True
            )
            total_matches += matches

        return {"users_processed": total_users, "total_matches_created": total_matches}

    # ===========================
    # MATCH MANAGEMENT
    # ===========================

    def get_user_matches(
        self, user_id: int, limit: int = 50, min_score: float = 0.0
    ) -> List[ScholarshipMatch]:
        """Get scholarship matches for a user"""
        return (
            self.db.query(ScholarshipMatch)
            .filter(
                ScholarshipMatch.user_id == user_id,
                ScholarshipMatch.match_score >= min_score,
            )
            .order_by(desc(ScholarshipMatch.match_score))
            .limit(limit)
            .all()
        )

    def update_match_status(
        self, user_id: int, scholarship_id: int, status_data: ScholarshipMatchUpdate
    ) -> Optional[ScholarshipMatch]:
        """Update user's interaction with a scholarship match"""
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
        if "viewed" in update_data and update_data["viewed"]:
            db_match.viewed_at = func.now()

        if "applied" in update_data and update_data["applied"]:
            db_match.applied_at = func.now()

        self.db.commit()
        self.db.refresh(db_match)
        return db_match

    def get_match_summary(self, user_id: int) -> ScholarshipMatchSummary:
        """Get summary statistics for a user's matches"""
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
        thirty_days_ago = datetime.now() - timedelta(days=30)
        matches_this_month = len(
            [m for m in matches if m.match_date >= thirty_days_ago]
        )

        # Upcoming deadlines (next 30 days)
        thirty_days_later = datetime.now() + timedelta(days=30)
        scholarship_ids = [m.scholarship_id for m in matches]
        upcoming_deadlines = (
            self.db.query(Scholarship)
            .filter(
                Scholarship.id.in_(scholarship_ids),
                Scholarship.deadline.between(datetime.now(), thirty_days_later),
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
            average_match_score=average_match_score,
            best_match_score=best_match_score,
            matches_this_month=matches_this_month,
            upcoming_deadlines=upcoming_deadlines,
        )

    # ===========================
    # UTILITY AND HELPER METHODS
    # ===========================

    def get_scholarship_statistics(self) -> Dict[str, Any]:
        """Get overall scholarship platform statistics"""
        total_scholarships = self.db.query(Scholarship).count()
        active_scholarships = (
            self.db.query(Scholarship)
            .filter(Scholarship.status == ScholarshipStatus.ACTIVE)
            .count()
        )
        verified_scholarships = (
            self.db.query(Scholarship).filter(Scholarship.verified == True).count()
        )

        # Total scholarship money available
        total_amount = (
            self.db.query(
                func.coalesce(func.sum(Scholarship.amount_exact), 0)
                + func.coalesce(func.sum(Scholarship.amount_max), 0)
            ).scalar()
            or 0
        )

        # Scholarship types breakdown
        type_breakdown = (
            self.db.query(Scholarship.scholarship_type, func.count(Scholarship.id))
            .group_by(Scholarship.scholarship_type)
            .all()
        )

        return {
            "total_scholarships": total_scholarships,
            "active_scholarships": active_scholarships,
            "verified_scholarships": verified_scholarships,
            "total_amount_available": total_amount,
            "scholarship_types": dict(type_breakdown),
        }

    def _get_match_reasons(
        self, scholarship: Scholarship, profile: UserProfile
    ) -> List[str]:
        """Get reasons why a scholarship matches a profile"""
        reasons = []

        # GPA match
        if scholarship.min_gpa and profile.gpa and profile.gpa >= scholarship.min_gpa:
            reasons.append(
                f"Meets GPA requirement ({profile.gpa} >= {scholarship.min_gpa})"
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
                reasons.append(f"Matching activities: {', '.join(common)}")

        return reasons

    def _get_mismatch_reasons(
        self, scholarship: Scholarship, profile: UserProfile
    ) -> List[str]:
        """Get reasons why a scholarship might not be a perfect match"""
        reasons = []

        # Missing test scores
        if scholarship.min_sat_score and not profile.sat_score:
            if scholarship.min_act_score and not profile.act_score:
                reasons.append("No test scores provided (SAT or ACT required)")

        # Missing essays
        if scholarship.essay_required and not profile.personal_statement:
            reasons.append("Essay required but not provided")

        if scholarship.leadership_essay_required and not profile.leadership_experience:
            reasons.append("Leadership essay required")

        # Missing activities
        if scholarship.required_activities and not profile.extracurricular_activities:
            reasons.append("Specific activities required")

        # Volunteer hours
        if scholarship.volunteer_hours_min and (
            not profile.volunteer_hours
            or profile.volunteer_hours < scholarship.volunteer_hours_min
        ):
            reasons.append(
                f"Minimum {scholarship.volunteer_hours_min} volunteer hours required"
            )

        return reasons
