#!/usr/bin/env python3
"""
Update NH Schools Tuition Data - FIXED VERSION
Matches actual database schema
ALL 12 NH Schools - 2024-2025 academic year
"""

import os
import sys
import psycopg2

# Complete tuition data for ALL 12 NH schools (2024-2025 academic year)
NH_TUITION_DATA = {
    183044: {  # University of New Hampshire-Main Campus
        "name": "University of New Hampshire-Main Campus",
        "tuition_in_state": 15908,
        "tuition_out_state": 37070,
        "room_board_on_campus": 14704,
    },
    182670: {  # Dartmouth College
        "name": "Dartmouth College",
        "tuition_in_state": 66441,
        "tuition_out_state": 66441,
        "room_board_on_campus": 22039,
    },
    183026: {  # Southern New Hampshire University
        "name": "Southern New Hampshire University",
        "tuition_in_state": 16200,
        "tuition_out_state": 16200,
        "room_board_on_campus": 22688,
    },
    183080: {  # Plymouth State University
        "name": "Plymouth State University",
        "tuition_in_state": 11938,
        "tuition_out_state": 22878,
        "room_board_on_campus": 12104,
    },
    183062: {  # Keene State College
        "name": "Keene State College",
        "tuition_in_state": 11828,
        "tuition_out_state": 23884,
        "room_board_on_campus": 13860,
    },
    183239: {  # Saint Anselm College
        "name": "Saint Anselm College",
        "tuition_in_state": 47400,
        "tuition_out_state": 47400,
        "room_board_on_campus": 17020,
    },
    182795: {  # Franklin Pierce University
        "name": "Franklin Pierce University",
        "tuition_in_state": 42096,
        "tuition_out_state": 42096,
        "room_board_on_campus": 15300,
    },
    182634: {  # Colby-Sawyer College
        "name": "Colby-Sawyer College",
        "tuition_in_state": 17500,
        "tuition_out_state": 17500,
        "room_board_on_campus": 16840,
    },
    182980: {  # New England College
        "name": "New England College",
        "tuition_in_state": 38778,
        "tuition_out_state": 38778,
        "room_board_on_campus": 17006,
    },
    183071: {  # University of New Hampshire at Manchester
        "name": "University of New Hampshire at Manchester",
        "tuition_in_state": 15240,
        "tuition_out_state": 36330,
        "room_board_on_campus": 13000,
    },
    183150: {  # Great Bay Community College
        "name": "Great Bay Community College",
        "tuition_in_state": 6900,
        "tuition_out_state": 15180,
        "room_board_on_campus": 17686,
    },
    182917: {  # Magdalen College
        "name": "Magdalen College",
        "tuition_in_state": 10300,
        "tuition_out_state": 10300,
        "room_board_on_campus": 10900,
    },
}


def get_database_connection(db_type="local"):
    """Connect to database"""
    if db_type == "local":
        db_url = os.getenv(
            "DATABASE_URL", "postgresql://postgres:@localhost:5432/college_db"
        )
    else:
        db_password = os.getenv("DB_PASSWORD")
        if not db_password:
            print("ERROR: DB_PASSWORD environment variable not set for production")
            sys.exit(1)
        db_url = f"postgresql://postgres:{db_password}@db:5432/magicscholar_db"

    try:
        conn = psycopg2.connect(db_url)
        print(f"✓ Connected to {db_type} database")
        return conn
    except Exception as e:
        print(f"✗ Failed to connect to {db_type} database: {e}")
        sys.exit(1)


def check_existing_records(conn):
    """Check which records exist"""
    cursor = conn.cursor()

    ipeds_ids = list(NH_TUITION_DATA.keys())
    query = """
        SELECT ipeds_id, academic_year, tuition_in_state, tuition_out_state 
        FROM tuition_data 
        WHERE ipeds_id = ANY(%s)
    """

    cursor.execute(query, (ipeds_ids,))
    results = cursor.fetchall()

    existing = {}
    for row in results:
        ipeds_id, academic_year, tuition_in, tuition_out = row
        existing[ipeds_id] = {
            "academic_year": academic_year,
            "has_tuition": tuition_in is not None and tuition_out is not None,
        }

    cursor.close()
    return existing


