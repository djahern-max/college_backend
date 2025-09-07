#!/usr/bin/env python3
"""
Check what carnegie_basic values are in your CSV
"""

import pandas as pd

# Read the CSV
df = pd.read_csv("data/raw_data/institutions_processed.csv")

print("Unique carnegie_basic values in your CSV:")
print("=" * 50)
carnegie_counts = df["carnegie_basic"].value_counts(dropna=False)
print(carnegie_counts)

print(f"\nTotal institutions: {len(df)}")
print(f"Institutions with null/NaN carnegie_basic: {df['carnegie_basic'].isna().sum()}")

# Check what Pacific Union College has
puc = df[df["name"].str.contains("Pacific Union College", na=False)]
if not puc.empty:
    print(f"\nPacific Union College carnegie_basic value:")
    print(f"'{puc.iloc[0]['carnegie_basic']}'")

print(f"\nSample institutions with carnegie_basic values:")
print("=" * 50)
for carnegie in df["carnegie_basic"].dropna().unique()[:5]:  # Show first 5
    examples = df[df["carnegie_basic"] == carnegie][
        ["name", "state", "carnegie_basic"]
    ].head(2)
    print(f"\nCarnegie: '{carnegie}'")
    for _, row in examples.iterrows():
        print(f"  - {row['name']} ({row['state']})")
