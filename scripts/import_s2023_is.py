#!/usr/bin/env python3
"""
Import S2023_IS Data Script
Imports the s2023_is.csv file into the database
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.s2023_is import S2023_ISService
from app.models.s2023_is import S2023_IS
import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def import_s2023_is_data(csv_file_path: str):
    """Import S2023_IS data from CSV file"""

    # Check if file exists
    if not os.path.exists(csv_file_path):
        logger.error(f"CSV file not found: {csv_file_path}")
        return False

    # Create database session
    db = SessionLocal()

    try:
        # Import the data
        records_imported = S2023_ISService.bulk_import_from_csv(db, csv_file_path)
        logger.info(f"Successfully imported {records_imported} S2023_IS records")
        return True

    except Exception as e:
        logger.error(f"Failed to import S2023_IS data: {e}")
        return False

    finally:
        db.close()


def verify_import(db: Session):
    """Verify the import by showing sample records"""
    try:
        total_records = db.query(S2023_IS).count()
        logger.info(f"Total S2023_IS records in database: {total_records}")

        # Show a few sample records
        sample_records = db.query(S2023_IS).limit(5).all()
        logger.info("Sample records:")
        for record in sample_records:
            logger.info(
                f"  UNITID {record.unitid}: {record.total_faculty} faculty, {record.diversity_category} diversity"
            )
            logger.info(f"    Highlights: {record.faculty_highlights}")

        # Show diversity breakdown
        diversity_stats = S2023_ISService.get_diversity_stats(db)
        logger.info(f"Diversity breakdown: {diversity_stats['diversity_breakdown']}")
        logger.info(f"Size breakdown: {diversity_stats['size_breakdown']}")

    except Exception as e:
        logger.error(f"Error during verification: {e}")


def main():
    parser = argparse.ArgumentParser(description="Import S2023_IS data from CSV")
    parser.add_argument(
        "--csv-file", default="data/raw_data/s2023_is.csv", help="Path to the CSV file"
    )
    parser.add_argument(
        "--verify", action="store_true", help="Verify import by showing sample records"
    )

    args = parser.parse_args()

    logger.info(f"Starting S2023_IS import from: {args.csv_file}")

    # Import the data
    success = import_s2023_is_data(args.csv_file)

    if success and args.verify:
        # Verify the import
        db = SessionLocal()
        try:
            verify_import(db)
        finally:
            db.close()

    if success:
        logger.info("S2023_IS import completed successfully!")
    else:
        logger.error("S2023_IS import failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
