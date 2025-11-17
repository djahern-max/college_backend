"""Convert tuition_data Float columns to Numeric to match CampusConnect

Revision ID: convert_float_to_numeric
Revises: align_schemas_cc
Create Date: 2025-11-17 14:00:00.000000

This migration converts Float (double precision) columns to Numeric(10,2)
in tuition_data to perfectly match CampusConnect schema.

NOTE: This is OPTIONAL - Float and Numeric are compatible for syncing.
Only run this if you want perfect type alignment.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "convert_float_to_numeric"
down_revision = "align_schemas_cc"
branch_labels = None
depends_on = None


def upgrade():
    """Convert Float columns to Numeric(10,2)"""

    print("Converting tuition_data columns from Float to Numeric(10,2)...")

    # Convert each monetary column from double precision to numeric(10,2)
    op.alter_column(
        "tuition_data",
        "tuition_in_state",
        existing_type=sa.Float(),
        type_=sa.Numeric(10, 2),
        existing_nullable=True,
    )

    op.alter_column(
        "tuition_data",
        "tuition_out_state",
        existing_type=sa.Float(),
        type_=sa.Numeric(10, 2),
        existing_nullable=True,
    )

    op.alter_column(
        "tuition_data",
        "required_fees_in_state",
        existing_type=sa.Float(),
        type_=sa.Numeric(10, 2),
        existing_nullable=True,
    )

    op.alter_column(
        "tuition_data",
        "required_fees_out_state",
        existing_type=sa.Float(),
        type_=sa.Numeric(10, 2),
        existing_nullable=True,
    )

    op.alter_column(
        "tuition_data",
        "room_board_on_campus",
        existing_type=sa.Float(),
        type_=sa.Numeric(10, 2),
        existing_nullable=True,
    )

    print("✅ Conversion complete! All monetary columns now use Numeric(10,2)")


def downgrade():
    """Convert Numeric(10,2) columns back to Float"""

    print("Converting tuition_data columns from Numeric(10,2) back to Float...")

    op.alter_column(
        "tuition_data",
        "room_board_on_campus",
        existing_type=sa.Numeric(10, 2),
        type_=sa.Float(),
        existing_nullable=True,
    )

    op.alter_column(
        "tuition_data",
        "required_fees_out_state",
        existing_type=sa.Numeric(10, 2),
        type_=sa.Float(),
        existing_nullable=True,
    )

    op.alter_column(
        "tuition_data",
        "required_fees_in_state",
        existing_type=sa.Numeric(10, 2),
        type_=sa.Float(),
        existing_nullable=True,
    )

    op.alter_column(
        "tuition_data",
        "tuition_out_state",
        existing_type=sa.Numeric(10, 2),
        type_=sa.Float(),
        existing_nullable=True,
    )

    op.alter_column(
        "tuition_data",
        "tuition_in_state",
        existing_type=sa.Numeric(10, 2),
        type_=sa.Float(),
        existing_nullable=True,
    )

    print("✅ Rollback complete!")
