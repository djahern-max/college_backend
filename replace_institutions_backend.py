import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import sys
import os

def replace_institutions_data(excel_path, db_params):
    """
    Replace institutions table data with data from Excel file
    """
    try:
        # Read the Excel file
        print(f"Reading {excel_path}...")
        df = pd.read_excel(excel_path)
        print(f"Found {len(df)} rows in Excel file")
        print(f"Columns: {list(df.columns)}")
        
        # Show first few rows for verification
        print("\nFirst 3 rows:")
        print(df.head(3).to_string())
        
        # Connect to database
        print("\nConnecting to database...")
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        
        # Get current institutions table structure
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'institutions' 
            ORDER BY ordinal_position
        """)
        table_columns = cur.fetchall()
        print("\nCurrent institutions table structure:")
        for col_name, col_type in table_columns:
            print(f"  {col_name}: {col_type}")
        
        # Backup current data
        print("\nChecking current institutions data...")
        cur.execute("SELECT COUNT(*) FROM institutions")
        current_count = cur.fetchone()[0]
        print(f"Current row count: {current_count}")
        
        # Ask for confirmation
        print("\n" + "="*60)
        print("CONFIRMATION REQUIRED")
        print("="*60)
        print(f"This will DELETE {current_count} existing rows")
        print(f"And INSERT {len(df)} new rows")
        response = input("\nType 'YES' to proceed: ")
        
        if response != 'YES':
            print("Operation cancelled.")
            cur.close()
            conn.close()
            return False
        
        # Begin transaction
        print("\nStarting replacement...")
        
        # Clear existing data
        cur.execute("DELETE FROM institutions")
        print(f"Deleted {cur.rowcount} rows")
        
        # Prepare data for insertion
        # Convert DataFrame to list of tuples, handling NaN values
        df_clean = df.where(pd.notna(df), None)
        records = [tuple(x) for x in df_clean.to_numpy()]
        columns = list(df.columns)
        
        # Create INSERT query
        columns_str = ', '.join([f'"{col}"' for col in columns])
        insert_query = f'INSERT INTO institutions ({columns_str}) VALUES %s'
        
        # Insert new data using execute_values for better performance
        print(f"Inserting {len(records)} new rows...")
        execute_values(cur, insert_query, records)
        
        # Commit transaction
        conn.commit()
        print(f"Successfully inserted {len(records)} rows")
        
        # Verify
        cur.execute("SELECT COUNT(*) FROM institutions")
        new_count = cur.fetchone()[0]
        print(f"\nVerification - New row count: {new_count}")
        
        # Show sample of new data
        cur.execute("SELECT * FROM institutions LIMIT 3")
        sample = cur.fetchall()
        print("\nSample of new data (first 3 rows):")
        for row in sample:
            print(f"  {row[:3]}...")  # Show first 3 columns
        
        cur.close()
        conn.close()
        
        print("\n✓ Institutions table successfully replaced!")
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Database connection parameters
    db_params = {
        'dbname': 'college_db',
        'user': 'postgres',
        'password': '',  # Add password if needed
        'host': 'localhost',
        'port': 5432
    }
    
    # Excel file path - relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(script_dir, 'data', 'institutions_export.xlsx')
    
    print(f"Script directory: {script_dir}")
    print(f"Excel file path: {excel_path}")
    
    if not os.path.exists(excel_path):
        print(f"\n✗ Error: Excel file not found at {excel_path}")
        sys.exit(1)
    
    # Run replacement
    success = replace_institutions_data(excel_path, db_params)
    sys.exit(0 if success else 1)
