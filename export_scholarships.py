#!/usr/bin/env python3
"""
Export scholarships from PostgreSQL database to readable text file
Run from backend directory: python export_scholarships.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:@localhost:5432/college_db")
engine = create_engine(DATABASE_URL)

def export_scholarships_to_text():
    """Export all scholarships to a formatted text file"""
    
    output_file = "scholarships_export.txt"
    
    with engine.connect() as conn:
        # Get all scholarships
        result = conn.execute(text("""
            SELECT 
                id,
                title,
                organization,
                scholarship_type,
                status,
                difficulty_level,
                amount_min,
                amount_max,
                is_renewable,
                number_of_awards,
                deadline,
                application_opens,
                for_academic_year,
                description,
                website_url,
                min_gpa,
                primary_image_url,
                verified,
                featured,
                views_count,
                applications_count,
                created_at,
                updated_at
            FROM scholarships
            ORDER BY id
        """))
        
        scholarships = result.fetchall()
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 100 + "\n")
            f.write("MAGIC SCHOLAR - SCHOLARSHIPS DATABASE EXPORT\n")
            f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Scholarships: {len(scholarships)}\n")
            f.write("=" * 100 + "\n\n")
            
            for idx, sch in enumerate(scholarships, 1):
                f.write(f"\n{'=' * 100}\n")
                f.write(f"SCHOLARSHIP #{idx} - ID: {sch.id}\n")
                f.write(f"{'=' * 100}\n\n")
                
                # Basic Info
                f.write(f"TITLE:              {sch.title or 'N/A'}\n")
                f.write(f"ORGANIZATION:       {sch.organization or 'N/A'}\n")
                f.write(f"TYPE:               {sch.scholarship_type or 'N/A'}\n")
                f.write(f"STATUS:             {sch.status or 'N/A'}\n")
                f.write(f"DIFFICULTY:         {sch.difficulty_level or 'N/A'}\n")
                f.write(f"\n")
                
                # Financial Info
                f.write(f"AMOUNT:\n")
                if sch.amount_min and sch.amount_max:
                    if sch.amount_min == sch.amount_max:
                        f.write(f"  - Fixed Amount:   ${sch.amount_min:,}\n")
                    else:
                        f.write(f"  - Min Amount:     ${sch.amount_min:,}\n")
                        f.write(f"  - Max Amount:     ${sch.amount_max:,}\n")
                else:
                    f.write(f"  - Not specified\n")
                
                f.write(f"RENEWABLE:          {'Yes' if sch.is_renewable else 'No'}\n")
                f.write(f"NUMBER OF AWARDS:   {sch.number_of_awards if sch.number_of_awards else 'Not specified'}\n")
                f.write(f"\n")
                
                # Dates
                f.write(f"DEADLINES:\n")
                f.write(f"  - Application Opens: {sch.application_opens if sch.application_opens else 'Not specified'}\n")
                f.write(f"  - Deadline:          {sch.deadline if sch.deadline else 'Not specified'}\n")
                f.write(f"  - Academic Year:     {sch.for_academic_year if sch.for_academic_year else 'Not specified'}\n")
                f.write(f"\n")
                
                # Requirements
                f.write(f"REQUIREMENTS:\n")
                f.write(f"  - Min GPA:        {sch.min_gpa if sch.min_gpa else 'Not specified'}\n")
                f.write(f"\n")
                
                # Description
                if sch.description:
                    f.write(f"DESCRIPTION:\n")
                    f.write(f"  {sch.description}\n")
                    f.write(f"\n")
                
                # Links
                f.write(f"WEBSITE:            {sch.website_url if sch.website_url else 'Not specified'}\n")
                f.write(f"IMAGE URL:          {sch.primary_image_url if sch.primary_image_url else 'Not specified'}\n")
                f.write(f"\n")
                
                # Status Flags
                f.write(f"FLAGS:\n")
                f.write(f"  - Verified:       {'Yes' if sch.verified else 'No'}\n")
                f.write(f"  - Featured:       {'Yes' if sch.featured else 'No'}\n")
                f.write(f"  - Views:          {sch.views_count}\n")
                f.write(f"  - Applications:   {sch.applications_count}\n")
                f.write(f"\n")
                
                # Timestamps
                f.write(f"TIMESTAMPS:\n")
                f.write(f"  - Created:        {sch.created_at}\n")
                f.write(f"  - Updated:        {sch.updated_at if sch.updated_at else 'Never'}\n")
                
            f.write(f"\n\n{'=' * 100}\n")
            f.write(f"END OF EXPORT - Total Scholarships: {len(scholarships)}\n")
            f.write(f"{'=' * 100}\n")
    
    print(f"✓ Successfully exported {len(scholarships)} scholarships to {output_file}")
    return output_file

if __name__ == "__main__":
    try:
        output_file = export_scholarships_to_text()
        print(f"\nFile saved: {output_file}")
        print(f"You can now review the scholarships in a readable format!")
    except Exception as e:
        print(f"Error exporting scholarships: {e}")
        import traceback
        traceback.print_exc()
