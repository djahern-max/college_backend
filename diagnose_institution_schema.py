#!/usr/bin/env python3
"""
Diagnostic script to identify the Institution model/database schema mismatch.
"""

import sys
from sqlalchemy import create_engine, inspect, text
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from app.models.institution import Institution
    from app.core.database import Base
except ImportError as e:
    print(f"Error importing models: {e}")
    print("Make sure you run this from the project root directory")
    sys.exit(1)


DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/unified_test"

DEPRECATED_FIELDS = {
    'admin_verified',
    'completeness_score',
    'cost_data_verified',
    'cost_data_verified_at',
    'admissions_data_verified',
    'admissions_data_verified_at',
    'last_admin_update',
    'data_quality_notes',
}


def check_model_definition():
    """Check if Institution model has deprecated fields."""
    print("\n" + "="*70)
    print("CHECKING MODEL DEFINITION")
    print("="*70)
    
    # Get all columns defined in the model
    model_columns = set()
    for column in Institution.__table__.columns:
        model_columns.add(column.name)
    
    # Check for deprecated fields
    deprecated_in_model = model_columns & DEPRECATED_FIELDS
    
    if deprecated_in_model:
        print("❌ PROBLEM: Deprecated fields found in Institution model:")
        for field in sorted(deprecated_in_model):
            print(f"   - {field}")
        print("\n💡 FIX: Remove these fields from app/models/institution.py")
        return False
    else:
        print("✅ Institution model is clean (no deprecated fields)")
        print(f"   Model has {len(model_columns)} columns")
        return True


def check_database_schema():
    """Check if database has deprecated columns."""
    print("\n" + "="*70)
    print("CHECKING DATABASE SCHEMA")
    print("="*70)
    
    try:
        engine = create_engine(DATABASE_URL)
        inspector = inspect(engine)
        
        # Get columns in institutions table
        db_columns = set()
        for column in inspector.get_columns('institutions'):
            db_columns.add(column['name'])
        
        # Check for deprecated fields
        deprecated_in_db = db_columns & DEPRECATED_FIELDS
        
        if deprecated_in_db:
            print("❌ PROBLEM: Deprecated columns found in database:")
            for field in sorted(deprecated_in_db):
                print(f"   - {field}")
            print("\n💡 FIX: Run SQL commands to remove these columns")
            return False
        else:
            print("✅ Database schema is clean (no deprecated columns)")
            print(f"   Table has {len(db_columns)} columns")
            return True
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False


def show_current_state():
    """Show current columns in both model and database."""
    print("\n" + "="*70)
    print("CURRENT STATE COMPARISON")
    print("="*70)
    
    # Model columns
    model_columns = set(col.name for col in Institution.__table__.columns)
    
    # Database columns
    try:
        engine = create_engine(DATABASE_URL)
        inspector = inspect(engine)
        db_columns = set(col['name'] for col in inspector.get_columns('institutions'))
        
        print("\nColumns in MODEL only:")
        model_only = model_columns - db_columns
        if model_only:
            for col in sorted(model_only):
                print(f"   - {col}")
        else:
            print("   (none)")
        
        print("\nColumns in DATABASE only:")
        db_only = db_columns - model_columns
        if db_only:
            for col in sorted(db_only):
                print(f"   - {col}")
        else:
            print("   (none)")
        
        print("\nColumns in BOTH:")
        both = model_columns & db_columns
        for col in sorted(both):
            print(f"   - {col}")
            
    except Exception as e:
        print(f"Error: {e}")


def main():
    print("Institution Model/Database Schema Diagnostic")
    print("="*70)
    
    model_ok = check_model_definition()
    db_ok = check_database_schema()
    show_current_state()
    
    print("\n" + "="*70)
    print("SUMMARY & RECOMMENDATIONS")
    print("="*70)
    
    if model_ok and db_ok:
        print("✅ Everything looks good!")
        print("   The test failures might be due to cached .pyc files.")
        print("   Try: find . -type d -name __pycache__ -exec rm -rf {} +")
    elif not model_ok and not db_ok:
        print("❌ Both model AND database need to be fixed!")
        print("\nFIX ORDER:")
        print("1. Remove deprecated fields from app/models/institution.py")
        print("2. Drop deprecated columns from database")
        print("3. Clear Python cache: find . -name '*.pyc' -delete")
        print("4. Run tests again")
    elif not model_ok:
        print("❌ Fix the MODEL first!")
        print("   Remove deprecated fields from app/models/institution.py")
    else:
        print("❌ Fix the DATABASE schema!")
        print("   Drop the deprecated columns from institutions table")
    
    print("="*70)


if __name__ == '__main__':
    main()
