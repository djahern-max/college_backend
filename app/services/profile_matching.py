# app/services/profile_matching.py
"""
Profile Matching Service - Ensures profile data aligns perfectly with scholarship requirements
"""
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy.orm import Session
from app.models.profile import UserProfile
from app.models.scholarship import Scholarship, ScholarshipType
from app.schemas.profile import ProfileCompletionStatus
import logging

logger = logging.getLogger(__name__)


class ProfileMatchingService:
    """Service to validate profile completeness for scholarship matching"""

    def __init__(self, db: Session):
        self.db = db

    def validate_profile_for_matching(self, user_id: int) -> Dict[str, Any]:
        """
        Comprehensive validation of profile for scholarship matching
        Returns detailed analysis of profile completeness and matching readiness
        """
        profile = (
            self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        )

        if not profile:
            return self._get_empty_profile_validation()

        validation_results = {
            "overall_match_readiness": 0,
            "critical_missing_fields": [],
            "recommended_fields": [],
            "scholarship_types_ready": [],
            "scholarship_types_limited": [],
            "matching_strengths": [],
            "matching_weaknesses": [],
            "completion_by_category": {},
            "optimization_suggestions": [],
        }

        # Validate critical matching fields
        critical_score = self._validate_critical_fields(profile, validation_results)

        # Validate academic fields
        academic_score = self._validate_academic_fields(profile, validation_results)

        # Validate demographic fields
        demographic_score = self._validate_demographic_fields(
            profile, validation_results
        )

        # Validate activity fields
        activity_score = self._validate_activity_fields(profile, validation_results)

        # Validate location fields
        location_score = self._validate_location_fields(profile, validation_results)

        # Calculate overall readiness score
        validation_results["overall_match_readiness"] = round(
            (
                critical_score * 0.4
                + academic_score * 0.25
                + demographic_score * 0.15
                + activity_score * 0.15
                + location_score * 0.05
            ),
            1,
        )

        # Store completion by category
        validation_results["completion_by_category"] = {
            "critical_fields": critical_score,
            "academic_info": academic_score,
            "demographics": demographic_score,
            "activities": activity_score,
            "location": location_score,
        }

        # Determine scholarship readiness
        self._assess_scholarship_readiness(profile, validation_results)

        # Generate optimization suggestions
        self._generate_optimization_suggestions(profile, validation_results)

        return validation_results

    def _validate_critical_fields(self, profile: UserProfile, results: Dict) -> float:
        """Validate fields critical for most scholarships"""
        critical_fields = {
            "gpa": profile.gpa,
            "graduation_year": profile.graduation_year,
            "intended_major": profile.intended_major,
            "high_school_name": profile.high_school_name,
        }

        completed = 0
        total = len(critical_fields)

        for field_name, value in critical_fields.items():
            if value is not None and str(value).strip():
                completed += 1
                results["matching_strengths"].append(
                    f"Has {field_name.replace('_', ' ')}"
                )
            else:
                results["critical_missing_fields"].append(
                    field_name.replace("_", " ").title()
                )
                results["matching_weaknesses"].append(
                    f"Missing {field_name.replace('_', ' ')}"
                )

        # Test scores are critical but either SAT or ACT is sufficient
        if profile.sat_score or profile.act_score:
            completed += 0.5  # Bonus for having test scores
            results["matching_strengths"].append("Has standardized test scores")
        else:
            results["recommended_fields"].append("SAT or ACT score")
            results["matching_weaknesses"].append("No standardized test scores")

        return (completed / total) * 100

    def _validate_academic_fields(self, profile: UserProfile, results: Dict) -> float:
        """Validate academic information fields"""
        academic_fields = {
            "academic_interests": profile.academic_interests,
            "career_goals": profile.career_goals,
            "personal_statement": profile.personal_statement,
        }

        completed = 0
        total = len(academic_fields)

        for field_name, value in academic_fields.items():
            if value and (
                isinstance(value, list)
                and len(value) > 0
                or isinstance(value, str)
                and value.strip()
            ):
                completed += 1
                results["matching_strengths"].append(
                    f"Has {field_name.replace('_', ' ')}"
                )
            else:
                results["recommended_fields"].append(
                    field_name.replace("_", " ").title()
                )

        # Bonus for having both SAT and ACT scores
        if profile.sat_score and profile.act_score:
            completed += 0.3
            results["matching_strengths"].append("Has both SAT and ACT scores")

        return (completed / total) * 100

    def _validate_demographic_fields(
        self, profile: UserProfile, results: Dict
    ) -> float:
        """Validate demographic fields for diversity scholarships"""
        demographic_fields = {
            "ethnicity": profile.ethnicity,
            "first_generation_college": profile.first_generation_college,
            "household_income_range": profile.household_income_range,
        }

        completed = 0
        total = len(demographic_fields)

        for field_name, value in demographic_fields.items():
            if value is not None and (
                isinstance(value, list)
                and len(value) > 0
                or isinstance(value, (str, bool))
                and str(value).strip()
            ):
                completed += 1
                if field_name == "first_generation_college" and value:
                    results["matching_strengths"].append(
                        "First-generation college student"
                    )
                elif field_name == "ethnicity" and value:
                    results["matching_strengths"].append(
                        "Demographic diversity information provided"
                    )
            else:
                results["recommended_fields"].append(
                    f"{field_name.replace('_', ' ').title()} (for diversity scholarships)"
                )

        return (completed / total) * 100

    def _validate_activity_fields(self, profile: UserProfile, results: Dict) -> float:
        """Validate activity and experience fields"""
        activity_fields = {
            "extracurricular_activities": profile.extracurricular_activities,
            "volunteer_experience": profile.volunteer_experience,
            "volunteer_hours": profile.volunteer_hours,
            "special_talents": profile.special_talents,
        }

        completed = 0
        total = len(activity_fields)

        for field_name, value in activity_fields.items():
            if value and (
                isinstance(value, list)
                and len(value) > 0
                or isinstance(value, (int, float))
                and value > 0
            ):
                completed += 1
                if field_name == "volunteer_hours" and value >= 50:
                    results["matching_strengths"].append(
                        f"Significant volunteer hours ({value})"
                    )
                elif (
                    field_name in ["extracurricular_activities", "volunteer_experience"]
                    and len(value) >= 3
                ):
                    results["matching_strengths"].append(
                        f"Strong {field_name.replace('_', ' ')}"
                    )
            else:
                results["recommended_fields"].append(
                    field_name.replace("_", " ").title()
                )

        return (completed / total) * 100

    def _validate_location_fields(self, profile: UserProfile, results: Dict) -> float:
        """Validate location fields for geographic scholarships"""
        location_fields = {
            "state": profile.state,
            "city": profile.city,
            "zip_code": profile.zip_code,
        }

        completed = 0
        total = len(location_fields)

        for field_name, value in location_fields.items():
            if value and str(value).strip():
                completed += 1
                if field_name == "state":
                    results["matching_strengths"].append(f"Located in {value}")

        return (completed / total) * 100

    def _assess_scholarship_readiness(self, profile: UserProfile, results: Dict):
        """Assess readiness for different types of scholarships"""
        # Academic/Merit scholarships
        if (
            profile.gpa
            and profile.gpa >= 3.0
            and (profile.sat_score or profile.act_score)
            and profile.intended_major
        ):
            results["scholarship_types_ready"].append("Academic Merit Scholarships")
        else:
            results["scholarship_types_limited"].append(
                "Academic Merit Scholarships (need GPA, test scores, major)"
            )

        # STEM scholarships
        if (
            profile.intended_major
            and any(
                stem_keyword in profile.intended_major.lower()
                for stem_keyword in [
                    "computer",
                    "engineer",
                    "math",
                    "science",
                    "physics",
                    "chemistry",
                    "biology",
                ]
            )
            and profile.gpa
            and profile.gpa >= 3.2
        ):
            results["scholarship_types_ready"].append("STEM Scholarships")
        elif profile.academic_interests and any(
            "STEM" in interest or "Technology" in interest
            for interest in profile.academic_interests
        ):
            results["scholarship_types_ready"].append("STEM Interest Scholarships")

        # Need-based scholarships
        if profile.household_income_range and profile.household_income_range in [
            "Under $25,000",
            "$25,000 - $50,000",
        ]:
            results["scholarship_types_ready"].append("Need-Based Scholarships")

        # Diversity scholarships
        if (
            profile.ethnicity
            and len(profile.ethnicity) > 0
            or profile.first_generation_college
        ):
            results["scholarship_types_ready"].append(
                "Diversity & Inclusion Scholarships"
            )

        # Community service scholarships
        if (
            profile.volunteer_experience
            and len(profile.volunteer_experience) > 0
            and profile.volunteer_hours
            and profile.volunteer_hours >= 25
        ):
            results["scholarship_types_ready"].append("Community Service Scholarships")

        # Local scholarships
        if profile.state and profile.city:
            results["scholarship_types_ready"].append("Local & Regional Scholarships")

        # Leadership scholarships
        if (
            profile.extracurricular_activities
            and any(
                "leader" in activity.lower()
                or "president" in activity.lower()
                or "captain" in activity.lower()
                for activity in profile.extracurricular_activities
            )
            or profile.leadership_essay
        ):
            results["scholarship_types_ready"].append("Leadership Scholarships")

    def _generate_optimization_suggestions(self, profile: UserProfile, results: Dict):
        """Generate specific suggestions to improve matching potential"""
        suggestions = []

        # Critical field suggestions
        if not profile.gpa:
            suggestions.append(
                {
                    "priority": "high",
                    "category": "academic",
                    "suggestion": "Add your GPA - this is required for 90% of scholarships",
                    "impact": "Unlock most academic merit scholarships",
                }
            )

        if not profile.sat_score and not profile.act_score:
            suggestions.append(
                {
                    "priority": "high",
                    "category": "academic",
                    "suggestion": "Add SAT or ACT scores to qualify for merit-based scholarships",
                    "impact": "Increase scholarship matches by ~60%",
                }
            )

        if not profile.intended_major:
            suggestions.append(
                {
                    "priority": "high",
                    "category": "academic",
                    "suggestion": "Specify your intended major to access field-specific scholarships",
                    "impact": "Unlock major-specific scholarship opportunities",
                }
            )

        # Academic improvement suggestions
        if not profile.academic_interests or len(profile.academic_interests) < 2:
            suggestions.append(
                {
                    "priority": "medium",
                    "category": "academic",
                    "suggestion": "Add 2-3 academic interests to improve matching accuracy",
                    "impact": "Better alignment with scholarship goals",
                }
            )

        if not profile.personal_statement:
            suggestions.append(
                {
                    "priority": "medium",
                    "category": "essays",
                    "suggestion": "Write a personal statement for scholarships requiring essays",
                    "impact": "Qualify for essay-based scholarships",
                }
            )

        # Activity suggestions
        if not profile.volunteer_experience or len(profile.volunteer_experience) == 0:
            suggestions.append(
                {
                    "priority": "medium",
                    "category": "activities",
                    "suggestion": "Add volunteer experience to access community service scholarships",
                    "impact": "Unlock service-based scholarships",
                }
            )

        if (
            not profile.extracurricular_activities
            or len(profile.extracurricular_activities) < 2
        ):
            suggestions.append(
                {
                    "priority": "medium",
                    "category": "activities",
                    "suggestion": "List extracurricular activities to show well-roundedness",
                    "impact": "Demonstrate leadership and involvement",
                }
            )

        # Demographic suggestions
        if profile.first_generation_college is None:
            suggestions.append(
                {
                    "priority": "low",
                    "category": "demographics",
                    "suggestion": "Indicate first-generation college status for targeted scholarships",
                    "impact": "Access first-generation specific scholarships",
                }
            )

        if not profile.ethnicity:
            suggestions.append(
                {
                    "priority": "low",
                    "category": "demographics",
                    "suggestion": "Consider adding ethnicity information for diversity scholarships (optional)",
                    "impact": "Access diversity and inclusion scholarships",
                }
            )

        # Location suggestions
        if not profile.state:
            suggestions.append(
                {
                    "priority": "medium",
                    "category": "location",
                    "suggestion": "Add your state to access local and regional scholarships",
                    "impact": "Unlock location-specific opportunities",
                }
            )

        results["optimization_suggestions"] = suggestions

    def _get_empty_profile_validation(self) -> Dict[str, Any]:
        """Return validation results for users without profiles"""
        return {
            "overall_match_readiness": 0,
            "critical_missing_fields": [
                "GPA",
                "Graduation Year",
                "Intended Major",
                "High School Name",
                "Test Scores",
            ],
            "recommended_fields": [
                "Academic Interests",
                "Personal Statement",
                "Extracurricular Activities",
                "Volunteer Experience",
            ],
            "scholarship_types_ready": [],
            "scholarship_types_limited": [
                "All scholarship types require basic profile completion"
            ],
            "matching_strengths": [],
            "matching_weaknesses": ["No profile information available"],
            "completion_by_category": {
                "critical_fields": 0,
                "academic_info": 0,
                "demographics": 0,
                "activities": 0,
                "location": 0,
            },
            "optimization_suggestions": [
                {
                    "priority": "high",
                    "category": "setup",
                    "suggestion": "Complete your profile to start finding scholarships",
                    "impact": "Begin receiving scholarship matches",
                }
            ],
        }

    def get_matching_field_map(self) -> Dict[str, List[str]]:
        """
        Returns a mapping of profile fields to scholarship criteria fields
        for ensuring complete alignment
        """
        return {
            # Academic matching
            "gpa": ["min_gpa", "max_gpa"],
            "sat_score": ["min_sat_score"],
            "act_score": ["min_act_score"],
            "intended_major": ["required_majors"],
            "academic_interests": ["academic_interests"],
            # Geographic matching
            "state": ["eligible_states"],
            "city": ["eligible_cities"],
            "zip_code": ["zip_codes"],
            # Demographic matching
            "ethnicity": ["eligible_ethnicities"],
            "first_generation_college": ["first_generation_college_required"],
            "household_income_range": ["income_min", "income_max"],
            # School matching
            "high_school_name": ["high_school_names"],
            "graduation_year": ["graduation_year_min", "graduation_year_max"],
            # Activity matching
            "extracurricular_activities": ["required_activities"],
            "volunteer_experience": ["required_activities"],
            "special_talents": ["special_talents"],
            "languages_preferred": ["languages_preferred"],
            # Essay requirements (mapped to boolean fields in scholarships)
            "personal_statement": ["essay_required"],
            "leadership_essay": ["leadership_essay_required"],
        }

    def validate_field_alignment(
        self, profile_field: str, scholarship_field: str
    ) -> bool:
        """
        Validate that a profile field properly aligns with a scholarship field
        """
        field_map = self.get_matching_field_map()

        if profile_field in field_map:
            return scholarship_field in field_map[profile_field]

        return False

    def get_profile_coverage_report(self, user_id: int) -> Dict[str, Any]:
        """
        Generate a report showing how well the profile covers different
        scholarship categories and requirements
        """
        profile = (
            self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        )

        if not profile:
            return {"error": "Profile not found"}

        # Get all active scholarships to analyze coverage
        active_scholarships = (
            self.db.query(Scholarship)
            .filter(Scholarship.status == "ACTIVE", Scholarship.verified == True)
            .all()
        )

        coverage_report = {
            "total_scholarships": len(active_scholarships),
            "potentially_eligible": 0,
            "fully_eligible": 0,
            "coverage_by_type": {},
            "missing_opportunities": [],
            "top_recommendations": [],
        }

        for scholarship in active_scholarships:
            eligibility_score = self._calculate_scholarship_eligibility(
                profile, scholarship
            )

            if eligibility_score > 0.5:
                coverage_report["potentially_eligible"] += 1

            if eligibility_score > 0.8:
                coverage_report["fully_eligible"] += 1

            # Track by scholarship type
            sch_type = scholarship.scholarship_type.value
            if sch_type not in coverage_report["coverage_by_type"]:
                coverage_report["coverage_by_type"][sch_type] = {
                    "total": 0,
                    "eligible": 0,
                    "fully_eligible": 0,
                }

            coverage_report["coverage_by_type"][sch_type]["total"] += 1
            if eligibility_score > 0.5:
                coverage_report["coverage_by_type"][sch_type]["eligible"] += 1
            if eligibility_score > 0.8:
                coverage_report["coverage_by_type"][sch_type]["fully_eligible"] += 1

        return coverage_report

    def _calculate_scholarship_eligibility(
        self, profile: UserProfile, scholarship: Scholarship
    ) -> float:
        """Calculate how eligible a profile is for a specific scholarship (0-1 score)"""
        score = 0.0
        criteria_count = 0

        # GPA criteria
        if scholarship.min_gpa:
            criteria_count += 1
            if profile.gpa and profile.gpa >= scholarship.min_gpa:
                score += 1

        # Test score criteria
        if scholarship.min_sat_score or scholarship.min_act_score:
            criteria_count += 1
            if (
                scholarship.min_sat_score
                and profile.sat_score
                and profile.sat_score >= scholarship.min_sat_score
            ) or (
                scholarship.min_act_score
                and profile.act_score
                and profile.act_score >= scholarship.min_act_score
            ):
                score += 1

        # Major criteria
        if scholarship.required_majors:
            criteria_count += 1
            if (
                profile.intended_major
                and profile.intended_major in scholarship.required_majors
            ):
                score += 1

        # Geographic criteria
        if scholarship.eligible_states:
            criteria_count += 1
            if profile.state and profile.state in scholarship.eligible_states:
                score += 1

        # Demographic criteria
        if scholarship.first_generation_college_required is not None:
            criteria_count += 1
            if (
                profile.first_generation_college
                == scholarship.first_generation_college_required
            ):
                score += 1

        if criteria_count == 0:
            return 1.0  # No specific criteria means potentially eligible

        return score / criteria_count


