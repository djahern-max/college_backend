# scripts/import_tuition_data.py
"""
Script to import magicscholar_financial_data.csv into the tuition_data table
"""

import csv
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.tuition import TuitionData, ValidationStatus
from app.services.tuition import TuitionService

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_float(value: str) -> Optional[float]:
    """Safely parse a string to float, handling empty strings and invalid values"""
    if (
        not value
        or value.strip() == ""
        or value.strip().lower() in ["nan", "null", "none"]
    ):
        return None
    try:
        return float(value.strip())
    except (ValueError, TypeError):
        return None


def parse_bool(value: str) -> bool:
    """Parse string to boolean"""
    if not value or value.strip() == "":
        return False
    return value.strip().lower() in ["true", "1", "yes", "t"]


def parse_int(value: str) -> Optional[int]:
    """Safely parse a string to int"""
    if not value or value.strip() == "":
        return None
    try:
        return int(float(value.strip()))  # Handle cases like "85.0"
    except (ValueError, TypeError):
        return None


def clean_csv_row(row: Dict[str, str]) -> Dict[str, Any]:
    """Clean and convert a CSV row to appropriate data types"""
    return {
        "ipeds_id": int(row["ipeds_id"]) if row["ipeds_id"] else None,
        "academic_year": (
            row["academic_year"].strip() if row["academic_year"] else "2023-24"
        ),
        "data_source": row["data_source"].strip() if row["data_source"] else "IPEDS",
        "tuition_in_state": parse_float(row["tuition_in_state"]),
        "tuition_out_state": parse_float(row["tuition_out_state"]),
        "required_fees_in_state": parse_float(row["required_fees_in_state"]),
        "required_fees_out_state": parse_float(row["required_fees_out_state"]),
        "tuition_fees_in_state": parse_float(row["tuition_fees_in_state"]),
        "tuition_fees_out_state": parse_float(row["tuition_fees_out_state"]),
        "room_board_on_campus": parse_float(row["room_board_on_campus"]),
        "room_board_off_campus": parse_float(row["room_board_off_campus"]),
        "books_supplies": parse_float(row["books_supplies"]),
        "personal_expenses": parse_float(row["personal_expenses"]),
        "transportation": parse_float(row["transportation"]),
        "has_tuition_data": parse_bool(row["has_tuition_data"]),
        "has_fees_data": parse_bool(row["has_fees_data"]),
        "has_living_data": parse_bool(row["has_living_data"]),
        "data_completeness_score": parse_int(row["data_completeness_score"]) or 0,
        "validation_status": (
            ValidationStatus.VALIDATED
            if row["validation_status"] == "validated"
            else ValidationStatus.PENDING
        ),
    }


