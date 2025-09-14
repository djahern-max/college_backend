#!/usr/bin/env python3
"""
Fix image files: convert formats, rename with proper extensions, remove spaces
"""
import os
import glob
from PIL import Image

def fix_image_files():
    """Convert and rename image files for scholarship upload"""
    
    # Get current directory
    current_dir = os.getcwd()
    print(f"Working in: {current_dir}")
    
    # Get all files
    all_files = glob.glob("*")
    image_files = [f for f in all_files if not f.startswith('.') and os.path.isfile(f)]
    
    print(f"Found {len(image_files)} files to process:")
    
    for filename in image_files:
        print(f"\nProcessing: {filename}")
        
        # Skip if already has proper extension
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            # Just rename to remove spaces if needed
            if ' ' in filename:
                new_name = filename.replace(' ', '_').replace('__', '_')
                os.rename(filename, new_name)
                print(f"  Renamed: {filename} -> {new_name}")
            else:
                print(f"  OK: {filename}")
            continue
        
        # Handle files without extensions or with .webp
        base_name = filename.replace(' ', '_').replace('__', '_')
        
        # Remove existing extension if present
        if '.' in base_name:
            base_name = base_name.rsplit('.', 1)[0]
        
        new_filename = f"{base_name}.jpg"
        
        try:
            # Open and convert image
            with Image.open(filename) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Save as JPG
                img.save(new_filename, 'JPEG', quality=95, optimize=True)
                print(f"  Converted: {filename} -> {new_filename}")
                
                # Remove original file
                os.remove(filename)
                
        except Exception as e:
            print(f"  Error processing {filename}: {e}")
    
    print(f"\nFinal files:")
    final_files = sorted([f for f in os.listdir('.') if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    for i, f in enumerate(final_files, 1):
        print(f"  {i}. {f}")

if __name__ == "__main__":
    fix_image_files()
