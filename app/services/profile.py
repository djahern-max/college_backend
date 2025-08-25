# app/services/profile.py
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.models.profile import UserProfile
from app.models.user import User
from app.schemas.profile import (
    ProfileCreate,
    ProfileUpdate,
    ProfileSummary,
    ProfileResponse,
    ProfileCompletionStatus,
)


class ProfileService:
    """Service class for handling user profile operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_profile_by_user_id(self, user_id: int) -> Optional[UserProfile]:
        """Get user profile by user ID"""
        return self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    def create_profile(self, user_id: int, profile_data: ProfileCreate) -> UserProfile:
        """Create a new user profile"""
        db_profile = UserProfile(
            user_id=user_id, **profile_data.model_dump(exclude_unset=True)
        )

        # Calculate completion status
        db_profile.update_completion_status()

        self.db.add(db_profile)
        self.db.commit()
        self.db.refresh(db_profile)
        return db_profile

    def update_profile(
        self, user_id: int, profile_data: ProfileUpdate
    ) -> Optional[UserProfile]:
        """Update existing user profile or create if doesn't exist"""
        db_profile = self.get_profile_by_user_id(user_id)

        if not db_profile:
            # Create profile if it doesn't exist
            return self.create_profile(
                user_id, ProfileCreate(**profile_data.model_dump(exclude_unset=True))
            )

        # Update existing profile
        update_data = profile_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_profile, field):
                setattr(db_profile, field, value)

        # Update completion status
        db_profile.update_completion_status()
        db_profile.updated_at = func.now()

        self.db.commit()
        self.db.refresh(db_profile)
        return db_profile

    def update_profile_field(
        self, user_id: int, field_name: str, field_value: Any
    ) -> Optional[UserProfile]:
        """Update a single profile field (for auto-save functionality)"""
        db_profile = self.get_profile_by_user_id(user_id)

        if not db_profile:
            # Create profile if it doesn't exist
            profile_data = {field_name: field_value}
            return self.create_profile(user_id, ProfileCreate(**profile_data))

        # Validate field exists on model
        if not hasattr(db_profile, field_name):
            raise ValueError(f"Invalid field name: {field_name}")

        # Update the field
        setattr(db_profile, field_name, field_value)

        # Update completion status and timestamp
        db_profile.update_completion_status()
        db_profile.updated_at = func.now()

        self.db.commit()
        self.db.refresh(db_profile)
        return db_profile

    def complete_profile(self, user_id: int) -> Optional[UserProfile]:
        """Mark profile as completed"""
        db_profile = self.get_profile_by_user_id(user_id)
        if not db_profile:
            return None

        # Update completion status
        db_profile.update_completion_status()

        # Force completion if not already marked
        if not db_profile.profile_completed:
            db_profile.profile_completed = True
            db_profile.completed_at = func.now()

        db_profile.updated_at = func.now()

        self.db.commit()
        self.db.refresh(db_profile)
        return db_profile

    def get_profile_summary(self, user_id: int) -> ProfileSummary:
        """Get profile completion summary"""
        db_profile = self.get_profile_by_user_id(user_id)

        if not db_profile:
            return ProfileSummary(
                profile_completed=False,
                completion_percentage=0,
                has_basic_info=False,
                has_academic_info=False,
                has_personal_info=False,
                missing_fields=self._get_default_missing_fields(),
            )

        return ProfileSummary(
            profile_completed=db_profile.profile_completed,
            completion_percentage=db_profile.completion_percentage,
            has_basic_info=db_profile.is_basic_info_complete,
            has_academic_info=db_profile.is_academic_info_complete,
            has_personal_info=db_profile.is_personal_info_complete,
            missing_fields=db_profile.get_missing_fields(),
        )

    def get_completion_status_by_section(
        self, user_id: int
    ) -> Dict[str, ProfileCompletionStatus]:
        """Get detailed completion status for each profile section"""
        db_profile = self.get_profile_by_user_id(user_id)

        if not db_profile:
            return self._get_default_section_status()

        sections = {
            "basic_info": self._get_basic_info_status(db_profile),
            "academic_info": self._get_academic_info_status(db_profile),
            "activities_experience": self._get_activities_status(db_profile),
            "background_demographics": self._get_background_status(db_profile),
            "essays_statements": self._get_essays_status(db_profile),
            "preferences": self._get_preferences_status(db_profile),
        }

        return sections

    def delete_profile(self, user_id: int) -> bool:
        """Delete user profile"""
        db_profile = self.get_profile_by_user_id(user_id)
        if not db_profile:
            return False

        self.db.delete(db_profile)
        self.db.commit()
        return True

    def _get_default_missing_fields(self) -> List[str]:
        """Get default list of missing fields for new profiles"""
        return [
            "High School Name",
            "Graduation Year",
            "GPA",
            "Intended Major",
            "Personal Statement",
            "SAT or ACT Score",
            "Academic Interests",
            "Extracurricular Activities",
        ]

    def _get_default_section_status(self) -> Dict[str, ProfileCompletionStatus]:
        """Get default section status for users without profiles"""
        default_status = ProfileCompletionStatus(
            section_name="",
            is_completed=False,
            completion_percentage=0.0,
            required_fields=[],
            completed_fields=[],
            missing_fields=[],
        )

        return {
            "basic_info": default_status.model_copy(
                update={"section_name": "Basic Information"}
            ),
            "academic_info": default_status.model_copy(
                update={"section_name": "Academic Information"}
            ),
            "activities_experience": default_status.model_copy(
                update={"section_name": "Activities & Experience"}
            ),
            "background_demographics": default_status.model_copy(
                update={"section_name": "Background & Demographics"}
            ),
            "essays_statements": default_status.model_copy(
                update={"section_name": "Essays & Statements"}
            ),
            "preferences": default_status.model_copy(
                update={"section_name": "Preferences"}
            ),
        }

    def _get_basic_info_status(self, profile: UserProfile) -> ProfileCompletionStatus:
        """Get completion status for basic information section"""
        required_fields = ["high_school_name", "graduation_year", "gpa"]
        completed_fields = [
            field for field in required_fields if getattr(profile, field)
        ]
        missing_fields = [
            field for field in required_fields if not getattr(profile, field)
        ]

        return ProfileCompletionStatus(
            section_name="Basic Information",
            is_completed=len(missing_fields) == 0,
            completion_percentage=len(completed_fields) / len(required_fields) * 100,
            required_fields=required_fields,
            completed_fields=completed_fields,
            missing_fields=missing_fields,
        )

    def _get_academic_info_status(
        self, profile: UserProfile
    ) -> ProfileCompletionStatus:
        """Get completion status for academic information section"""
        required_fields = ["intended_major", "academic_interests"]
        test_score_required = profile.sat_score or profile.act_score

        completed_fields = []
        if profile.intended_major:
            completed_fields.append("intended_major")
        if profile.academic_interests:
            completed_fields.append("academic_interests")
        if test_score_required:
            completed_fields.append("test_scores")

        missing_fields = []
        if not profile.intended_major:
            missing_fields.append("intended_major")
        if not profile.academic_interests:
            missing_fields.append("academic_interests")
        if not test_score_required:
            missing_fields.append("test_scores")

        total_required = len(required_fields) + 1  # +1 for test scores

        return ProfileCompletionStatus(
            section_name="Academic Information",
            is_completed=len(missing_fields) == 0,
            completion_percentage=len(completed_fields) / total_required * 100,
            required_fields=required_fields + ["test_scores"],
            completed_fields=completed_fields,
            missing_fields=missing_fields,
        )

    def _get_activities_status(self, profile: UserProfile) -> ProfileCompletionStatus:
        """Get completion status for activities & experience section"""
        required_fields = ["extracurricular_activities", "volunteer_experience"]
        completed_fields = []
        missing_fields = []

        if profile.extracurricular_activities:
            completed_fields.append("extracurricular_activities")
        else:
            missing_fields.append("extracurricular_activities")

        if profile.volunteer_experience:
            completed_fields.append("volunteer_experience")
        else:
            missing_fields.append("volunteer_experience")

        return ProfileCompletionStatus(
            section_name="Activities & Experience",
            is_completed=len(missing_fields) == 0,
            completion_percentage=len(completed_fields) / len(required_fields) * 100,
            required_fields=required_fields,
            completed_fields=completed_fields,
            missing_fields=missing_fields,
        )

    def _get_background_status(self, profile: UserProfile) -> ProfileCompletionStatus:
        """Get completion status for background & demographics section"""
        required_fields = ["household_income_range", "state"]
        completed_fields = []
        missing_fields = []

        if profile.household_income_range:
            completed_fields.append("household_income_range")
        else:
            missing_fields.append("household_income_range")

        if profile.state:
            completed_fields.append("state")
        else:
            missing_fields.append("state")

        return ProfileCompletionStatus(
            section_name="Background & Demographics",
            is_completed=len(missing_fields) == 0,
            completion_percentage=len(completed_fields) / len(required_fields) * 100,
            required_fields=required_fields,
            completed_fields=completed_fields,
            missing_fields=missing_fields,
        )

    def _get_essays_status(self, profile: UserProfile) -> ProfileCompletionStatus:
        """Get completion status for essays & statements section"""
        required_fields = ["personal_statement"]
        completed_fields = []
        missing_fields = []

        if profile.personal_statement:
            completed_fields.append("personal_statement")
        else:
            missing_fields.append("personal_statement")

        return ProfileCompletionStatus(
            section_name="Essays & Statements",
            is_completed=len(missing_fields) == 0,
            completion_percentage=len(completed_fields) / len(required_fields) * 100,
            required_fields=required_fields,
            completed_fields=completed_fields,
            missing_fields=missing_fields,
        )

    def _get_preferences_status(self, profile: UserProfile) -> ProfileCompletionStatus:
        """Get completion status for preferences section"""
        required_fields = ["scholarship_types_interested"]
        completed_fields = []
        missing_fields = []

        if profile.scholarship_types_interested:
            completed_fields.append("scholarship_types_interested")
        else:
            missing_fields.append("scholarship_types_interested")

        return ProfileCompletionStatus(
            section_name="Preferences",
            is_completed=len(missing_fields) == 0,
            completion_percentage=len(completed_fields) / len(required_fields) * 100,
            required_fields=required_fields,
            completed_fields=completed_fields,
            missing_fields=missing_fields,
        )
