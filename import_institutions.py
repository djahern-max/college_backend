"""
Import institutions from CSV using FastAPI database connection
Place this file in the backend root directory (same level as run.py)

Works with both:
- Local: postgresql://postgres:@localhost:5432/college_db
- Production: postgresql://postgres:password@db:5432/magicscholar_db
"""

import sys
import os
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
from sqlalchemy import select, func
from app.core.database import SessionLocal, engine
from app.models.institution import Institution
from datetime import datetime

# Print database info for confirmation
print(f"Database URL: {os.getenv('DATABASE_URL', 'Not set - using app config')}")


class InstitutionsImporter:
    """Import institutions using FastAPI database models"""

    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.db = SessionLocal()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()

    def load_csv(self):
        """Load and validate CSV"""
        print(f"Loading CSV: {self.csv_path}")

        if not os.path.exists(self.csv_path):
            print(f"✗ CSV file not found: {self.csv_path}")
            return None

        df = pd.read_csv(self.csv_path)
        print(f"✓ Loaded {len(df)} rows from CSV")

        # Validate columns
        required = [
            "ipeds_id",
            "name",
            "city",
            "state",
            "control_type",
            "primary_image_url",
        ]
        missing = [col for col in required if col not in df.columns]

        if missing:
            print(f"✗ Missing columns: {missing}")
            return None

        print(f"✓ All required columns present")
        return df

    def get_existing_ipeds_ids(self):
        """Get set of existing IPEDS IDs"""
        stmt = select(Institution.ipeds_id)
        result = self.db.execute(stmt)
        existing = set(row[0] for row in result)
        print(f"✓ Found {len(existing)} existing institutions")
        return existing

    def filter_new_schools(self, df, existing_ids):
        """Filter out duplicates"""
        print("\nFiltering for new schools...")
        initial = len(df)
        df_new = df[~df["ipeds_id"].isin(existing_ids)].copy()
        filtered = initial - len(df_new)

        if filtered > 0:
            print(f"⚠ Filtered out {filtered} duplicates (already in database)")

        print(f"✓ {len(df_new)} new schools to import")
        return df_new

    def preview_data(self, df, n=10):
        """Show preview of data to import"""
        print(f"\nPreview (first {n} schools):")
        print("-" * 100)

        for _, row in df.head(n).iterrows():
            print(
                f"{row['ipeds_id']:6d} | {row['name'][:50]:50s} | {row['city'][:15]:15s} | {row['state']}"
            )

        print("-" * 100)

        # Summary by state
        print(f"\nSchools by state:")
        state_counts = df["state"].value_counts().sort_index()
        for state, count in state_counts.items():
            print(f"  {state}: {count}")

        # Summary by control type
        print(f"\nControl type breakdown:")
        for control_type, count in df["control_type"].value_counts().items():
            print(f"  {control_type}: {count}")

    def bulk_insert(self, df):
        """Bulk insert institutions"""
        print(f"\nInserting {len(df)} institutions...")

        institutions = []
        now = datetime.utcnow()

        for _, row in df.iterrows():
            inst = Institution(
                ipeds_id=int(row["ipeds_id"]),
                name=row["name"].strip(),
                city=row["city"].strip(),
                state=row["state"].strip(),
                control_type=row["control_type"].strip(),
                primary_image_url=(
                    row["primary_image_url"].strip()
                    if pd.notna(row["primary_image_url"])
                    else ""
                ),
                created_at=now,
                updated_at=now,
            )
            institutions.append(inst)

        try:
            # Bulk insert
            self.db.bulk_save_objects(institutions)
            self.db.commit()
            print(f"✓ Successfully inserted {len(institutions)} institutions")
            return True

        except Exception as e:
            self.db.rollback()
            print(f"✗ Error during insert: {e}")
            return False

    def verify_import(self, df):
        """Verify all schools were imported"""
        print("\nVerifying import...")

        ipeds_ids = df["ipeds_id"].tolist()
        stmt = (
            select(func.count())
            .select_from(Institution)
            .where(Institution.ipeds_id.in_(ipeds_ids))
        )
        count = self.db.execute(stmt).scalar()

        if count == len(df):
            print(f"✓ Verification successful: All {count} schools found")
            return True
        else:
            print(f"⚠ Verification issue: Expected {len(df)}, found {count}")
            return False

    def get_final_stats(self):
        """Get final database statistics"""
        print("\nFinal database statistics:")

        # Total count
        total = self.db.query(func.count(Institution.id)).scalar()
        print(f"  Total institutions: {total}")

        # States count
        states = self.db.query(func.count(Institution.state.distinct())).scalar()
        print(f"  States covered: {states}")

        # By control type
        stmt = select(Institution.control_type, func.count(Institution.id)).group_by(
            Institution.control_type
        )

        print(f"  By control type:")
        for control_type, count in self.db.execute(stmt):
            print(f"    {control_type}: {count}")

    def run(self, dry_run=False):
        """Main import process"""
        print("=" * 100)
        print("MAGICSCHOLAR INSTITUTIONS IMPORT")
        print("=" * 100)

        # Load CSV
        df = self.load_csv()
        if df is None:
            return False

        # Get existing schools
        existing_ids = self.get_existing_ipeds_ids()

        # Filter for new schools
        df_new = self.filter_new_schools(df, existing_ids)

        if len(df_new) == 0:
            print("\n⚠ No new schools to import")
            return True

        # Preview
        self.preview_data(df_new)

        if dry_run:
            print("\n" + "=" * 100)
            print("⚠ DRY RUN MODE - No data was imported")
            print("=" * 100)
            return True

        # Confirm
        print("\n" + "=" * 100)
        response = input(f"Import {len(df_new)} schools? (yes/no): ").strip().lower()

        if response != "yes":
            print("✗ Import cancelled")
            return False

        # Import
        success = self.bulk_insert(df_new)

        if success:
            # Verify
            self.verify_import(df_new)

            # Final stats
            self.get_final_stats()

            print("\n" + "=" * 100)
            print("✅ IMPORT COMPLETE")
            print("=" * 100)

        return success


if __name__ == "__main__":
    # Parse arguments
    dry_run = "--dry-run" in sys.argv or "-d" in sys.argv

    # CSV file path
    csv_path = "institutions_new_states.csv"

    # Check if custom path provided
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        csv_path = sys.argv[1]

    if dry_run:
        print("Running in DRY RUN mode (no data will be imported)\n")

    # Run import
    with InstitutionsImporter(csv_path) as importer:
        success = importer.run(dry_run=dry_run)

    sys.exit(0 if success else 1)
