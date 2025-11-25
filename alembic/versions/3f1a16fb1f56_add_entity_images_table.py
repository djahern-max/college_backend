"""add_entity_images_table

Revision ID: 3f1a16fb1f56
Revises: 56b5460a7805
Create Date: 2025-11-25 03:54:05.619639

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f1a16fb1f56'
down_revision: Union[str, None] = '56b5460a7805'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create entity_images table
    op.create_table(
        'entity_images',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entity_type', sa.String(length=20), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('image_url', sa.String(length=500), nullable=False),
        sa.Column('cdn_url', sa.String(length=500), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('caption', sa.Text(), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_featured', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('image_type', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint(
            "entity_type IN ('institution', 'scholarship')",
            name='check_entity_type'
        )
    )
    
    # Create index
    op.create_index('ix_entity_images_id', 'entity_images', ['id'])


def downgrade() -> None:
    # Drop index
    op.drop_index('ix_entity_images_id', table_name='entity_images')
    
    # Drop table
    op.drop_table('entity_images')
