#!/usr/bin/env python3
"""
Fixed Tuition Processor - Using the exact logic from the working simple test
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import json

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def safe_float(value):
    """Simple safe float conversion - copied from working test"""
    if pd.isna(value):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        value = value.strip()
        if value in ["", ".", "NULL", "N/A", "-", "Not applicable"]:
            return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def process_ipeds_data():
    """Process IPEDS data using the working logic from simple test"""

    # Find the data file
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    data_file = project_root / "data" / "raw_data" / "ic2023_ay.csv"
    processed_dir = project_root / "processed_data"
    processed_dir.mkdir(exist_ok=True)

    print(f"📄 Found data file: {data_file}")

    # Load data
    logger.info(f"Loading data from {data_file}")
    df = pd.read_csv(data_file, low_memory=False)
    logger.info(f"Loaded {len(df)} records with {len(df.columns)} columns")

    # Process records
    processed_records = []

    for index, row in df.iterrows():
        try:
            # Get UNITID
            unitid = safe_float(row.get("UNITID"))
            if not unitid:
                continue

            unitid = int(unitid)

            # Get financial data
            tuition_in_state = safe_float(row.get("CHG2AT3"))
            tuition_out_state = safe_float(row.get("CHG3AT3"))
            fees_in_state = safe_float(row.get("CHG2AF3"))
            fees_out_state = safe_float(row.get("CHG3AF3"))
            combined_in_state = safe_float(row.get("CHG2AY3"))
            combined_out_state = safe_float(row.get("CHG3AY3"))

            # Living expenses
            room_board_on = safe_float(row.get("CHG5AY3"))
            room_board_off = safe_float(row.get("CHG6AY3"))
            books_supplies = safe_float(row.get("CHG4AY3"))
            personal_expenses = safe_float(row.get("CHG7AY3"))
            transportation = safe_float(row.get("CHG8AY3"))

            # Skip if no tuition data
            has_any_data = bool(
                tuition_in_state
                or tuition_out_state
                or combined_in_state
                or combined_out_state
            )
            if not has_any_data:
                continue

            # Calculate fees if missing
            if not fees_in_state and combined_in_state and tuition_in_state:
                fees_in_state = max(0, combined_in_state - tuition_in_state)
            if not fees_out_state and combined_out_state and tuition_out_state:
                fees_out_state = max(0, combined_out_state - tuition_out_state)

            # Data quality assessment
            has_tuition_data = bool(tuition_in_state or tuition_out_state)
            has_fees_data = bool(fees_in_state or fees_out_state)
            has_living_data = bool(room_board_on or room_board_off)

            data_completeness_score = sum(
                [
                    25 if tuition_in_state else 0,
                    25 if tuition_out_state else 0,
                    15 if combined_in_state else 0,
                    15 if combined_out_state else 0,
                    10 if room_board_on else 0,
                    5 if room_board_off else 0,
                    3 if books_supplies else 0,
                    2 if personal_expenses else 0,
                ]
            )

            # Create record
            record = {
                "ipeds_id": unitid,
                "academic_year": "2023-24",
                "data_source": "IC2023_AY",
                "tuition_in_state": tuition_in_state,
                "tuition_out_state": tuition_out_state,
                "required_fees_in_state": fees_in_state,
                "required_fees_out_state": fees_out_state,
                "tuition_fees_in_state": combined_in_state,
                "tuition_fees_out_state": combined_out_state,
                "room_board_on_campus": room_board_on,
                "room_board_off_campus": room_board_off,
                "books_supplies": books_supplies,
                "personal_expenses": personal_expenses,
                "transportation": transportation,
                "has_tuition_data": has_tuition_data,
                "has_fees_data": has_fees_data,
                "has_living_data": has_living_data,
                "data_completeness_score": data_completeness_score,
                "validation_status": (
                    "clean" if data_completeness_score >= 70 else "incomplete"
                ),
            }

            processed_records.append(record)

            # Progress every 500 records
            if len(processed_records) % 500 == 0:
                logger.info(f"Processed {len(processed_records)} records so far...")

        except Exception as e:
            logger.error(f"Error processing row {index}: {e}")
            continue

    logger.info(f"Successfully processed {len(processed_records)} financial records")

    if len(processed_records) == 0:
        print("❌ No records were processed!")
        return False

    # Generate basic analytics
    tuition_values = [
        r["tuition_in_state"] for r in processed_records if r["tuition_in_state"]
    ]

    analytics = {
        "dataset_info": {
            "total_institutions": len(processed_records),
            "institutions_with_tuition_data": len(tuition_values),
            "data_completeness_rate": round(
                (len(tuition_values) / len(processed_records)) * 100, 1
            ),
            "academic_year": "2023-24",
        },
        "tuition_statistics": {
            "in_state_tuition": {
                "count": len(tuition_values),
                "mean": round(np.mean(tuition_values)) if tuition_values else 0,
                "median": round(np.median(tuition_values)) if tuition_values else 0,
                "min": round(np.min(tuition_values)) if tuition_values else 0,
                "max": round(np.max(tuition_values)) if tuition_values else 0,
            }
        },
    }

    # Export to CSV
    output_filename = f"magicscholar_financial_data.csv"
    output_path = processed_dir / output_filename

    df_output = pd.DataFrame(processed_records)
    df_output.to_csv(output_path, index=False, na_rep="")
    logger.info(f"Exported {len(df_output)} records to {output_path}")

    # Save analytics
    analytics_path = processed_dir / "magicscholar_analytics.json"
    with open(analytics_path, "w") as f:
        json.dump(analytics, f, indent=2)

    # Print summary
    print("\n" + "=" * 60)
    print("🎓 MAGICSCHOLAR TUITION DATA SUMMARY")
    print("=" * 60)

    dataset_info = analytics["dataset_info"]
    tuition_stats = analytics["tuition_statistics"]["in_state_tuition"]

    print(f"📊 Dataset: {dataset_info['total_institutions']} institutions")
    print(
        f"✅ Complete data: {dataset_info['institutions_with_tuition_data']} ({dataset_info['data_completeness_rate']}%)"
    )
    print(f"📅 Academic Year: {dataset_info['academic_year']}")

    print(f"\n💰 In-State Tuition Statistics:")
    print(f"   Mean: ${tuition_stats['mean']:,}")
    print(f"   Median: ${tuition_stats['median']:,}")
    print(f"   Range: ${tuition_stats['min']:,} - ${tuition_stats['max']:,}")

    print(f"\n📁 Files created:")
    print(f"   - Financial data: {output_path}")
    print(f"   - Analytics: {analytics_path}")

    return True


if __name__ == "__main__":
    success = process_ipeds_data()
    if success:
        print("\n✅ Processing completed successfully!")
    else:
        print("\n❌ Processing failed!")
        exit(1)
