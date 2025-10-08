# scripts/import_tuition_data.py
"""
Script to import tuition and cost data from structured CSV files.

This script reads tuition data from a CSV file and imports it into the 
tuition_data table, linking it to institutions by IPEDS ID.

CSV Format Expected:
ipeds_id,academic_year,data_source,tuition_in_state,tuition_out_state,required_fees_in_state,required_fees_out_state,room_board_on_campus,room_board_off_campus,books_supplies,personal_expenses,transportation

Usage:
    python scripts/import_tuition_data.py --file data/alaska_tuition.csv
"""

import os
import sys
import csv
import argparse
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()


class TuitionImporter:
    def __init__(self):
        db_url = os.getenv('DATABASE_URL')
        self.engine = create_engine(db_url)
        
    def clean_number(self, value):
        """Convert string to float, handling empty values"""
        if not value or value.strip() == '':
            return None
        
        # Remove $ , and other non-numeric characters except .
        cleaned = value.replace('$', '').replace(',', '').strip()
        
        try:
            return float(cleaned)
        except:
            return None
    
    def verify_ipeds_exists(self, ipeds_id):
        """Verify that IPEDS ID exists in institutions table"""
        with self.engine.connect() as conn:
            query = text("SELECT name FROM institutions WHERE ipeds_id = :ipeds_id")
            result = conn.execute(query, {"ipeds_id": ipeds_id})
            row = result.fetchone()
            return row[0] if row else None
    
    def calculate_completeness_score(self, data):
        """Calculate data completeness score (0-100)"""
        fields_to_check = [
            'tuition_in_state', 'tuition_out_state',
            'required_fees_in_state', 'required_fees_out_state',
            'room_board_on_campus', 'room_board_off_campus',
            'books_supplies', 'personal_expenses', 'transportation'
        ]
        
        filled_fields = sum(1 for field in fields_to_check if data.get(field) is not None and data.get(field) > 0)
        return int((filled_fields / len(fields_to_check)) * 100)
    
    def import_csv(self, csv_path):
        """Import tuition data from CSV"""
        if not Path(csv_path).exists():
            print(f"Error: File {csv_path} not found")
            return
        
        print(f"\nImporting tuition data from {csv_path}\n")
        
        imported_count = 0
        updated_count = 0
        skipped_count = 0
        
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                ipeds_id = int(row['ipeds_id'])
                institution_name = self.verify_ipeds_exists(ipeds_id)
                
                if not institution_name:
                    print(f"✗ Institution not found for IPEDS ID {ipeds_id}")
                    skipped_count += 1
                    continue
                
                # Prepare data
                tuition_in_state = self.clean_number(row.get('tuition_in_state'))
                tuition_out_state = self.clean_number(row.get('tuition_out_state'))
                required_fees_in_state = self.clean_number(row.get('required_fees_in_state'))
                required_fees_out_state = self.clean_number(row.get('required_fees_out_state'))
                room_board_on_campus = self.clean_number(row.get('room_board_on_campus'))
                room_board_off_campus = self.clean_number(row.get('room_board_off_campus'))
                books_supplies = self.clean_number(row.get('books_supplies'))
                personal_expenses = self.clean_number(row.get('personal_expenses'))
                transportation = self.clean_number(row.get('transportation'))
                
                # Calculate combined tuition + fees
                tuition_fees_in_state = None
                if tuition_in_state is not None and required_fees_in_state is not None:
                    tuition_fees_in_state = tuition_in_state + required_fees_in_state
                elif tuition_in_state is not None:
                    tuition_fees_in_state = tuition_in_state
                
                tuition_fees_out_state = None
                if tuition_out_state is not None and required_fees_out_state is not None:
                    tuition_fees_out_state = tuition_out_state + required_fees_out_state
                elif tuition_out_state is not None:
                    tuition_fees_out_state = tuition_out_state
                
                tuition_data = {
                    'ipeds_id': ipeds_id,
                    'academic_year': row['academic_year'],
                    'data_source': row.get('data_source', 'MANUAL'),
                    'tuition_in_state': tuition_in_state,
                    'tuition_out_state': tuition_out_state,
                    'required_fees_in_state': required_fees_in_state,
                    'required_fees_out_state': required_fees_out_state,
                    'tuition_fees_in_state': tuition_fees_in_state,
                    'tuition_fees_out_state': tuition_fees_out_state,
                    'room_board_on_campus': room_board_on_campus,
                    'room_board_off_campus': room_board_off_campus,
                    'books_supplies': books_supplies,
                    'personal_expenses': personal_expenses,
                    'transportation': transportation,
                    'has_tuition_data': tuition_in_state is not None or tuition_out_state is not None,
                    'has_fees_data': required_fees_in_state is not None or required_fees_out_state is not None,
                    'has_living_data': room_board_on_campus is not None or room_board_off_campus is not None,
                    'validation_status': 'PENDING'
                }
                
                # Calculate completeness score
                tuition_data['data_completeness_score'] = self.calculate_completeness_score(tuition_data)
                
                # Check if record exists
                with self.engine.connect() as conn:
                    check_query = text("""
                        SELECT id FROM tuition_data 
                        WHERE ipeds_id = :ipeds_id 
                        AND academic_year = :academic_year
                        AND data_source = :data_source
                    """)
                    result = conn.execute(check_query, {
                        'ipeds_id': ipeds_id,
                        'academic_year': tuition_data['academic_year'],
                        'data_source': tuition_data['data_source']
                    })
                    existing = result.fetchone()
                    
                    if existing:
                        # Update existing record
                        update_query = text("""
                            UPDATE tuition_data SET
                                tuition_in_state = :tuition_in_state,
                                tuition_out_state = :tuition_out_state,
                                required_fees_in_state = :required_fees_in_state,
                                required_fees_out_state = :required_fees_out_state,
                                tuition_fees_in_state = :tuition_fees_in_state,
                                tuition_fees_out_state = :tuition_fees_out_state,
                                room_board_on_campus = :room_board_on_campus,
                                room_board_off_campus = :room_board_off_campus,
                                books_supplies = :books_supplies,
                                personal_expenses = :personal_expenses,
                                transportation = :transportation,
                                has_tuition_data = :has_tuition_data,
                                has_fees_data = :has_fees_data,
                                has_living_data = :has_living_data,
                                data_completeness_score = :data_completeness_score,
                                validation_status = :validation_status,
                                updated_at = NOW()
                            WHERE ipeds_id = :ipeds_id 
                            AND academic_year = :academic_year
                            AND data_source = :data_source
                        """)
                        conn.execute(update_query, tuition_data)
                        conn.commit()
                        print(f"✓ Updated: {institution_name} ({tuition_data['academic_year']}) - Score: {tuition_data['data_completeness_score']}%")
                        updated_count += 1
                    else:
                        # Insert new record
                        insert_query = text("""
                            INSERT INTO tuition_data (
                                ipeds_id, academic_year, data_source,
                                tuition_in_state, tuition_out_state,
                                required_fees_in_state, required_fees_out_state,
                                tuition_fees_in_state, tuition_fees_out_state,
                                room_board_on_campus, room_board_off_campus,
                                books_supplies, personal_expenses, transportation,
                                has_tuition_data, has_fees_data, has_living_data,
                                data_completeness_score, validation_status,
                                created_at, updated_at
                            ) VALUES (
                                :ipeds_id, :academic_year, :data_source,
                                :tuition_in_state, :tuition_out_state,
                                :required_fees_in_state, :required_fees_out_state,
                                :tuition_fees_in_state, :tuition_fees_out_state,
                                :room_board_on_campus, :room_board_off_campus,
                                :books_supplies, :personal_expenses, :transportation,
                                :has_tuition_data, :has_fees_data, :has_living_data,
                                :data_completeness_score, :validation_status,
                                NOW(), NOW()
                            )
                        """)
                        conn.execute(insert_query, tuition_data)
                        conn.commit()
                        print(f"✓ Imported: {institution_name} ({tuition_data['academic_year']}) - Score: {tuition_data['data_completeness_score']}%")
                        imported_count += 1
        
        print(f"\n{'='*60}")
        print(f"Import Summary:")
        print(f"  New records imported: {imported_count}")
        print(f"  Existing records updated: {updated_count}")
        print(f"  Records skipped: {skipped_count}")
        print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Import tuition data from CSV file'
    )
    parser.add_argument(
        '--file',
        type=str,
        required=True,
        help='Path to CSV file containing tuition data'
    )
    
    args = parser.parse_args()
    
    importer = TuitionImporter()
    importer.import_csv(args.file)


if __name__ == "__main__":
    main()
