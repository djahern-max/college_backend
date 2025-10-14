# app/services/tuition.py
"""
Simplified Tuition Service - Basic CRUD operations for tuition data
"""

from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.models.tuition import TuitionData
from app.schemas.tuition import TuitionDataCreate, TuitionDataUpdate

logger = logging.getLogger(__name__)


class TuitionService:
    """Service class for tuition data operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_ipeds_id(self, ipeds_id: int) -> Optional[TuitionData]:
        """Get most recent tuition data by institution IPEDS ID"""
        return (
            self.db.query(TuitionData)
            .filter(TuitionData.ipeds_id == ipeds_id)
            .order_by(TuitionData.academic_year.desc())
            .first()
        )

    def get_all_by_ipeds_id(self, ipeds_id: int) -> List[TuitionData]:
        """Get all tuition data records for an institution"""
        return (
            self.db.query(TuitionData)
            .filter(TuitionData.ipeds_id == ipeds_id)
            .order_by(TuitionData.academic_year.desc())
            .all()
        )

    def get_by_id(self, tuition_id: int) -> Optional[TuitionData]:
        """Get tuition data by database ID"""
        return self.db.query(TuitionData).filter(TuitionData.id == tuition_id).first()

    def create(self, tuition_data: TuitionDataCreate) -> TuitionData:
        """Create new tuition data record"""
        db_tuition = TuitionData(**tuition_data.model_dump())

        self.db.add(db_tuition)
        self.db.commit()
        self.db.refresh(db_tuition)

        logger.info(f"Created tuition data for IPEDS {db_tuition.ipeds_id}")
        return db_tuition

    def update(
        self, tuition_id: int, update_data: TuitionDataUpdate
    ) -> Optional[TuitionData]:
        """Update tuition data by record ID"""
        db_tuition = self.get_by_id(tuition_id)
        if not db_tuition:
            return None

        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(db_tuition, field, value)

        self.db.commit()
        self.db.refresh(db_tuition)

        logger.info(f"Updated tuition data record {tuition_id}")
        return db_tuition

    def delete(self, tuition_id: int) -> bool:
        """Delete tuition data by record ID"""
        db_tuition = self.get_by_id(tuition_id)
        if not db_tuition:
            return False

        self.db.delete(db_tuition)
        self.db.commit()
        logger.info(f"Deleted tuition data record {tuition_id}")
        return True

    def bulk_create(self, tuition_records: List[TuitionDataCreate]) -> int:
        """Bulk create tuition data records"""
        db_tuitions = []
        for record in tuition_records:
            db_tuition = TuitionData(**record.model_dump())
            db_tuitions.append(db_tuition)

        self.db.add_all(db_tuitions)
        self.db.commit()

        logger.info(f"Bulk created {len(db_tuitions)} tuition records")
        return len(db_tuitions)

    def list_all(
        self, skip: int = 0, limit: int = 100, state: Optional[str] = None
    ) -> List[TuitionData]:
        """List tuition data with optional filters"""
        query = self.db.query(TuitionData)

        if state:
            from app.models.institution import Institution

            query = query.join(
                Institution, TuitionData.ipeds_id == Institution.ipeds_id
            ).filter(Institution.state == state)

        return query.offset(skip).limit(limit).all()

    def count(self, state: Optional[str] = None) -> int:
        """Count total tuition records"""
        query = self.db.query(TuitionData)

        if state:
            from app.models.institution import Institution

            query = query.join(
                Institution, TuitionData.ipeds_id == Institution.ipeds_id
            ).filter(Institution.state == state)

        return query.count()
