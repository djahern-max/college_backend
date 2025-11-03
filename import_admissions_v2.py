#!/usr/bin/env python3
"""
Import admissions data from Excel file to PostgreSQL database
Run from college-backend directory: python import_admissions_v3.py
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
import sys
import os

# Database connection parameters
DB_PARAMS = {
    "dbname": "college_db",
    "user": "postgres",
    "password": "",  # Add password if needed
    "host": "localhost",
    "port": "5432",
}

# File path - relative to script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(SCRIPT_DIR, "data", "admissions_upload_v2.xlsx")


def clean_numeric_value(value):
    """Convert value to appropriate numeric type or None"""
    if pd.isna(value) or value == "" or value == "NULL":
        return None
    try:
        # Try to convert to float first
        num_val = float(value)
        # If it's a whole number, convert to int
        if num_val.is_integer():
            return int(num_val)
        return num_val
    except (ValueError, TypeError):
        return None


def import_admissions_data(academic_year=None):
    """Import admissions data from Excel to PostgreSQL"""

    print(f"Reading Excel file: {EXCEL_FILE}")
    try:
        # Read the Excel file
        df = pd.read_excel(EXCEL_FILE)
        print(f"✓ Loaded {len(df)} rows from Excel file")
        print(f"✓ Columns found: {list(df.columns)}\n")

    except FileNotFoundError:
        print(f"❌ Error: File not found at {EXCEL_FILE}")
        return False
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return False

    # Prompt for academic year if not provided
    if academic_year is None:
        print("No 'academic_year' column found in Excel file.")
        academic_year = input(
            "Enter the academic year for this data (e.g., '2022-2023'): "
        ).strip()

        if not academic_year:
            print("❌ Academic year is required!")
            return False

        print(f"✓ Using academic year: {academic_year}\n")

    # Connect to PostgreSQL
    print("Connecting to PostgreSQL database...")
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        conn.autocommit = False  # Use manual transaction control
        cursor = conn.cursor()
        print("✓ Connected successfully!\n")

    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return False

    # Check if unique constraint exists - in a separate transaction
    print("Checking database constraints...")
    try:
        cursor.execute(
            """
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name = 'admissions_data' 
            AND constraint_type = 'UNIQUE'
            AND constraint_name = 'admissions_data_unique'
        """
        )

        unique_constraint = cursor.fetchone()

        if not unique_constraint:
            print("Creating unique constraint...")
            try:
                cursor.execute(
                    """
                    ALTER TABLE admissions_data 
                    ADD CONSTRAINT admissions_data_unique 
                    UNIQUE (ipeds_id, academic_year)
                """
                )
                conn.commit()
                print("✓ Unique constraint created successfully\n")
            except psycopg2.errors.DuplicateTable as e:
                conn.rollback()
                print(f"✓ Constraint already exists\n")
            except Exception as e:
                conn.rollback()
                print(f"⚠️  Could not create constraint: {e}")
                print("Continuing anyway...\n")
        else:
            print(f"✓ Found unique constraint: {unique_constraint[0]}\n")
    except Exception as e:
        conn.rollback()
        print(f"⚠️  Error checking constraints: {e}")
        print("Continuing anyway...\n")

    # Prepare data for insertion
    print("Preparing data for import...")
    rows_to_insert = []
    skipped_rows = 0

    for idx, row in df.iterrows():
        try:
            # Extract and clean values
            data = {
                "ipeds_id": clean_numeric_value(row.get("ipeds_id", row.get("UNITID"))),
                "academic_year": academic_year,
                "applications_total": clean_numeric_value(
                    row.get("applications_total", row.get("APPLCN"))
                ),
                "admissions_total": clean_numeric_value(
                    row.get("admissions_total", row.get("ADMSSN"))
                ),
                "enrolled_total": clean_numeric_value(
                    row.get(
                        "enrollment_total", row.get("enrolled_total", row.get("ENRLT"))
                    )
                ),
                "acceptance_rate": clean_numeric_value(row.get("acceptance_rate")),
                "yield_rate": clean_numeric_value(row.get("yield_rate")),
                "sat_reading_25th": clean_numeric_value(
                    row.get("sat_reading_25th", row.get("SATVR25"))
                ),
                "sat_reading_50th": clean_numeric_value(
                    row.get("sat_reading_50th", row.get("SATVR50"))
                ),
                "sat_reading_75th": clean_numeric_value(
                    row.get("sat_reading_75th", row.get("SATVR75"))
                ),
                "sat_math_25th": clean_numeric_value(
                    row.get("sat_math_25th", row.get("SATMT25"))
                ),
                "sat_math_50th": clean_numeric_value(
                    row.get("sat_math_50th", row.get("SATMT50"))
                ),
                "sat_math_75th": clean_numeric_value(
                    row.get("sat_math_75th", row.get("SATMT75"))
                ),
                "percent_submitting_sat": clean_numeric_value(
                    row.get("percent_submitting_sat", row.get("SATPCT"))
                ),
            }

            # Skip rows without required fields
            if data["ipeds_id"] is None:
                skipped_rows += 1
                continue

            rows_to_insert.append(data)

        except Exception as e:
            print(f"⚠️  Error processing row {idx}: {e}")
            skipped_rows += 1
            continue

    print(f"✓ Prepared {len(rows_to_insert)} rows for import")
    if skipped_rows > 0:
        print(f"⚠️  Skipped {skipped_rows} rows due to missing required data\n")

    if len(rows_to_insert) == 0:
        print("❌ No valid rows to import!")
        return False

    # Insert data using INSERT ... ON CONFLICT
    print("Inserting data into database...")
    insert_query = """
        INSERT INTO admissions_data (
            ipeds_id, academic_year, applications_total, admissions_total,
            enrolled_total, acceptance_rate, yield_rate,
            sat_reading_25th, sat_reading_50th, sat_reading_75th,
            sat_math_25th, sat_math_50th, sat_math_75th,
            percent_submitting_sat, created_at
        ) VALUES %s
        ON CONFLICT (ipeds_id, academic_year) 
        DO UPDATE SET
            applications_total = EXCLUDED.applications_total,
            admissions_total = EXCLUDED.admissions_total,
            enrolled_total = EXCLUDED.enrolled_total,
            acceptance_rate = EXCLUDED.acceptance_rate,
            yield_rate = EXCLUDED.yield_rate,
            sat_reading_25th = EXCLUDED.sat_reading_25th,
            sat_reading_50th = EXCLUDED.sat_reading_50th,
            sat_reading_75th = EXCLUDED.sat_reading_75th,
            sat_math_25th = EXCLUDED.sat_math_25th,
            sat_math_50th = EXCLUDED.sat_math_50th,
            sat_math_75th = EXCLUDED.sat_math_75th,
            percent_submitting_sat = EXCLUDED.percent_submitting_sat
    """

    try:
        # Prepare values for batch insert
        values = [
            (
                row["ipeds_id"],
                row["academic_year"],
                row["applications_total"],
                row["admissions_total"],
                row["enrolled_total"],
                row["acceptance_rate"],
                row["yield_rate"],
                row["sat_reading_25th"],
                row["sat_reading_50th"],
                row["sat_reading_75th"],
                row["sat_math_25th"],
                row["sat_math_50th"],
                row["sat_math_75th"],
                row["percent_submitting_sat"],
                datetime.now(),
            )
            for row in rows_to_insert
        ]

        # Execute batch insert
        execute_values(cursor, insert_query, values)
        conn.commit()

        print(f"✅ Successfully imported {len(rows_to_insert)} rows!")

        # Get count of total records
        cursor.execute("SELECT COUNT(*) FROM admissions_data")
        total_count = cursor.fetchone()[0]
        print(f"✓ Total records in admissions_data table: {total_count}")

        # Show sample of data
        cursor.execute(
            """
            SELECT ipeds_id, academic_year, applications_total, admissions_total, acceptance_rate 
            FROM admissions_data 
            WHERE academic_year = %s
            ORDER BY ipeds_id 
            LIMIT 5
        """,
            (academic_year,),
        )
        print("\n📊 Sample of imported data:")
        print("-" * 80)
        for row in cursor.fetchall():
            print(
                f"IPEDS: {row[0]}, Year: {row[1]}, Apps: {row[2]}, Admits: {row[3]}, Accept Rate: {row[4]}%"
            )

    except Exception as e:
        print(f"❌ Error inserting data: {e}")
        conn.rollback()
        return False

    finally:
        cursor.close()
        conn.close()
        print("\n✓ Database connection closed.")

    return True


if __name__ == "__main__":
    print("=" * 80)
    print(" " * 20 + "Admissions Data Import Tool")
    print("=" * 80 + "\n")

    # You can pass academic year as command line argument
    academic_year = sys.argv[1] if len(sys.argv) > 1 else None

    success = import_admissions_data(academic_year)

    if success:
        print("\n" + "=" * 80)
        print("✅ Import completed successfully!")
        print("=" * 80)
        sys.exit(0)
    else:
        print("\n" + "=" * 80)
        print("❌ Import failed!")
        print("=" * 80)
        sys.exit(1)
