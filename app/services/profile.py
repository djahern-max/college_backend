"""
Profile service for managing user profiles.
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from app.models.profile import UserProfile
from app.schemas.profile import UserProfileCreate, UserProfileUpdate


class ProfileService:
    """Service for managing user profiles."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get(self, profile_id: int) -> Optional[UserProfile]:
        """Get profile by ID."""
        result = await self.db.execute(
            select(UserProfile).where(UserProfile.id == profile_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_user_id(self, user_id: int) -> Optional[UserProfile]:
        """Get profile by user ID."""
        result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def create(self, user_id: int, profile_data: UserProfileCreate) -> UserProfile:
        """Create a new profile."""
        # Convert schema to dict and add user_id
        profile_dict = profile_data.model_dump(exclude_unset=True)
        profile_dict['user_id'] = user_id
        
        # Calculate initial completion percentage
        profile_dict['completion_percentage'] = self._calculate_completion_percentage(profile_dict)
        profile_dict['profile_completed'] = profile_dict['completion_percentage'] >= 80
        
        profile = UserProfile(**profile_dict)
        self.db.add(profile)
        await self.db.flush()
        await self.db.refresh(profile)
        
        return profile
    
    async def update(self, profile_id: int, profile_data: UserProfileUpdate) -> Optional[UserProfile]:
        """Update a profile."""
        # Get the current profile
        profile = await self.get(profile_id)
        if not profile:
            return None
        
        # Update only provided fields
        update_dict = profile_data.model_dump(exclude_unset=True)
        
        if update_dict:
            # Update the profile
            await self.db.execute(
                update(UserProfile)
                .where(UserProfile.id == profile_id)
                .values(**update_dict)
            )
            
            # Flush to make changes visible in this transaction
            await self.db.flush()
            
            # Get updated profile to recalculate completion
            updated_profile = await self.get(profile_id)
            
            if updated_profile:
                # Recalculate completion percentage
                completion_percentage = self._calculate_completion_percentage_from_model(updated_profile)
                profile_completed = completion_percentage >= 80
                
                await self.db.execute(
                    update(UserProfile)
                    .where(UserProfile.id == profile_id)
                    .values(
                        completion_percentage=completion_percentage,
                        profile_completed=profile_completed
                    )
                )
                
                # Flush again but don't commit - let endpoint handle commit
                await self.db.flush()
                
                # Get final updated profile
                return await self.get(profile_id)
        
        return profile
    
    async def delete(self, profile_id: int) -> bool:
        """Delete a profile."""
        result = await self.db.execute(
            delete(UserProfile).where(UserProfile.id == profile_id)
        )
        # DON'T commit here - let the endpoint dependency handle it
        await self.db.flush()  # Just flush to make the change visible
        return result.rowcount > 0
    
    async def get_multi(self, skip: int = 0, limit: int = 100) -> List[UserProfile]:
        """Get multiple profiles with pagination."""
        result = await self.db.execute(
            select(UserProfile)
            .offset(skip)
            .limit(limit)
            .order_by(UserProfile.created_at.desc())
        )
        return result.scalars().all()
    
    def _calculate_completion_percentage(self, profile_dict: dict) -> int:
        """Calculate profile completion percentage based on filled fields."""
        # Define important fields and their weights
        important_fields = {
            # Basic info (30%)
            'high_school_name': 5,
            'graduation_year': 5,
            'city': 3,
            'state': 3,
            'phone': 2,
            'date_of_birth': 2,
            
            # Academic info (25%)
            'gpa': 8,
            'sat_score': 5,
            'act_score': 4,
            'honors_courses': 4,
            'academic_awards': 4,
            
            # Activities (25%)
            'sports_played': 6,
            'athletic_awards': 4,
            'extracurricular_activities': 6,
            'volunteer_organizations': 5,
            'volunteer_hours': 4,
            
            # Future plans (20%)
            'intended_major': 6,
            'career_goals': 6,
            'college_preferences': 4,
            'personal_statement': 4,
        }
        
        total_possible = sum(important_fields.values())
        earned_points = 0
        
        for field, points in important_fields.items():
            value = profile_dict.get(field)
            if value is not None:
                if isinstance(value, (list, dict)):
                    if value:  # Non-empty list or dict
                        earned_points += points
                elif isinstance(value, str):
                    if value.strip():  # Non-empty string
                        earned_points += points
                else:
                    earned_points += points  # Numbers, bools, etc.
        
        return min(100, int((earned_points / total_possible) * 100))
    
    def _calculate_completion_percentage_from_model(self, profile: UserProfile) -> int:
        """Calculate completion percentage from UserProfile model."""
        profile_dict = {
            'high_school_name': profile.high_school_name,
            'graduation_year': profile.graduation_year,
            'city': profile.city,
            'state': profile.state,
            'phone': profile.phone,
            'date_of_birth': profile.date_of_birth,
            'gpa': profile.gpa,
            'sat_score': profile.sat_score,
            'act_score': profile.act_score,
            'honors_courses': profile.honors_courses,
            'academic_awards': profile.academic_awards,
            'sports_played': profile.sports_played,
            'athletic_awards': profile.athletic_awards,
            'extracurricular_activities': profile.extracurricular_activities,
            'volunteer_organizations': profile.volunteer_organizations,
            'volunteer_hours': profile.volunteer_hours,
            'intended_major': profile.intended_major,
            'career_goals': profile.career_goals,
            'college_preferences': profile.college_preferences,
            'personal_statement': profile.personal_statement,
        }
        
        return self._calculate_completion_percentage(profile_dict)