"""Add image columns to institutions table

Revision ID: 86fd2b11055e
Revises: ae6abdd449d0
Create Date: 2025-09-07 11:36:51.598693

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "86fd2b11055e"
down_revision: Union[str, None] = "ae6abdd449d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create the enum type first
    image_extraction_status_enum = sa.Enum(
        "PENDING",
        "PROCESSING",
        "SUCCESS",
        "FAILED",
        "NEEDS_REVIEW",
        "FALLBACK_APPLIED",
        name="imageextractionstatus",
    )
    image_extraction_status_enum.create(op.get_bind(), checkfirst=True)

    # Then add the columns
    op.add_column(
        "institutions",
        sa.Column(
            "primary_image_url",
            sa.String(length=500),
            nullable=True,
            comment="CDN URL to standardized 400x300px image for school cards",
        ),
    )
    op.add_column(
        "institutions",
        sa.Column(
            "primary_image_quality_score",
            sa.Integer(),
            nullable=True,
            comment="Quality score 0-100 for ranking schools by image quality",
        ),
    )
    op.add_column(
        "institutions",
        sa.Column(
            "logo_image_url",
            sa.String(length=500),
            nullable=True,
            comment="CDN URL to school logo for headers/search results",
        ),
    )
    op.add_column(
        "institutions",
        sa.Column(
            "image_extraction_status",
            image_extraction_status_enum,
            nullable=True,
            comment="Status of image extraction process",
        ),
    )
    op.add_column(
        "institutions",
        sa.Column(
            "image_extraction_date",
            sa.DateTime(),
            nullable=True,
            comment="When images were last extracted/updated",
        ),
    )

    # Create indexes
    op.create_index(
        op.f("ix_institutions_image_extraction_status"),
        "institutions",
        ["image_extraction_status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_institutions_primary_image_quality_score"),
        "institutions",
        ["primary_image_quality_score"],
        unique=False,
    )

    # Set default values
    op.execute(
        "UPDATE institutions SET primary_image_quality_score = 0 WHERE primary_image_quality_score IS NULL"
    )
    op.execute(
        "UPDATE institutions SET image_extraction_status = 'PENDING' WHERE image_extraction_status IS NULL"
    )


def downgrade():
    # Drop indexes
    op.drop_index(
        op.f("ix_institutions_primary_image_quality_score"), table_name="institutions"
    )
    op.drop_index(
        op.f("ix_institutions_image_extraction_status"), table_name="institutions"
    )

    # Drop columns
    op.drop_column("institutions", "image_extraction_date")
    op.drop_column("institutions", "image_extraction_status")
    op.drop_column("institutions", "logo_image_url")
    op.drop_column("institutions", "primary_image_quality_score")
    op.drop_column("institutions", "primary_image_url")

    # Drop the enum type
    sa.Enum(name="imageextractionstatus").drop(op.get_bind(), checkfirst=True)
