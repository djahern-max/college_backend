#!/usr/bin/env python3
"""
Script to fix DigitalOcean Spaces permissions for existing images
Run this to make all uploaded images publicly accessible
"""

import boto3
from botocore.exceptions import ClientError
import os
from urllib.parse import urlparse
import psycopg2
from psycopg2.extras import RealDictCursor

# Configure your DigitalOcean Spaces connection
SPACES_ACCESS_KEY = os.getenv('DIGITAL_OCEAN_SPACES_ACCESS_KEY')
SPACES_SECRET_KEY = os.getenv('DIGITAL_OCEAN_SPACES_SECRET_KEY')
SPACES_ENDPOINT = os.getenv('DIGITAL_OCEAN_SPACES_ENDPOINT')
SPACES_REGION = os.getenv('DIGITAL_OCEAN_SPACES_REGION')
BUCKET_NAME = os.getenv('DIGITAL_OCEAN_SPACES_BUCKET')

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL')

def create_spaces_client():
    """Create DigitalOcean Spaces client"""
    return boto3.client(
        's3',
        endpoint_url=SPACES_ENDPOINT,
        aws_access_key_id=SPACES_ACCESS_KEY,
        aws_secret_access_key=SPACES_SECRET_KEY,
        region_name=SPACES_REGION
    )

def get_image_urls_from_db():
    """Get all image URLs from database"""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    query = """
    SELECT DISTINCT primary_image_url 
    FROM institutions 
    WHERE primary_image_url IS NOT NULL
    AND primary_image_url LIKE '%nyc3.digitaloceanspaces.com%'
    """
    
    cursor.execute(query)
    urls = [row['primary_image_url'] for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    return urls

def url_to_key(url):
    """Convert full URL to Spaces object key"""
    parsed = urlparse(url)
    # Remove leading slash
    return parsed.path.lstrip('/')

def fix_single_file_permissions(spaces_client, object_key):
    """Fix permissions for a single file"""
    try:
        # Copy the object to itself with public-read ACL
        copy_source = {
            'Bucket': BUCKET_NAME,
            'Key': object_key
        }
        
        spaces_client.copy_object(
            CopySource=copy_source,
            Bucket=BUCKET_NAME,
            Key=object_key,
            ACL='public-read',
            MetadataDirective='COPY'
        )
        
        print(f"✅ Fixed permissions: {object_key}")
        return True
        
    except ClientError as e:
        print(f"❌ Failed to fix {object_key}: {e}")
        return False

def main():
    """Main function to fix all image permissions"""
    print("🔧 Starting DigitalOcean Spaces permissions fix...")
    
    # Validate environment variables
    required_vars = [
        'DIGITAL_OCEAN_SPACES_ACCESS_KEY',
        'DIGITAL_OCEAN_SPACES_SECRET_KEY', 
        'DIGITAL_OCEAN_SPACES_ENDPOINT',
        'DIGITAL_OCEAN_SPACES_BUCKET',
        'DATABASE_URL'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return
    
    # Create Spaces client
    spaces_client = create_spaces_client()
    
    # Get all image URLs from database
    print("📊 Getting image URLs from database...")
    image_urls = get_image_urls_from_db()
    print(f"Found {len(image_urls)} image URLs to check")
    
    # Fix permissions for each file
    fixed_count = 0
    failed_count = 0
    
    for url in image_urls:
        object_key = url_to_key(url)
        if fix_single_file_permissions(spaces_client, object_key):
            fixed_count += 1
        else:
            failed_count += 1
    
    print(f"\n🎉 Permissions fix complete!")
    print(f"✅ Fixed: {fixed_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📊 Total: {len(image_urls)}")

if __name__ == "__main__":
    main()
