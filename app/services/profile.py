# app/services/profile.py - UPDATED VERSION
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from datetime import datetime
import logging

from app.models.profile import UserProfile, ProfileTier
from app.schemas.profile import (
    ProfileCreate,
    ProfileUpdate,
    BasicProfileCreate,
    ActivityUpdate,
    DemographicsUpdate,
    AcademicEnhancement,
    EssayUpdate,
    CollegePreferences,
)

logger = logging.getLogger(__name__)


class ProfileService:
    """Enhanced profile service with progressive onboarding support"""

    def __init__(self, db: Session):
        self.db = db

    def get_profile_by_user_id(self, user_id: int) -> Optional[UserProfile]:
        """Get user profile by user ID"""
        try:
            return (
                self.db.query(UserProfile)
                .filter(UserProfile.user_id == user_id)
                .first()
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error getting profile for user {user_id}: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

    # =========================
    # PROGRESSIVE ONBOARDING METHODS
    # =========================

    def create_basic_profile(
        self, user_id: int, profile_data: BasicProfileCreate
    ) -> UserProfile:
        """Phase 1: Create basic profile with minimum required fields"""
        try:
            # Check if profile already exists
            existing_profile = self.get_profile_by_user_id(user_id)
            if existing_profile:
                raise ValueError("Profile already exists for this user")

            # Create basic profile - EXPLICIT field mapping
            db_profile = UserProfile(
                user_id=user_id,
                high_school_name=profile_data.high_school_name,
                graduation_year=profile_data.graduation_year,
                gpa=profile_data.gpa,
                gpa_scale=profile_data.gpa_scale,
                intended_major=profile_data.intended_major,
                state=profile_data.state,
                sat_score=profile_data.sat_score,
                act_score=profile_data.act_score,
                academic_interests=profile_data.academic_interests,
                has_personal_statement=profile_data.has_essays,
                profile_tier=ProfileTier.BASIC,  # Use the enum directly
            )

            # Calculate completion status
            db_profile.update_completion_status()

            self.db.add(db_profile)
            self.db.commit()
            self.db.refresh(db_profile)

            logger.info(f"Created basic profile for user {user_id}")
            return db_profile

        except IntegrityError as e:
            self.db.rollback()
            logger.error(
                f"Integrity error creating basic profile for user {user_id}: {str(e)}"
            )
            raise ValueError(
                "Profile creation failed - user may already have a profile"
            )
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating basic profile for user {user_id}: {str(e)}")
            raise

    # DEBUG: Add this method to your ProfileService to test enum values
    def debug_enum_values(self):
        """Debug method to check enum values"""
        print(f"ProfileTier.BASIC = {ProfileTier.BASIC}")
        print(f"ProfileTier.BASIC.value = {ProfileTier.BASIC.value}")
        print(f"str(ProfileTier.BASIC) = {str(ProfileTier.BASIC)}")
        return {
            "enum_name": ProfileTier.BASIC.name,
            "enum_value": ProfileTier.BASIC.value,
            "str_representation": str(ProfileTier.BASIC),
        }

    def add_activities(
        self, user_id: int, activities_data: ActivityUpdate
    ) -> UserProfile:
        """Phase 2A: Add activities and leadership information"""
        try:
            profile = self._get_existing_profile(user_id)

            # Update activities
            if activities_data.extracurricular_activities:
                profile.extracurricular_activities = (
                    activities_data.extracurricular_activities
                )
            if activities_data.volunteer_experience:
                profile.volunteer_experience = activities_data.volunteer_experience
            if activities_data.volunteer_hours is not None:
                profile.volunteer_hours = activities_data.volunteer_hours
            if activities_data.leadership_positions:
                profile.leadership_positions = activities_data.leadership_positions
            if activities_data.sports_activities:
                profile.sports_activities = activities_data.sports_activities
            if activities_data.arts_activities:
                profile.arts_activities = activities_data.arts_activities

            # Advance tier if appropriate
            if profile.profile_tier == ProfileTier.BASIC:
                profile.profile_tier = ProfileTier.ENHANCED

            profile.update_completion_status()
            self.db.commit()
            self.db.refresh(profile)

            logger.info(f"Updated activities for user {user_id}")
            return profile

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating activities for user {user_id}: {str(e)}")
            raise

    def add_demographics(
        self, user_id: int, demographics_data: DemographicsUpdate
    ) -> UserProfile:
        """Phase 2B: Add demographic information"""
        try:
            profile = self._get_existing_profile(user_id)

            # Update demographics
            if demographics_data.ethnicity:
                profile.ethnicity = demographics_data.ethnicity
            if demographics_data.gender:
                profile.gender = demographics_data.gender
            if demographics_data.first_generation_college is not None:
                profile.first_generation_college = (
                    demographics_data.first_generation_college
                )
            if demographics_data.household_income_range:
                profile.household_income_range = (
                    demographics_data.household_income_range
                )
            if demographics_data.family_size:
                profile.family_size = demographics_data.family_size
            if demographics_data.military_connection is not None:
                profile.military_connection = demographics_data.military_connection
            if demographics_data.disability_status is not None:
                profile.disability_status = demographics_data.disability_status
            if demographics_data.lgbtq_identification is not None:
                profile.lgbtq_identification = demographics_data.lgbtq_identification
            if demographics_data.rural_background is not None:
                profile.rural_background = demographics_data.rural_background

            # Advance tier if appropriate
            if profile.profile_tier == ProfileTier.BASIC:
                profile.profile_tier = ProfileTier.ENHANCED

            profile.update_completion_status()
            self.db.commit()
            self.db.refresh(profile)

            logger.info(f"Updated demographics for user {user_id}")
            return profile

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating demographics for user {user_id}: {str(e)}")
            raise

    def enhance_academic_info(
        self, user_id: int, academic_data: AcademicEnhancement
    ) -> UserProfile:
        """Phase 2C: Enhance academic information"""
        try:
            profile = self._get_existing_profile(user_id)

            # Update test scores
            if academic_data.sat_math:
                profile.sat_math = academic_data.sat_math
            if academic_data.sat_verbal:
                profile.sat_verbal = academic_data.sat_verbal
            if academic_data.act_math:
                profile.act_math = academic_data.act_math
            if academic_data.act_english:
                profile.act_english = academic_data.act_english
            if academic_data.act_science:
                profile.act_science = academic_data.act_science
            if academic_data.act_reading:
                profile.act_reading = academic_data.act_reading

            # Update academic plans
            if academic_data.secondary_major:
                profile.secondary_major = academic_data.secondary_major
            if academic_data.minor_interests:
                profile.minor_interests = academic_data.minor_interests
            if academic_data.career_goals:
                profile.career_goals = academic_data.career_goals

            # Update coursework
            if academic_data.ap_courses:
                profile.ap_courses = academic_data.ap_courses
            if academic_data.honors_courses:
                profile.honors_courses = academic_data.honors_courses
            if academic_data.dual_enrollment is not None:
                profile.dual_enrollment = academic_data.dual_enrollment
            if academic_data.class_rank:
                profile.class_rank = academic_data.class_rank
            if academic_data.class_size:
                profile.class_size = academic_data.class_size

            profile.update_completion_status()
            self.db.commit()
            self.db.refresh(profile)

            logger.info(f"Enhanced academic info for user {user_id}")
            return profile

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error enhancing academic info for user {user_id}: {str(e)}")
            raise

    def update_essay_status(self, user_id: int, essay_data: EssayUpdate) -> UserProfile:
        """Update essay completion status"""
        try:
            profile = self._get_existing_profile(user_id)

            profile.has_personal_statement = essay_data.has_personal_statement
            profile.has_leadership_essay = essay_data.has_leadership_essay
            profile.has_challenges_essay = essay_data.has_challenges_essay
            profile.has_diversity_essay = essay_data.has_diversity_essay
            profile.has_community_service_essay = essay_data.has_community_service_essay
            profile.has_academic_interest_essay = essay_data.has_academic_interest_essay

            profile.update_completion_status()
            self.db.commit()
            self.db.refresh(profile)

            logger.info(f"Updated essay status for user {user_id}")
            return profile

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating essay status for user {user_id}: {str(e)}")
            raise

    def add_college_preferences(
        self, user_id: int, preferences_data: CollegePreferences
    ) -> UserProfile:
        """Phase 3: Add college preferences"""
        try:
            profile = self._get_existing_profile(user_id)

            if preferences_data.preferred_college_size:
                profile.preferred_college_size = preferences_data.preferred_college_size
            if preferences_data.preferred_states:
                profile.preferred_states = preferences_data.preferred_states
            if preferences_data.max_tuition_budget:
                profile.max_tuition_budget = preferences_data.max_tuition_budget
            if preferences_data.financial_aid_needed is not None:
                profile.financial_aid_needed = preferences_data.financial_aid_needed
            if preferences_data.campus_setting:
                profile.campus_setting = preferences_data.campus_setting
            if preferences_data.religious_affiliation:
                profile.religious_affiliation = preferences_data.religious_affiliation
            if preferences_data.greek_life_interest is not None:
                profile.greek_life_interest = preferences_data.greek_life_interest
            if preferences_data.research_opportunities_important is not None:
                profile.research_opportunities_important = (
                    preferences_data.research_opportunities_important
                )
            if preferences_data.study_abroad_interest is not None:
                profile.study_abroad_interest = preferences_data.study_abroad_interest

            # Advance to complete tier
            if profile.profile_tier in [ProfileTier.BASIC, ProfileTier.ENHANCED]:
                profile.profile_tier = ProfileTier.COMPLETE

            profile.update_completion_status()
            self.db.commit()
            self.db.refresh(profile)

            logger.info(f"Added college preferences for user {user_id}")
            return profile

        except Exception as e:
            self.db.rollback()
            logger.error(
                f"Error adding college preferences for user {user_id}: {str(e)}"
            )
            raise

    # =========================
    # PROGRESS TRACKING METHODS
    # =========================

    def get_completion_progress(self, user_id: int) -> Dict[str, Any]:
        """Get detailed completion progress for a user"""
        profile = self.get_profile_by_user_id(user_id)

        if not profile:
            return {
                "completion_percentage": 0,
                "tier": ProfileTier.BASIC,
                "missing_basic_fields": [
                    "high_school_name",
                    "graduation_year",
                    "gpa",
                    "intended_major",
                    "state",
                    "test_scores",
                ],
                "next_steps": [
                    {
                        "action": "create_basic_profile",
                        "title": "Complete Basic Profile",
                        "impact": "Start receiving scholarship matches",
                        "time_estimate": "3 minutes",
                    }
                ],
                "can_advance": False,
            }

        missing_basic = profile.get_missing_basic_fields()
        next_steps = self._generate_next_steps(profile)

        return {
            "completion_percentage": profile.completion_percentage,
            "tier": profile.profile_tier,
            "missing_basic_fields": missing_basic,
            "next_steps": next_steps,
            "can_advance": profile.can_advance_to_enhanced(),
            "profile_completed": profile.profile_completed,
        }

    def _generate_next_steps(self, profile: UserProfile) -> List[Dict[str, str]]:
        """Generate personalized next steps based on current profile state"""
        steps = []

        # Missing basic fields
        missing_basic = profile.get_missing_basic_fields()
        if missing_basic:
            steps.append(
                {
                    "action": "complete_basic_fields",
                    "title": f"Complete {len(missing_basic)} basic fields",
                    "impact": "Required for scholarship matching",
                    "time_estimate": "2 minutes",
                }
            )

        # Activities enhancement
        if not profile.extracurricular_activities and not profile.volunteer_experience:
            steps.append(
                {
                    "action": "add_activities",
                    "title": "Add Activities & Leadership",
                    "impact": "+15-25 new matches",
                    "time_estimate": "4 minutes",
                }
            )

        # Essay status
        if not profile.has_personal_statement:
            steps.append(
                {
                    "action": "upload_essay",
                    "title": "Upload Personal Statement",
                    "impact": "+20-35 new matches",
                    "time_estimate": "1 minute",
                }
            )

        # Demographics for targeted scholarships
        if not profile.ethnicity and profile.first_generation_college is None:
            steps.append(
                {
                    "action": "add_demographics",
                    "title": "Add Background Info",
                    "impact": "+10-20 targeted matches",
                    "time_estimate": "2 minutes",
                }
            )

        return steps[:3]  # Return top 3 recommendations

    # =========================
    # TRADITIONAL CRUD METHODS
    # =========================

    def create_profile(self, user_id: int, profile_data: ProfileCreate) -> UserProfile:
        """CREATE - Create a comprehensive profile from ProfileCreate data"""
        try:
            # Check if profile already exists
            existing_profile = self.get_profile_by_user_id(user_id)
            if existing_profile:
                raise ValueError("Profile already exists for this user")

            # Create profile with comprehensive data
            profile_dict = profile_data.model_dump(exclude_unset=True)

            # CRITICAL FIX: Ensure profile_tier is set to the correct enum value
            profile_dict["profile_tier"] = (
                ProfileTier.BASIC
            )  # This should use the enum, not the string
            profile_dict["user_id"] = user_id

            db_profile = UserProfile(**profile_dict)

            # Calculate completion status
            db_profile.update_completion_status()

            self.db.add(db_profile)
            self.db.commit()
            self.db.refresh(db_profile)

            logger.info(f"Created comprehensive profile for user {user_id}")
            return db_profile

        except IntegrityError as e:
            self.db.rollback()
            logger.error(
                f"Integrity error creating profile for user {user_id}: {str(e)}"
            )
            raise ValueError(
                "Profile creation failed - user may already have a profile"
            )
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating profile for user {user_id}: {str(e)}")
            raise

    def update_profile(self, user_id: int, profile_data: ProfileUpdate) -> UserProfile:
        """UPDATE - Update existing profile"""
        try:
            profile = self._get_existing_profile(user_id)

            # Update fields with new data
            update_dict = profile_data.model_dump(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(profile, field, value)

            profile.update_completion_status()
            self.db.commit()
            self.db.refresh(profile)

            logger.info(f"Updated profile for user {user_id}")
            return profile

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating profile for user {user_id}: {str(e)}")
            raise

    def delete_profile(self, user_id: int) -> bool:
        """DELETE - Remove user profile"""
        try:
            profile = self._get_existing_profile(user_id)
            self.db.delete(profile)
            self.db.commit()

            logger.info(f"Deleted profile for user {user_id}")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting profile for user {user_id}: {str(e)}")
            raise

    # =========================
    # HELPER METHODS
    # =========================

    def _get_existing_profile(self, user_id: int) -> UserProfile:
        """Get existing profile or raise exception"""
        profile = self.get_profile_by_user_id(user_id)
        if not profile:
            raise ValueError(f"No profile found for user {user_id}")
        return profile

    def get_contextual_suggestions(
        self, user_id: int, context: str
    ) -> List[Dict[str, Any]]:
        """Get contextual suggestions based on user behavior"""
        profile = self.get_profile_by_user_id(user_id)
        if not profile:
            return []

        suggestions = []

        if context == "viewing_stem_scholarships":
            if not profile.ap_courses:
                suggestions.append(
                    {
                        "field": "ap_courses",
                        "message": "Add your AP math/science courses to strengthen STEM matches",
                        "impact": "Better STEM scholarship rankings",
                        "priority": "high",
                    }
                )
            if (
                not profile.intended_major
                or "computer" not in profile.intended_major.lower()
            ):
                suggestions.append(
                    {
                        "field": "intended_major",
                        "message": "Specify your STEM major for targeted scholarships",
                        "impact": "Access field-specific opportunities",
                        "priority": "medium",
                    }
                )

        elif context == "viewing_need_based_aid":
            if not profile.household_income_range:
                suggestions.append(
                    {
                        "field": "household_income_range",
                        "message": "Add income information to access need-based scholarships",
                        "impact": "Unlock need-based opportunities",
                        "priority": "high",
                        "privacy_note": "This information is kept private and secure",
                    }
                )

        elif context == "viewing_diversity_scholarships":
            if not profile.ethnicity and profile.first_generation_college is None:
                suggestions.append(
                    {
                        "field": "demographics",
                        "message": "Add background information for diversity scholarships",
                        "impact": "Access targeted diversity opportunities",
                        "priority": "medium",
                    }
                )

        return suggestions
