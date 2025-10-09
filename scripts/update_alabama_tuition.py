"""
Alabama Schools Tuition Data Updater - Docker/Production Version
Run from container: docker exec -it magicscholar_api python scripts/update_alabama_tuition.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import psycopg2
from datetime import datetime
from typing import Optional, Dict
import json

# For Docker, use environment variables or fallback to docker-compose service names
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", os.getenv("POSTGRES_DB", "magicscholar_db")),
    "user": os.getenv("DB_USER", os.getenv("POSTGRES_USER", "postgres")),
    "password": os.getenv("DB_PASSWORD", os.getenv("POSTGRES_PASSWORD", "")),
    "host": os.getenv("DB_HOST", "db"),  # 'db' is the docker-compose service name
    "port": os.getenv("DB_PORT", "5432"),
}

print(
    f"🔧 Connecting to: {DB_CONFIG['user']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
)

# Alabama schools with complete data
ALABAMA_SCHOOLS = {
    "Alabama A & M University": {
        "ipeds_id": None,
        "data": {
            "academic_year": "2024-2025",
            "data_source": "institution_website",
            "tuition_in_state": 10566.00,
            "tuition_out_state": 19176.00,
            "required_fees_in_state": None,
            "required_fees_out_state": None,
            "tuition_fees_in_state": 10566.00,
            "tuition_fees_out_state": 19176.00,
            "room_board_on_campus": 9465.00,
            "room_board_off_campus": None,
            "room_board_breakdown": {
                "note": "Annual room and board for 2024-2025",
                "on_campus_total": 9465.00,
            },
            "books_supplies": 1400.00,
            "personal_expenses": 3962.00,
            "transportation": None,
        },
    },
    "Auburn University": {
        "ipeds_id": None,
        "data": {
            "academic_year": "2025-2026",
            "data_source": "institution_website",
            "tuition_in_state": 6659.00,
            "tuition_out_state": 18011.00,
            "required_fees_in_state": None,
            "required_fees_out_state": None,
            "tuition_fees_in_state": 6659.00,
            "tuition_fees_out_state": 18011.00,
            "room_board_on_campus": 8605.00,
            "room_board_off_campus": 7936.00,
            "room_board_breakdown": {
                "on_campus": 8605.00,
                "off_campus": 7936.00,
                "living_with_parent": 4304.00,
            },
            "books_supplies": 1400.00,
            "personal_expenses": 3760.00,
            "transportation": None,
        },
    },
    "Auburn University at Montgomery": {
        "ipeds_id": None,
        "data": {
            "academic_year": "2025-2026",
            "data_source": "institution_website",
            "tuition_in_state": 6659.00,
            "tuition_out_state": 18011.00,
            "required_fees_in_state": None,
            "required_fees_out_state": None,
            "tuition_fees_in_state": 6659.00,
            "tuition_fees_out_state": 18011.00,
            "room_board_on_campus": 8605.00,
            "room_board_off_campus": 7936.00,
            "room_board_breakdown": {
                "on_campus": 8605.00,
                "off_campus": 7936.00,
                "living_with_parent": 4304.00,
            },
            "books_supplies": 1400.00,
            "personal_expenses": 3760.00,
            "transportation": None,
        },
    },
    "Jacksonville State University": {
        "ipeds_id": None,
        "data": {
            "academic_year": "2024-2025",
            "data_source": "institution_website",
            "tuition_in_state": 12426.00,
            "tuition_out_state": None,
            "required_fees_in_state": None,
            "required_fees_out_state": None,
            "tuition_fees_in_state": 12426.00,
            "tuition_fees_out_state": None,
            "room_board_on_campus": 8894.00,
            "room_board_off_campus": None,
            "room_board_breakdown": {"on_campus_total": 8894.00},
            "books_supplies": 998.00,
            "personal_expenses": 2506.00,
            "transportation": None,
        },
    },
    "Samford University": {
        "ipeds_id": None,
        "data": {
            "academic_year": "2025-2026",
            "data_source": "institution_website",
            "tuition_in_state": 40760.00,
            "tuition_out_state": 40760.00,
            "required_fees_in_state": 1150.00,
            "required_fees_out_state": 1150.00,
            "tuition_fees_in_state": 41910.00,
            "tuition_fees_out_state": 41910.00,
            "room_board_on_campus": 14260.00,
            "room_board_off_campus": None,
            "room_board_breakdown": {
                "room_vail_smith": 7600.00,
                "board_meal_plan": 6660.00,
                "total": 14260.00,
            },
            "books_supplies": 1400.00,
            "personal_expenses": None,
            "transportation": None,
        },
    },
    "The University of Alabama": {
        "ipeds_id": None,
        "data": {
            "academic_year": "2024-2025",
            "data_source": "institution_website",
            "tuition_in_state": 12180.00,
            "tuition_out_state": 34172.00,
            "required_fees_in_state": None,
            "required_fees_out_state": None,
            "tuition_fees_in_state": 12180.00,
            "tuition_fees_out_state": 34172.00,
            "room_board_on_campus": 10134.00,
            "room_board_off_campus": None,
            "room_board_breakdown": {
                "housing": 5900.00,
                "dining": 4234.00,
                "total": 10134.00,
                "note": "Based on 2021 data, actual costs may vary",
            },
            "books_supplies": 1400.00,
            "personal_expenses": None,
            "transportation": None,
        },
    },
    "Troy University": {
        "ipeds_id": None,
        "data": {
            "academic_year": "2024-2025",
            "data_source": "institution_website",
            "tuition_in_state": 10176.00,
            "tuition_out_state": None,
            "required_fees_in_state": None,
            "required_fees_out_state": None,
            "tuition_fees_in_state": 10176.00,
            "tuition_fees_out_state": None,
            "room_board_on_campus": 10068.00,
            "room_board_off_campus": 5430.00,
            "room_board_breakdown": {
                "on_campus": 10068.00,
                "living_with_parent": 5430.00,
            },
            "books_supplies": 1000.00,
            "personal_expenses": None,
            "transportation": 1000.00,
        },
    },
    "University of Alabama at Birmingham": {
        "ipeds_id": None,
        "data": {
            "academic_year": "2023-2024",
            "data_source": "institution_website",
            "tuition_in_state": 11640.00,
            "tuition_out_state": 28980.00,
            "required_fees_in_state": None,
            "required_fees_out_state": None,
            "tuition_fees_in_state": 11640.00,
            "tuition_fees_out_state": 28980.00,
            "room_board_on_campus": 9955.00,
            "room_board_off_campus": None,
            "room_board_breakdown": {
                "housing_min": 7180.00,
                "housing_max": 10050.00,
                "meal_plan_min": 450.00,
                "meal_plan_max": 5360.00,
                "typical_total": 9955.00,
            },
            "books_supplies": 1200.00,
            "personal_expenses": None,
            "transportation": None,
        },
    },
    "University of Alabama in Huntsville": {
        "ipeds_id": None,
        "data": {
            "academic_year": "2025-2026",
            "data_source": "institution_website",
            "tuition_in_state": 11770.00,
            "tuition_out_state": 24662.00,
            "required_fees_in_state": None,
            "required_fees_out_state": None,
            "tuition_fees_in_state": 11770.00,
            "tuition_fees_out_state": 24662.00,
            "room_board_on_campus": None,
            "room_board_off_campus": None,
            "room_board_breakdown": None,
            "books_supplies": 2796.00,
            "personal_expenses": None,
            "transportation": None,
        },
    },
    "University of North Alabama": {
        "ipeds_id": None,
        "data": {
            "academic_year": "2024-2025",
            "data_source": "institution_website",
            "tuition_in_state": 12240.00,
            "tuition_out_state": None,
            "required_fees_in_state": None,
            "required_fees_out_state": None,
            "tuition_fees_in_state": 12240.00,
            "tuition_fees_out_state": None,
            "room_board_on_campus": None,
            "room_board_off_campus": None,
            "room_board_breakdown": {
                "dining_per_term": 350.00,
                "dining_annual_estimate": 700.00,
                "note": "Housing costs not provided",
            },
            "books_supplies": 1400.00,
            "personal_expenses": None,
            "transportation": None,
        },
    },
    "University of South Alabama": {
        "ipeds_id": None,
        "data": {
            "academic_year": "2025-2026",
            "data_source": "institution_website",
            "tuition_in_state": 13460.00,
            "tuition_out_state": 27410.00,
            "required_fees_in_state": None,
            "required_fees_out_state": None,
            "tuition_fees_in_state": 13460.00,
            "tuition_fees_out_state": 27410.00,
            "room_board_on_campus": None,
            "room_board_off_campus": None,
            "room_board_breakdown": None,
            "books_supplies": 1400.00,
            "personal_expenses": None,
            "transportation": None,
        },
    },
    "University of West Alabama": {
        "ipeds_id": None,
        "data": {
            "academic_year": "2025-2026",
            "data_source": "institution_website",
            "tuition_in_state": None,
            "tuition_out_state": None,
            "required_fees_in_state": None,
            "required_fees_out_state": None,
            "tuition_fees_in_state": 23072.00,
            "tuition_fees_out_state": 36322.00,
            "room_board_on_campus": None,
            "room_board_off_campus": None,
            "room_board_breakdown": {
                "note": "Total includes tuition, fees, room, and board but not broken down"
            },
            "books_supplies": 1400.00,
            "personal_expenses": None,
            "transportation": None,
        },
    },
}


def get_ipeds_ids(conn):
    """Fetch IPEDS IDs for Alabama schools from database"""
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT name, ipeds_id 
        FROM institutions 
        WHERE state = 'AL' AND primary_image_url IS NOT NULL 
        ORDER BY name
    """
    )

    ipeds_map = {}
    for row in cursor.fetchall():
        name = row[0]
        ipeds_id = row[1]
        ipeds_map[name] = ipeds_id

        if name in ALABAMA_SCHOOLS:
            ALABAMA_SCHOOLS[name]["ipeds_id"] = ipeds_id

    cursor.close()
    return ipeds_map


