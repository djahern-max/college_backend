# app/services/admissions.py
"""
Service layer for admissions data operations
"""

from sqlalchemy.orm import Session
from app.models.admissions import AdmissionsData
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class AdmissionsService:
    """Service class for admissions data operations"""

    @staticmethod
    def get_latest_by_ipeds(db: Session, ipeds_id: int) -> Optional[AdmissionsData]:
        """
        Get the most recent admissions data for an institution.

        Args:
            db: Database session
            ipeds_id: IPEDS institution identifier

        Returns:
            Most recent AdmissionsData or None if not found
        """
        try:
            return (
                db.query(AdmissionsData)
                .filter(AdmissionsData.ipeds_id == ipeds_id)
                .order_by(AdmissionsData.academic_year.desc())
                .first()
            )
        except Exception as e:
            logger.error(
                f"Error fetching latest admissions for IPEDS {ipeds_id}: {str(e)}"
            )
            raise

    @staticmethod
    def get_all_by_ipeds(db: Session, ipeds_id: int) -> List[AdmissionsData]:
        """
        Get all admissions data (all years) for an institution.

        Useful for historical analysis and trending.

        Args:
            db: Database session
            ipeds_id: IPEDS institution identifier

        Returns:
            List of AdmissionsData ordered by year (most recent first)
        """
        try:
            return (
                db.query(AdmissionsData)
                .filter(AdmissionsData.ipeds_id == ipeds_id)
                .order_by(AdmissionsData.academic_year.desc())
                .all()
            )
        except Exception as e:
            logger.error(
                f"Error fetching all admissions for IPEDS {ipeds_id}: {str(e)}"
            )
            raise

    @staticmethod
    def get_by_academic_year(
        db: Session, ipeds_id: int, academic_year: str
    ) -> Optional[AdmissionsData]:
        """
        Get admissions data for a specific academic year.

        Args:
            db: Database session
            ipeds_id: IPEDS institution identifier
            academic_year: Academic year (e.g., "2023-24")

        Returns:
            AdmissionsData or None if not found
        """
        try:
            return (
                db.query(AdmissionsData)
                .filter(
                    AdmissionsData.ipeds_id == ipeds_id,
                    AdmissionsData.academic_year == academic_year,
                )
                .first()
            )
        except Exception as e:
            logger.error(
                f"Error fetching admissions for IPEDS {ipeds_id}, year {academic_year}: {str(e)}"
            )
            raise
