"""add_tuition_data_filter_index

Revision ID: 92e14d33943b
Revises: fix_validation_enum_values
Create Date: 2025-09-18 15:20:43.114217

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "92e14d33943b"
down_revision: Union[str, None] = "fix_validation_enum_values"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create index without CONCURRENTLY (works in transactions)
    op.create_index(
        "ix_tuition_data_has_data_ipeds",
        "tuition_data",
        ["ipeds_id"],
        postgresql_where=sa.text("has_tuition_data = true"),
    )


def downgrade():
    op.drop_index("ix_tuition_data_has_data_ipeds", table_name="tuition_data")
