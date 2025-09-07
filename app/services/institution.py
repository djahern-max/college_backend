# app/services/institution.py
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging

from app.models.institution import Institution
from app.schemas.institution import (
    InstitutionCreate,
    InstitutionUpdate,
    InstitutionSearch,
    ControlType,
    SizeCategory,
    USRegion,
)

logger = logging.getLogger(__name__)


class InstitutionService:
    """Service class for institution CRUD operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_institution_by_id(self, institution_id: int) -> Optional[Institution]:
        """Get institution by database ID"""
        try:
            return (
                self.db.query(Institution)
                .filter(Institution.id == institution_id)
                .first()
            )
        except SQLAlchemyError as e:
            logger.error(
                f"Database error getting institution {institution_id}: {str(e)}"
            )
            raise Exception(f"Database error: {str(e)}")

    def get_institution_by_ipeds_id(self, ipeds_id: int) -> Optional[Institution]:
        """Get institution by IPEDS ID"""
        try:
            return (
                self.db.query(Institution)
                .filter(Institution.ipeds_id == ipeds_id)
                .first()
            )
        except SQLAlchemyError as e:
            logger.error(
                f"Database error getting institution with IPEDS ID {ipeds_id}: {str(e)}"
            )
            raise Exception(f"Database error: {str(e)}")

    def create_institution(self, institution_data: InstitutionCreate) -> Institution:
        """Create a new institution"""
        try:
            # Check if IPEDS ID already exists
            existing = self.get_institution_by_ipeds_id(institution_data.ipeds_id)
            if existing:
                raise ValueError(
                    f"Institution with IPEDS ID {institution_data.ipeds_id} already exists"
                )

            # Create new institution
            db_institution = Institution(**institution_data.model_dump())

            self.db.add(db_institution)
            self.db.commit()
            self.db.refresh(db_institution)

            logger.info(
                f"Successfully created institution: {db_institution.name} (ID: {db_institution.id})"
            )
            return db_institution

        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Integrity error creating institution: {str(e)}")
            raise ValueError("Institution with this IPEDS ID already exists")
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error creating institution: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

    def update_institution(
        self, institution_id: int, update_data: InstitutionUpdate
    ) -> Optional[Institution]:
        """Update an existing institution"""
        try:
            institution = self.get_institution_by_id(institution_id)
            if not institution:
                return None

            # Update only provided fields
            update_dict = update_data.model_dump(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(institution, field, value)

            self.db.commit()
            self.db.refresh(institution)

            logger.info(
                f"Successfully updated institution: {institution.name} (ID: {institution.id})"
            )
            return institution

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(
                f"Database error updating institution {institution_id}: {str(e)}"
            )
            raise Exception(f"Database error: {str(e)}")

    def delete_institution(self, institution_id: int) -> bool:
        """Delete an institution"""
        try:
            institution = self.get_institution_by_id(institution_id)
            if not institution:
                return False

            self.db.delete(institution)
            self.db.commit()

            logger.info(f"Successfully deleted institution ID: {institution_id}")
            return True

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(
                f"Database error deleting institution {institution_id}: {str(e)}"
            )
            raise Exception(f"Database error: {str(e)}")

    def search_institutions(
        self, search_params: InstitutionSearch, page: int = 1, per_page: int = 50
    ) -> Tuple[List[Institution], int]:
        """Search institutions with filters and pagination"""
        try:
            query = self.db.query(Institution)

            # Apply search filters
            if search_params.name:
                query = query.filter(Institution.name.ilike(f"%{search_params.name}%"))

            if search_params.state:
                query = query.filter(Institution.state == search_params.state.upper())

            if search_params.city:
                query = query.filter(Institution.city.ilike(f"%{search_params.city}%"))

            if search_params.region:
                query = query.filter(Institution.region == search_params.region)

            if search_params.control_type:
                query = query.filter(
                    Institution.control_type == search_params.control_type
                )

            if search_params.size_category:
                query = query.filter(
                    Institution.size_category == search_params.size_category
                )

            # Get total count before pagination
            total = query.count()

            # Apply pagination
            offset = (page - 1) * per_page
            institutions = query.offset(offset).limit(per_page).all()

            return institutions, total

        except SQLAlchemyError as e:
            logger.error(f"Database error searching institutions: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

    def get_institutions_by_state(self, state: str) -> List[Institution]:
        """Get all institutions in a specific state"""
        try:
            return (
                self.db.query(Institution)
                .filter(Institution.state == state.upper())
                .order_by(Institution.name)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(
                f"Database error getting institutions for state {state}: {str(e)}"
            )
            raise Exception(f"Database error: {str(e)}")

    def get_institutions_by_region(self, region: USRegion) -> List[Institution]:
        """Get all institutions in a specific region"""
        try:
            return (
                self.db.query(Institution)
                .filter(Institution.region == region)
                .order_by(Institution.state, Institution.name)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(
                f"Database error getting institutions for region {region}: {str(e)}"
            )
            raise Exception(f"Database error: {str(e)}")

    def get_public_institutions(self) -> List[Institution]:
        """Get all public institutions"""
        try:
            return (
                self.db.query(Institution)
                .filter(Institution.control_type == ControlType.PUBLIC)
                .order_by(Institution.state, Institution.name)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error getting public institutions: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

    def get_private_institutions(self) -> List[Institution]:
        """Get all private institutions (both nonprofit and for-profit)"""
        try:
            return (
                self.db.query(Institution)
                .filter(
                    or_(
                        Institution.control_type == ControlType.PRIVATE_NONPROFIT,
                        Institution.control_type == ControlType.PRIVATE_FOR_PROFIT,
                    )
                )
                .order_by(Institution.state, Institution.name)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error getting private institutions: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

    def get_stats(self) -> dict:
        """Get institution statistics"""
        try:
            total = self.db.query(Institution).count()

            # Count by control type
            control_stats = (
                self.db.query(Institution.control_type, func.count(Institution.id))
                .group_by(Institution.control_type)
                .all()
            )

            # Count by size category
            size_stats = (
                self.db.query(Institution.size_category, func.count(Institution.id))
                .group_by(Institution.size_category)
                .all()
            )

            # Count by region
            region_stats = (
                self.db.query(Institution.region, func.count(Institution.id))
                .group_by(Institution.region)
                .all()
            )

            return {
                "total_institutions": total,
                "by_control_type": {str(ct): count for ct, count in control_stats},
                "by_size_category": {str(sc): count for sc, count in size_stats if sc},
                "by_region": {str(r): count for r, count in region_stats if r},
            }

        except SQLAlchemyError as e:
            logger.error(f"Database error getting institution stats: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

    def bulk_create_institutions(
        self, institutions_data: List[InstitutionCreate]
    ) -> Tuple[int, int, List[str]]:
        """
        Bulk create institutions from a list
        Returns: (successful_count, failed_count, error_messages)
        """
        successful = 0
        failed = 0
        errors = []

        for i, institution_data in enumerate(institutions_data):
            try:
                self.create_institution(institution_data)
                successful += 1
            except Exception as e:
                failed += 1
                errors.append(f"Row {i+1}: {str(e)}")
                logger.error(
                    f"Failed to create institution {institution_data.name}: {str(e)}"
                )

        logger.info(f"Bulk create completed: {successful} successful, {failed} failed")
        return successful, failed, errors
