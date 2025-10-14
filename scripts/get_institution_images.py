import os
import boto3
from botocore.client import Config
import psycopg2
from psycopg2.extras import RealDictCursor

# Digital Ocean Spaces Configuration
SPACES_REGION = 'nyc3'
SPACES_ENDPOINT = f'https://{SPACES_REGION}.digitaloceanspaces.com'
# TODO: You need to provide these values
SPACES_KEY = 'YOUR_SPACES_ACCESS_KEY'  # TODO: Replace with your Digital Ocean Spaces key
SPACES_SECRET = 'YOUR_SPACES_SECRET_KEY'  # TODO: Replace with your Digital Ocean Spaces secret
SPACES_BUCKET = 'magicscholar-images'  # Based on your screenshot
SPACES_FOLDER = 'institutions/ak'  # Change to the folder you want to scan

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',  # Since you're running this on the same server
    'database': 'magicscholar_db',
    'user': 'postgres',
    'password': 'gFwhY0Ibgtgb7n52nhaF8cvPVxvz72fsuzuDxGcV55s='
}

# CDN URL (if you have one configured)
# Based on your screenshot, it looks like you're using the direct Spaces URL
CDN_URL = None  # Set to your CDN URL if you have one

def get_spaces_client():
    """Initialize and return a Digital Ocean Spaces client."""
    session = boto3.session.Session()
    client = session.client(
        's3',
        region_name=SPACES_REGION,
        endpoint_url=SPACES_ENDPOINT,
        aws_access_key_id=SPACES_KEY,
        aws_secret_access_key=SPACES_SECRET,
        config=Config(signature_version='s3v4')
    )
    return client

def list_images_in_folder(folder_path):
    """List all images in a specific folder in Digital Ocean Spaces."""
    client = get_spaces_client()
    
    try:
        response = client.list_objects_v2(
            Bucket=SPACES_BUCKET,
            Prefix=folder_path
        )
        
        if 'Contents' not in response:
            print(f"No files found in folder: {folder_path}")
            return []
        
        images = []
        for obj in response['Contents']:
            key = obj['Key']
            # Only include actual image files, not folders
            if key != folder_path and key.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                # Generate the full URL
                if CDN_URL:
                    url = f"{CDN_URL}/{key}"
                else:
                    url = f"{SPACES_ENDPOINT}/{SPACES_BUCKET}/{key}"
                
                # Extract filename
                filename = key.split('/')[-1]
                
                images.append({
                    'filename': filename,
                    'key': key,
                    'url': url,
                    'size': obj['Size']
                })
        
        return images
        
    except Exception as e:
        print(f"Error listing images: {e}")
        return []

def extract_institution_info_from_filename(filename):
    """
    Extract institution information from filename.
    Assumes format like: 'arizona_state_university_immersion.jpeg'
    Returns a dict with potential institution identifiers.
    """
    # Remove file extension
    name_part = filename.rsplit('.', 1)[0]
    
    # Replace underscores with spaces for matching
    readable_name = name_part.replace('_', ' ').title()
    
    return {
        'filename': filename,
        'readable_name': readable_name,
        'search_pattern': f"%{name_part.replace('_', '%')}%"
    }

def find_institution_by_name(cursor, search_pattern, state='AZ'):
    """Find institution in database by name pattern."""
    query = """
        SELECT id, ipeds_id, name, city, state, primary_image_url
        FROM institutions
        WHERE LOWER(name) LIKE LOWER(%s) AND state = %s
        ORDER BY name
    """
    cursor.execute(query, (search_pattern, state))
    return cursor.fetchall()

def update_institution_image(cursor, institution_id, image_url):
    """Update the primary_image_url for an institution."""
    query = """
        UPDATE institutions
        SET primary_image_url = %s, updated_at = NOW()
        WHERE id = %s
        RETURNING id, name, primary_image_url
    """
    cursor.execute(query, (image_url, institution_id))
    return cursor.fetchone()

def main():
    print("=" * 80)
    print("Digital Ocean Spaces Image URL Retriever")
    print("=" * 80)
    print()
    
    # Allow user to specify folder
    print(f"Default folder: {SPACES_FOLDER}")
    print("Enter folder path (or press Enter to use default): ", end='')
    custom_folder = input().strip()
    folder_to_scan = custom_folder if custom_folder else SPACES_FOLDER
    
    # Extract state from folder path if possible
    state_code = folder_to_scan.split('/')[-1].upper() if '/' in folder_to_scan else 'AZ'
    
    # Get images from Digital Ocean Spaces
    print(f"\nFetching images from: {folder_to_scan}")
    images = list_images_in_folder(folder_to_scan)
    
    if not images:
        print("No images found!")
        return
    
    print(f"\nFound {len(images)} images:\n")
    print("-" * 80)
    
    # Display all images with their URLs
    for idx, img in enumerate(images, 1):
        print(f"{idx}. {img['filename']}")
        print(f"   URL: {img['url']}")
        print(f"   Size: {img['size'] / 1024:.2f} KB")
        print()
    
    print("-" * 80)
    print("\nDo you want to update the database with these URLs? (yes/no): ", end='')
    update_db = input().strip().lower()
    
    if update_db != 'yes':
        print("\nImage URLs retrieved successfully! No database updates made.")
        print("\nYou can copy the URLs above to update your database manually.")
        return
    
    # Connect to database and update
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("\n" + "=" * 80)
        print(f"Matching images to institutions in state: {state_code}")
        print("=" * 80 + "\n")
        
        for img in images:
            info = extract_institution_info_from_filename(img['filename'])
            print(f"Processing: {img['filename']}")
            print(f"Readable name: {info['readable_name']}")
            
            # Find matching institution
            institutions = find_institution_by_name(cursor, info['search_pattern'], state_code)
            
            if not institutions:
                print(f"  ⚠️  No matching institution found")
                print()
                continue
            
            if len(institutions) > 1:
                print(f"  ⚠️  Multiple matches found:")
                for inst in institutions:
                    print(f"     - {inst['name']} (ID: {inst['id']})")
                print(f"  Please specify which institution ID to update, or 'skip': ", end='')
                choice = input().strip()
                if choice.lower() == 'skip':
                    print()
                    continue
                try:
                    selected_id = int(choice)
                    selected = next((i for i in institutions if i['id'] == selected_id), None)
                    if not selected:
                        print(f"  ⚠️  Invalid ID, skipping")
                        print()
                        continue
                except ValueError:
                    print(f"  ⚠️  Invalid input, skipping")
                    print()
                    continue
            else:
                selected = institutions[0]
            
            print(f"  ✓ Match found: {selected['name']} (ID: {selected['id']})")
            
            if selected['primary_image_url']:
                print(f"  ⚠️  Institution already has an image URL:")
                print(f"     Current: {selected['primary_image_url']}")
                print(f"     New: {img['url']}")
                print(f"  Overwrite? (yes/no): ", end='')
                overwrite = input().strip().lower()
                if overwrite != 'yes':
                    print(f"  Skipped")
                    print()
                    continue
            
            # Update the database
            result = update_institution_image(cursor, selected['id'], img['url'])
            if result:
                print(f"  ✓ Updated: {result['name']}")
                print(f"     New URL: {result['primary_image_url']}")
            
            print()
        
        conn.commit()
        print("\n" + "=" * 80)
        print("✓ Database updates completed successfully!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ Error updating database: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
