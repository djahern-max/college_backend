"""
Find which institutions are missing tuition data

Usage:
    python find_institutions_without_tuition.py
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()


def find_institutions_without_tuition():
    # Connect to database
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)

    with engine.connect() as conn:
        # Find institutions without any tuition data
        query = text(
            """
            SELECT 
                i.ipeds_id,
                i.name,
                i.state,
                i.city
            FROM institutions i
            LEFT JOIN tuition_data t ON i.ipeds_id = t.ipeds_id
            WHERE t.id IS NULL
            ORDER BY i.state, i.name
        """
        )

        result = conn.execute(query)
        missing = list(result)

        if missing:
            print(f"\n{'=' * 100}")
            print(f"INSTITUTIONS WITHOUT TUITION DATA: {len(missing)} schools")
            print("=" * 100)
            print(f"{'IPEDS ID':<10} {'State':<7} {'City':<20} {'Institution Name'}")
            print("-" * 100)

            for row in missing:
                ipeds_id, name, state, city = row
                print(f"{ipeds_id:<10} {state:<7} {city:<20} {name}")

            print("=" * 100)

            # Summary by state
            print("\nBreakdown by state:")
            state_counts = {}
            for row in missing:
                state = row[2]
                state_counts[state] = state_counts.get(state, 0) + 1

            for state, count in sorted(state_counts.items()):
                print(f"  {state}: {count}")
        else:
            print("\n✓ All institutions have tuition data!")

        # Also show summary stats
        print(f"\n{'=' * 100}")
        print("SUMMARY STATISTICS:")
        print("=" * 100)

        stats_query = text(
            """
            SELECT 
                COUNT(DISTINCT i.ipeds_id) as total_institutions,
                COUNT(DISTINCT t.ipeds_id) as institutions_with_tuition,
                COUNT(DISTINCT i.ipeds_id) - COUNT(DISTINCT t.ipeds_id) as missing_tuition
            FROM institutions i
            LEFT JOIN tuition_data t ON i.ipeds_id = t.ipeds_id
        """
        )

        result = conn.execute(stats_query)
        stats = result.fetchone()

        print(f"Total institutions in database: {stats[0]}")
        print(f"Institutions with tuition data: {stats[1]}")
        print(f"Institutions missing tuition data: {stats[2]}")
        print(f"Coverage: {stats[1]/stats[0]*100:.1f}%")
        print("=" * 100)


if __name__ == "__main__":
    find_institutions_without_tuition()
