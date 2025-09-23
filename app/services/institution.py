# app/services/institution.py - STREAMLINED CURATED SCHOOLS SERVICE

from typing import Optional, List, Tuple, Dict
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
    """Streamlined service for curated premium schools business model"""

    # ============================================================================
    # CURATED SCHOOLS CONFIGURATION
    # ============================================================================

    CURATED_SCHOOLS = {
        "NH": [
            183044,  # University of New Hampshire-Main Campus
            182670,  # Dartmouth College
            183026,  # Southern New Hampshire University
            183080,  # Plymouth State University
            183062,  # Keene State College
            183239,  # Saint Anselm College
            182980,  # New England College
            182795,  # Franklin Pierce University
            182634,  # Colby-Sawyer College
            183071,  # University of New Hampshire at Manchester
            182917,  # Magdalen College
            183150,  # Great Bay Community College
        ],
        "MA": [
            166027,  # Harvard University
            166683,  # Massachusetts Institute of Technology
            164988,  # Boston University
            168342,  # Williams College
            164465,  # Amherst College
            168218,  # Wellesley College
            168148,  # Tufts University
            164924,  # Boston College
            167358,  # Northeastern University
            166629,  # University of Massachusetts-Amherst
            165015,  # Brandeis University
            167835,  # Smith College
        ],
    }

    # Premium tiers for business model
    TIER_1_SCHOOLS = [166027, 166683, 182670, 183044, 168342, 164465]  # Ultra premium
    TIER_2_SCHOOLS = [168218, 168148, 164988, 164924, 167358, 183026]  # Premium

    def __init__(self, db: Session):
        self.db = db

    # ============================================================================
    # CORE QUERY BUILDER (single method replaces 3 legacy methods)
    # ============================================================================

    def _build_curated_query(self, states: List[str] = None):
        """Build query for curated schools only"""
        from app.models.tuition import TuitionData

        # Get target schools
        if states is None:
            # All curated schools
            target_ipeds = []
            for schools in self.CURATED_SCHOOLS.values():
                target_ipeds.extend(schools)
        else:
            # Specific states only
            target_ipeds = []
            for state in states:
                if state.upper() in self.CURATED_SCHOOLS:
                    target_ipeds.extend(self.CURATED_SCHOOLS[state.upper()])

        if not target_ipeds:
            return self.db.query(Institution).filter(
                Institution.id == -1
            )  # Empty query

        return self.db.query(Institution).filter(
            and_(
                Institution.ipeds_id.in_(target_ipeds),
                exists().where(
                    and_(
                        TuitionData.ipeds_id == Institution.ipeds_id,
                        TuitionData.has_tuition_data == True,
                    )
                ),
            )
        )

    # ============================================================================
    # ESSENTIAL CRUD METHODS (keep these)
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

    # ============================================================================
    # MAIN API METHODS (what your endpoints actually need)
    # ============================================================================

    def get_featured_institutions(
        self, limit: int = 20, offset: int = 0
    ) -> List[Institution]:
        """Get featured curated institutions"""
        try:
            return (
                self._build_curated_query()
                .filter(
                    and_(
                        Institution.primary_image_url.isnot(None),
                        Institution.primary_image_quality_score >= 60,
                    )
                )
                .order_by(
                    Institution.ipeds_id.in_(
                        self.TIER_1_SCHOOLS
                    ).desc(),  # Premium first
                    Institution.state.asc(),  # NH first, then MA
                    desc(Institution.customer_rank).nulls_last(),
                    Institution.name,
                )
                .offset(offset)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error getting featured institutions: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

    def search_institutions(
        self,
        search_params: InstitutionSearch,
        page: int = 1,
        per_page: int = 50,
    ) -> Tuple[List[Institution], int]:
        """Search within curated institutions"""
        try:
            query = self._build_curated_query()

            # Apply filters
            if search_params.query:
                search_term = f"%{search_params.query}%"
                query = query.filter(
                    or_(
                        Institution.name.ilike(search_term),
                        Institution.city.ilike(search_term),
                        Institution.state.ilike(search_term),
                    )
                )

            if search_params.state:
                # Filter to specific state within curated list
                query = self._build_curated_query([search_params.state])

            if search_params.control_type:
                query = query.filter(
                    Institution.control_type == search_params.control_type
                )

            if search_params.min_image_quality is not None:
                query = query.filter(
                    Institution.primary_image_quality_score
                    >= search_params.min_image_quality
                )

            # Order by premium status
            query = query.order_by(
                Institution.ipeds_id.in_(self.TIER_1_SCHOOLS).desc(),
                Institution.state.asc(),
                desc(Institution.customer_rank).nulls_last(),
                Institution.name,
            )

            total = query.count()
            offset = (page - 1) * per_page
            institutions = query.offset(offset).limit(per_page).all()

            return institutions, total

        except SQLAlchemyError as e:
            logger.error(f"Database error searching institutions: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

    # ============================================================================
    # BUSINESS MODEL METHODS
    # ============================================================================

    def get_schools_by_state(self, state: str) -> List[Institution]:
        """Get curated schools for specific state"""
        return (
            self._build_curated_query([state])
            .order_by(
                Institution.ipeds_id.in_(self.TIER_1_SCHOOLS).desc(),
                desc(Institution.customer_rank).nulls_last(),
                Institution.name,
            )
            .all()
        )

    def is_school_curated(self, ipeds_id: int) -> bool:
        """Check if school is in curated list"""
        for schools in self.CURATED_SCHOOLS.values():
            if ipeds_id in schools:
                return True
        return False

    def get_available_states(self) -> List[Dict]:
        """Get states for frontend filter buttons"""
        states = []
        for state_code, schools in self.CURATED_SCHOOLS.items():
            states.append(
                {
                    "code": state_code,
                    "name": self._get_state_name(state_code),
                    "school_count": len(schools),
                    "available": True,
                }
            )

        # Coming soon states
        for state_code in ["CT", "VT", "RI", "ME"]:
            states.append(
                {
                    "code": state_code,
                    "name": self._get_state_name(state_code),
                    "school_count": 0,
                    "available": False,
                }
            )

        return states

    def _get_state_name(self, state_code: str) -> str:
        """Convert state code to name"""
        names = {
            "NH": "New Hampshire",
            "MA": "Massachusetts",
            "CT": "Connecticut",
            "VT": "Vermont",
            "RI": "Rhode Island",
            "ME": "Maine",
        }
        return names.get(state_code, state_code)

    def get_curated_stats(self) -> Dict:
        """Get business stats"""
        try:
            from app.models.tuition import TuitionData

            total_curated = sum(
                len(schools) for schools in self.CURATED_SCHOOLS.values()
            )
            all_ipeds = []
            for schools in self.CURATED_SCHOOLS.values():
                all_ipeds.extend(schools)

            with_data = (
                self.db.query(TuitionData)
                .filter(
                    and_(
                        TuitionData.ipeds_id.in_(all_ipeds),
                        TuitionData.has_tuition_data == True,
                    )
                )
                .count()
            )

            return {
                "total_curated_schools": total_curated,
                "schools_with_data": with_data,
                "completion_rate": (
                    f"{(with_data/total_curated*100):.1f}%"
                    if total_curated > 0
                    else "0%"
                ),
                "tier_1_count": len(self.TIER_1_SCHOOLS),
                "tier_2_count": len(self.TIER_2_SCHOOLS),
                "states": list(self.CURATED_SCHOOLS.keys()),
            }

        except SQLAlchemyError as e:
            logger.error(f"Database error getting stats: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

    # ============================================================================
    # ADMIN/CUSTOMER MANAGEMENT (only if you need these)
    # ============================================================================

    def update_customer_rank(
        self, institution_id: int, new_rank: int
    ) -> Optional[Institution]:
        """Update customer ranking"""
        try:
            institution = self.get_institution_by_id(institution_id)
            if not institution:
                return None

            institution.customer_rank = new_rank
            self.db.commit()
            self.db.refresh(institution)
            return institution

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error updating customer rank: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

    # ============================================================================
    # LEGACY COMPATIBILITY (temporary - for existing API endpoints)
    # ============================================================================

    def get_institutions_by_customer_priority(
        self, limit: int = 50, offset: int = 0, priority_states_only: bool = True
    ) -> List[Institution]:
        """Legacy method - maps to curated query"""
        return (
            self._build_curated_query()
            .order_by(
                Institution.ipeds_id.in_(self.TIER_1_SCHOOLS).desc(),
                Institution.state.asc(),
                desc(Institution.customer_rank).nulls_last(),
                Institution.name,
            )
            .offset(offset)
            .limit(limit)
            .all()
        )
