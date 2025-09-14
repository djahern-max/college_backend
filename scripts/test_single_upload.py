# test_single_upload.py - Simple test of one image upload
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.upload_scholarship_images import upload_image_to_scholarship, list_all_scholarships

def test_upload():
    print("=== Testing Single Image Upload ===")
    
    # First, list scholarships to confirm database connection
    print("1. Listing scholarships...")
    list_all_scholarships()
    
    # Check if image file exists
    image_file = "Hispanic_Scholarship_Fund_General_Scholarship.jpg"
    image_paths = [
        image_file,
        f"manual_images/{image_file}",
        f"../manual_images/{image_file}"
    ]
    
    print(f"\n2. Checking for image file: {image_file}")
    found_path = None
    for path in image_paths:
        if os.path.exists(path):
            found_path = path
            print(f"   Found: {path}")
            break
        else:
            print(f"   Not found: {path}")
    
    if not found_path:
        print("\nERROR: Image file not found. Please check file location.")
        return
    
    # Test upload to scholarship ID 13 (Hispanic Scholarship Fund)
    print(f"\n3. Attempting upload to scholarship ID 13...")
    success = upload_image_to_scholarship(13, image_file)
    
    if success:
        print("SUCCESS: Upload completed!")
    else:
        print("FAILED: Upload did not complete.")

if __name__ == "__main__":
    test_upload()
