# app/services/scholarship.py - UPDATED FOR SIMPLIFIED SCHEMA
"""
Scholarship service - updated to work with simplified schema (no boolean flags)
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from typing import List, Tuple, Optional
from app.models.scholarship import Scholarship, ScholarshipStatus, ScholarshipType
from app.schemas.scholarship import ScholarshipCreate, ScholarshipSearchFilter
import logging

logger = logging.getLogger(__name__)


class ScholarshipService:
    def __init__(self, db: Session):
        self.db = db

    def get_scholarship_by_id(self, scholarship_id: int) -> Optional[Scholarship]:
        """Get a single scholarship by ID"""
        return (
            self.db.query(Scholarship).filter(Scholarship.id == scholarship_id).first()
        )

    def get_all_scholarships(
        self, limit: int = 100, active_only: bool = True
    ) -> List[Scholarship]:
        """Get all scholarships"""
        try:
            query = self.db.query(Scholarship)

            if active_only:
                query = query.filter(Scholarship.status == ScholarshipStatus.ACTIVE)

            return query.limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting scholarships: {str(e)}")
            raise Exception(f"Failed to get scholarships: {str(e)}")

    def create_scholarship(self, scholarship_data: ScholarshipCreate) -> Scholarship:
        """Create a new scholarship"""
        try:
            scholarship = Scholarship(**scholarship_data.model_dump())
            self.db.add(scholarship)
            self.db.commit()
            self.db.refresh(scholarship)
            return scholarship
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating scholarship: {str(e)}")
            raise Exception(f"Failed to create scholarship: {str(e)}")

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

    def search_scholarships(
        self, filters: ScholarshipSearchFilter
    ) -> Tuple[List[Scholarship], int]:
        """
        Search scholarships with simplified filters
        REMOVED: essay_required, interview_required filters (columns no longer exist)
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

            # Financial filters
            if filters.min_amount:
                query = query.filter(Scholarship.amount_exact >= filters.min_amount)

            if filters.max_amount:
                query = query.filter(Scholarship.amount_exact <= filters.max_amount)

            # Renewable filter (this field still exists)
            if filters.renewable_only:
                query = query.filter(Scholarship.is_renewable == True)

            # Count total before pagination
            total = query.count()

            # Sorting
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

    def delete_scholarship(self, scholarship_id: int) -> bool:
        """Delete a scholarship"""
        try:
            scholarship = self.get_scholarship_by_id(scholarship_id)
            if not scholarship:
                return False

            self.db.delete(scholarship)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting scholarship: {str(e)}")
            return False
