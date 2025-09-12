#!/usr/bin/env python3
"""
Step 2: IC2023_AY Data Processor - Corrected Version
Process Academic Year tuition and fee data from IPEDS IC2023_AY.csv using official field mappings
Outputs: step2_financial_data.csv for MagicScholar database
"""

import pandas as pd
from pathlib import Path
import logging
from typing import Dict, Any, Optional, List
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class IC2023AYProcessor:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.project_root = self.script_dir.parent
        self.data_dir = self.project_root / "raw_data"
        self.processed_dir = self.project_root / "processed_data"

        # Ensure processed_data directory exists
        self.processed_dir.mkdir(exist_ok=True)

        self.academic_year = "2023-24"

        # Official IPEDS field mappings from data dictionary
        self.field_mappings = {
            # CORRECTED - Use CHG fields instead of TUITION2/TUITION3
            "tuition_in_state": "CHG2AT3",  # Published in-state TUITION 2023-24
            "tuition_out_state": "CHG3AT3",  # Published out-of-state TUITION 2023-24
            "fees_in_state": "CHG2AF3",  # Published in-state FEES 2023-24
            "fees_out_state": "CHG3AF3",  # Published out-of-state FEES 2023-24
            # Keep the rest the same...
            "combined_in_state": "CHG2AY3",
            "combined_out_state": "CHG3AY3",
            "books_supplies": "CHG4AY3",
            "room_board_on_campus": "CHG5AY3",  # On campus, food and housing 2023-24
            "personal_expenses": "CHG6AY3",  # On campus, other expenses 2023-24
            "room_board_off_campus": "CHG7AY3",  # Off campus (not with family), food and housing 2023-24
            "off_campus_other": "CHG8AY3",  # Off campus (not with family), other expenses 2023-24
            "transportation": "CHG9AY3",  # Off campus (with family), other expenses 2023-24
        }

        logger.info("Using OFFICIAL IPEDS field mappings from data dictionary:")
        for field_type, ipeds_field in self.field_mappings.items():
            logger.info(f"  {field_type}: {ipeds_field}")

    def load_ic2023_ay_data(self) -> Optional[pd.DataFrame]:
        """Load IC2023_AY data from IPEDS"""

        possible_files = ["ic2023_ay.csv", "IC2023_AY.csv", "IC2023_AY_Data_Stata.csv"]

        for filename in possible_files:
            file_path = self.data_dir / filename
            if file_path.exists():
                logger.info(f"Found IPEDS file: {filename}")
                try:
                    # Try reading with different encodings
                    for encoding in ["utf-8", "latin-1", "iso-8859-1", "cp1252"]:
                        try:
                            df = pd.read_csv(
                                file_path, encoding=encoding, low_memory=False
                            )
                            logger.info(
                                f"Successfully read file with {encoding} encoding"
                            )
                            logger.info(
                                f"Loaded {len(df):,} rows with {len(df.columns)} columns"
                            )

                            # Verify required fields exist
                            self._verify_required_fields(df)
                            return df

                        except UnicodeDecodeError:
                            continue
                except Exception as e:
                    logger.error(f"Error reading {file_path}: {e}")
                    continue

        logger.error(f"No IC2023_AY file found in {self.data_dir}")
        return None

    def _verify_required_fields(self, df: pd.DataFrame):
        """Verify that required IPEDS fields exist in the dataset"""
        essential_fields = ["UNITID", "CHG2AT3", "CHG3AT3", "CHG2AY3", "CHG3AY3"]

        missing_fields = []
        available_fields = []

        for field in essential_fields:
            if field in df.columns:
                available_fields.append(field)
            else:
                missing_fields.append(field)

        logger.info(f"Required field verification:")
        for field in available_fields:
            logger.info(f"  ✓ {field}")

        if missing_fields:
            logger.warning(f"Missing fields:")
            for field in missing_fields:
                logger.warning(f"  ✗ {field}")

    def safe_float(self, value) -> Optional[float]:
        """Safely convert value to float, handling IPEDS codes"""
        if pd.isna(value):
            return None

        if isinstance(value, str):
            value = value.strip()
            # Handle IPEDS missing data codes
            if value in ["", ".", "NULL", "N/A", "-", "Not applicable"]:
                return None

        try:
            numeric_value = float(value)
            # Validate reasonable range
            if (
                numeric_value < 0 or numeric_value > 300000
            ):  # Extended range for expensive schools
                return None
            return numeric_value
        except (ValueError, TypeError):
            return None

    def extract_financial_data(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Extract financial data using official IPEDS field mappings"""

        logger.info("Extracting financial data using OFFICIAL IPEDS field mappings...")

        financial_records = []

        # Track extraction methods
        separate_fields_count = 0
        combined_fields_count = 0

        for index, row in df.iterrows():
            try:
                ipeds_id = self.safe_float(row.get("UNITID"))
                if not ipeds_id:
                    continue

                ipeds_id = int(ipeds_id)

                # Method 1: Try separate tuition and fees fields (preferred)
                tuition_in_state = self.safe_float(row.get("CHG2AT3"))  # ← Corrected!
                tuition_out_state = self.safe_float(row.get("CHG3AT3"))  # ← Corrected!
                fees_in_state = self.safe_float(row.get("CHG2AF3"))  # ← Corrected!
                fees_out_state = self.safe_float(row.get("CHG3AF3"))

                # Method 2: Combined tuition + fees (backup)
                combined_in_state = self.safe_float(row.get("CHG2AY3"))
                combined_out_state = self.safe_float(row.get("CHG3AY3"))

                # Determine which method to use
                use_separate = (
                    tuition_in_state is not None and tuition_out_state is not None
                )
                use_combined = (
                    combined_in_state is not None and combined_out_state is not None
                )

                if use_separate:
                    separate_fields_count += 1
                    data_method = "separate_fields"

                    # Calculate combined costs from separate fields
                    tuition_fees_in_state = None
                    tuition_fees_out_state = None
                    required_fees = None

                    if tuition_in_state is not None and fees_in_state is not None:
                        tuition_fees_in_state = tuition_in_state + fees_in_state
                        required_fees = fees_in_state  # Use in-state fees as default
                    elif tuition_in_state is not None:
                        tuition_fees_in_state = (
                            tuition_in_state  # Just tuition if no fees
                        )

                    if tuition_out_state is not None and fees_out_state is not None:
                        tuition_fees_out_state = tuition_out_state + fees_out_state
                        if required_fees is None:
                            required_fees = fees_out_state  # Use out-state fees if in-state not available
                    elif tuition_out_state is not None:
                        tuition_fees_out_state = (
                            tuition_out_state  # Just tuition if no fees
                        )

                    # If we have different fee amounts, average them for the required_fees field
                    if (
                        fees_in_state is not None
                        and fees_out_state is not None
                        and fees_in_state != fees_out_state
                    ):
                        required_fees = (fees_in_state + fees_out_state) / 2

                elif use_combined:
                    combined_fields_count += 1
                    data_method = "combined_fields"

                    # Use combined fields directly
                    tuition_fees_in_state = combined_in_state
                    tuition_fees_out_state = combined_out_state

                    # Can't separate tuition from fees in combined method
                    tuition_in_state = None
                    tuition_out_state = None
                    required_fees = None

                else:
                    # No usable data for this institution
                    continue

                # Extract other cost components
                books_supplies = self.safe_float(row.get("CHG4AY3"))
                room_board_on_campus = self.safe_float(row.get("CHG5AY3"))
                personal_expenses = self.safe_float(row.get("CHG6AY3"))
                room_board_off_campus = self.safe_float(row.get("CHG7AY3"))
                transportation = self.safe_float(row.get("CHG9AY3"))

                # Calculate data completeness
                core_fields = [
                    tuition_in_state,
                    tuition_out_state,
                    tuition_fees_in_state,
                    tuition_fees_out_state,
                    required_fees,
                ]
                other_fields = [
                    room_board_on_campus,
                    room_board_off_campus,
                    books_supplies,
                    personal_expenses,
                    transportation,
                ]
                all_fields = core_fields + other_fields

                filled_fields = sum(1 for f in all_fields if f is not None)
                completeness_score = int((filled_fields / len(all_fields)) * 100)

                # Determine data flags
                has_tuition_data = bool(
                    tuition_in_state
                    or tuition_out_state
                    or tuition_fees_in_state
                    or tuition_fees_out_state
                )
                has_fees_data = bool(required_fees)

                # Validation
                validation_issues = self._validate_record(
                    {
                        "tuition_in_state": tuition_in_state,
                        "tuition_out_state": tuition_out_state,
                        "tuition_fees_in_state": tuition_fees_in_state,
                        "tuition_fees_out_state": tuition_fees_out_state,
                        "required_fees": required_fees,
                    }
                )

                record = {
                    "ipeds_id": ipeds_id,
                    "academic_year": self.academic_year,
                    "data_source": f"IC2023_AY_{data_method}",
                    "tuition_in_state": tuition_in_state,
                    "tuition_out_state": tuition_out_state,
                    "required_fees": required_fees,
                    "tuition_fees_in_state": tuition_fees_in_state,
                    "tuition_fees_out_state": tuition_fees_out_state,
                    "room_board_on_campus": room_board_on_campus,
                    "room_board_off_campus": room_board_off_campus,
                    "books_supplies": books_supplies,
                    "personal_expenses": personal_expenses,
                    "transportation": transportation,
                    "has_tuition_data": has_tuition_data,
                    "has_fees_data": has_fees_data,
                    "data_completeness_score": completeness_score,
                    "validation_issues": validation_issues,
                    "validation_status": "warning" if validation_issues else "clean",
                }

                financial_records.append(record)

                if len(financial_records) % 1000 == 0:
                    logger.info(f"Processed {len(financial_records):,} records...")

            except Exception as e:
                logger.error(
                    f"Error processing row {index} (IPEDS {row.get('UNITID', 'unknown')}): {e}"
                )
                continue

        logger.info(
            f"Successfully extracted {len(financial_records):,} financial records"
        )
        logger.info(f"  Using separate fields: {separate_fields_count:,}")
        logger.info(f"  Using combined fields: {combined_fields_count:,}")

        return financial_records

    def _validate_record(self, record: Dict[str, Any]) -> Optional[str]:
        """Validate financial record for logical consistency"""
        issues = []

        tuition_in = record.get("tuition_in_state")
        tuition_out = record.get("tuition_out_state")
        total_in = record.get("tuition_fees_in_state")
        total_out = record.get("tuition_fees_out_state")
        fees = record.get("required_fees")

        # Check tuition relationship
        if tuition_in is not None and tuition_out is not None:
            if tuition_in > tuition_out:
                issues.append(f"In-state tuition > out-state tuition")

        # Check total cost relationship
        if total_in is not None and total_out is not None:
            if total_in > total_out:
                issues.append(f"In-state total > out-state total")

        # Check consistency between tuition+fees and total
        if tuition_in is not None and fees is not None and total_in is not None:
            expected = tuition_in + fees
            if abs(expected - total_in) > 100:  # Allow $100 variance
                issues.append(f"In-state calculation inconsistent")

        return "; ".join(issues) if issues else None

    def save_financial_data(
        self,
        financial_data: List[Dict[str, Any]],
        filename: str = "step2_financial_data.csv",
    ):
        """Save processed financial data to CSV"""

        if not financial_data:
            logger.error("No financial data to save!")
            return None

        output_path = self.processed_dir / filename

        df = pd.DataFrame(financial_data)

        # Sort by data completeness score (highest first) and IPEDS ID
        df = df.sort_values(
            ["data_completeness_score", "ipeds_id"], ascending=[False, True]
        )

        df.to_csv(output_path, index=False)

        logger.info(f"Saved {len(financial_data):,} records to: {output_path}")
        return output_path

    def generate_summary_report(self, financial_data: List[Dict[str, Any]]):
        """Generate comprehensive summary report"""

        if not financial_data:
            logger.warning("No financial data to summarize!")
            return

        logger.info("\n" + "=" * 80)
        logger.info("STEP 2 FINANCIAL DATA SUMMARY REPORT")
        logger.info("=" * 80)

        total_records = len(financial_data)
        logger.info(f"Total records processed: {total_records:,}")

        # Data availability
        with_tuition = sum(1 for r in financial_data if r["has_tuition_data"])
        with_fees = sum(1 for r in financial_data if r["has_fees_data"])

        logger.info(f"\nData Availability:")
        logger.info(
            f"  Records with tuition data: {with_tuition:,} ({with_tuition/total_records*100:.1f}%)"
        )
        logger.info(
            f"  Records with fees data: {with_fees:,} ({with_fees/total_records*100:.1f}%)"
        )

        # Check for realistic tuition differences
        with_both_totals = [
            r
            for r in financial_data
            if r.get("tuition_fees_in_state") and r.get("tuition_fees_out_state")
        ]

        if with_both_totals:
            different_costs = [
                r
                for r in with_both_totals
                if abs(r["tuition_fees_in_state"] - r["tuition_fees_out_state"]) > 100
            ]

            logger.info(f"\nTuition Analysis:")
            logger.info(
                f"  Records with both in-state and out-state totals: {len(with_both_totals):,}"
            )
            logger.info(
                f"  Records with significant differences (>$100): {len(different_costs):,}"
            )
            logger.info(
                f"  Percentage with realistic differences: {len(different_costs)/len(with_both_totals)*100:.1f}%"
            )

            if different_costs:
                differences = [
                    r["tuition_fees_out_state"] - r["tuition_fees_in_state"]
                    for r in different_costs
                ]
                logger.info(
                    f"  Average out-state premium: ${np.mean(differences):,.0f}"
                )
                logger.info(
                    f"  Median out-state premium: ${np.median(differences):,.0f}"
                )

        # Cost statistics
        cost_fields = [
            "tuition_fees_in_state",
            "tuition_fees_out_state",
            "room_board_on_campus",
            "books_supplies",
        ]

        for field in cost_fields:
            values = [r[field] for r in financial_data if r.get(field)]
            if values:
                logger.info(f"\n{field.replace('_', ' ').title()} Statistics:")
                logger.info(f"  Count: {len(values):,}")
                logger.info(f"  Range: ${min(values):,.0f} - ${max(values):,.0f}")
                logger.info(f"  Average: ${np.mean(values):,.0f}")
                logger.info(f"  Median: ${np.median(values):,.0f}")

        # Validation issues
        with_issues = sum(1 for r in financial_data if r.get("validation_issues"))
        if with_issues > 0:
            logger.info(f"\nValidation:")
            logger.info(
                f"  Records with issues: {with_issues:,} ({with_issues/total_records*100:.1f}%)"
            )

        # Test Commonwealth University if present
        commonwealth = next(
            (r for r in financial_data if r["ipeds_id"] == 498562), None
        )
        if commonwealth:
            logger.info(f"\nCommonwealth University (IPEDS 498562) Verification:")
            logger.info(f"  Data source: {commonwealth.get('data_source')}")
            logger.info(
                f"  In-state tuition+fees: ${commonwealth.get('tuition_fees_in_state', 'N/A')}"
            )
            logger.info(
                f"  Out-of-state tuition+fees: ${commonwealth.get('tuition_fees_out_state', 'N/A')}"
            )
            logger.info(
                f"  Data completeness: {commonwealth.get('data_completeness_score')}%"
            )

        # Sample of high-quality records
        high_quality = sorted(
            [r for r in financial_data if r["data_completeness_score"] >= 80],
            key=lambda x: x["data_completeness_score"],
            reverse=True,
        )[:5]

        if high_quality:
            logger.info(f"\nSample High-Quality Records:")
            for r in high_quality:
                in_state = (
                    f"${r['tuition_fees_in_state']:,.0f}"
                    if r.get("tuition_fees_in_state")
                    else "N/A"
                )
                out_state = (
                    f"${r['tuition_fees_out_state']:,.0f}"
                    if r.get("tuition_fees_out_state")
                    else "N/A"
                )
                logger.info(
                    f"  IPEDS {r['ipeds_id']}: In-state {in_state}, Out-state {out_state} ({r['data_completeness_score']}%)"
                )


def main():
    """Main processing function"""
    processor = IC2023AYProcessor()

    # Load data
    df = processor.load_ic2023_ay_data()
    if df is None:
        logger.error("Failed to load IPEDS data file")
        return

    # Extract financial data using corrected field mappings
    financial_data = processor.extract_financial_data(df)

    if not financial_data:
        logger.error("No financial data extracted!")
        return

    # Generate comprehensive summary
    processor.generate_summary_report(financial_data)

    # Save to CSV
    output_path = processor.save_financial_data(financial_data)

    if output_path:
        logger.info(f"\n" + "=" * 80)
        logger.info("STEP 2 PROCESSING COMPLETE!")
        logger.info("=" * 80)
        logger.info(f"✅ Output file: {output_path}")
        logger.info(f"✅ Records processed: {len(financial_data):,}")
        logger.info(f"✅ Ready for database import!")
        logger.info(f"\nTo import to database:")
        logger.info(
            f"  COPY step2_ic2023_ay(ipeds_id, academic_year, data_source, tuition_in_state, tuition_out_state, required_fees, tuition_fees_in_state, tuition_fees_out_state, room_board_on_campus, room_board_off_campus, books_supplies, personal_expenses, transportation, has_tuition_data, has_fees_data, data_completeness_score, validation_issues, validation_status)"
        )
        logger.info(f"  FROM '{output_path.absolute()}'")
        logger.info(f"  WITH CSV HEADER;")
    else:
        logger.error("Failed to save financial data!")


if __name__ == "__main__":
    main()
