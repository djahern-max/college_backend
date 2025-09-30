#!/usr/bin/env python3
"""
Analyze profile completeness field by field
Run from backend directory: python profile_field_analysis.py
"""

from app.core.database import SessionLocal
from app.models.profile import UserProfile
from app.models.user import User


def analyze_profile_fields():
    """Detailed field-by-field analysis of profile completion"""
    db = SessionLocal()

    try:
        # Get your profile
        profile = db.query(UserProfile).filter(UserProfile.user_id == 5).first()

        if not profile:
            print("No profile found for user_id 5")
            return

        user = db.query(User).filter(User.id == 5).first()

        print("\n" + "=" * 80)
        print(f"  PROFILE FIELD ANALYSIS - User: {user.username}")
        print("=" * 80)

        # Define all fields by category
        categories = {
            "BASIC INFORMATION": [
                "high_school_name",
                "graduation_year",
                "gpa",
                "gpa_scale",
                "intended_major",
                "state",
                "city",
                "zip_code",
                "date_of_birth",
                "phone_number",
            ],
            "TEST SCORES": [
                "sat_score",
                "act_score",
                "sat_math",
                "sat_verbal",
                "act_math",
                "act_english",
                "act_science",
                "act_reading",
            ],
            "ACADEMIC DETAILS": [
                "secondary_major",
                "minor_interests",
                "academic_interests",
                "career_goals",
                "ap_courses",
                "honors_courses",
                "dual_enrollment",
                "class_rank",
                "class_size",
            ],
            "ACTIVITIES & EXPERIENCE": [
                "extracurricular_activities",
                "volunteer_experience",
                "volunteer_hours",
                "work_experience",
                "leadership_positions",
                "awards_honors",
                "competitions",
                "sports_activities",
                "arts_activities",
                "musical_instruments",
            ],
            "DEMOGRAPHICS": [
                "ethnicity",
                "gender",
                "first_generation_college",
                "family_income_range",
                "household_size",
                "military_connection",
                "disability_status",
                "lgbtq_identification",
                "rural_background",
            ],
            "COLLEGE PREFERENCES": [
                "preferred_college_size",
                "preferred_states",
                "college_application_status",
                "max_tuition_budget",
                "financial_aid_needed",
                "work_study_interest",
                "campus_setting",
                "religious_affiliation",
                "greek_life_interest",
                "research_opportunities_important",
                "study_abroad_interest",
            ],
            "ESSAYS & STATEMENTS": [
                "has_personal_statement",
                "has_leadership_essay",
                "has_challenges_essay",
                "has_diversity_essay",
                "has_community_service_essay",
                "has_academic_interest_essay",
            ],
            "SCHOLARSHIP PREFERENCES": [
                "scholarship_types_interested",
                "application_deadline_preference",
                "min_scholarship_amount",
                "renewable_scholarships_only",
                "local_scholarships_priority",
            ],
            "ADDITIONAL": [
                "languages_spoken",
                "special_talents",
                "certifications",
                "additional_notes",
                "parent_education_level",
                "parent_occupation",
                "parent_employer",
            ],
        }

        total_fields = 0
        filled_fields = 0

        for category, fields in categories.items():
            print(f"\n{category}")
            print("-" * 80)

            category_total = len(fields)
            category_filled = 0

            for field in fields:
                value = getattr(profile, field, None)
                is_filled = _is_field_filled(value)

                total_fields += 1
                if is_filled:
                    filled_fields += 1
                    category_filled += 1

                status = "✓" if is_filled else "✗"
                value_display = _format_value_for_display(value)

                print(f"  {status} {field:40s} {value_display}")

            category_pct = (
                (category_filled / category_total * 100) if category_total > 0 else 0
            )
            print(
                f"\n  Category completion: {category_filled}/{category_total} ({category_pct:.1f}%)"
            )

        # Summary
        overall_pct = (filled_fields / total_fields * 100) if total_fields > 0 else 0

        print("\n" + "=" * 80)
        print("  SUMMARY")
        print("=" * 80)
        print(f"  Total fields in schema:        {total_fields}")
        print(f"  Fields with data:              {filled_fields}")
        print(f"  Empty fields:                  {total_fields - filled_fields}")
        print(f"  Actual completion:             {overall_pct:.1f}%")
        print(f"\n  Database completion_percentage: {profile.completion_percentage}%")
        print(f"  Profile tier:                   {profile.profile_tier}")
        print("=" * 80)

        # Export to text file
        with open("profile_field_report.txt", "w") as f:
            f.write("=" * 80 + "\n")
            f.write(f"PROFILE FIELD REPORT - User: {user.username}\n")
            f.write("=" * 80 + "\n\n")

            for category, fields in categories.items():
                f.write(f"\n{category}\n")
                f.write("-" * 80 + "\n")

                category_filled = 0
                for field in fields:
                    value = getattr(profile, field, None)
                    is_filled = _is_field_filled(value)
                    if is_filled:
                        category_filled += 1

                    status = "FILLED" if is_filled else "EMPTY"
                    value_display = _format_value_for_display(value)
                    f.write(f"{status:8s} {field:40s} {value_display}\n")

                category_pct = (
                    (category_filled / len(fields) * 100) if len(fields) > 0 else 0
                )
                f.write(
                    f"\nCategory: {category_filled}/{len(fields)} ({category_pct:.1f}%)\n"
                )

            f.write("\n" + "=" * 80 + "\n")
            f.write("SUMMARY\n")
            f.write("=" * 80 + "\n")
            f.write(f"Total fields:     {total_fields}\n")
            f.write(f"Filled:           {filled_fields}\n")
            f.write(f"Empty:            {total_fields - filled_fields}\n")
            f.write(f"Completion:       {overall_pct:.1f}%\n")
            f.write(f"DB Percentage:    {profile.completion_percentage}%\n")
            f.write("=" * 80 + "\n")

        print(f"\n  Report saved to: profile_field_report.txt")
        print()

    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback

        traceback.print_exc()
    finally:
        db.close()


def _is_field_filled(value):
    """Check if a field has meaningful data"""
    if value is None:
        return False

    if isinstance(value, bool):
        # For boolean fields, only True counts as filled
        # False could be default, so we don't count it
        return value is True

    if isinstance(value, (list, dict)):
        return len(value) > 0

    if isinstance(value, str):
        return bool(value.strip())

    if isinstance(value, (int, float)):
        return True

    return bool(value)


def _format_value_for_display(value):
    """Format value for readable display"""
    if value is None:
        return "(empty)"

    if isinstance(value, bool):
        return str(value)

    if isinstance(value, list):
        if len(value) == 0:
            return "(empty list)"
        return f"{value[:2]}..." if len(value) > 2 else str(value)

    if isinstance(value, dict):
        if len(value) == 0:
            return "(empty dict)"
        return f"{{...{len(value)} items}}"

    if isinstance(value, str):
        if len(value) > 40:
            return f'"{value[:37]}..."'
        return f'"{value}"'

    return str(value)


if __name__ == "__main__":
    analyze_profile_fields()
