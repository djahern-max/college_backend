#!/usr/bin/env python3
"""
Analyze which fields are actually being used in Scholarship and Institution models
This helps identify bloat and unused fields that can be removed
"""

import psycopg2
from collections import defaultdict
import json

DB_CONFIG = {
    "dbname": "college_db",
    "user": "postgres",
    "password": "",
    "host": "localhost",
    "port": 5432,
}


def analyze_table(cursor, table_name):
    """Analyze a table to see which fields have data"""
    print(f"\n{'='*80}")
    print(f"ANALYZING TABLE: {table_name}")
    print(f"{'='*80}\n")

    # Get all columns
    cursor.execute(
        f"""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = '{table_name}'
        ORDER BY ordinal_position;
    """
    )
    columns = cursor.fetchall()

    # Get total row count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    total_rows = cursor.fetchone()[0]
    print(f"Total records: {total_rows}\n")

    if total_rows == 0:
        print("⚠️  No data in table - cannot analyze field usage\n")
        return

    results = []

    for col_name, data_type, is_nullable in columns:
        # Count non-null values
        cursor.execute(
            f"""
            SELECT COUNT(*) 
            FROM {table_name} 
            WHERE {col_name} IS NOT NULL
        """
        )
        non_null_count = cursor.fetchone()[0]

        # For array/JSON fields, also check if they're non-empty
        if "json" in data_type.lower():
            cursor.execute(
                f"""
                SELECT COUNT(*) 
                FROM {table_name} 
                WHERE {col_name} IS NOT NULL 
                AND {col_name}::text NOT IN ('{{}}', '[]', 'null')
            """
            )
            non_empty_count = cursor.fetchone()[0]
        elif "ARRAY" in data_type.upper() or "[]" in data_type:
            cursor.execute(
                f"""
                SELECT COUNT(*) 
                FROM {table_name} 
                WHERE {col_name} IS NOT NULL 
                AND array_length({col_name}, 1) > 0
            """
            )
            non_empty_count = cursor.fetchone()[0]
        else:
            non_empty_count = non_null_count

        usage_percent = (non_empty_count / total_rows * 100) if total_rows > 0 else 0

        # Categorize field
        if usage_percent == 0:
            category = "❌ UNUSED"
            status = "REMOVE"
        elif usage_percent < 5:
            category = "⚠️  BARELY USED"
            status = "CONSIDER REMOVING"
        elif usage_percent < 25:
            category = "🟡 LOW USAGE"
            status = "REVIEW"
        elif usage_percent < 75:
            category = "🟢 MODERATE"
            status = "KEEP"
        else:
            category = "✅ HIGH USAGE"
            status = "KEEP"

        results.append(
            {
                "field": col_name,
                "type": data_type,
                "nullable": is_nullable,
                "usage_percent": usage_percent,
                "used_count": non_empty_count,
                "category": category,
                "status": status,
            }
        )

    # Print results grouped by status
    print("FIELD USAGE ANALYSIS:")
    print("-" * 80)

    for status_group in ["REMOVE", "CONSIDER REMOVING", "REVIEW", "KEEP"]:
        fields_in_group = [r for r in results if r["status"] == status_group]
        if fields_in_group:
            print(f"\n{status_group} ({len(fields_in_group)} fields):")
            print("-" * 80)
            for r in sorted(fields_in_group, key=lambda x: x["usage_percent"]):
                print(
                    f"{r['category']} {r['field']:40s} {r['type']:20s} {r['usage_percent']:>6.1f}% used ({r['used_count']}/{total_rows})"
                )

    return results


def generate_recommendations(results, table_name):
    """Generate recommendations for model cleanup"""
    print(f"\n{'='*80}")
    print(f"RECOMMENDATIONS FOR {table_name.upper()}")
    print(f"{'='*80}\n")

    to_remove = [r["field"] for r in results if r["status"] == "REMOVE"]
    to_consider = [r["field"] for r in results if r["status"] == "CONSIDER REMOVING"]
    to_review = [r["field"] for r in results if r["status"] == "REVIEW"]

    if to_remove:
        print("🗑️  SAFE TO REMOVE (0% usage):")
        for field in to_remove:
            print(f"    - {field}")
        print()

    if to_consider:
        print("⚠️  CONSIDER REMOVING (<5% usage):")
        for field in to_consider:
            print(f"    - {field}")
        print()

    if to_review:
        print("🔍 REVIEW (<25% usage - may be niche but important):")
        for field in to_review:
            print(f"    - {field}")
        print()

    keep_count = len([r for r in results if r["status"] == "KEEP"])
    print(f"✅ KEEP: {keep_count} fields with >25% usage\n")

    # Calculate potential savings
    total_fields = len(results)
    removable_fields = len(to_remove) + len(to_consider)
    savings_percent = (removable_fields / total_fields * 100) if total_fields > 0 else 0

    print(f"📊 SUMMARY:")
    print(f"    Total fields: {total_fields}")
    print(f"    Potentially removable: {removable_fields} ({savings_percent:.1f}%)")
    print(f"    Fields to keep: {keep_count}")


def main():
    """Main analysis function"""
    print("\n" + "=" * 80)
    print("SCHOLARSHIP & INSTITUTION MODEL FIELD USAGE ANALYZER")
    print("=" * 80)

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Analyze scholarships table
        scholarship_results = analyze_table(cursor, "scholarships")
        if scholarship_results:
            generate_recommendations(scholarship_results, "scholarships")

        # Analyze institutions table
        institution_results = analyze_table(cursor, "institutions")
        if institution_results:
            generate_recommendations(institution_results, "institutions")

        cursor.close()
        conn.close()

        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE!")
        print("=" * 80)
        print("\nNext steps:")
        print("1. Review fields marked for removal")
        print("2. Check if any 'BARELY USED' fields are critical for future features")
        print("3. Create Alembic migration to drop unused columns")
        print("4. Update model files to remove unused fields")
        print("5. Update schemas to match simplified models\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("1. PostgreSQL is running")
        print("2. Database 'college_db' exists")
        print("3. You have data in the tables")
        print("4. Credentials in DB_CONFIG are correct\n")


if __name__ == "__main__":
    main()
