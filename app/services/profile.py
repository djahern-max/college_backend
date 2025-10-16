# app/services/profile.py
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.models.profile import UserProfile
from app.models.institution import Institution
from app.schemas.profile import ProfileCreate, ProfileUpdate


class ProfileService:
    """Service for user profile database operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, profile_id: int) -> Optional[UserProfile]:
        """Get profile by ID"""
        return self.db.query(UserProfile).filter(UserProfile.id == profile_id).first()

    def get_by_user_id(self, user_id: int) -> Optional[UserProfile]:
        """Get profile by user ID"""
        return self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    def create_profile(self, user_id: int, profile_data: ProfileCreate) -> UserProfile:
        """Create a new profile for a user"""
        db_profile = UserProfile(
            user_id=user_id, **profile_data.dict(exclude_unset=True)
        )

        self.db.add(db_profile)
        self.db.commit()
        self.db.refresh(db_profile)
        return db_profile

    def update_profile(
        self, user_id: int, profile_data: ProfileUpdate
    ) -> Optional[UserProfile]:
        """Update user profile"""
        db_profile = self.get_by_user_id(user_id)
        if not db_profile:
            return None

        update_data = profile_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_profile, field, value)

        db_profile.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_profile)
        return db_profile

    def delete_profile(self, user_id: int) -> bool:
        """Delete a user profile"""
        db_profile = self.get_by_user_id(user_id)
        if not db_profile:
            return False

        self.db.delete(db_profile)
        self.db.commit()
        return True

    def find_matching_institutions(
        self, user_id: int, limit: int = 50
    ) -> List[Institution]:
        """
        Find institutions matching user's location preference

        Args:
            user_id: The user's ID
            limit: Maximum number of results to return

        Returns:
            List of matching institutions
        """
        profile = self.get_by_user_id(user_id)

        if not profile or not profile.location_preference:
            return []

        return (
            self.db.query(Institution)
            .filter(Institution.state == profile.location_preference)
            .order_by(Institution.name)
            .limit(limit)
            .all()
        )

    def get_profiles_by_state(self, state: str, limit: int = 100) -> List[UserProfile]:
        """Get profiles by home state"""
        return (
            self.db.query(UserProfile)
            .filter(UserProfile.state == state)
            .limit(limit)
            .all()
        )

    def get_profiles_by_graduation_year(
        self, year: int, limit: int = 100
    ) -> List[UserProfile]:
        """Get profiles by graduation year"""
        return (
            self.db.query(UserProfile)
            .filter(UserProfile.graduation_year == year)
            .limit(limit)
            .all()
        )
