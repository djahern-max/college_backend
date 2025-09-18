"""Fix validation status enum values to uppercase

Revision ID: fix_validation_enum_values
Revises: 8ff4633ad0e0
Create Date: 2025-09-18 14:30:00.000000

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "fix_validation_enum_values"
down_revision: Union[str, None] = "8ff4633ad0e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


"""Fix validation status enum values to uppercase

Revision ID: fix_validation_enum_values
Revises: 8ff4633ad0e0
Create Date: 2025-09-18 14:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "fix_validation_enum_values"
down_revision: Union[str, None] = "8ff4633ad0e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Fix validation status values to match enum definition"""

    # Cast enum to text for comparison to handle PostgreSQL strict enum checking
    op.execute(
        """
        UPDATE tuition_data 
        SET validation_status = 'PENDING' 
        WHERE validation_status::text = 'pending'
    """
    )

    op.execute(
        """
        UPDATE tuition_data 
        SET validation_status = 'VALIDATED' 
        WHERE validation_status::text = 'validated'
    """
    )

    op.execute(
        """
        UPDATE tuition_data 
        SET validation_status = 'NEEDS_REVIEW' 
        WHERE validation_status::text = 'needs_review'
    """
    )

    op.execute(
        """
        UPDATE tuition_data 
        SET validation_status = 'FAILED' 
        WHERE validation_status::text = 'failed'
    """
    )


def downgrade() -> None:
    """Revert validation status values to lowercase"""

    op.execute(
        """
        UPDATE tuition_data 
        SET validation_status = 'pending' 
        WHERE validation_status::text = 'PENDING'
    """
    )

    op.execute(
        """
        UPDATE tuition_data 
        SET validation_status = 'validated' 
        WHERE validation_status::text = 'VALIDATED'
    """
    )

    op.execute(
        """
        UPDATE tuition_data 
        SET validation_status = 'needs_review' 
        WHERE validation_status::text = 'NEEDS_REVIEW'
    """
    )

    op.execute(
        """
        UPDATE tuition_data 
        SET validation_status = 'failed' 
        WHERE validation_status::text = 'FAILED'
    """
    )
