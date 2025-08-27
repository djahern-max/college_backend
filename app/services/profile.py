# app/services/profile.py
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from datetime import datetime

from app.models.profile import UserProfile
from app.schemas.profile import ProfileCreate, ProfileUpdate


class ProfileService:
    """Simple service class for profile CRUD operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_profile_by_user_id(self, user_id: int) -> Optional[UserProfile]:
        """READ - Get user profile by user ID"""
        return self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    def create_profile(self, user_id: int, profile_data: ProfileCreate) -> UserProfile:
        """CREATE - Create a new user profile"""
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
        return db_profile

    def update_profile(
        self, user_id: int, profile_data: ProfileUpdate
    ) -> Optional[UserProfile]:
        """UPDATE - Update existing user profile"""
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
        return db_profile

    def delete_profile(self, user_id: int) -> bool:
        """DELETE - Delete user profile"""
        db_profile = self.get_profile_by_user_id(user_id)
        if not db_profile:
            return False

        self.db.delete(db_profile)
        self.db.commit()
        return True

    def profile_exists(self, user_id: int) -> bool:
        """Check if user already has a profile"""
        return (
            self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
            is not None
        )
