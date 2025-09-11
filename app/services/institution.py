# app/services/institution.py - FIXED SQL syntax for customer_rank ordering

from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, desc
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging
from datetime import datetime

from app.models.institution import Institution, ImageExtractionStatus
from app.schemas.institution import (
    InstitutionCreate,
    InstitutionUpdate,
    InstitutionSearch,
    ImageUpdateRequest,
    InstitutionImageStats,
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

            # If image fields are being updated, update the extraction date
            image_fields = {
                "primary_image_url",
                "primary_image_quality_score",
                "logo_image_url",
                "image_extraction_status",
            }
            if any(field in update_dict for field in image_fields):
                institution.image_extraction_date = datetime.utcnow()

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

    def update_institution_images(
        self, institution_id: int, image_data: ImageUpdateRequest
    ) -> Optional[Institution]:
        """Update institution image information"""
        try:
            institution = self.get_institution_by_id(institution_id)
            if not institution:
                return None

            # Update image info using the model method
            institution.update_image_info(
                image_url=image_data.primary_image_url,
                quality_score=image_data.primary_image_quality_score,
                logo_url=image_data.logo_image_url,
                status=image_data.image_extraction_status,
            )

            self.db.commit()
            self.db.refresh(institution)

            logger.info(
                f"Successfully updated images for institution: {institution.name} (Score: {image_data.primary_image_quality_score})"
            )
            return institution

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(
                f"Database error updating institution images {institution_id}: {str(e)}"
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

            # Apply generic search query (searches across name, city, state)
            if search_params.query:
                search_term = f"%{search_params.query}%"
                query = query.filter(
                    or_(
                        Institution.name.ilike(search_term),
                        Institution.city.ilike(search_term),
                        Institution.state.ilike(search_term),
                    )
                )

            # Apply specific field filters (for advanced filtering)
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

            # Image-based filters
            if search_params.min_image_quality is not None:
                query = query.filter(
                    Institution.primary_image_quality_score
                    >= search_params.min_image_quality
                )

            if search_params.has_image is not None:
                if search_params.has_image:
                    query = query.filter(Institution.primary_image_url.isnot(None))
                else:
                    query = query.filter(Institution.primary_image_url.is_(None))

            if search_params.image_status:
                query = query.filter(
                    Institution.image_extraction_status == search_params.image_status
                )

            # Simple ordering - just use customer rank and name
            query = query.order_by(
                desc(Institution.customer_rank).nulls_last(),
                desc(Institution.primary_image_quality_score).nulls_last(),
                Institution.name,
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

    def get_institutions_by_customer_priority(
        self, limit: int = 50, offset: int = 0
    ) -> List[Institution]:
        """Get institutions ordered by customer ranking (for admin/advertising management)"""
        try:
            return (
                self.db.query(Institution)
                .order_by(
                    desc(Institution.customer_rank).nulls_last(),
                    desc(Institution.primary_image_quality_score).nulls_last(),
                    Institution.name,
                )
                .offset(offset)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error getting institutions by priority: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

    def update_customer_rank(
        self, institution_id: int, new_rank: int
    ) -> Optional[Institution]:
        """Update customer ranking for an institution (when they change advertising tier)"""
        try:
            institution = self.get_institution_by_id(institution_id)
            if not institution:
                return None

            institution.customer_rank = new_rank
            self.db.commit()
            self.db.refresh(institution)

            logger.info(f"Updated customer rank for {institution.name}: {new_rank}")
            return institution

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(
                f"Database error updating customer rank for institution {institution_id}: {str(e)}"
            )
            raise Exception(f"Database error: {str(e)}")

    def get_institutions_by_image_quality(
        self, min_score: int = 60, limit: int = 50
    ) -> List[Institution]:
        """Get institutions ordered by customer_rank first, then image quality"""
        try:
            return (
                self.db.query(Institution)
                .filter(Institution.primary_image_quality_score >= min_score)
                .order_by(
                    desc(Institution.customer_rank).nulls_last(),
                    desc(Institution.primary_image_quality_score).nulls_last(),
                    Institution.name,
                )
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(
                f"Database error getting institutions by image quality: {str(e)}"
            )
            raise Exception(f"Database error: {str(e)}")

    def get_institutions_needing_image_review(self) -> List[Institution]:
        """Get institutions that need manual image review"""
        try:
            return Institution.get_needing_image_review(self.db)
        except SQLAlchemyError as e:
            logger.error(
                f"Database error getting institutions needing review: {str(e)}"
            )
            raise Exception(f"Database error: {str(e)}")

    def get_institutions_by_state(self, state: str) -> List[Institution]:
        """Get all institutions in a specific state - UPDATED to use customer_rank first"""
        try:
            return (
                self.db.query(Institution)
                .filter(Institution.state == state.upper())
                .order_by(
                    desc(Institution.customer_rank).nulls_last(),
                    desc(Institution.primary_image_quality_score).nulls_last(),
                    Institution.name,
                )
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(
                f"Database error getting institutions for state {state}: {str(e)}"
            )
            raise Exception(f"Database error: {str(e)}")

    def get_institutions_by_region(self, region: USRegion) -> List[Institution]:
        """Get all institutions in a specific region - UPDATED to use customer_rank first"""
        try:
            return (
                self.db.query(Institution)
                .filter(Institution.region == region)
                .order_by(
                    desc(Institution.customer_rank).nulls_last(),
                    desc(Institution.primary_image_quality_score).nulls_last(),
                    Institution.state,
                    Institution.name,
                )
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(
                f"Database error getting institutions for region {region}: {str(e)}"
            )
            raise Exception(f"Database error: {str(e)}")

    def get_public_institutions(self) -> List[Institution]:
        """Get all public institutions - UPDATED to use customer_rank first"""
        try:
            return (
                self.db.query(Institution)
                .filter(Institution.control_type == ControlType.PUBLIC)
                .order_by(
                    desc(Institution.customer_rank).nulls_last(),
                    desc(Institution.primary_image_quality_score).nulls_last(),
                    Institution.state,
                    Institution.name,
                )
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error getting public institutions: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

    def get_private_institutions(self) -> List[Institution]:
        """Get all private institutions (both nonprofit and for-profit) - UPDATED to use customer_rank first"""
        try:
            return (
                self.db.query(Institution)
                .filter(
                    or_(
                        Institution.control_type == ControlType.PRIVATE_NONPROFIT,
                        Institution.control_type == ControlType.PRIVATE_FOR_PROFIT,
                    )
                )
                .order_by(
                    desc(Institution.customer_rank).nulls_last(),
                    desc(Institution.primary_image_quality_score).nulls_last(),
                    Institution.state,
                    Institution.name,
                )
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error getting private institutions: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

    def get_image_stats(self) -> InstitutionImageStats:
        """Get institution image statistics"""
        try:
            total = self.db.query(Institution).count()

            # Count institutions with images
            with_images = (
                self.db.query(Institution)
                .filter(Institution.primary_image_url.isnot(None))
                .count()
            )

            # Count by quality thresholds
            with_high_quality = (
                self.db.query(Institution)
                .filter(Institution.primary_image_quality_score >= 80)
                .count()
            )

            with_good_quality = (
                self.db.query(Institution)
                .filter(Institution.primary_image_quality_score >= 60)
                .count()
            )

            # Count needing review
            needs_review = (
                self.db.query(Institution)
                .filter(
                    or_(
                        Institution.image_extraction_status
                        == ImageExtractionStatus.FAILED,
                        Institution.image_extraction_status
                        == ImageExtractionStatus.NEEDS_REVIEW,
                        Institution.primary_image_quality_score < 40,
                    )
                )
                .count()
            )

            # Count by status
            status_stats = (
                self.db.query(
                    Institution.image_extraction_status, func.count(Institution.id)
                )
                .group_by(Institution.image_extraction_status)
                .all()
            )

            # Average quality score
            avg_quality = (
                self.db.query(func.avg(Institution.primary_image_quality_score))
                .filter(Institution.primary_image_quality_score.isnot(None))
                .scalar()
            )

            return InstitutionImageStats(
                total_institutions=total,
                with_images=with_images,
                with_high_quality_images=with_high_quality,
                with_good_images=with_good_quality,
                needs_review=needs_review,
                by_status={
                    str(status): count for status, count in status_stats if status
                },
                avg_quality_score=float(avg_quality) if avg_quality else None,
            )

        except SQLAlchemyError as e:
            logger.error(f"Database error getting image stats: {str(e)}")
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

    def bulk_update_institution_images(
        self, image_updates: List[Tuple[int, ImageUpdateRequest]]
    ) -> Tuple[int, int, List[str]]:
        """
        Bulk update institution images from a list of (ipeds_id, image_data) tuples
        Returns: (successful_count, failed_count, error_messages)
        """
        successful = 0
        failed = 0
        errors = []

        for i, (ipeds_id, image_data) in enumerate(image_updates):
            try:
                institution = self.get_institution_by_ipeds_id(ipeds_id)
                if not institution:
                    failed += 1
                    errors.append(
                        f"Update {i+1}: Institution with IPEDS ID {ipeds_id} not found"
                    )
                    continue

                self.update_institution_images(institution.id, image_data)
                successful += 1

            except Exception as e:
                failed += 1
                errors.append(f"Update {i+1} (IPEDS ID {ipeds_id}): {str(e)}")
                logger.error(
                    f"Failed to update images for IPEDS ID {ipeds_id}: {str(e)}"
                )

        logger.info(
            f"Bulk image update completed: {successful} successful, {failed} failed"
        )
        return successful, failed, errors

    def get_featured_institutions(
        self, limit: int = 20, offset: int = 0
    ) -> List[Institution]:
        """Get featured institutions with best images and pagination support"""
        try:
            return (
                self.db.query(Institution)
                .filter(
                    and_(
                        Institution.primary_image_url.isnot(None),
                        Institution.primary_image_quality_score
                        >= 60,  # Good quality threshold
                    )
                )
                .order_by(
                    desc(Institution.customer_rank).nulls_last(),
                    desc(Institution.primary_image_quality_score).nulls_last(),
                    Institution.name,
                )
                .offset(offset)  # THIS IS KEY FOR PAGINATION
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error getting featured institutions: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

    def mark_institution_for_image_review(
        self, institution_id: int, reason: str = None
    ) -> bool:
        """Mark an institution for manual image review"""
        try:
            institution = self.get_institution_by_id(institution_id)
            if not institution:
                return False

            institution.image_extraction_status = ImageExtractionStatus.NEEDS_REVIEW
            institution.image_extraction_date = datetime.utcnow()

            self.db.commit()

            logger.info(
                f"Marked institution {institution.name} for image review. Reason: {reason}"
            )
            return True

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error marking institution for review: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

    def reset_image_extraction_status(
        self, status_to_reset: ImageExtractionStatus = ImageExtractionStatus.FAILED
    ) -> int:
        """Reset image extraction status for institutions (useful for re-processing)"""
        try:
            count = (
                self.db.query(Institution)
                .filter(Institution.image_extraction_status == status_to_reset)
                .update(
                    {Institution.image_extraction_status: ImageExtractionStatus.PENDING}
                )
            )

            self.db.commit()

            logger.info(f"Reset {count} institutions from {status_to_reset} to PENDING")
            return count

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error resetting image status: {str(e)}")
            raise Exception(f"Database error: {str(e)}")
