# app/services/scholarship.py - UPDATED FOR NEW SCHEMA
"""
Scholarship service - updated to work with new essential fields
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc, and_, case
from typing import List, Tuple, Optional
from app.models.scholarship import Scholarship, ScholarshipStatus, ScholarshipType
from app.schemas.scholarship import (
    ScholarshipCreate,
    ScholarshipSearchFilter,
    ScholarshipUpdate,
)
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

    def update_scholarship(
        self, scholarship_id: int, scholarship_data: ScholarshipUpdate
    ) -> Optional[Scholarship]:
        """Update an existing scholarship"""
        try:
            scholarship = self.get_scholarship_by_id(scholarship_id)
            if not scholarship:
                return None

            # Update only provided fields
            update_data = scholarship_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(scholarship, field, value)

            self.db.commit()
            self.db.refresh(scholarship)
            return scholarship
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating scholarship: {str(e)}")
            raise Exception(f"Failed to update scholarship: {str(e)}")

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
        Search scholarships with all available filters
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

            # Text search (title, organization, description)
            if filters.search_query:
                search_term = f"%{filters.search_query}%"
                query = query.filter(
                    or_(
                        Scholarship.title.ilike(search_term),
                        Scholarship.organization.ilike(search_term),
                        Scholarship.description.ilike(search_term),
                    )
                )

            # Financial filters - check if award amount overlaps with filter range
            if filters.min_amount:
                # Scholarship max amount must be >= filter min
                query = query.filter(Scholarship.amount_max >= filters.min_amount)

            if filters.max_amount:
                # Scholarship min amount must be <= filter max
                query = query.filter(Scholarship.amount_min <= filters.max_amount)

            # Renewable filter
            if filters.renewable_only:
                query = query.filter(Scholarship.is_renewable == True)

            # GPA filter - show scholarships where user meets or exceeds requirement
            if filters.min_gpa_filter:
                # Show scholarships with no GPA requirement OR where user's GPA >= requirement
                query = query.filter(
                    or_(
                        Scholarship.min_gpa == None,
                        Scholarship.min_gpa <= filters.min_gpa_filter,
                    )
                )

            # Date filters
            if filters.deadline_before:
                query = query.filter(
                    and_(
                        Scholarship.deadline != None,
                        Scholarship.deadline <= filters.deadline_before,
                    )
                )

            if filters.deadline_after:
                query = query.filter(
                    and_(
                        Scholarship.deadline != None,
                        Scholarship.deadline >= filters.deadline_after,
                    )
                )

            # Academic year filter
            if filters.academic_year:
                query = query.filter(
                    Scholarship.for_academic_year == filters.academic_year
                )

            # Count total before pagination
            total = query.count()

            # Priority sorting - specific scholarships first
            priority_order = case(
                (Scholarship.title.ilike("%Lowe%Educational%"), 1),
                (Scholarship.title.ilike("%Target%Community%"), 2),
                (Scholarship.title.ilike("%Google%Lime%"), 3),
                (Scholarship.title.ilike("%Coca%Cola%"), 4),
                (Scholarship.title.ilike("%Violet%Richardson%"), 5),
                (Scholarship.title.ilike("%National%Merit%"), 6),
                (Scholarship.title.ilike("%Do%Something%"), 7),
                # Then other scholarships with images
                (Scholarship.primary_image_url.isnot(None), 8),
                # Finally scholarships without images
                else_=9,
            )

            query = query.order_by(asc(priority_order))

            # Then apply user's requested sorting
            valid_sort_fields = [
                "created_at",
                "amount_min",
                "amount_max",
                "deadline",
                "title",
                "views_count",
            ]
            sort_field = (
                filters.sort_by
                if filters.sort_by in valid_sort_fields
                else "created_at"
            )

            sort_column = getattr(Scholarship, sort_field, Scholarship.created_at)

            # Handle NULL values in deadline sorting by putting them last
            if sort_field == "deadline":
                if filters.sort_order == "desc":
                    query = query.order_by(desc(sort_column.nullslast()))
                else:
                    query = query.order_by(asc(sort_column.nullslast()))
            else:
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

    def get_scholarships_by_deadline(
        self, days_ahead: int = 30, limit: int = 50
    ) -> List[Scholarship]:
        """Get scholarships with upcoming deadlines"""
        try:
            from datetime import datetime, timedelta

            today = datetime.now().date()
            future_date = today + timedelta(days=days_ahead)

            # Priority order for featured scholarships
            priority_order = case(
                (Scholarship.title.ilike("%Lowe%Educational%"), 1),
                (Scholarship.title.ilike("%Target%Community%"), 2),
                (Scholarship.title.ilike("%Google%Lime%"), 3),
                (Scholarship.title.ilike("%Coca%Cola%"), 4),
                (Scholarship.title.ilike("%Violet%Richardson%"), 5),
                (Scholarship.title.ilike("%National%Merit%"), 6),
                (Scholarship.title.ilike("%Do%Something%"), 7),
                (Scholarship.primary_image_url.isnot(None), 8),
                else_=9,
            )

            query = (
                self.db.query(Scholarship)
                .filter(Scholarship.status == ScholarshipStatus.ACTIVE)
                .filter(Scholarship.deadline != None)
                .filter(Scholarship.deadline >= today)
                .filter(Scholarship.deadline <= future_date)
                .order_by(asc(priority_order))
                .order_by(asc(Scholarship.deadline))
                .limit(limit)
            )

            return query.all()
        except Exception as e:
            logger.error(f"Error getting scholarships by deadline: {str(e)}")
            raise Exception(f"Failed to get scholarships by deadline: {str(e)}")
