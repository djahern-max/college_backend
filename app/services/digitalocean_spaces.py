# app/services/digitalocean_spaces.py
"""
Service for uploading files to Digital Ocean Spaces
"""

import boto3
from botocore.exceptions import ClientError
from typing import Optional
import logging
import os
import time
from app.core.config import settings

logger = logging.getLogger(__name__)


class DigitalOceanSpaces:
    """Handle file uploads to Digital Ocean Spaces"""

    def __init__(self):
        """Initialize S3 client for Digital Ocean Spaces"""
        self.client = boto3.client(
            "s3",
            region_name=settings.DIGITAL_OCEAN_SPACES_REGION,
            endpoint_url=settings.DIGITAL_OCEAN_SPACES_ENDPOINT,
            aws_access_key_id=settings.DIGITAL_OCEAN_SPACES_ACCESS_KEY,
            aws_secret_access_key=settings.DIGITAL_OCEAN_SPACES_SECRET_KEY,
        )
        self.bucket = settings.DIGITAL_OCEAN_SPACES_BUCKET
        self.cdn_base = settings.IMAGE_CDN_BASE_URL

    def upload_file(
        self,
        file_path: str,
        destination_path: str,
        content_type: Optional[str] = None,
        is_public: bool = True,
    ) -> str:
        """
        Upload a file to Digital Ocean Spaces

        Args:
            file_path: Local path to the file
            destination_path: Path in the bucket (e.g., 'profiles/123/resume.pdf')
            content_type: MIME type of the file
            is_public: Whether file should be publicly accessible

        Returns:
            CDN URL of the uploaded file
        """
        try:
            extra_args = {}

            if content_type:
                extra_args["ContentType"] = content_type

            if is_public:
                extra_args["ACL"] = "public-read"

            # Upload file
            self.client.upload_file(
                file_path, self.bucket, destination_path, ExtraArgs=extra_args
            )

            # Return CDN URL
            cdn_url = f"{self.cdn_base}/{destination_path}"
            logger.info(f"File uploaded successfully to: {cdn_url}")
            return cdn_url

        except ClientError as e:
            logger.error(f"Error uploading file to DO Spaces: {str(e)}")
            raise Exception(f"Failed to upload file: {str(e)}")

    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from Digital Ocean Spaces

        Args:
            file_path: Path in the bucket (e.g., 'profiles/123/resume.pdf')

        Returns:
            True if successful
        """
        try:
            self.client.delete_object(Bucket=self.bucket, Key=file_path)
            logger.info(f"File deleted successfully: {file_path}")
            return True
        except ClientError as e:
            logger.error(f"Error deleting file from DO Spaces: {str(e)}")
            return False

    def generate_profile_path(self, user_id: int, filename: str) -> str:
        """
        Generate standardized path for user profile files

        For headshots, adds a timestamp to ensure uniqueness and prevent
        caching/overwrite issues across different users.

        Args:
            user_id: User's ID
            filename: Name of the file (e.g., 'resume.pdf', 'headshot.jpg')

        Returns:
            Path in bucket (e.g., 'profiles/123/headshot_1699000000.jpg')
        """
        # For headshots, add timestamp to ensure uniqueness
        if filename.startswith("headshot"):
            timestamp = int(time.time())
            # Extract extension
            extension = filename.split(".")[-1] if "." in filename else "jpg"
            filename = f"headshot_{timestamp}.{extension}"

        return f"profiles/{user_id}/{filename}"

    def get_content_type(self, filename: str) -> str:
        """
        Determine content type from filename

        Args:
            filename: Name of the file

        Returns:
            MIME type string
        """
        extension = filename.lower().split(".")[-1]

        content_types = {
            "pdf": "application/pdf",
            "doc": "application/msword",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "gif": "image/gif",
            "webp": "image/webp",
        }

        return content_types.get(extension, "application/octet-stream")