def calculate_derived_fields(data: Dict) -> Dict:
    """Calculate tuition_fees totals and data completeness"""
    if data.get("tuition_fees_in_state") is None:
        if data.get("tuition_in_state") and data.get("required_fees_in_state"):
            data["tuition_fees_in_state"] = (
                data["tuition_in_state"] + data["required_fees_in_state"]
            )
        elif data.get("tuition_in_state"):
            data["tuition_fees_in_state"] = data["tuition_in_state"]

    if data.get("tuition_fees_out_state") is None:
        if data.get("tuition_out_state") and data.get("required_fees_out_state"):
            data["tuition_fees_out_state"] = (
                data["tuition_out_state"] + data["required_fees_out_state"]
            )
        elif data.get("tuition_out_state"):
            data["tuition_fees_out_state"] = data["tuition_out_state"]

    data["has_tuition_data"] = bool(
        data.get("tuition_in_state")
        or data.get("tuition_out_state")
        or data.get("tuition_fees_in_state")
    )
    data["has_fees_data"] = bool(
        data.get("required_fees_in_state") or data.get("required_fees_out_state")
    )
    data["has_living_data"] = bool(
        data.get("room_board_on_campus") or data.get("books_supplies")
    )

    fields_to_check = [
        "tuition_fees_in_state",
        "tuition_fees_out_state",
        "room_board_on_campus",
        "books_supplies",
    ]
    filled_fields = sum(1 for field in fields_to_check if data.get(field) is not None)
    data["data_completeness_score"] = int((filled_fields / len(fields_to_check)) * 100)

    data["validation_status"] = "VALIDATED"

    return data