def calculate_derived_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate derived fields from the raw data"""
    # Calculate tuition + fees if not provided
    if (
        data["tuition_fees_in_state"] is None
        and data["tuition_in_state"]
        and data["required_fees_in_state"]
    ):
        data["tuition_fees_in_state"] = (
            data["tuition_in_state"] + data["required_fees_in_state"]
        )

    if (
        data["tuition_fees_out_state"] is None
        and data["tuition_out_state"]
        and data["required_fees_out_state"]
    ):
        data["tuition_fees_out_state"] = (
            data["tuition_out_state"] + data["required_fees_out_state"]
        )

    # Set default fees if tuition is available but fees are not
    if data["tuition_in_state"] and not data["required_fees_in_state"]:
        data["required_fees_in_state"] = (
            data["tuition_in_state"] * 0.1
        )  # Estimate 10% fees

    if data["tuition_out_state"] and not data["required_fees_out_state"]:
        data["required_fees_out_state"] = (
            data["tuition_out_state"] * 0.1
        )  # Estimate 10% fees

    # Update data availability flags based on actual data
    data["has_tuition_data"] = bool(
        data["tuition_in_state"] or data["tuition_out_state"]
    )
    data["has_fees_data"] = bool(
        data["required_fees_in_state"] or data["required_fees_out_state"]
    )
    data["has_living_data"] = bool(
        data["room_board_on_campus"]
        or data["room_board_off_campus"]
        or data["books_supplies"]
    )

    return data


def import_csv_to_database(csv_file_path: str, batch_size: int = 100):
    """Import CSV data to the database using the TuitionService"""

    if not os.path.exists(csv_file_path):
        logger.error(f"CSV file not found: {csv_file_path}")
        return False

    logger.info(f"Starting import from {csv_file_path}")

    db = SessionLocal()
    try:
        tuition_service = TuitionService(db)

        # Read and process CSV
        batch = []
        total_processed = 0
        total_created = 0
        total_errors = 0

        with open(csv_file_path, "r", encoding="utf-8") as file:
            # Use DictReader to handle headers automatically
            csv_reader = csv.DictReader(file)

            logger.info(f"CSV columns: {csv_reader.fieldnames}")

            for row_num, row in enumerate(csv_reader, 1):
                try:
                    # Clean and convert the row
                    cleaned_data = clean_csv_row(row)

                    # Skip rows without IPEDS ID
                    if not cleaned_data["ipeds_id"]:
                        logger.warning(f"Row {row_num}: Missing IPEDS ID, skipping")
                        continue

                    # Calculate derived fields
                    cleaned_data = calculate_derived_fields(cleaned_data)

                    # Check if record already exists
                    existing = tuition_service.get_by_ipeds_id(cleaned_data["ipeds_id"])
                    if existing:
                        logger.info(
                            f"Row {row_num}: IPEDS {cleaned_data['ipeds_id']} already exists, skipping"
                        )
                        continue

                    # Create TuitionData object
                    tuition_record = TuitionData(**cleaned_data)
                    batch.append(tuition_record)

                    # Process batch when it reaches batch_size
                    if len(batch) >= batch_size:
                        try:
                            db.add_all(batch)
                            db.commit()
                            total_created += len(batch)
                            logger.info(
                                f"Processed batch: {total_created} records created so far"
                            )
                            batch = []
                        except Exception as e:
                            db.rollback()
                            logger.error(
                                f"Error processing batch at row {row_num}: {e}"
                            )
                            total_errors += len(batch)
                            batch = []

                    total_processed += 1

                    # Progress logging
                    if total_processed % 500 == 0:
                        logger.info(f"Processed {total_processed} rows...")

                except Exception as e:
                    logger.error(f"Error processing row {row_num}: {e}")
                    logger.error(f"Row data: {row}")
                    total_errors += 1
                    continue

            # Process remaining batch
            if batch:
                try:
                    db.add_all(batch)
                    db.commit()
                    total_created += len(batch)
                    logger.info(f"Processed final batch: {len(batch)} records")
                except Exception as e:
                    db.rollback()
                    logger.error(f"Error processing final batch: {e}")
                    total_errors += len(batch)

        # Final statistics
        logger.info("=" * 50)
        logger.info("IMPORT SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Total rows processed: {total_processed}")
        logger.info(f"Total records created: {total_created}")
        logger.info(f"Total errors: {total_errors}")
        logger.info(
            f"Success rate: {(total_created/total_processed)*100:.1f}%"
            if total_processed > 0
            else "N/A"
        )

        # Validate the import
        final_count = db.query(TuitionData).count()
        logger.info(f"Final tuition_data table count: {final_count}")

        return True

    except Exception as e:
        logger.error(f"Critical error during import: {e}")
        db.rollback()
        return False

    finally:
        db.close()


def validate_data_quality(db: Session):
    """Run data quality checks after import"""
    logger.info("Running data quality validation...")

    tuition_service = TuitionService(db)

    # Get summary stats
    analytics = tuition_service.get_analytics_summary()

    if "error" not in analytics:
        logger.info("Data Quality Report:")
        logger.info(
            f"- Total institutions: {analytics['dataset_info']['total_institutions']}"
        )
        logger.info(
            f"- With tuition data: {analytics['data_quality_metrics']['with_tuition_data']}"
        )
        logger.info(
            f"- With fees data: {analytics['data_quality_metrics']['with_fees_data']}"
        )
        logger.info(
            f"- With living data: {analytics['data_quality_metrics']['with_living_data']}"
        )
        logger.info(
            f"- Comprehensive data: {analytics['data_quality_metrics']['comprehensive_data']}"
        )

        if "tuition_statistics" in analytics:
            if "in_state_tuition" in analytics["tuition_statistics"]:
                stats = analytics["tuition_statistics"]["in_state_tuition"]
                logger.info(
                    f"- In-state tuition range: ${stats['min']:,.0f} - ${stats['max']:,.0f}"
                )
                logger.info(f"- In-state tuition median: ${stats['median']:,.0f}")


def main():
    """Main function to run the import"""
    # Default CSV file path (adjust as needed)
    csv_file_path = "data/magicscholar_financial_data.csv"

    # Check if custom path provided via command line
    if len(sys.argv) > 1:
        csv_file_path = sys.argv[1]

    logger.info("Starting MagicScholar Tuition Data Import")
    logger.info(f"CSV file: {csv_file_path}")

    # Run the import
    success = import_csv_to_database(csv_file_path)

    if success:
        logger.info("Import completed successfully!")

        # Run validation
        db = SessionLocal()
        try:
            validate_data_quality(db)
        finally:
            db.close()
    else:
        logger.error("Import failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
