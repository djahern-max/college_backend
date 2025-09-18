#!/usr/bin/env python3
"""
Check the structure of the processed CSV file
"""

import pandas as pd
from pathlib import Path


def check_csv_structure():
    """Check the column structure of the processed CSV"""

    # Load the CSV file
    csv_path = Path("magicscholar_financial_data.csv")

    print(f"Analyzing: {csv_path}")

    # Read the CSV
    df = pd.read_csv(csv_path)

    print(f"\nDataset Info:")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    print(f"\nColumn Names and Types:")
    print("-" * 50)

    for i, (col_name, dtype) in enumerate(df.dtypes.items()):
        # Get some sample values
        non_null_values = df[col_name].dropna()
        sample_values = (
            non_null_values.head(3).tolist()
            if len(non_null_values) > 0
            else ["No data"]
        )

        print(f"{i+1:2d}. {col_name}")
        print(f"    Type: {dtype}")
        print(
            f"    Non-null: {df[col_name].count()} / {len(df)} ({(df[col_name].count()/len(df)*100):.1f}%)"
        )
        print(f"    Sample: {sample_values}")
        print()

    print(f"\nFirst 3 rows (transposed for readability):")
    print("-" * 50)
    sample_df = df.head(3).T
    print(sample_df)

    print(f"\nSQL CREATE TABLE statement:")
    print("-" * 50)
    print("CREATE TABLE step2_ic2023_ay (")
    print("    id SERIAL PRIMARY KEY,")

    for col_name, dtype in df.dtypes.items():
        if col_name == "ipeds_id":
            print(f"    {col_name} INTEGER NOT NULL,")
        elif dtype == "object":  # String columns
            print(f"    {col_name} VARCHAR(255),")
        elif dtype in ["int64", "int32"]:
            print(f"    {col_name} INTEGER,")
        elif dtype in ["float64", "float32"]:
            print(f"    {col_name} FLOAT,")
        elif dtype == "bool":
            print(f"    {col_name} BOOLEAN,")
        else:
            print(f"    {col_name} TEXT,  -- Unknown type: {dtype}")

    print("    created_at TIMESTAMP DEFAULT NOW(),")
    print("    updated_at TIMESTAMP DEFAULT NOW()")
    print(");")


if __name__ == "__main__":
    check_csv_structure()
