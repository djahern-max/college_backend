#!/usr/bin/env python3
"""
FIXED College Data Import Script for MagicScholar

This version correctly maps the region values from your CSV.
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from sqlalchemy.orm import Session
import logging
from typing import Dict, Any, Optional

# Add app directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.institution import Institution, ControlType, SizeCategory, USRegion

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class InstitutionDataImporter:
    """Import IPEDS institution data into MagicScholar database"""

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
        """Import institution data from processed IPEDS CSV"""

        logger.info(f"Starting institution data import from {csv_path}")

        try:
            # Load the CSV
            df = pd.read_csv(csv_path)
            self.import_stats["total_rows"] = len(df)

            logger.info(f"Loaded {len(df)} rows from CSV")

            # Process each row
            for index, row in df.iterrows():
                try:
                    institution_data = self._process_row(row)
                    if institution_data:
                        self._create_or_update_institution(institution_data)
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

    def _process_row(self, row: pd.Series) -> Optional[Dict[str, Any]]:
        """Process a single row from the CSV into institution data"""

        try:
            # Skip if missing essential data
            if pd.isna(row.get("ipeds_id")) or pd.isna(row.get("name")):
                return None

            # Map control type
            control_type = self._map_control_type(row.get("control_type"))
            if not control_type:
                logger.warning(f"Unknown control type: {row.get('control_type')}")
                return None

            # Map size category
            size_category = self._map_size_category(row.get("size_category"))

            # Map region - FIXED to handle your actual CSV values
            region = self._map_region(row.get("region"))

            # Create institution data
            institution_data = {
                "ipeds_id": int(row["ipeds_id"]),
                "name": self._clean_string(row.get("name")),
                "address": self._clean_string(row.get("address")),
                "city": self._clean_string(row.get("city")),
                "state": self._clean_string(row.get("state")),
                "zip_code": self._clean_string(row.get("zip_code")),
                "region": region,
                "website": self._clean_website(row.get("website")),
                "phone": self._get_float(row.get("phone")),
                "president_name": self._clean_string(row.get("president_name")),
                "president_title": self._clean_string(row.get("president_title")),
                "control_type": control_type,
                "size_category": size_category,
            }

            return institution_data

        except Exception as e:
            logger.error(f"Error processing row: {str(e)}")
            return None

    def _create_or_update_institution(self, institution_data: Dict[str, Any]):
        """Create or update institution in database"""

        # Check if institution already exists
        existing = (
            self.db.query(Institution)
            .filter(Institution.ipeds_id == institution_data["ipeds_id"])
            .first()
        )

        if existing:
            # Update existing institution
            for field, value in institution_data.items():
                if field != "ipeds_id" and value is not None:  # Don't update ID
                    setattr(existing, field, value)
        else:
            # Create new institution
            institution = Institution(**institution_data)
            self.db.add(institution)

    def _map_control_type(self, control_type_str: str) -> Optional[ControlType]:
        """Map control type string to enum"""
        if pd.isna(control_type_str):
            return None

        control_type_str = str(control_type_str).lower().strip()

        if control_type_str in ["public"]:
            return ControlType.PUBLIC
        elif control_type_str in [
            "private nonprofit",
            "private_nonprofit",
            "private non-profit",
        ]:
            return ControlType.PRIVATE_NONPROFIT
        elif control_type_str in [
            "private for-profit",
            "private_for_profit",
            "private for profit",
        ]:
            return ControlType.PRIVATE_FOR_PROFIT
        else:
            return None

    def _map_size_category(self, size_str: str) -> Optional[SizeCategory]:
        """Map size category string to enum"""
        if pd.isna(size_str):
            return None

        size_str = str(size_str).lower().strip()

        if "very small" in size_str or "< 1,000" in size_str or "<1,000" in size_str:
            return SizeCategory.VERY_SMALL
        elif "small" in size_str and "very" not in size_str:
            return SizeCategory.SMALL
        elif "medium" in size_str:
            return SizeCategory.MEDIUM
        elif "large" in size_str and "very" not in size_str:
            return SizeCategory.LARGE
        elif "very large" in size_str:
            return SizeCategory.VERY_LARGE
        else:
            return None

    def _map_region(self, region_str: str) -> Optional[USRegion]:
        """Map region string to enum - CORRECT mapping for your actual CSV values"""
        if pd.isna(region_str):
            return None

        region_str = str(region_str).strip()

        # Map your actual CSV region values to the enum values
        region_mapping = {
            "Southeast": USRegion.SOUTH_ATLANTIC,
            "Mid East": USRegion.MID_ATLANTIC,
            "Far West": USRegion.PACIFIC,
            "Great Lakes": USRegion.EAST_NORTH_CENTRAL,
            "Southwest": USRegion.WEST_SOUTH_CENTRAL,
            "Plains": USRegion.WEST_NORTH_CENTRAL,
            "New England": USRegion.NEW_ENGLAND,
            "Rocky Mountains": USRegion.MOUNTAIN,
            "Outlying Areas": USRegion.PACIFIC,  # Group with Pacific for now
            "Unknown": USRegion.MID_ATLANTIC,  # Default to Mid Atlantic for unknowns
        }

        return region_mapping.get(region_str)

    def _clean_string(self, value) -> Optional[str]:
        """Clean string values"""
        if pd.isna(value):
            return None

        cleaned = str(value).strip()
        return cleaned if cleaned else None

    def _clean_website(self, value) -> Optional[str]:
        """Clean website URLs"""
        if pd.isna(value):
            return None

        website = str(value).strip()
        if not website:
            return None

        # Add https:// if not present
        if not website.startswith(("http://", "https://")):
            website = "https://" + website

        return website

    def _get_float(self, value) -> Optional[float]:
        """Convert value to float"""
        if pd.isna(value):
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None


def main():
    """Main function to run the import"""

    # Database setup
    db = SessionLocal()

    try:
        # CSV file path
        csv_path = "data/raw_data/institutions_processed.csv"

        # Check if file exists
        if not Path(csv_path).exists():
            logger.error(f"CSV file not found: {csv_path}")
            return

        # Run import
        importer = InstitutionDataImporter(db)
        stats = importer.import_from_csv(csv_path)

        # Print results
        logger.info("\n" + "=" * 50)
        logger.info("IMPORT SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Total rows processed: {stats['total_rows']}")
        logger.info(f"Successful imports: {stats['successful_imports']}")
        logger.info(f"Skipped rows: {stats['skipped']}")
        logger.info(f"Errors: {stats['errors']}")

        if stats["error_details"]:
            logger.info("\nFirst 10 errors:")
            for error in stats["error_details"][:10]:
                logger.info(f"  - {error}")

        logger.info("=" * 50)

    except Exception as e:
        logger.error(f"Import failed: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