class ProfileCompletionAnalyzer:
    """Analyzer specifically for profile completion tracking"""

    def __init__(self, db: Session):
        self.db = db

    def analyze_section_completion(
        self, profile: UserProfile, section_name: str
    ) -> ProfileCompletionStatus:
        """Analyze completion of a specific profile section"""

        analyzers = {
            "basic_info": self._analyze_basic_info,
            "academic_info": self._analyze_academic_info,
            "activities_experience": self._analyze_activities,
            "background_demographics": self._analyze_demographics,
            "essays_statements": self._analyze_essays,
            "preferences": self._analyze_preferences,
        }

        if section_name in analyzers:
            return analyzers[section_name](profile)

        # Default empty status
        return ProfileCompletionStatus(
            section_name=section_name,
            is_completed=False,
            completion_percentage=0.0,
            required_fields=[],
            completed_fields=[],
            missing_fields=[],
        )

    def _analyze_basic_info(self, profile: UserProfile) -> ProfileCompletionStatus:
        """Analyze basic information section completion"""
        required_fields = ["high_school_name", "graduation_year", "gpa", "state"]
        completed_fields = []
        missing_fields = []

        field_mapping = {
            "high_school_name": profile.high_school_name,
            "graduation_year": profile.graduation_year,
            "gpa": profile.gpa,
            "state": profile.state,
        }

        for field, value in field_mapping.items():
            if value is not None and str(value).strip():
                completed_fields.append(field)
            else:
                missing_fields.append(field)

        return ProfileCompletionStatus(
            section_name="Basic Information",
            is_completed=len(missing_fields) == 0,
            completion_percentage=round(
                (len(completed_fields) / len(required_fields)) * 100, 1
            ),
            required_fields=required_fields,
            completed_fields=completed_fields,
            missing_fields=missing_fields,
        )

    def _analyze_academic_info(self, profile: UserProfile) -> ProfileCompletionStatus:
        """Analyze academic information section completion"""
        required_fields = ["intended_major", "test_scores", "academic_interests"]
        completed_fields = []
        missing_fields = []

        # Check intended major
        if profile.intended_major:
            completed_fields.append("intended_major")
        else:
            missing_fields.append("intended_major")

        # Check test scores (either SAT or ACT)
        if profile.sat_score or profile.act_score:
            completed_fields.append("test_scores")
        else:
            missing_fields.append("test_scores")

        # Check academic interests
        if profile.academic_interests and len(profile.academic_interests) > 0:
            completed_fields.append("academic_interests")
        else:
            missing_fields.append("academic_interests")

        return ProfileCompletionStatus(
            section_name="Academic Information",
            is_completed=len(missing_fields) == 0,
            completion_percentage=round(
                (len(completed_fields) / len(required_fields)) * 100, 1
            ),
            required_fields=required_fields,
            completed_fields=completed_fields,
            missing_fields=missing_fields,
        )

    def _analyze_activities(self, profile: UserProfile) -> ProfileCompletionStatus:
        """Analyze activities and experience section completion"""
        required_fields = ["extracurricular_activities", "volunteer_experience"]
        completed_fields = []
        missing_fields = []

        # Check extracurricular activities
        if (
            profile.extracurricular_activities
            and len(profile.extracurricular_activities) > 0
        ):
            completed_fields.append("extracurricular_activities")
        else:
            missing_fields.append("extracurricular_activities")

        # Check volunteer experience
        if profile.volunteer_experience and len(profile.volunteer_experience) > 0:
            completed_fields.append("volunteer_experience")
        else:
            missing_fields.append("volunteer_experience")

        return ProfileCompletionStatus(
            section_name="Activities & Experience",
            is_completed=len(missing_fields) == 0,
            completion_percentage=round(
                (len(completed_fields) / len(required_fields)) * 100, 1
            ),
            required_fields=required_fields,
            completed_fields=completed_fields,
            missing_fields=missing_fields,
        )

    def _analyze_demographics(self, profile: UserProfile) -> ProfileCompletionStatus:
        """Analyze demographics section completion"""
        required_fields = ["household_income_range"]
        completed_fields = []
        missing_fields = []

        if profile.household_income_range:
            completed_fields.append("household_income_range")
        else:
            missing_fields.append("household_income_range")

        return ProfileCompletionStatus(
            section_name="Background & Demographics",
            is_completed=len(missing_fields) == 0,
            completion_percentage=round(
                (len(completed_fields) / len(required_fields)) * 100, 1
            ),
            required_fields=required_fields,
            completed_fields=completed_fields,
            missing_fields=missing_fields,
        )

    def _analyze_essays(self, profile: UserProfile) -> ProfileCompletionStatus:
        """Analyze essays section completion"""
        required_fields = ["personal_statement"]
        completed_fields = []
        missing_fields = []

        if profile.personal_statement and profile.personal_statement.strip():
            completed_fields.append("personal_statement")
        else:
            missing_fields.append("personal_statement")

        return ProfileCompletionStatus(
            section_name="Essays & Statements",
            is_completed=len(missing_fields) == 0,
            completion_percentage=round(
                (len(completed_fields) / len(required_fields)) * 100, 1
            ),
            required_fields=required_fields,
            completed_fields=completed_fields,
            missing_fields=missing_fields,
        )

    def _analyze_preferences(self, profile: UserProfile) -> ProfileCompletionStatus:
        """Analyze preferences section completion"""
        required_fields = ["scholarship_types_interested"]
        completed_fields = []
        missing_fields = []

        if (
            profile.scholarship_types_interested
            and len(profile.scholarship_types_interested) > 0
        ):
            completed_fields.append("scholarship_types_interested")
        else:
            missing_fields.append("scholarship_types_interested")

        return ProfileCompletionStatus(
            section_name="Scholarship Preferences",
            is_completed=len(missing_fields) == 0,
            completion_percentage=round(
                (len(completed_fields) / len(required_fields)) * 100, 1
            ),
            required_fields=required_fields,
            completed_fields=completed_fields,
            missing_fields=missing_fields,
        )