def insert_or_update_tuition_data(conn, school_name: str, ipeds_id: int, data: Dict):
    """Insert or update tuition data for a school"""
    cursor = conn.cursor()

    data = calculate_derived_fields(data)
    room_board_json = (
        json.dumps(data.get("room_board_breakdown"))
        if data.get("room_board_breakdown")
        else None
    )

    cursor.execute(
        """
        SELECT id FROM tuition_data 
        WHERE ipeds_id = %s AND academic_year = %s AND data_source = %s
    """,
        (ipeds_id, data["academic_year"], data["data_source"]),
    )

    existing = cursor.fetchone()

    if existing:
        cursor.execute(
            """
            UPDATE tuition_data SET
                tuition_in_state = %s,
                tuition_out_state = %s,
                required_fees_in_state = %s,
                required_fees_out_state = %s,
                tuition_fees_in_state = %s,
                tuition_fees_out_state = %s,
                room_board_on_campus = %s,
                room_board_off_campus = %s,
                room_board_breakdown = %s,
                books_supplies = %s,
                personal_expenses = %s,
                transportation = %s,
                has_tuition_data = %s,
                has_fees_data = %s,
                has_living_data = %s,
                data_completeness_score = %s,
                validation_status = %s,
                updated_at = NOW()
            WHERE id = %s
        """,
            (
                data.get("tuition_in_state"),
                data.get("tuition_out_state"),
                data.get("required_fees_in_state"),
                data.get("required_fees_out_state"),
                data.get("tuition_fees_in_state"),
                data.get("tuition_fees_out_state"),
                data.get("room_board_on_campus"),
                data.get("room_board_off_campus"),
                room_board_json,
                data.get("books_supplies"),
                data.get("personal_expenses"),
                data.get("transportation"),
                data["has_tuition_data"],
                data["has_fees_data"],
                data["has_living_data"],
                data["data_completeness_score"],
                data["validation_status"],
                existing[0],
            ),
        )
        print(
            f"✅ Updated: {school_name} (Completeness: {data['data_completeness_score']}%)"
        )
    else:
        cursor.execute(
            """
            INSERT INTO tuition_data (
                ipeds_id, academic_year, data_source,
                tuition_in_state, tuition_out_state,
                required_fees_in_state, required_fees_out_state,
                tuition_fees_in_state, tuition_fees_out_state,
                room_board_on_campus, room_board_off_campus,
                room_board_breakdown,
                books_supplies, personal_expenses, transportation,
                has_tuition_data, has_fees_data, has_living_data,
                data_completeness_score, validation_status,
                created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, NOW(), NOW()
            )
        """,
            (
                ipeds_id,
                data["academic_year"],
                data["data_source"],
                data.get("tuition_in_state"),
                data.get("tuition_out_state"),
                data.get("required_fees_in_state"),
                data.get("required_fees_out_state"),
                data.get("tuition_fees_in_state"),
                data.get("tuition_fees_out_state"),
                data.get("room_board_on_campus"),
                data.get("room_board_off_campus"),
                room_board_json,
                data.get("books_supplies"),
                data.get("personal_expenses"),
                data.get("transportation"),
                data["has_tuition_data"],
                data["has_fees_data"],
                data["has_living_data"],
                data["data_completeness_score"],
                data["validation_status"],
            ),
        )
        print(
            f"✅ Inserted: {school_name} (Completeness: {data['data_completeness_score']}%)"
        )

    conn.commit()
    cursor.close()


