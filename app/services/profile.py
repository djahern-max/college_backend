# app/services/profile.py
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from datetime import datetime
import logging

from app.models.profile import UserProfile
from app.schemas.profile import ProfileCreate, ProfileUpdate

logger = logging.getLogger(__name__)


class ProfileService:
    """Service class for profile CRUD operations with better error handling"""

    def __init__(self, db: Session):
        self.db = db

    def get_profile_by_user_id(self, user_id: int) -> Optional[UserProfile]:
        """READ - Get user profile by user ID"""
        try:
            return (
                self.db.query(UserProfile)
                .filter(UserProfile.user_id == user_id)
                .first()
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error getting profile for user {user_id}: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

    def create_profile(self, user_id: int, profile_data: ProfileCreate) -> UserProfile:
        """CREATE - Create a new user profile"""
        try:
            # Convert ProfileCreate to dict and remove None values for cleaner creation
            profile_dict = profile_data.model_dump(exclude_unset=True)

            # Create new profile with user_id
            db_profile = UserProfile(user_id=user_id, **profile_dict)

            # Calculate completion status using the model's built-in method
            db_profile.update_completion_status()

            # Save to database
            self.db.add(db_profile)
            self.db.commit()
            self.db.refresh(db_profile)

            logger.info(f"Successfully created profile for user {user_id}")
            return db_profile

        except IntegrityError as e:
            self.db.rollback()
            logger.error(
                f"Integrity error creating profile for user {user_id}: {str(e)}"
            )
            if "unique constraint" in str(e).lower():
                raise Exception("Profile already exists for this user")
            raise Exception(f"Database constraint error: {str(e)}")
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(
                f"Database error creating profile for user {user_id}: {str(e)}"
            )
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            self.db.rollback()
            logger.error(
                f"Unexpected error creating profile for user {user_id}: {str(e)}"
            )
            raise Exception(f"Unexpected error: {str(e)}")

    def update_profile(
        self, user_id: int, profile_data: ProfileUpdate
    ) -> Optional[UserProfile]:
        """UPDATE - Update existing user profile"""
        try:
            # Get existing profile
            db_profile = self.get_profile_by_user_id(user_id)
            if not db_profile:
                return None

            # Get update data, excluding unset fields (partial updates)
            update_data = profile_data.model_dump(exclude_unset=True)

            # Update each field that was provided
            for field, value in update_data.items():
                if hasattr(db_profile, field):
                    setattr(db_profile, field, value)

            # Update completion status and timestamp
            db_profile.update_completion_status()
            db_profile.updated_at = func.now()

            # Save changes
            self.db.commit()
            self.db.refresh(db_profile)

            logger.info(f"Successfully updated profile for user {user_id}")
            return db_profile

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(
                f"Database error updating profile for user {user_id}: {str(e)}"
            )
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            self.db.rollback()
            logger.error(
                f"Unexpected error updating profile for user {user_id}: {str(e)}"
            )
            raise Exception(f"Unexpected error: {str(e)}")

    def delete_profile(self, user_id: int) -> bool:
        """DELETE - Delete user profile"""
        try:
            db_profile = self.get_profile_by_user_id(user_id)
            if not db_profile:
                return False

            self.db.delete(db_profile)
            self.db.commit()

            logger.info(f"Successfully deleted profile for user {user_id}")
            return True

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(
                f"Database error deleting profile for user {user_id}: {str(e)}"
            )
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            self.db.rollback()
            logger.error(
                f"Unexpected error deleting profile for user {user_id}: {str(e)}"
            )
            raise Exception(f"Unexpected error: {str(e)}")

    def profile_exists(self, user_id: int) -> bool:
        """Check if user already has a profile"""
        try:
            return (
                self.db.query(UserProfile)
                .filter(UserProfile.user_id == user_id)
                .first()
                is not None
            )
        except SQLAlchemyError as e:
            logger.error(
                f"Database error checking profile existence for user {user_id}: {str(e)}"
            )
            raise Exception(f"Database error: {str(e)}")