def update_tuition_data(conn, dry_run=False):
    """Update tuition data - ONLY columns that exist in schema"""
    cursor = conn.cursor()

    print("\n" + "=" * 80)
    print("UPDATING NH SCHOOLS TUITION DATA")
    print("=" * 80)

    existing = check_existing_records(conn)

    updated_count = 0
    skipped_count = 0

    for ipeds_id, data in NH_TUITION_DATA.items():
        school_name = data["name"]

        if ipeds_id not in existing:
            print(f"\n✗ {school_name} (IPEDS: {ipeds_id})")
            print(f"  No record found - skipping")
            skipped_count += 1
            continue

        academic_year = existing[ipeds_id]["academic_year"]

        # Update query - ONLY fields that exist in your schema
        update_query = """
            UPDATE tuition_data
            SET 
                tuition_in_state = %s,
                tuition_out_state = %s,
                room_board_on_campus = %s,
                updated_at = NOW()
            WHERE ipeds_id = %s 
              AND academic_year = %s
            RETURNING id
        """

        values = (
            data["tuition_in_state"],
            data["tuition_out_state"],
            data["room_board_on_campus"],
            ipeds_id,
            academic_year,
        )

        if dry_run:
            print(f"\n✓ {school_name} (IPEDS: {ipeds_id}) [DRY RUN]")
            print(f"  Academic Year: {academic_year}")
            print(f"  Tuition In-State: ${data['tuition_in_state']:,}")
            print(f"  Tuition Out-of-State: ${data['tuition_out_state']:,}")
            print(f"  Room & Board: ${data['room_board_on_campus']:,}")
        else:
            try:
                cursor.execute(update_query, values)
                if cursor.fetchone():
                    updated_count += 1
                    print(f"\n✓ {school_name} (IPEDS: {ipeds_id}) - UPDATED")
                    print(f"  Tuition In-State: ${data['tuition_in_state']:,}")
                    print(f"  Tuition Out-of-State: ${data['tuition_out_state']:,}")
            except Exception as e:
                print(f"\n✗ {school_name} (IPEDS: {ipeds_id}) - ERROR")
                print(f"  {str(e)}")
                skipped_count += 1

    cursor.close()

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Schools updated: {updated_count}")
    print(f"Schools skipped: {skipped_count}")
    print(f"Total NH schools: {len(NH_TUITION_DATA)}")

    return updated_count


def verify_updates(conn):
    """Verify the updates"""
    cursor = conn.cursor()

    print("\n" + "=" * 80)
    print("VERIFICATION - All NH Schools with Complete Data")
    print("=" * 80)

    query = """
        SELECT 
            i.ipeds_id,
            i.name,
            t.academic_year,
            t.tuition_in_state,
            t.tuition_out_state,
            t.required_fees_in_state,
            t.required_fees_out_state,
            (t.tuition_in_state + COALESCE(t.required_fees_in_state, 0)) AS total_in_state,
            (t.tuition_out_state + COALESCE(t.required_fees_out_state, 0)) AS total_out_state,
            t.room_board_on_campus
        FROM institutions i
        JOIN tuition_data t ON i.ipeds_id = t.ipeds_id
        WHERE i.state = 'NH'
          AND t.tuition_in_state IS NOT NULL
        ORDER BY i.name
    """

    cursor.execute(query)
    results = cursor.fetchall()

    if results:
        print(
            f"\n{'School':<45} {'Year':<10} {'In-State':<12} {'Out-State':<12} {'R&B':<10}"
        )
        print("-" * 95)
        for row in results:
            ipeds_id, name, year, tis, tos, fis, fos, total_in, total_out, rb = row
            name_short = name[:44]
            rb_val = rb if rb else 0
            print(
                f"{name_short:<45} {year:<10} ${total_in:>10,} ${total_out:>10,} ${rb_val:>8,}"
            )
        print("-" * 95)
        print(f"Total schools with complete data: {len(results)}")
    else:
        print("No records found")

    cursor.close()


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Update NH schools tuition data")
    parser.add_argument(
        "--db",
        choices=["local", "prod"],
        default="local",
        help="Which database to update (default: local)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be updated without making changes",
    )

    args = parser.parse_args()

    print("\n" + "=" * 80)
    print("NH SCHOOLS TUITION DATA UPDATE SCRIPT - FIXED VERSION")
    print("=" * 80)
    print(f"Database: {args.db}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE UPDATE'}")
    print(f"Schools to update: {len(NH_TUITION_DATA)}")

    conn = get_database_connection(args.db)

    try:
        updated = update_tuition_data(conn, dry_run=args.dry_run)

        if not args.dry_run and updated > 0:
            conn.commit()
            print("\n✓ Changes committed to database")
            verify_updates(conn)
        elif args.dry_run:
            print("\n⚠ DRY RUN - No changes were made to the database")
            print("  Run without --dry-run to apply changes")

    except Exception as e:
        conn.rollback()
        print(f"\n✗ Error occurred: {e}")
        print("✗ Changes rolled back")
        sys.exit(1)
    finally:
        conn.close()
        print("\n✓ Database connection closed")


if __name__ == "__main__":
    main()
