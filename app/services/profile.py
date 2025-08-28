# app/services/profile.py
from typing import Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.models.profile import UserProfile
from app.schemas.profile import ProfileCreate, ProfileUpdate, ProfileSummary


class ProfileService:
    """Rebuilt profile service with proper create/update patterns"""

    def __init__(self, db: Session):
        self.db = db

    def get_profile_by_user_id(self, user_id: int) -> Optional[UserProfile]:
        """Get user profile by user ID"""
        return self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    def get_or_create_profile(self, user_id: int) -> UserProfile:
        """Get existing profile or create empty one if doesn't exist"""
        profile = self.get_profile_by_user_id(user_id)
        if not profile:
            # Create minimal empty profile
            profile = UserProfile(user_id=user_id)
            profile.update_completion_status()
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)
        return profile

    def upsert_profile(self, user_id: int, profile_data: ProfileCreate) -> UserProfile:
        """Create new profile or completely replace existing one"""
        # Get or create profile
        profile = self.get_or_create_profile(user_id)

        # Update all provided fields
        profile_dict = profile_data.model_dump(exclude_unset=True)
        for field, value in profile_dict.items():
            if hasattr(profile, field):
                setattr(profile, field, value)

        # Update metadata
        profile.update_completion_status()
        profile.updated_at = func.now()

        self.db.commit()
        self.db.refresh(profile)
        return profile

    def update_profile_fields(
        self, user_id: int, profile_data: ProfileUpdate
    ) -> UserProfile:
        """Update only provided fields (partial update)"""
        # Get or create profile
        profile = self.get_or_create_profile(user_id)

        # Update only provided fields
        update_data = profile_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(profile, field):
                setattr(profile, field, value)

        # Update metadata
        profile.update_completion_status()
        profile.updated_at = func.now()

        self.db.commit()
        self.db.refresh(profile)
        return profile

    def update_single_field(
        self, user_id: int, field_name: str, field_value: Any
    ) -> UserProfile:
        """Update a single field (for auto-save)"""
        # Get or create profile
        profile = self.get_or_create_profile(user_id)

        # Validate field exists
        if not hasattr(profile, field_name):
            raise ValueError(f"Invalid field name: {field_name}")

        # Update the field
        setattr(profile, field_name, field_value)

        # Update metadata
        profile.update_completion_status()
        profile.updated_at = func.now()

        self.db.commit()
        self.db.refresh(profile)
        return profile

    def delete_profile(self, user_id: int) -> bool:
        """Delete user profile"""
        profile = self.get_profile_by_user_id(user_id)
        if not profile:
            return False

        self.db.delete(profile)
        self.db.commit()
        return True

    def get_profile_summary(self, user_id: int) -> ProfileSummary:
        """Get profile completion summary"""
        profile = self.get_or_create_profile(user_id)

        return ProfileSummary(
            profile_completed=profile.profile_completed,
            completion_percentage=profile.completion_percentage,
            has_basic_info=profile.is_basic_info_complete,
            has_academic_info=profile.is_academic_info_complete,
            has_personal_info=profile.is_personal_info_complete,
            missing_fields=profile.get_missing_fields(),
        )
