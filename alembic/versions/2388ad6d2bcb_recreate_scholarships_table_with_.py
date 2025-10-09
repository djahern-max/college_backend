"""recreate scholarships table with essential fields

Revision ID: 2388ad6d2bcb
Revises: 5004fa491e95
Create Date: 2025-10-09 15:35:33.280407

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "2388ad6d2bcb"
down_revision: Union[str, None] = "5004fa491e95"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Drop existing enum types if they exist
    # This must happen BEFORE creating the table
    op.execute("DROP TYPE IF EXISTS scholarshiptype CASCADE")
    op.execute("DROP TYPE IF EXISTS scholarshipstatus CASCADE")
    op.execute("DROP TYPE IF EXISTS difficultylevel CASCADE")

    # Create the new scholarships table
    # SQLAlchemy will automatically create the enum types
    op.create_table(
        "scholarships",
        # Primary key
        sa.Column("id", sa.Integer(), nullable=False),
        # Core identification
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("organization", sa.String(length=255), nullable=False),
        # Classification - SQLAlchemy will create these enum types automatically
        sa.Column(
            "scholarship_type",
            sa.Enum(
                "ACADEMIC_MERIT",
                "NEED_BASED",
                "STEM",
                "ARTS",
                "DIVERSITY",
                "ATHLETIC",
                "LEADERSHIP",
                "MILITARY",
                "CAREER_SPECIFIC",
                "OTHER",
                name="scholarshiptype",
                create_type=True,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "ACTIVE",
                "INACTIVE",
                "EXPIRED",
                "DRAFT",
                "PENDING_REVIEW",
                name="scholarshipstatus",
                create_type=True,
            ),
            nullable=False,
            server_default="ACTIVE",
        ),
        sa.Column(
            "difficulty_level",
            sa.Enum(
                "EASY",
                "MODERATE",
                "HARD",
                "VERY_HARD",
                name="difficultylevel",
                create_type=True,
            ),
            nullable=False,
            server_default="MODERATE",
        ),
        # Financial info
        sa.Column("amount_min", sa.Integer(), nullable=False),
        sa.Column("amount_max", sa.Integer(), nullable=False),
        sa.Column(
            "is_renewable",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("number_of_awards", sa.Integer(), nullable=True),
        # Dates
        sa.Column("deadline", sa.Date(), nullable=True),
        sa.Column("application_opens", sa.Date(), nullable=True),
        sa.Column("for_academic_year", sa.String(length=20), nullable=True),
        # Details
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("website_url", sa.String(length=500), nullable=True),
        # Requirements
        sa.Column("min_gpa", sa.Numeric(precision=3, scale=2), nullable=True),
        # Images
        sa.Column("primary_image_url", sa.String(length=500), nullable=True),
        # Metadata
        sa.Column(
            "verified", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.Column(
            "featured", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.Column(
            "views_count", sa.Integer(), nullable=False, server_default=sa.text("0")
        ),
        sa.Column(
            "applications_count",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        # Timestamps
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")
        ),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for better query performance
    op.create_index("ix_scholarships_id", "scholarships", ["id"], unique=False)
    op.create_index("ix_scholarships_title", "scholarships", ["title"], unique=False)
    op.create_index(
        "ix_scholarships_organization", "scholarships", ["organization"], unique=False
    )
    op.create_index(
        "ix_scholarships_scholarship_type",
        "scholarships",
        ["scholarship_type"],
        unique=False,
    )
    op.create_index(
        "ix_scholarships_deadline", "scholarships", ["deadline"], unique=False
    )


def downgrade():
    # Drop the table and indexes
    op.drop_index("ix_scholarships_deadline", table_name="scholarships")
    op.drop_index("ix_scholarships_scholarship_type", table_name="scholarships")
    op.drop_index("ix_scholarships_organization", table_name="scholarships")
    op.drop_index("ix_scholarships_title", table_name="scholarships")
    op.drop_index("ix_scholarships_id", table_name="scholarships")
    op.drop_table("scholarships")

    # Drop the enum types
    op.execute("DROP TYPE IF EXISTS scholarshiptype CASCADE")
    op.execute("DROP TYPE IF EXISTS scholarshipstatus CASCADE")
    op.execute("DROP TYPE IF EXISTS difficultylevel CASCADE")
