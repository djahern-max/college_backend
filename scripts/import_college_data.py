#!/usr/bin/env python3
"""
College Data Import Script for MagicScholar

This script imports IPEDS data from your processed CSV files into the MagicScholar database.
Run this after setting up the college tables.

Usage:
    python scripts/import_college_data.py [--csv-path path/to/unified_ipeds_dataset.csv]
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, MetaData
import logging
from typing import Dict, Any, Optional
import argparse

# Add app directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.college import College, CollegeType, CollegeSize, CarnegieClassification
from app.schemas.college import CollegeCreate

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CollegeDataImporter:
    """Import IPEDS college data into MagicScholar database"""

    def __init__(self, db: Session):
        self.db = db
        self.import_stats = {
            "total_rows": 0,
            "successful_imports": 0,
            "skipped": 0,
            "errors": 0,
            "error_details": [],
        }

    def import_from_csv(self, csv_path: str) -> Dict[str, Any]:
        """Import college data from processed IPEDS CSV"""

        logger.info(f"Starting college data import from {csv_path}")

        try:
            # Load the CSV
            df = pd.read_csv(csv_path)
            self.import_stats["total_rows"] = len(df)

            logger.info(f"Loaded {len(df)} rows from CSV")

            # Process each row
            for index, row in df.iterrows():
                try:
                    college_data = self._process_row(row)
                    if college_data:
                        self._create_or_update_college(college_data)
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
                    continue

            # Commit all changes
            self.db.commit()

            logger.info("Import completed successfully")
            return self.import_stats

        except Exception as e:
            self.db.rollback()
            logger.error(f"Import failed: {str(e)}")
            raise

    def _process_row(self, row: pd.Series) -> Optional[CollegeCreate]:
        """Process a single row from the CSV into CollegeCreate schema"""

        try:
            # Skip if missing essential data
            if pd.isna(row.get("UNITID")) or pd.isna(row.get("INSTNM")):
                return None

            # Map control type
            control_mapping = {
                1: CollegeType.PUBLIC,
                2: CollegeType.PRIVATE_NONPROFIT,
                3: CollegeType.PRIVATE_FOR_PROFIT,
            }

            college_type = control_mapping.get(row.get("CONTROL"))
            if not college_type:
                return None  # Skip if we can't determine type

            # Map size category based on enrollment
            size_category = self._get_size_category(
                row.get("student_body_size") or row.get("total_enrollment")
            )

            # Map Carnegie classification
            carnegie_class = self._map_carnegie_classification(row.get("CCBASIC"))

            # Create college data
            college_data = CollegeCreate(
                unitid=int(row["UNITID"]),
                name=self._clean_string(row.get("INSTNM")),
                alias=self._clean_string(row.get("IALIAS")),
                website=self._clean_website(row.get("WEBADDR")),
                # Location
                address=self._clean_string(row.get("ADDR")),
                city=self._clean_string(row.get("CITY")),
                state=self._clean_string(row.get("STABBR")),
                zip_code=self._clean_string(row.get("ZIP")),
                region=self._get_region(row.get("STABBR")),
                # Institution characteristics
                college_type=college_type,
                size_category=size_category,
                carnegie_classification=carnegie_class,
                # Special designations
                is_hbcu=self._get_boolean(row.get("HBCU")),
                is_hsi=self._get_boolean(row.get("PBI")),  # Using PBI as proxy for HSI
                is_tribal=self._get_boolean(row.get("TRIBAL")),
                # Enrollment
                total_enrollment=self._get_int(
                    row.get("student_body_size") or row.get("total_enrollment")
                ),
                undergraduate_enrollment=self._get_int(
                    row.get("undergraduate_enrollment")
                ),
                graduate_enrollment=self._get_int(row.get("graduate_enrollment")),
                # Admissions
                acceptance_rate=self._get_float(row.get("acceptance_rate")),
                yield_rate=self._get_float(row.get("yield_rate")),
                # Test scores
                sat_reading_25=self._get_int(row.get("SATVR25")),
                sat_reading_75=self._get_int(row.get("SATVR75")),
                sat_math_25=self._get_int(row.get("SATMT25")),
                sat_math_75=self._get_int(row.get("SATMT75")),
                sat_total_25=self._get_int(row.get("sat_total_25")),
                sat_total_75=self._get_int(row.get("sat_total_75")),
                act_composite_25=self._get_int(row.get("ACTCM25")),
                act_composite_75=self._get_int(row.get("ACTCM75")),
                act_english_25=self._get_int(row.get("ACTEN25")),
                act_english_75=self._get_int(row.get("ACTEN75")),
                act_math_25=self._get_int(row.get("ACTMT25")),
                act_math_75=self._get_int(row.get("ACTMT75")),
                # Admission requirements
                is_test_optional=self._get_boolean(row.get("likely_test_optional")),
                # Financial
                tuition_in_state=self._get_int(row.get("tuition_in_state")),
                tuition_out_state=self._get_int(row.get("tuition_out_state")),
                required_fees=self._get_int(row.get("required_fees")),
                room_and_board=self._get_int(row.get("room_and_board")),
                total_cost_in_state=self._get_int(row.get("total_cost_in_state")),
                total_cost_out_state=self._get_int(row.get("total_cost_out_state")),
                # Academic metrics
                graduation_rate_6_year=self._get_float(
                    row.get("graduation_rate_6_year")
                ),
                retention_rate=self._get_float(row.get("retention_rate")),
                # Scores
                competitiveness_score=self._get_float(row.get("competitiveness_score")),
                affordability_score=self._get_float(row.get("affordability_score")),
                value_score=self._get_float(row.get("value_score")),
                # Metadata
                data_year=2023,
                is_active=True,
                is_verified=True,  # IPEDS data is considered verified
                data_completeness=self._get_float(row.get("data_completeness")),
            )

            return college_data

        except Exception as e:
            logger.error(f"Error processing row: {str(e)}")
            return None

    def _create_or_update_college(self, college_data: CollegeCreate):
        """Create or update college in database"""

        # Check if college already exists
        existing = (
            self.db.query(College).filter(College.unitid == college_data.unitid).first()
        )

        if existing:
            # Update existing college
            update_data = college_data.model_dump(exclude={"unitid"})
            for field, value in update_data.items():
                if value is not None:  # Only update non-null values
                    setattr(existing, field, value)
        else:
            # Create new college
            college = College(**college_data.model_dump())
            self.db.add(college)

    def _get_size_category(self, enrollment) -> Optional[CollegeSize]:
        """Map enrollment to size category"""
        if pd.isna(enrollment):
            return None

        enrollment = int(enrollment)
        if enrollment < 1000:
            return CollegeSize.VERY_SMALL
        elif enrollment < 3000:
            return CollegeSize.SMALL
        elif enrollment < 10000:
            return CollegeSize.MEDIUM
        elif enrollment < 20000:
            return CollegeSize.LARGE
        else:
            return CollegeSize.VERY_LARGE

    def _map_carnegie_classification(self, ccbasic) -> Optional[CarnegieClassification]:
        """Map IPEDS Carnegie classification to our enum"""
        if pd.isna(ccbasic):
            return None

        # Mapping based on IPEDS Carnegie codes
        carnegie_mapping = {
            15: CarnegieClassification.R1_VERY_HIGH_RESEARCH,
            16: CarnegieClassification.R2_HIGH_RESEARCH,
            17: CarnegieClassification.DOCTORAL_PROFESSIONAL,
            18: CarnegieClassification.MASTERS_LARGE,
            19: CarnegieClassification.MASTERS_MEDIUM,
            20: CarnegieClassification.MASTERS_SMALL,
            21: CarnegieClassification.BACCALAUREATE_ARTS_SCIENCES,
            22: CarnegieClassification.BACCALAUREATE_DIVERSE,
            23: CarnegieClassification.BACCALAUREATE_DIVERSE,  # Baccalaureate/Associate's
            # Associate's colleges
            24: CarnegieClassification.ASSOCIATES_HIGH_TRANSFER,
            25: CarnegieClassification.ASSOCIATES_MIXED,
            26: CarnegieClassification.ASSOCIATES_HIGH_TRANSFER,
            27: CarnegieClassification.ASSOCIATES_MIXED,
            28: CarnegieClassification.ASSOCIATES_MIXED,
            29: CarnegieClassification.ASSOCIATES_MIXED,
            30: CarnegieClassification.ASSOCIATES_HIGH_CAREER,
            31: CarnegieClassification.ASSOCIATES_HIGH_CAREER,
            32: CarnegieClassification.ASSOCIATES_HIGH_CAREER,
            # Special focus
            33: CarnegieClassification.SPECIAL_FOCUS,
            34: CarnegieClassification.SPECIAL_FOCUS,
            35: CarnegieClassification.SPECIAL_FOCUS,
            36: CarnegieClassification.SPECIAL_FOCUS,
            37: CarnegieClassification.SPECIAL_FOCUS,
            38: CarnegieClassification.SPECIAL_FOCUS,
            39: CarnegieClassification.SPECIAL_FOCUS,
            40: CarnegieClassification.SPECIAL_FOCUS,
            41: CarnegieClassification.SPECIAL_FOCUS,
            42: CarnegieClassification.SPECIAL_FOCUS,
            43: CarnegieClassification.SPECIAL_FOCUS,
        }

        return carnegie_mapping.get(int(ccbasic))

    def _get_region(self, state_abbr: str) -> Optional[str]:
        """Map state to region"""
        if not state_abbr:
            return None

        region_mapping = {
            # Northeast
            "CT": "Northeast",
            "ME": "Northeast",
            "MA": "Northeast",
            "NH": "Northeast",
            "NJ": "Northeast",
            "NY": "Northeast",
            "PA": "Northeast",
            "RI": "Northeast",
            "VT": "Northeast",
            # Southeast
            "AL": "Southeast",
            "AR": "Southeast",
            "DE": "Southeast",
            "FL": "Southeast",
            "GA": "Southeast",
            "KY": "Southeast",
            "LA": "Southeast",
            "MD": "Southeast",
            "MS": "Southeast",
            "NC": "Southeast",
            "SC": "Southeast",
            "TN": "Southeast",
            "VA": "Southeast",
            "WV": "Southeast",
            # Midwest
            "IL": "Midwest",
            "IN": "Midwest",
            "IA": "Midwest",
            "KS": "Midwest",
            "MI": "Midwest",
            "MN": "Midwest",
            "MO": "Midwest",
            "NE": "Midwest",
            "ND": "Midwest",
            "OH": "Midwest",
            "SD": "Midwest",
            "WI": "Midwest",
            # Southwest
            "AZ": "Southwest",
            "NM": "Southwest",
            "TX": "Southwest",
            "OK": "Southwest",
            # West
            "AK": "West",
            "CA": "West",
            "CO": "West",
            "HI": "West",
            "ID": "West",
            "MT": "West",
            "NV": "West",
            "OR": "West",
            "UT": "West",
            "WA": "West",
            "WY": "West",
            # Other
            "DC": "Northeast",
        }

        return region_mapping.get(state_abbr.upper())

    def _clean_string(self, value) -> Optional[str]:
        """Clean string values"""
        if pd.isna(value) or value == "" or str(value).lower() in ["nan", "none"]:
            return None
        return str(value).strip()

    def _clean_website(self, value) -> Optional[str]:
        """Clean website URL"""
        if pd.isna(value) or value == "":
            return None

        url = str(value).strip()
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        return url

    def _get_int(self, value) -> Optional[int]:
        """Convert to int, handling NaN"""
        if pd.isna(value):
            return None
        try:
            return int(
                float(value)
            )  # Convert through float first to handle decimal strings
        except (ValueError, TypeError):
            return None

    def _get_float(self, value) -> Optional[float]:
        """Convert to float, handling NaN"""
        if pd.isna(value):
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def _get_boolean(self, value) -> bool:
        """Convert to boolean"""
        if pd.isna(value):
            return False

        if isinstance(value, bool):
            return value

        if isinstance(value, (int, float)):
            return value == 1

        if isinstance(value, str):
            return value.lower() in ["true", "1", "yes", "y"]

        return False


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="Import college data into MagicScholar"
    )
    parser.add_argument(
        "--csv-path",
        type=str,
        default="unified_ipeds_dataset.csv",
        help="Path to the unified IPEDS dataset CSV file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without actually importing data (validation only)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Number of records to process before committing to database",
    )

    args = parser.parse_args()

    # Check if CSV file exists
    csv_path = Path(args.csv_path)
    if not csv_path.exists():
        logger.error(f"CSV file not found: {csv_path}")
        sys.exit(1)

    logger.info(f"🏫 MagicScholar College Data Import")
    logger.info(f"CSV file: {csv_path}")
    logger.info(f"Dry run: {args.dry_run}")

    try:
        # Create database session
        db = SessionLocal()

        if args.dry_run:
            logger.info("🧪 Running in dry-run mode (no data will be imported)")

            # Just validate the CSV structure
            df = pd.read_csv(csv_path, nrows=10)
            logger.info(f"CSV validation: {len(df)} sample rows loaded successfully")

            required_columns = ["UNITID", "INSTNM", "CONTROL", "STABBR"]
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                logger.error(f"Missing required columns: {missing_columns}")
                sys.exit(1)
            else:
                logger.info("✅ CSV structure validation passed")

        else:
            # Run actual import
            importer = CollegeDataImporter(db)
            stats = importer.import_from_csv(str(csv_path))

            # Print results
            logger.info("📊 Import Results:")
            logger.info(f"Total rows processed: {stats['total_rows']}")
            logger.info(f"Successful imports: {stats['successful_imports']}")
            logger.info(f"Skipped rows: {stats['skipped']}")
            logger.info(f"Errors: {stats['errors']}")

            if stats["errors"] > 0:
                logger.info("❌ Error details:")
                for error in stats["error_details"][:5]:  # Show first 5 errors
                    logger.info(f"  {error}")
                if len(stats["error_details"]) > 5:
                    logger.info(
                        f"  ... and {len(stats['error_details']) - 5} more errors"
                    )

            success_rate = (stats["successful_imports"] / stats["total_rows"]) * 100
            logger.info(f"✅ Success rate: {success_rate:.1f}%")

            if success_rate >= 90:
                logger.info("🎉 Import completed successfully!")
            elif success_rate >= 75:
                logger.info("⚠️ Import completed with some issues")
            else:
                logger.warning("🚨 Import completed with significant issues")

        db.close()

    except KeyboardInterrupt:
        logger.info("Import cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Import failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
