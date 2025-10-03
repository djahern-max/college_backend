# app/services/scholarship.py - SIMPLIFIED VERSION
"""
Streamlined scholarship service - removed references to dropped fields
Only uses fields that exist in the simplified model
"""

from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from datetime import datetime
import logging

from app.models.scholarship import Scholarship, ScholarshipStatus, ScholarshipType
from app.schemas.scholarship import ScholarshipCreate, ScholarshipSearchFilter

logger = logging.getLogger(__name__)


class ScholarshipService:
    """Service for scholarship operations"""

    def __init__(self, db: Session):
        self.db = db

    # ===========================
    # CREATE & UPDATE
    # ===========================

    def create_scholarship(
        self,
        scholarship_data: ScholarshipCreate,
        created_by_user_id: Optional[int] = None,
    ) -> Scholarship:
        """Create a new scholarship"""
        try:
            db_scholarship = Scholarship(**scholarship_data.model_dump())

            self.db.add(db_scholarship)
            self.db.commit()
            self.db.refresh(db_scholarship)

            logger.info(f"Created scholarship: {db_scholarship.id}")
            return db_scholarship

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating scholarship: {str(e)}")
            raise Exception(f"Failed to create scholarship: {str(e)}")

    # ===========================
    # READ OPERATIONS
    # ===========================

    def get_scholarship_by_id(self, scholarship_id: int) -> Optional[Scholarship]:
        """Get scholarship by ID"""
        return (
            self.db.query(Scholarship).filter(Scholarship.id == scholarship_id).first()
        )

    def get_all_scholarships(
        self, skip: int = 0, limit: int = 100, active_only: bool = False
    ) -> List[Scholarship]:
        """Get all scholarships with optional filtering"""
        query = self.db.query(Scholarship)

        if active_only:
            query = query.filter(Scholarship.status == ScholarshipStatus.ACTIVE)

        return query.offset(skip).limit(limit).all()

    def increment_view_count(self, scholarship_id: int) -> bool:
        """Increment scholarship view count"""
        try:
            scholarship = self.get_scholarship_by_id(scholarship_id)
            if scholarship:
                scholarship.views_count += 1
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error incrementing view count: {str(e)}")
            return False

    # ===========================
    # SEARCH AND FILTERING
    # ===========================

    def search_scholarships(
        self, filters: ScholarshipSearchFilter
    ) -> Tuple[List[Scholarship], int]:
        """
        Search scholarships with simplified filters
        Only uses fields that exist in the streamlined model
        """
        try:
            query = self.db.query(Scholarship)

            # Status filters
            if filters.active_only:
                query = query.filter(Scholarship.status == ScholarshipStatus.ACTIVE)

            if filters.verified_only:
                query = query.filter(Scholarship.verified == True)

            if filters.featured_only:
                query = query.filter(Scholarship.featured == True)

            # Scholarship type filter
            if filters.scholarship_type:
                try:
                    scholarship_type = ScholarshipType(filters.scholarship_type)
                    query = query.filter(
                        Scholarship.scholarship_type == scholarship_type
                    )
                except ValueError:
                    logger.warning(
                        f"Invalid scholarship type: {filters.scholarship_type}"
                    )

            # Text search (only searchable fields: title, organization)
            if filters.search_query:
                search_term = f"%{filters.search_query}%"
                query = query.filter(
                    or_(
                        Scholarship.title.ilike(search_term),
                        Scholarship.organization.ilike(search_term),
                    )
                )

            # Financial filters (only amount_exact exists now)
            if filters.min_amount:
                query = query.filter(Scholarship.amount_exact >= filters.min_amount)

            if filters.max_amount:
                query = query.filter(Scholarship.amount_exact <= filters.max_amount)

            # Application requirement filters
            if filters.requires_essay is not None:
                query = query.filter(
                    Scholarship.essay_required == filters.requires_essay
                )

            if filters.requires_interview is not None:
                query = query.filter(
                    Scholarship.interview_required == filters.requires_interview
                )

            if filters.renewable_only:
                query = query.filter(Scholarship.is_renewable == True)

            # Count total before pagination
            total = query.count()

            # Sorting (only on existing fields)
            valid_sort_fields = ["created_at", "amount_exact", "title", "views_count"]
            sort_field = (
                filters.sort_by
                if filters.sort_by in valid_sort_fields
                else "created_at"
            )

            sort_column = getattr(Scholarship, sort_field, Scholarship.created_at)
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
    # DELETE
    # ===========================

    def delete_scholarship(self, scholarship_id: int) -> bool:
        """Delete a scholarship"""
        try:
            scholarship = self.get_scholarship_by_id(scholarship_id)
            if not scholarship:
                return False

            self.db.delete(scholarship)
            self.db.commit()

            logger.info(f"Deleted scholarship: {scholarship_id}")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting scholarship {scholarship_id}: {str(e)}")
            raise Exception(f"Failed to delete scholarship: {str(e)}")

    # ===========================
    # BULK OPERATIONS
    # ===========================

    def bulk_create_scholarships(
        self, scholarships_data: List[ScholarshipCreate]
    ) -> Tuple[List[Scholarship], List[dict]]:
        """Bulk create scholarships"""
        created_scholarships = []
        errors = []

        for idx, scholarship_data in enumerate(scholarships_data):
            try:
                scholarship = self.create_scholarship(scholarship_data)
                created_scholarships.append(scholarship)
            except Exception as e:
                errors.append(
                    {"index": idx, "title": scholarship_data.title, "error": str(e)}
                )
                logger.error(f"Error creating scholarship at index {idx}: {str(e)}")

        return created_scholarships, errors

    # ===========================
    # STATISTICS
    # ===========================

    def get_scholarship_stats(self) -> dict:
        """Get scholarship statistics"""
        try:
            total = self.db.query(Scholarship).count()
            active = (
                self.db.query(Scholarship)
                .filter(Scholarship.status == ScholarshipStatus.ACTIVE)
                .count()
            )
            verified = (
                self.db.query(Scholarship).filter(Scholarship.verified == True).count()
            )
            featured = (
                self.db.query(Scholarship).filter(Scholarship.featured == True).count()
            )

            return {
                "total_scholarships": total,
                "active_scholarships": active,
                "verified_scholarships": verified,
                "featured_scholarships": featured,
            }

        except Exception as e:
            logger.error(f"Error getting scholarship stats: {str(e)}")
            return {}
