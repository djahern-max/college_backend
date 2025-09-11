#!/usr/bin/env python3
"""
Import Step2 Financial Data Script for MagicScholar

Imports the step2_financial_data.csv into the database
following the same pattern as the S2023_IS import
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from sqlalchemy.orm import Session
import logging
from typing import Dict, Any, Optional

# Add app directory to path - adjust for your project structure
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.append(str(project_root))

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.step2_ic2023_ay import Step2_IC2023_AY
from app.models.institution import Institution

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Step2FinancialDataImporter:
    """Import Step2 financial data into MagicScholar database"""

    def __init__(self, db: Session):
        self.db = db
        self.import_stats = {
            "total_rows": 0,
            "successful_imports": 0,
            "skipped": 0,
            "errors": 0,
            "updated": 0,
            "error_details": [],
        }

    def import_from_csv(self, csv_path: str) -> Dict[str, Any]:
        """Import step2 financial data from CSV"""

        logger.info(f"Starting Step2 financial data import from {csv_path}")

        try:
            # Load the CSV
            df = pd.read_csv(csv_path)
            self.import_stats["total_rows"] = len(df)

            logger.info(f"Loaded {len(df)} rows from CSV")
            logger.info(f"Columns: {list(df.columns)}")

            # Process each row
            for index, row in df.iterrows():
                try:
                    financial_data = self._process_row(row)
                    if financial_data:
                        self._create_or_update_financial_record(financial_data)
                        self.import_stats["successful_imports"] += 1
                    else:
                        self.import_stats["skipped"] += 1

                    # Log progress every 100 rows
                    if (index + 1) % 100 == 0:
                        logger.info(f"Processed {index + 1}/{len(df)} rows")

                except Exception as e:
                    error_msg = f"Row {index + 1}: {str(e)}"
                    self.import_stats["errors"] += 1
                    self.import_stats["error_details"].append(error_msg)
                    logger.error(error_msg)

            # Commit all changes
            self.db.commit()
            logger.info("All changes committed to database")

            return self.import_stats

        except Exception as e:
            logger.error(f"Failed to import Step2 financial data: {e}")
            self.db.rollback()
            return {"error": str(e)}

    def _process_row(self, row: pd.Series) -> Optional[Dict[str, Any]]:
        """Process a single row from the CSV"""

        ipeds_id = row.get("ipeds_id")
        if pd.isna(ipeds_id) or ipeds_id <= 0:
            return None

        # Check if institution exists
        institution = (
            self.db.query(Institution)
            .filter(Institution.ipeds_id == int(ipeds_id))
            .first()
        )

        if not institution:
            logger.warning(f"Institution {ipeds_id} not found, skipping financial data")
            return None

        # Convert pandas values to Python types, handling NaN
        def safe_float(value):
            """Safely convert value to float, returning None for NaN"""
            if pd.isna(value) or value == "" or value == ".":
                return None
            try:
                return float(value)
            except (ValueError, TypeError):
                return None

        def safe_int(value):
            """Safely convert value to int, returning None for NaN"""
            if pd.isna(value) or value == "" or value == ".":
                return None
            try:
                return int(value)
            except (ValueError, TypeError):
                return None

        def safe_bool(value):
            """Safely convert value to bool"""
            if pd.isna(value):
                return False
            return bool(value)

        def safe_str(value):
            """Safely convert value to string, returning None for NaN"""
            if pd.isna(value) or value == "" or value == ".":
                return None
            return str(value).strip()

        # Process financial data
        financial_data = {
            "ipeds_id": int(ipeds_id),
            "academic_year": safe_str(row.get("academic_year")) or "2023-24",
            "data_source": safe_str(row.get("data_source")) or "IC2023_AY",
            "tuition_in_state": safe_float(row.get("tuition_in_state")),
            "tuition_out_state": safe_float(row.get("tuition_out_state")),
            "required_fees": safe_float(row.get("required_fees")),
            "tuition_fees_in_state": safe_float(row.get("tuition_fees_in_state")),
            "tuition_fees_out_state": safe_float(row.get("tuition_fees_out_state")),
            "room_board_on_campus": safe_float(row.get("room_board_on_campus")),
            "room_board_off_campus": safe_float(row.get("room_board_off_campus")),
            "books_supplies": safe_float(row.get("books_supplies")),
            "personal_expenses": safe_float(row.get("personal_expenses")),
            "transportation": safe_float(row.get("transportation")),
            "has_tuition_data": safe_bool(row.get("has_tuition_data")),
            "has_fees_data": safe_bool(row.get("has_fees_data")),
            "data_completeness_score": safe_int(row.get("data_completeness_score"))
            or 0,
            "validation_issues": safe_str(row.get("validation_issues")),
            "validation_status": safe_str(row.get("validation_status")) or "pending",
        }

        return financial_data

    def _create_or_update_financial_record(
        self, financial_data: Dict[str, Any]
    ) -> None:
        """Create or update a financial record in the database"""

        ipeds_id = financial_data["ipeds_id"]

        # Check if record already exists
        existing_record = (
            self.db.query(Step2_IC2023_AY)
            .filter(Step2_IC2023_AY.ipeds_id == ipeds_id)
            .first()
        )

        if existing_record:
            # Update existing record
            for key, value in financial_data.items():
                if key != "ipeds_id":  # Don't update the ID
                    setattr(existing_record, key, value)

            self.import_stats["updated"] += 1
            logger.debug(f"Updated financial data for IPEDS ID: {ipeds_id}")
        else:
            # Create new record
            new_record = Step2_IC2023_AY(**financial_data)
            self.db.add(new_record)
            logger.debug(f"Created financial data for IPEDS ID: {ipeds_id}")

    def generate_summary_report(self) -> None:
        """Generate a summary report of the import"""
        logger.info("\n" + "=" * 60)
        logger.info("STEP2 FINANCIAL DATA IMPORT SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total rows processed: {self.import_stats['total_rows']:,}")
        logger.info(f"Successful imports: {self.import_stats['successful_imports']:,}")
        logger.info(f"Updated records: {self.import_stats['updated']:,}")
        logger.info(f"Skipped: {self.import_stats['skipped']:,}")
        logger.info(f"Errors: {self.import_stats['errors']:,}")

        if self.import_stats["error_details"]:
            logger.info(f"\nFirst 5 errors:")
            for error in self.import_stats["error_details"][:5]:
                logger.info(f"  - {error}")

        # Query database for verification
        total_financial_records = self.db.query(Step2_IC2023_AY).count()
        records_with_tuition = (
            self.db.query(Step2_IC2023_AY)
            .filter(Step2_IC2023_AY.tuition_in_state.isnot(None))
            .count()
        )

        logger.info(f"\nDatabase verification:")
        logger.info(f"Total financial records in database: {total_financial_records:,}")
        logger.info(f"Records with tuition data: {records_with_tuition:,}")
        logger.info("=" * 60)


def main():
    """Main import function"""
    import argparse

    parser = argparse.ArgumentParser(description="Import Step2 financial data")
    parser.add_argument(
        "--csv-path", required=True, help="Path to step2_financial_data.csv file"
    )

    args = parser.parse_args()

    # Verify file exists
    csv_path = Path(args.csv_path)
    if not csv_path.exists():
        logger.error(f"CSV file not found: {csv_path}")
        return

    # Create database session
    db = SessionLocal()

    try:
        importer = Step2FinancialDataImporter(db)

        # Import the data
        results = importer.import_from_csv(str(csv_path))

        # Generate summary
        importer.generate_summary_report()

        if "error" in results:
            logger.error(f"Import failed: {results['error']}")
        else:
            logger.info("Import completed successfully!")

    except Exception as e:
        logger.error(f"Import failed with exception: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
