"""alter enums

Revision ID: 8e1e010606de
Revises: 3d829ff1a67c
Create Date: 2025-09-24 10:12:07.114693

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "8e1e010606de"  # FIXED: Use the actual revision ID from the docstring
down_revision: Union[str, None] = (
    "3d829ff1a67c"  # FIXED: Use the actual parent revision
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # First, check what columns currently exist and their types
    # This prevents errors if columns already exist or don't exist

    # Step 1: Handle existing data in enum columns before dropping types
    # Convert any existing profile_tier data to temporary storage if needed
    op.execute(
        """
        DO $$ 
        DECLARE
            column_exists BOOLEAN;
        BEGIN 
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'user_profiles' 
                AND column_name = 'profile_tier'
            ) INTO column_exists;
            
            IF column_exists THEN
                -- Add a temporary column to store existing data
                ALTER TABLE user_profiles ADD COLUMN profile_tier_temp VARCHAR(20);
                UPDATE user_profiles SET profile_tier_temp = profile_tier::text;
                
                -- Drop the existing column
                ALTER TABLE user_profiles DROP COLUMN profile_tier;
            END IF;
        END $$;
    """
    )

    # Do the same for other enum columns
    op.execute(
        """
        DO $$ 
        DECLARE
            column_exists BOOLEAN;
        BEGIN 
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'user_profiles' 
                AND column_name = 'household_income_range'
            ) INTO column_exists;
            
            IF column_exists THEN
                ALTER TABLE user_profiles ADD COLUMN household_income_range_temp VARCHAR(20);
                UPDATE user_profiles SET household_income_range_temp = household_income_range::text;
                ALTER TABLE user_profiles DROP COLUMN household_income_range;
            END IF;
        END $$;
    """
    )

    op.execute(
        """
        DO $$ 
        DECLARE
            column_exists BOOLEAN;
        BEGIN 
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'user_profiles' 
                AND column_name = 'preferred_college_size'
            ) INTO column_exists;
            
            IF column_exists THEN
                ALTER TABLE user_profiles ADD COLUMN preferred_college_size_temp VARCHAR(20);
                UPDATE user_profiles SET preferred_college_size_temp = preferred_college_size::text;
                ALTER TABLE user_profiles DROP COLUMN preferred_college_size;
            END IF;
        END $$;
    """
    )

    # Step 2: Now safely drop and recreate the enum types
    op.execute("DROP TYPE IF EXISTS profiletier CASCADE")
    op.execute("DROP TYPE IF EXISTS incomerange CASCADE")
    op.execute("DROP TYPE IF EXISTS collegesize CASCADE")

    # Recreate with correct values (lowercase with underscores)
    op.execute(
        "CREATE TYPE profiletier AS ENUM ('basic', 'enhanced', 'complete', 'optimized')"
    )
    op.execute(
        "CREATE TYPE incomerange AS ENUM ('under_30k', '30k_50k', '50k_75k', '75k_100k', '100k_150k', 'over_150k', 'prefer_not_to_say')"
    )
    op.execute(
        "CREATE TYPE collegesize AS ENUM ('very_small', 'small', 'medium', 'large', 'very_large', 'no_preference')"
    )

    # Step 3: Add the columns back with proper enum types and defaults
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
        sa.Column("household_income_range", sa.Enum(name="incomerange"), nullable=True),
    )

    op.add_column(
        "user_profiles",
        sa.Column("preferred_college_size", sa.Enum(name="collegesize"), nullable=True),
    )

    # Step 4: Restore data from temporary columns, converting values as needed
    op.execute(
        """
        DO $$ 
        DECLARE
            temp_column_exists BOOLEAN;
        BEGIN 
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'user_profiles' 
                AND column_name = 'profile_tier_temp'
            ) INTO temp_column_exists;
            
            IF temp_column_exists THEN
                -- Convert old values to new enum values
                UPDATE user_profiles 
                SET profile_tier = CASE 
                    WHEN profile_tier_temp = 'BASIC' THEN 'basic'::profiletier
                    WHEN profile_tier_temp = 'ENHANCED' THEN 'enhanced'::profiletier  
                    WHEN profile_tier_temp = 'COMPLETE' THEN 'complete'::profiletier
                    WHEN profile_tier_temp = 'OPTIMIZED' THEN 'optimized'::profiletier
                    WHEN profile_tier_temp = 'basic' THEN 'basic'::profiletier
                    WHEN profile_tier_temp = 'enhanced' THEN 'enhanced'::profiletier
                    WHEN profile_tier_temp = 'complete' THEN 'complete'::profiletier  
                    WHEN profile_tier_temp = 'optimized' THEN 'optimized'::profiletier
                    ELSE 'basic'::profiletier
                END
                WHERE profile_tier_temp IS NOT NULL;
                
                -- Drop temporary column
                ALTER TABLE user_profiles DROP COLUMN profile_tier_temp;
            END IF;
        END $$;
    """
    )

    # Similar restoration for other enum columns
    op.execute(
        """
        DO $$ 
        DECLARE
            temp_column_exists BOOLEAN;
        BEGIN 
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'user_profiles' 
                AND column_name = 'household_income_range_temp'
            ) INTO temp_column_exists;
            
            IF temp_column_exists THEN
                UPDATE user_profiles 
                SET household_income_range = household_income_range_temp::incomerange
                WHERE household_income_range_temp IS NOT NULL;
                
                ALTER TABLE user_profiles DROP COLUMN household_income_range_temp;
            END IF;
        END $$;
    """
    )

    op.execute(
        """
        DO $$ 
        DECLARE
            temp_column_exists BOOLEAN;
        BEGIN 
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'user_profiles' 
                AND column_name = 'preferred_college_size_temp'
            ) INTO temp_column_exists;
            
            IF temp_column_exists THEN
                UPDATE user_profiles 
                SET preferred_college_size = preferred_college_size_temp::collegesize
                WHERE preferred_college_size_temp IS NOT NULL;
                
                ALTER TABLE user_profiles DROP COLUMN preferred_college_size_temp;
            END IF;
        END $$;
    """
    )


def downgrade() -> None:
    # Remove the enum columns
    op.drop_column("user_profiles", "profile_tier")
    op.drop_column("user_profiles", "household_income_range")
    op.drop_column("user_profiles", "preferred_college_size")

    # Drop the enum types
    op.execute("DROP TYPE IF EXISTS profiletier")
    op.execute("DROP TYPE IF EXISTS incomerange")
    op.execute("DROP TYPE IF EXISTS collegesize")
