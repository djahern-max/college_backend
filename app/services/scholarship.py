# app/services/scholarship.py - SIMPLIFIED VERSION
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, desc, asc
from datetime import datetime

from app.models.scholarship import Scholarship, ScholarshipStatus
from app.schemas.scholarship import ScholarshipCreate, ScholarshipSearchFilter
import logging

logger = logging.getLogger(__name__)


class ScholarshipService:
    """Simplified service class for basic scholarship operations"""

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
        """Search scholarships with filters"""
        try:
            query = self.db.query(Scholarship)

            # Basic status filters
            if filters.active_only:
                query = query.filter(Scholarship.status == ScholarshipStatus.ACTIVE)

            if filters.verified_only:
                query = query.filter(Scholarship.verified == True)

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

            # Application requirement filters
            if filters.requires_essay is not None:
                query = query.filter(
                    Scholarship.essay_required == filters.requires_essay
                )

            # Deadline filters (simplified)
            if filters.deadline_after:
                try:
                    # Try to parse the date string
                    deadline_date = datetime.fromisoformat(
                        filters.deadline_after.replace("Z", "+00:00")
                    )
                    query = query.filter(
                        or_(
                            Scholarship.deadline.is_(None),
                            Scholarship.deadline >= deadline_date,
                        )
                    )
                except ValueError:
                    logger.warning(
                        f"Invalid deadline_after format: {filters.deadline_after}"
                    )

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
    # UTILITY METHODS
    # ===========================

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
