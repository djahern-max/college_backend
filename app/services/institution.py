# app/services/institution.py - MODIFIED for New Hampshire focus

from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, desc, exists
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
    """Service class for institution CRUD operations - NEW HAMPSHIRE FOCUSED"""

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

    def _build_base_query_nh_with_tuition_filter(self):
        """Build base query for NEW HAMPSHIRE institutions with tuition data"""
        from app.models.tuition import TuitionData

        print(
            "DEBUG: Using NH + tuition filter - limiting to NH institutions with tuition data"
        )

        query = self.db.query(Institution).filter(
            and_(
                Institution.state == "NH",  # NEW HAMPSHIRE FILTER
                exists().where(
                    and_(
                        TuitionData.ipeds_id == Institution.ipeds_id,
                        TuitionData.has_tuition_data == True,
                    )
                ),
            )
        )

        # Debug count
        count = query.count()
        print(f"DEBUG: NH filtered query returns {count} institutions")

        return query

    def _build_base_query_with_tuition_filter(self):
        """Build base query that only includes institutions with tuition data"""
        from app.models.tuition import TuitionData

        print("DEBUG: Using tuition filter - should limit to 1,018 institutions")

        query = self.db.query(Institution).filter(
            exists().where(
                and_(
                    TuitionData.ipeds_id == Institution.ipeds_id,
                    TuitionData.has_tuition_data == True,
                )
            )
        )

        # Debug count
        count = query.count()
        print(f"DEBUG: Filtered query returns {count} institutions")

        return query

    def get_institutions_with_financial_data(
        self, limit: int = 50, offset: int = 0, nh_only: bool = True
    ) -> List[dict]:
        """Get institutions ordered by customer_rank first, then financial data richness"""
        try:
            from app.models.tuition import TuitionData

            # Choose base query based on nh_only flag
            base_query = self.db.query(Institution)
            if nh_only:
                base_query = base_query.filter(Institution.state == "NH")

            # Query with JOIN to get financial data
            results = (
                base_query.add_columns(
                    TuitionData.tuition_in_state,
                    TuitionData.tuition_out_state,
                    TuitionData.tuition_fees_in_state,
                    TuitionData.room_board_on_campus,
                    TuitionData.data_completeness_score,
                    # Calculate data richness score
                    func.coalesce(TuitionData.data_completeness_score, 0).label(
                        "base_score"
                    ),
                )
                .join(TuitionData, Institution.ipeds_id == TuitionData.ipeds_id)
                .filter(TuitionData.has_tuition_data == True)
                .order_by(
                    desc(Institution.customer_rank).nulls_last(),
                    desc(TuitionData.data_completeness_score).nulls_last(),
                    desc(Institution.primary_image_quality_score).nulls_last(),
                    Institution.name,
                )
                .offset(offset)
                .limit(limit)
                .all()
            )

            # Format results
            institutions_with_data = []
            for result in results:
                institution = result[0]
                inst_dict = {
                    "institution": institution,
                    "tuition_in_state": result[1],
                    "tuition_out_state": result[2],
                    "tuition_fees_in_state": result[3],
                    "room_board_on_campus": result[4],
                    "data_completeness_score": result[5] or 0,
                    "has_rich_financial_data": result[5] is not None
                    and result[5] >= 80,
                }
                institutions_with_data.append(inst_dict)

            return institutions_with_data

        except SQLAlchemyError as e:
            logger.error(
                f"Database error getting institutions with financial data: {str(e)}"
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
        self,
        search_params: InstitutionSearch,
        page: int = 1,
        per_page: int = 50,
        nh_only: bool = True,
    ) -> Tuple[List[Institution], int]:
        """Search institutions with filters and pagination - NH FOCUSED"""
        try:
            # Choose base query based on nh_only flag
            if nh_only:
                query = self._build_base_query_nh_with_tuition_filter()
            else:
                query = self._build_base_query_with_tuition_filter()

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

            # Only apply state filter if not already filtered to NH
            if search_params.state and not nh_only:
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
        self, limit: int = 50, offset: int = 0, nh_only: bool = True
    ) -> List[Institution]:
        """Get institutions ordered by customer ranking (for admin/advertising management)"""
        try:
            if nh_only:
                base_query = self._build_base_query_nh_with_tuition_filter()
            else:
                base_query = self._build_base_query_with_tuition_filter()

            return (
                base_query.order_by(
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
        self, min_score: int = 60, limit: int = 50, nh_only: bool = True
    ) -> List[Institution]:
        """Get institutions ordered by customer_rank first, then image quality"""
        try:
            if nh_only:
                base_query = self._build_base_query_nh_with_tuition_filter()
            else:
                base_query = self._build_base_query_with_tuition_filter()

            return (
                base_query.filter(Institution.primary_image_quality_score >= min_score)
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

    def get_institutions_needing_image_review(
        self, nh_only: bool = True
    ) -> List[Institution]:
        """Get institutions that need manual image review"""
        try:
            if nh_only:
                # For NH only, we need to modify the Institution.get_needing_image_review method
                # or build our own query
                return (
                    self.db.query(Institution)
                    .filter(Institution.state == "NH")
                    .filter(
                        or_(
                            Institution.image_extraction_status
                            == ImageExtractionStatus.FAILED,
                            Institution.image_extraction_status
                            == ImageExtractionStatus.NEEDS_REVIEW,
                            Institution.primary_image_quality_score < 40,
                        )
                    )
                    .order_by(
                        desc(Institution.customer_rank).nulls_last(), Institution.name
                    )
                    .all()
                )
            else:
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

    def get_nh_institutions(self) -> List[Institution]:
        """Get all New Hampshire institutions with tuition data"""
        try:
            return (
                self._build_base_query_nh_with_tuition_filter()
                .order_by(
                    desc(Institution.customer_rank).nulls_last(),
                    desc(Institution.primary_image_quality_score).nulls_last(),
                    Institution.name,
                )
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error getting NH institutions: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

    def get_featured_institutions(
        self, limit: int = 20, offset: int = 0, nh_only: bool = True
    ) -> List[Institution]:
        """Get featured institutions with best images and pagination support"""
        try:
            if nh_only:
                base_query = self._build_base_query_nh_with_tuition_filter()
            else:
                base_query = self._build_base_query_with_tuition_filter()

            return (
                base_query.filter(
                    and_(
                        Institution.primary_image_url.isnot(None),
                        Institution.primary_image_quality_score >= 60,
                    )
                )
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
            logger.error(f"Database error getting featured institutions: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

    # ... (rest of the methods remain the same but can accept nh_only parameter where relevant)

    def get_nh_stats(self) -> dict:
        """Get New Hampshire specific institution statistics"""
        try:
            nh_query = self.db.query(Institution).filter(Institution.state == "NH")
            nh_with_tuition_query = self._build_base_query_nh_with_tuition_filter()

            total_nh = nh_query.count()
            nh_with_tuition = nh_with_tuition_query.count()

            # Count by control type in NH
            control_stats = (
                nh_query.with_entities(
                    Institution.control_type, func.count(Institution.id)
                )
                .group_by(Institution.control_type)
                .all()
            )

            # Count by size category in NH
            size_stats = (
                nh_query.with_entities(
                    Institution.size_category, func.count(Institution.id)
                )
                .group_by(Institution.size_category)
                .all()
            )

            return {
                "state": "New Hampshire",
                "total_institutions": total_nh,
                "institutions_with_tuition_data": nh_with_tuition,
                "tuition_data_coverage": (
                    f"{(nh_with_tuition/total_nh)*100:.1f}%" if total_nh > 0 else "0%"
                ),
                "by_control_type": {str(ct): count for ct, count in control_stats},
                "by_size_category": {str(sc): count for sc, count in size_stats if sc},
            }

        except SQLAlchemyError as e:
            logger.error(f"Database error getting NH institution stats: {str(e)}")
            raise Exception(f"Database error: {str(e)}")
