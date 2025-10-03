# app/services/institution.py - SIMPLIFIED VERSION
"""
Streamlined institution service - only uses fields that exist
Removed references to dropped fields (customer_rank, image_quality, etc.)
"""

from typing import Optional, List, Tuple, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, desc
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.models.institution import Institution, ControlType
from app.schemas.institution import InstitutionSearchFilter

logger = logging.getLogger(__name__)


class InstitutionService:
    """Simplified service for institution operations"""

    def __init__(self, db: Session):
        self.db = db

    # ============================================================================
    # BASIC CRUD
    # ============================================================================

    def get_institution_by_id(self, institution_id: int) -> Optional[Institution]:
        """Get institution by database ID"""
        try:
            return (
                self.db.query(Institution)
                .filter(Institution.id == institution_id)
                .first()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error getting institution {institution_id}: {str(e)}")
            raise

    def get_institution_by_ipeds_id(self, ipeds_id: int) -> Optional[Institution]:
        """Get institution by IPEDS ID"""
        try:
            return (
                self.db.query(Institution)
                .filter(Institution.ipeds_id == ipeds_id)
                .first()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error getting institution with IPEDS {ipeds_id}: {str(e)}")
            raise

    # ============================================================================
    # SEARCH & FILTERING
    # ============================================================================

    def search_institutions(
        self, filters: InstitutionSearchFilter
    ) -> Tuple[List[Institution], int]:
        """Search institutions with filters"""
        try:
            query = self.db.query(Institution)

            # State filter
            if filters.state:
                query = query.filter(Institution.state == filters.state.upper())

            # Control type filter
            if filters.control_type:
                try:
                    control_type = ControlType(filters.control_type)
                    query = query.filter(Institution.control_type == control_type)
                except ValueError:
                    logger.warning(f"Invalid control type: {filters.control_type}")

            # Text search
            if filters.search_query:
                search_term = f"%{filters.search_query}%"
                query = query.filter(
                    or_(
                        Institution.name.ilike(search_term),
                        Institution.city.ilike(search_term),
                    )
                )

            # Count total
            total = query.count()

            # Sorting
            sort_column = getattr(Institution, filters.sort_by, Institution.name)
            if filters.sort_order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(sort_column)

            # Pagination
            offset = (filters.page - 1) * filters.limit
            institutions = query.offset(offset).limit(filters.limit).all()

            return institutions, total

        except SQLAlchemyError as e:
            logger.error(f"Error searching institutions: {str(e)}")
            raise

    # ============================================================================
    # UTILITY METHODS
    # ============================================================================

    def get_available_states(self) -> List[str]:
        """Get list of states that have institutions"""
        try:
            states = (
                self.db.query(Institution.state)
                .distinct()
                .order_by(Institution.state)
                .all()
            )
            return [state[0] for state in states if state[0]]
        except SQLAlchemyError as e:
            logger.error(f"Error getting available states: {str(e)}")
            raise

    def get_by_state(self, state: str, limit: int = 50) -> List[Institution]:
        """Get institutions by state"""
        try:
            return (
                self.db.query(Institution)
                .filter(Institution.state == state.upper())
                .order_by(Institution.name)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error getting institutions for state {state}: {str(e)}")
            raise
