"""
Import IPEDS tuition data from ic2023_ay.csv into tuition_data table

Usage:
    python import_ipeds_tuition.py
"""

import os
import sys
import csv
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()


class IPEDSTuitionImporter:
    def __init__(self):
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise ValueError("DATABASE_URL not found in environment")

        self.engine = create_engine(db_url)
        print(
            f"Connected to database: {db_url.split('@')[1] if '@' in db_url else 'localhost'}"
        )

    def clean_number(self, value):
        """Convert value to float, handling empty strings and None"""
        if value is None or value == "" or value == "0":
            return None

        try:
            cleaned = str(value).replace("$", "").replace(",", "").strip()
            num = float(cleaned)
            return num if num > 0 else None
        except (ValueError, AttributeError):
            return None

    def verify_ipeds_exists(self, ipeds_id):
        """Check if IPEDS ID exists in institutions table"""
        with self.engine.connect() as conn:
            query = text("SELECT name FROM institutions WHERE ipeds_id = :ipeds_id")
            result = conn.execute(query, {"ipeds_id": ipeds_id})
            row = result.fetchone()
            return row[0] if row else None

    def check_existing_record(self, ipeds_id, academic_year, data_source):
        """Check if record already exists"""
        with self.engine.connect() as conn:
            query = text(
                """
                SELECT id FROM tuition_data 
                WHERE ipeds_id = :ipeds_id 
                AND academic_year = :academic_year 
                AND data_source = :data_source
            """
            )
            result = conn.execute(
                query,
                {
                    "ipeds_id": ipeds_id,
                    "academic_year": academic_year,
                    "data_source": data_source,
                },
            )
            return result.fetchone() is not None

    def import_csv(self, csv_path):
        """Import tuition data from IPEDS CSV"""
        if not Path(csv_path).exists():
            print(f"Error: File {csv_path} not found")
            return

        print(f"\nImporting IPEDS tuition data from {csv_path}\n")
        print("-" * 80)

        imported_count = 0
        skipped_institution = 0
        skipped_duplicate = 0
        error_count = 0
        missing_institutions = []

        with open(csv_path, "r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)

            # Verify columns exist - strip whitespace from fieldnames
            fieldnames = (
                [field.strip() for field in reader.fieldnames]
                if reader.fieldnames
                else []
            )

            if "ipeds_id" not in fieldnames:
                print(f"Error: CSV must have 'ipeds_id' column")
                print(f"Found columns: {fieldnames}")
                return

            for idx, raw_row in enumerate(reader, 1):
                try:
                    # Strip whitespace from keys
                    row = {k.strip(): v for k, v in raw_row.items()}

                    ipeds_id = int(row["ipeds_id"])
                    academic_year = row["academic_year"]
                    data_source = row["data_source"]

                    # Check if institution exists
                    institution_name = self.verify_ipeds_exists(ipeds_id)
                    if not institution_name:
                        if idx <= 10:
                            print(
                                f"Row {idx}: ✗ Institution not found - IPEDS {ipeds_id}"
                            )
                        missing_institutions.append(
                            {
                                "ipeds_id": ipeds_id,
                                "academic_year": academic_year,
                                "row": idx,
                            }
                        )
                        skipped_institution += 1
                        continue

                    # Check for duplicate
                    if self.check_existing_record(ipeds_id, academic_year, data_source):
                        if idx <= 10:
                            print(
                                f"Row {idx}: ⚠ Duplicate skipped - {institution_name[:40]}"
                            )
                        skipped_duplicate += 1
                        continue

                    # Clean and prepare data
                    tuition_in = self.clean_number(row.get("tuition_in_state"))
                    tuition_out = self.clean_number(row.get("tuition_out_state"))
                    fees_in = self.clean_number(row.get("required_fees_in_state"))
                    fees_out = self.clean_number(row.get("required_fees_out_state"))
                    room_board = self.clean_number(row.get("room_board_on_campus"))

                    # Skip if no meaningful data
                    if all(
                        v is None
                        for v in [
                            tuition_in,
                            tuition_out,
                            fees_in,
                            fees_out,
                            room_board,
                        ]
                    ):
                        if idx <= 10:
                            print(f"Row {idx}: ⚠ No data - {institution_name[:40]}")
                        skipped_institution += 1
                        continue

                    # Insert record
                    with self.engine.connect() as conn:
                        insert_query = text(
                            """
                            INSERT INTO tuition_data (
                                ipeds_id, academic_year, data_source,
                                tuition_in_state, tuition_out_state,
                                required_fees_in_state, required_fees_out_state,
                                room_board_on_campus
                            ) VALUES (
                                :ipeds_id, :academic_year, :data_source,
                                :tuition_in_state, :tuition_out_state,
                                :required_fees_in_state, :required_fees_out_state,
                                :room_board_on_campus
                            )
                        """
                        )

                        conn.execute(
                            insert_query,
                            {
                                "ipeds_id": ipeds_id,
                                "academic_year": academic_year,
                                "data_source": data_source,
                                "tuition_in_state": tuition_in,
                                "tuition_out_state": tuition_out,
                                "required_fees_in_state": fees_in,
                                "required_fees_out_state": fees_out,
                                "room_board_on_campus": room_board,
                            },
                        )
                        conn.commit()

                    imported_count += 1
                    if imported_count <= 10:
                        print(
                            f"Row {idx}: ✓ Imported - {institution_name[:40]} ({academic_year})"
                        )
                    elif imported_count % 100 == 0:
                        print(f"... {imported_count} records imported so far ...")

                except Exception as e:
                    error_count += 1
                    if error_count <= 5:
                        print(f"Row {idx}: ✗ Error - {str(e)}")
                    continue

        # Summary
        print("-" * 80)
        print("\nImport Summary:")
        print(f"✓ Successfully imported: {imported_count}")
        print(f"⚠ Skipped (institution not found): {skipped_institution}")
        print(f"⚠ Skipped (duplicate): {skipped_duplicate}")
        if error_count > 0:
            print(f"✗ Errors: {error_count}")
        print(
            f"\nTotal processed: {imported_count + skipped_institution + skipped_duplicate + error_count}"
        )

        # Show missing institutions
        if missing_institutions:
            print("\n" + "=" * 80)
            print("MISSING INSTITUTIONS (not found in institutions table):")
            print("=" * 80)
            for inst in missing_institutions:
                print(
                    f"  Row {inst['row']}: IPEDS ID {inst['ipeds_id']} (Academic Year: {inst['academic_year']})"
                )
            print("=" * 80)
            print(f"\nTo find these institutions, run:")
            print(
                f"SELECT ipeds_id FROM institutions WHERE ipeds_id IN ({','.join(str(i['ipeds_id']) for i in missing_institutions)});"
            )


def main():
    # Default CSV path
    csv_path = "data/ic2023_ay.csv"

    # Allow override from command line
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]

    try:
        importer = IPEDSTuitionImporter()
        importer.import_csv(csv_path)
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
