"""Improving Profile Model for Progressive Onboarding

Revision ID: 74d4d6720607
Revises: 92e14d33943b
Create Date: 2025-09-21 15:36:25.444795

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "74d4d6720607"
down_revision: Union[str, None] = "92e14d33943b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### FIRST: Drop the problematic tuition indexes ###
    op.drop_index("ix_tuition_data_has_data_flags", table_name="tuition_data")
    op.drop_index(
        "ix_tuition_data_has_data_ipeds",
        table_name="tuition_data",
        postgresql_where="(has_tuition_data = true)",
    )
    op.drop_index("ix_tuition_data_ipeds_academic_year", table_name="tuition_data")
    op.drop_index("ix_tuition_data_quality_validation", table_name="tuition_data")

    # ### SECOND: Create new ENUMs first ###
    # Create the enums with correct values (lowercase with underscores, not UPPERCASE)
    op.execute(
        "CREATE TYPE incomerange AS ENUM ('under_30k', '30k_50k', '50k_75k', '75k_100k', '100k_150k', 'over_150k', 'prefer_not_to_say')"
    )
    op.execute(
        "CREATE TYPE profiletier AS ENUM ('basic', 'enhanced', 'complete', 'optimized')"
    )
    op.execute(
        "CREATE TYPE collegesize AS ENUM ('very_small', 'small', 'medium', 'large', 'very_large', 'no_preference')"
    )

    # ### THIRD: Add new columns ###

    # Academic enhancements
    op.add_column(
        "user_profiles",
        sa.Column(
            "gpa_scale", sa.String(length=10), nullable=True, server_default="4.0"
        ),
    )
    op.add_column("user_profiles", sa.Column("sat_math", sa.Integer(), nullable=True))
    op.add_column("user_profiles", sa.Column("sat_verbal", sa.Integer(), nullable=True))
    op.add_column("user_profiles", sa.Column("act_math", sa.Integer(), nullable=True))
    op.add_column(
        "user_profiles", sa.Column("act_english", sa.Integer(), nullable=True)
    )
    op.add_column(
        "user_profiles", sa.Column("act_science", sa.Integer(), nullable=True)
    )
    op.add_column(
        "user_profiles", sa.Column("act_reading", sa.Integer(), nullable=True)
    )

    op.add_column(
        "user_profiles",
        sa.Column("secondary_major", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "user_profiles",
        sa.Column("minor_interests", postgresql.ARRAY(sa.String()), nullable=True),
    )
    op.add_column(
        "user_profiles",
        sa.Column("ap_courses", postgresql.ARRAY(sa.String()), nullable=True),
    )
    op.add_column(
        "user_profiles",
        sa.Column("honors_courses", postgresql.ARRAY(sa.String()), nullable=True),
    )
    op.add_column(
        "user_profiles",
        sa.Column(
            "dual_enrollment", sa.Boolean(), nullable=True, server_default="false"
        ),
    )
    op.add_column("user_profiles", sa.Column("class_rank", sa.Integer(), nullable=True))
    op.add_column("user_profiles", sa.Column("class_size", sa.Integer(), nullable=True))

    # Enhanced activities
    op.add_column(
        "user_profiles", sa.Column("leadership_positions", sa.JSON(), nullable=True)
    )
    op.add_column(
        "user_profiles",
        sa.Column("awards_honors", postgresql.ARRAY(sa.String()), nullable=True),
    )
    op.add_column("user_profiles", sa.Column("competitions", sa.JSON(), nullable=True))
    op.add_column(
        "user_profiles", sa.Column("sports_activities", sa.JSON(), nullable=True)
    )
    op.add_column(
        "user_profiles", sa.Column("arts_activities", sa.JSON(), nullable=True)
    )
    op.add_column(
        "user_profiles",
        sa.Column("musical_instruments", postgresql.ARRAY(sa.String()), nullable=True),
    )

    # Enhanced demographics
    op.add_column(
        "user_profiles", sa.Column("gender", sa.String(length=50), nullable=True)
    )
    op.add_column(
        "user_profiles", sa.Column("family_size", sa.Integer(), nullable=True)
    )
    op.add_column(
        "user_profiles",
        sa.Column(
            "military_connection", sa.Boolean(), nullable=True, server_default="false"
        ),
    )
    op.add_column(
        "user_profiles", sa.Column("disability_status", sa.Boolean(), nullable=True)
    )
    op.add_column(
        "user_profiles", sa.Column("lgbtq_identification", sa.Boolean(), nullable=True)
    )
    op.add_column(
        "user_profiles", sa.Column("rural_background", sa.Boolean(), nullable=True)
    )

    # College preferences
    op.add_column(
        "user_profiles",
        sa.Column("preferred_states", postgresql.ARRAY(sa.String()), nullable=True),
    )
    op.add_column(
        "user_profiles", sa.Column("max_tuition_budget", sa.Integer(), nullable=True)
    )
    op.add_column(
        "user_profiles", sa.Column("financial_aid_needed", sa.Boolean(), nullable=True)
    )
    op.add_column(
        "user_profiles",
        sa.Column(
            "work_study_interest", sa.Boolean(), nullable=True, server_default="false"
        ),
    )

    op.add_column(
        "user_profiles",
        sa.Column("campus_setting", postgresql.ARRAY(sa.String()), nullable=True),
    )
    op.add_column(
        "user_profiles",
        sa.Column("religious_affiliation", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "user_profiles", sa.Column("greek_life_interest", sa.Boolean(), nullable=True)
    )
    op.add_column(
        "user_profiles",
        sa.Column(
            "research_opportunities_important",
            sa.Boolean(),
            nullable=True,
            server_default="false",
        ),
    )
    op.add_column(
        "user_profiles",
        sa.Column(
            "study_abroad_interest", sa.Boolean(), nullable=True, server_default="false"
        ),
    )

    # Additional essay types
    op.add_column(
        "user_profiles",
        sa.Column(
            "has_community_service_essay",
            sa.Boolean(),
            nullable=True,
            server_default="false",
        ),
    )
    op.add_column(
        "user_profiles",
        sa.Column(
            "has_academic_interest_essay",
            sa.Boolean(),
            nullable=True,
            server_default="false",
        ),
    )

    # Enhanced scholarship preferences
    op.add_column(
        "user_profiles",
        sa.Column("min_scholarship_amount", sa.Integer(), nullable=True),
    )
    op.add_column(
        "user_profiles",
        sa.Column(
            "renewable_scholarships_only",
            sa.Boolean(),
            nullable=True,
            server_default="false",
        ),
    )
    op.add_column(
        "user_profiles",
        sa.Column(
            "local_scholarships_priority",
            sa.Boolean(),
            nullable=True,
            server_default="true",
        ),
    )

    # Additional information
    op.add_column(
        "user_profiles",
        sa.Column("certifications", postgresql.ARRAY(sa.String()), nullable=True),
    )

    # Parent/guardian information
    op.add_column(
        "user_profiles",
        sa.Column("parent_education_level", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "user_profiles",
        sa.Column("parent_occupation", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "user_profiles",
        sa.Column("parent_employer", sa.String(length=255), nullable=True),
    )

    # Profile tracking - FIXED: Add with correct enum values and default
    op.add_column(
        "user_profiles",
        sa.Column(
            "profile_tier",
            sa.Enum("basic", "enhanced", "complete", "optimized", name="profiletier"),
            nullable=False,
            server_default="basic",
        ),
    )
    op.add_column(
        "user_profiles",
        sa.Column("last_matching_update", sa.DateTime(timezone=True), nullable=True),
    )

    # ### FOURTH: Modify existing columns ###

    # Convert array columns to JSON
    op.execute(
        "ALTER TABLE user_profiles ALTER COLUMN extracurricular_activities TYPE JSON USING "
        "CASE WHEN extracurricular_activities IS NULL THEN NULL "
        "ELSE json_build_object('legacy_data', extracurricular_activities) END"
    )

    op.execute(
        "ALTER TABLE user_profiles ALTER COLUMN volunteer_experience TYPE JSON USING "
        "CASE WHEN volunteer_experience IS NULL THEN NULL "
        "ELSE json_build_object('legacy_data', volunteer_experience) END"
    )

    # Convert household_income_range to new enum (only if it's not already the enum type)
    op.execute(
        "ALTER TABLE user_profiles ALTER COLUMN household_income_range TYPE incomerange "
        "USING CASE "
        "WHEN household_income_range = 'under_30k' THEN 'under_30k'::incomerange "
        "WHEN household_income_range = '30k_50k' THEN '30k_50k'::incomerange "
        "WHEN household_income_range = '50k_75k' THEN '50k_75k'::incomerange "
        "WHEN household_income_range = '75k_100k' THEN '75k_100k'::incomerange "
        "WHEN household_income_range = '100k_150k' THEN '100k_150k'::incomerange "
        "WHEN household_income_range = 'over_150k' THEN 'over_150k'::incomerange "
        "ELSE 'prefer_not_to_say'::incomerange END"
    )

    # Convert preferred_college_size to new enum
    op.execute(
        "ALTER TABLE user_profiles ALTER COLUMN preferred_college_size TYPE collegesize "
        "USING CASE "
        "WHEN preferred_college_size = 'very_small' THEN 'very_small'::collegesize "
        "WHEN preferred_college_size = 'small' THEN 'small'::collegesize "
        "WHEN preferred_college_size = 'medium' THEN 'medium'::collegesize "
        "WHEN preferred_college_size = 'large' THEN 'large'::collegesize "
        "WHEN preferred_college_size = 'very_large' THEN 'very_large'::collegesize "
        "ELSE 'no_preference'::collegesize END"
    )

    # Convert additional_notes to TEXT
    op.alter_column(
        "user_profiles",
        "additional_notes",
        existing_type=sa.VARCHAR(length=500),
        type_=sa.Text(),
        existing_nullable=True,
    )

    # ### FIFTH: Create indexes ###
    op.create_index(
        op.f("ix_user_profiles_act_score"), "user_profiles", ["act_score"], unique=False
    )
    op.create_index(
        op.f("ix_user_profiles_city"), "user_profiles", ["city"], unique=False
    )
    op.create_index(
        op.f("ix_user_profiles_first_generation_college"),
        "user_profiles",
        ["first_generation_college"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_profiles_gpa"), "user_profiles", ["gpa"], unique=False
    )
    op.create_index(
        op.f("ix_user_profiles_graduation_year"),
        "user_profiles",
        ["graduation_year"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_profiles_high_school_name"),
        "user_profiles",
        ["high_school_name"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_profiles_household_income_range"),
        "user_profiles",
        ["household_income_range"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_profiles_intended_major"),
        "user_profiles",
        ["intended_major"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_profiles_sat_score"), "user_profiles", ["sat_score"], unique=False
    )
    op.create_index(
        op.f("ix_user_profiles_state"), "user_profiles", ["state"], unique=False
    )
    op.create_index(
        op.f("ix_user_profiles_zip_code"), "user_profiles", ["zip_code"], unique=False
    )

    # ### SIXTH: Clean up - remove preferred_college_location since we're using preferred_states instead ###
    op.drop_column("user_profiles", "preferred_college_location")


def downgrade() -> None:
    # ### Reverse all changes ###

    # Add back the dropped column
    op.add_column(
        "user_profiles",
        sa.Column(
            "preferred_college_location",
            sa.VARCHAR(length=100),
            autoincrement=False,
            nullable=True,
        ),
    )

    # Drop indexes
    op.drop_index(op.f("ix_user_profiles_zip_code"), table_name="user_profiles")
    op.drop_index(op.f("ix_user_profiles_state"), table_name="user_profiles")
    op.drop_index(op.f("ix_user_profiles_sat_score"), table_name="user_profiles")
    op.drop_index(op.f("ix_user_profiles_intended_major"), table_name="user_profiles")
    op.drop_index(
        op.f("ix_user_profiles_household_income_range"), table_name="user_profiles"
    )
    op.drop_index(op.f("ix_user_profiles_high_school_name"), table_name="user_profiles")
    op.drop_index(op.f("ix_user_profiles_graduation_year"), table_name="user_profiles")
    op.drop_index(op.f("ix_user_profiles_gpa"), table_name="user_profiles")
    op.drop_index(
        op.f("ix_user_profiles_first_generation_college"), table_name="user_profiles"
    )
    op.drop_index(op.f("ix_user_profiles_city"), table_name="user_profiles")
    op.drop_index(op.f("ix_user_profiles_act_score"), table_name="user_profiles")

    # Revert column type changes
    op.alter_column(
        "user_profiles",
        "additional_notes",
        existing_type=sa.Text(),
        type_=sa.VARCHAR(length=500),
        existing_nullable=True,
    )

    # Revert enum columns back to VARCHAR
    op.execute(
        "ALTER TABLE user_profiles ALTER COLUMN preferred_college_size TYPE VARCHAR(50) "
        "USING preferred_college_size::text"
    )

    op.execute(
        "ALTER TABLE user_profiles ALTER COLUMN household_income_range TYPE VARCHAR(50) "
        "USING household_income_range::text"
    )

    # Revert JSON columns back to ARRAY
    op.execute(
        "ALTER TABLE user_profiles ALTER COLUMN volunteer_experience TYPE text[] "
        "USING CASE WHEN volunteer_experience IS NULL THEN NULL "
        "ELSE ARRAY[volunteer_experience->>'legacy_data'] END"
    )

    op.execute(
        "ALTER TABLE user_profiles ALTER COLUMN extracurricular_activities TYPE text[] "
        "USING CASE WHEN extracurricular_activities IS NULL THEN NULL "
        "ELSE ARRAY[extracurricular_activities->>'legacy_data'] END"
    )

    # Drop all new columns
    op.drop_column("user_profiles", "last_matching_update")
    op.drop_column("user_profiles", "profile_tier")
    op.drop_column("user_profiles", "parent_employer")
    op.drop_column("user_profiles", "parent_occupation")
    op.drop_column("user_profiles", "parent_education_level")
    op.drop_column("user_profiles", "certifications")
    op.drop_column("user_profiles", "local_scholarships_priority")
    op.drop_column("user_profiles", "renewable_scholarships_only")
    op.drop_column("user_profiles", "min_scholarship_amount")
    op.drop_column("user_profiles", "has_academic_interest_essay")
    op.drop_column("user_profiles", "has_community_service_essay")
    op.drop_column("user_profiles", "study_abroad_interest")
    op.drop_column("user_profiles", "research_opportunities_important")
    op.drop_column("user_profiles", "greek_life_interest")
    op.drop_column("user_profiles", "religious_affiliation")
    op.drop_column("user_profiles", "campus_setting")
    op.drop_column("user_profiles", "work_study_interest")
    op.drop_column("user_profiles", "financial_aid_needed")
    op.drop_column("user_profiles", "max_tuition_budget")
    op.drop_column("user_profiles", "preferred_states")
    op.drop_column("user_profiles", "rural_background")
    op.drop_column("user_profiles", "lgbtq_identification")
    op.drop_column("user_profiles", "disability_status")
    op.drop_column("user_profiles", "military_connection")
    op.drop_column("user_profiles", "family_size")
    op.drop_column("user_profiles", "gender")
    op.drop_column("user_profiles", "musical_instruments")
    op.drop_column("user_profiles", "arts_activities")
    op.drop_column("user_profiles", "sports_activities")
    op.drop_column("user_profiles", "competitions")
    op.drop_column("user_profiles", "awards_honors")
    op.drop_column("user_profiles", "leadership_positions")
    op.drop_column("user_profiles", "class_size")
    op.drop_column("user_profiles", "class_rank")
    op.drop_column("user_profiles", "dual_enrollment")
    op.drop_column("user_profiles", "honors_courses")
    op.drop_column("user_profiles", "ap_courses")
    op.drop_column("user_profiles", "minor_interests")
    op.drop_column("user_profiles", "secondary_major")
    op.drop_column("user_profiles", "act_reading")
    op.drop_column("user_profiles", "act_science")
    op.drop_column("user_profiles", "act_english")
    op.drop_column("user_profiles", "act_math")
    op.drop_column("user_profiles", "sat_verbal")
    op.drop_column("user_profiles", "sat_math")
    op.drop_column("user_profiles", "gpa_scale")

    # Drop the new enums
    op.execute("DROP TYPE IF EXISTS profiletier")
    op.execute("DROP TYPE IF EXISTS collegesize")
    op.execute("DROP TYPE IF EXISTS incomerange")

    # Recreate the tuition indexes that were dropped
    op.create_index(
        "ix_tuition_data_quality_validation",
        "tuition_data",
        ["data_completeness_score", "validation_status"],
        unique=False,
    )
    op.create_index(
        "ix_tuition_data_ipeds_academic_year",
        "tuition_data",
        ["ipeds_id", "academic_year"],
        unique=False,
    )
    op.create_index(
        "ix_tuition_data_has_data_ipeds",
        "tuition_data",
        ["ipeds_id"],
        unique=False,
        postgresql_where="(has_tuition_data = true)",
    )
    op.create_index(
        "ix_tuition_data_has_data_flags",
        "tuition_data",
        ["has_tuition_data", "has_fees_data", "has_living_data"],
        unique=False,
    )
