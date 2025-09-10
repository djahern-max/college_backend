# app/services/s2023_is.py
from sqlalchemy.orm import Session
from app.models.s2023_is import S2023_IS
from typing import Optional, List
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class S2023_ISService:
    """Service for S2023_IS operations"""

    @staticmethod
    def get_by_unitid(db: Session, unitid: str) -> Optional[S2023_IS]:
        """Get S2023_IS metrics for a specific institution"""
        return db.query(S2023_IS).filter(S2023_IS.unitid == unitid).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[S2023_IS]:
        """Get all S2023_IS metrics with pagination"""
        return db.query(S2023_IS).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_diversity_category(db: Session, category: str) -> List[S2023_IS]:
        """Get institutions by diversity category"""
        return db.query(S2023_IS).filter(S2023_IS.diversity_category == category).all()

    @staticmethod
    def get_by_size_category(db: Session, category: str) -> List[S2023_IS]:
        """Get institutions by faculty size category"""
        return (
            db.query(S2023_IS).filter(S2023_IS.faculty_size_category == category).all()
        )

    @staticmethod
    def search_institutions(
        db: Session,
        min_faculty: Optional[int] = None,
        max_faculty: Optional[int] = None,
        diversity_categories: Optional[List[str]] = None,
        size_categories: Optional[List[str]] = None,
        min_female_percent: Optional[float] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[S2023_IS]:
        """Advanced search for institutions based on S2023_IS criteria"""
        query = db.query(S2023_IS)

        if min_faculty is not None:
            query = query.filter(S2023_IS.total_faculty >= min_faculty)

        if max_faculty is not None:
            query = query.filter(S2023_IS.total_faculty <= max_faculty)

        if diversity_categories:
            query = query.filter(S2023_IS.diversity_category.in_(diversity_categories))

        if size_categories:
            query = query.filter(S2023_IS.faculty_size_category.in_(size_categories))

        if min_female_percent is not None:
            query = query.filter(S2023_IS.female_faculty_percent >= min_female_percent)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def bulk_import_from_csv(db: Session, csv_file_path: str) -> int:
        """Import S2023_IS data from CSV file"""
        try:
            # Read CSV
            df = pd.read_csv(csv_file_path)
            logger.info(f"Loading {len(df)} S2023_IS records from CSV")

            # Clear existing data
            db.query(S2023_IS).delete()

            # Convert DataFrame to model instances
            records_created = 0
            for _, row in df.iterrows():
                s2023_is_record = S2023_IS(
                    unitid=str(row["UNITID"]),
                    total_faculty=int(row["total_faculty"]),
                    female_faculty_percent=float(row["female_faculty_percent"]),
                    male_faculty_percent=float(row["male_faculty_percent"]),
                    diversity_category=str(row["diversity_category"]),
                    faculty_size_category=str(row["faculty_size_category"]),
                    faculty_description=str(row["faculty_description"]),
                    diversity_index=float(row["diversity_index"]),
                    asian_faculty_percent=float(row["asian_faculty_percent"]),
                    black_faculty_percent=float(row["black_faculty_percent"]),
                    hispanic_faculty_percent=float(row["hispanic_faculty_percent"]),
                    white_faculty_percent=float(row["white_faculty_percent"]),
                )
                db.add(s2023_is_record)
                records_created += 1

            db.commit()
            logger.info(f"Successfully imported {records_created} S2023_IS records")
            return records_created

        except Exception as e:
            db.rollback()
            logger.error(f"Error importing S2023_IS data: {e}")
            raise e

    @staticmethod
    def get_diversity_stats(db: Session) -> dict:
        """Get aggregated diversity statistics"""
        total_institutions = db.query(S2023_IS).count()

        diversity_breakdown = (
            db.query(S2023_IS.diversity_category, db.func.count(S2023_IS.id))
            .group_by(S2023_IS.diversity_category)
            .all()
        )

        size_breakdown = (
            db.query(S2023_IS.faculty_size_category, db.func.count(S2023_IS.id))
            .group_by(S2023_IS.faculty_size_category)
            .all()
        )

        return {
            "total_institutions": total_institutions,
            "diversity_breakdown": {
                category: count for category, count in diversity_breakdown
            },
            "size_breakdown": {category: count for category, count in size_breakdown},
        }
