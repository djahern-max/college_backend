# test_upload.py
import sys
sys.path.append('.')

from app.core.config import settings
from app.services.image_extractor import DigitalOceanSpacesUploader

print("=== CONFIGURATION CHECK ===")
print(f"Endpoint: {getattr(settings, 'DIGITAL_OCEAN_SPACES_ENDPOINT', 'NOT SET')}")
print(f"Bucket: {getattr(settings, 'DIGITAL_OCEAN_SPACES_BUCKET', 'NOT SET')}")
print(f"Region: {getattr(settings, 'DIGITAL_OCEAN_SPACES_REGION', 'NOT SET')}")
print(f"CDN URL: {getattr(settings, 'IMAGE_CDN_BASE_URL', 'NOT SET')}")

print("\n=== TESTING UPLOAD ===")
try:
    uploader = DigitalOceanSpacesUploader()
    result = uploader.upload_image(b'test content', 'debug/test-upload.txt', 'text/plain')
    print(f"Upload result: {result}")
except Exception as e:
    print(f"Upload failed: {e}")
