"""merge_entity_images_and_verification_fields

Revision ID: a49cb5395f79
Revises: 3f1a16fb1f56, 5578c2cab6f6
Create Date: 2025-11-27 14:26:31.177516

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a49cb5395f79'
down_revision: Union[str, None] = ('3f1a16fb1f56', '5578c2cab6f6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
