#!/usr/bin/env python3
"""
Schema Verification Script
Compares MagicScholar (college_db) and CampusConnect (campusconnect_db) schemas
to ensure they're aligned for syncing.

Usage:
    python verify_schema_alignment.py
"""

import psycopg2
from typing import Dict, List, Tuple
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection strings
# Try to get from DATABASE_URL first, then fall back to specific vars
MAGICSCHOLAR_DB = os.getenv("DATABASE_URL") or os.getenv(
    "MAGICSCHOLAR_DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/college_db",
)
CAMPUSCONNECT_DB = os.getenv(
    "CAMPUSCONNECT_DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/campusconnect_db",
)

SHARED_TABLES = ["institutions", "scholarships", "admissions_data", "tuition_data"]


def get_table_columns(conn, table_name: str) -> Dict[str, str]:
    """Get column definitions for a table"""
    cursor = conn.cursor()
    cursor.execute(
        f"""
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position;
    """,
        (table_name,),
    )

    columns = {}
    for row in cursor.fetchall():
        col_name, data_type, is_nullable, default = row
        columns[col_name] = {
            "type": data_type,
            "nullable": is_nullable == "YES",
            "default": default,
        }
    cursor.close()
    return columns


def compare_tables(table_name: str) -> Tuple[bool, List[str]]:
    """Compare a table between both databases"""
    print(f"\n{'='*60}")
    print(f"Comparing: {table_name}")
    print(f"{'='*60}")

    differences = []

    # Connect to both databases
    magic_conn = psycopg2.connect(MAGICSCHOLAR_DB)
    campus_conn = psycopg2.connect(CAMPUSCONNECT_DB)

    magic_cols = get_table_columns(magic_conn, table_name)
    campus_cols = get_table_columns(campus_conn, table_name)

    # Check for columns in CampusConnect but missing in MagicScholar
    for col_name, col_def in campus_cols.items():
        if col_name not in magic_cols:
            diff = f"❌ MagicScholar MISSING column: {col_name} ({col_def['type']})"
            differences.append(diff)
            print(diff)

    # Check for columns in MagicScholar but missing in CampusConnect
    for col_name, col_def in magic_cols.items():
        if col_name not in campus_cols:
            diff = f"⚠️  CampusConnect MISSING column: {col_name} ({col_def['type']})"
            differences.append(diff)
            print(diff)

    # Check for type mismatches
    for col_name in set(magic_cols.keys()) & set(campus_cols.keys()):
        magic_type = magic_cols[col_name]["type"]
        campus_type = campus_cols[col_name]["type"]

        # Normalize type names (numeric vs double precision, etc.)
        magic_type_norm = normalize_type(magic_type)
        campus_type_norm = normalize_type(campus_type)

        if magic_type_norm != campus_type_norm:
            diff = f"⚠️  Type mismatch for '{col_name}': MagicScholar={magic_type} vs CampusConnect={campus_type}"
            differences.append(diff)
            print(diff)

    magic_conn.close()
    campus_conn.close()

    if not differences:
        print(f"✅ {table_name} - SCHEMAS MATCH PERFECTLY!")
        return True, []
    else:
        print(f"\n❌ {table_name} - Found {len(differences)} difference(s)")
        return False, differences


def normalize_type(pg_type: str) -> str:
    """Normalize PostgreSQL type names for comparison"""
    type_map = {
        "double precision": "float",
        "character varying": "varchar",
        "timestamp without time zone": "timestamp",
        "timestamp with time zone": "timestamptz",
    }
    return type_map.get(pg_type, pg_type)


def main():
    """Main verification function"""
    print("=" * 60)
    print("SCHEMA ALIGNMENT VERIFICATION")
    print("MagicScholar vs CampusConnect")
    print("=" * 60)

    all_aligned = True
    total_differences = 0

    for table in SHARED_TABLES:
        is_aligned, diffs = compare_tables(table)
        if not is_aligned:
            all_aligned = False
            total_differences += len(diffs)

    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)

    if all_aligned:
        print("✅ SUCCESS! All schemas are aligned.")
        print("   Databases are ready for syncing.")
    else:
        print(f"❌ FAILED! Found {total_differences} difference(s) across tables.")
        print("   Run the migration script to align schemas.")
        print("\n   Next steps:")
        print("   1. cd ~/projects/college-backend")
        print("   2. Copy the migration file to alembic/versions/")
        print("   3. alembic upgrade head")

    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("1. Both databases are running")
        print("2. Connection strings in .env are correct")
        print("3. You have psycopg2 installed: pip install psycopg2-binary")