def main():
    """Main function to update all Alabama schools data"""
    conn = None
    try:
        print(f"\n{'='*60}")
        print("Alabama Schools Tuition Data Updater")
        print(f"{'='*60}\n")

        conn = psycopg2.connect(**DB_CONFIG)
        print("🔌 Connected to database\n")

        ipeds_map = get_ipeds_ids(conn)
        print(f"📚 Found {len(ipeds_map)} Alabama schools in database\n")

        updated_count = 0
        missing_ipeds = []

        for school_name, school_info in ALABAMA_SCHOOLS.items():
            if school_info["ipeds_id"] is None:
                missing_ipeds.append(school_name)
                print(f"⚠️  Skipping {school_name} - No IPEDS ID found")
                continue

            insert_or_update_tuition_data(
                conn, school_name, school_info["ipeds_id"], school_info["data"]
            )
            updated_count += 1

        print(f"\n{'='*60}")
        print(f"✅ Successfully updated {updated_count} Alabama schools!")
        print(f"{'='*60}\n")

        if missing_ipeds:
            print(f"⚠️  {len(missing_ipeds)} schools missing IPEDS IDs:")
            for school in missing_ipeds:
                print(f"   - {school}")
            print()

        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                AVG(data_completeness_score)::int as avg_completeness,
                COUNT(*) as total_records,
                COUNT(CASE WHEN data_completeness_score >= 75 THEN 1 END) as high_quality,
                COUNT(CASE WHEN data_completeness_score >= 50 AND data_completeness_score < 75 THEN 1 END) as medium_quality,
                COUNT(CASE WHEN data_completeness_score < 50 THEN 1 END) as low_quality
            FROM tuition_data 
            WHERE ipeds_id IN (
                SELECT ipeds_id FROM institutions WHERE state = 'AL'
            ) AND data_source = 'institution_website'
        """
        )
        stats = cursor.fetchone()

        if stats and stats[1] > 0:
            print("📊 Data Quality Summary:")
            print(f"   Average Completeness: {stats[0]}%")
            print(f"   High Quality (75%+): {stats[2]} schools")
            print(f"   Medium Quality (50-74%): {stats[3]} schools")
            print(f"   Low Quality (<50%): {stats[4]} schools\n")

        cursor.close()

    except psycopg2.Error as e:
        print(f"❌ Database Error: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            print("🔌 Database connection closed")


if __name__ == "__main__":
    main()
