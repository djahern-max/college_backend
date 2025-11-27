"""add verification fields to institutions

Revision ID: 5578c2cab6f6
Revises: 56b5460a7805
Create Date: 2025-11-27

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5578c2cab6f6'
down_revision = '56b5460a7805'
branch_labels = None
depends_on = None


def upgrade():
    """Add verification tracking fields to institutions table"""
    
    # Add verification status fields
    op.add_column('institutions', 
        sa.Column('admin_verified', sa.Boolean(), 
                  nullable=False, server_default='false',
                  comment='Whether institution is managed by admin'))
    
    op.add_column('institutions', 
        sa.Column('completeness_score', sa.Integer(), 
                  nullable=False, server_default='0',
                  comment='Data completeness percentage (0-100)'))
    
    # Cost data verification
    op.add_column('institutions', 
        sa.Column('cost_data_verified', sa.Boolean(), 
                  nullable=False, server_default='false',
                  comment='Cost data verified by admin'))
    
    op.add_column('institutions', 
        sa.Column('cost_data_verified_at', sa.DateTime(timezone=True), 
                  nullable=True,
                  comment='When cost data was last verified'))
    
    # Admissions data verification
    op.add_column('institutions', 
        sa.Column('admissions_data_verified', sa.Boolean(), 
                  nullable=False, server_default='false',
                  comment='Admissions data verified by admin'))
    
    op.add_column('institutions', 
        sa.Column('admissions_data_verified_at', sa.DateTime(timezone=True), 
                  nullable=True,
                  comment='When admissions data was last verified'))
    
    # General tracking
    op.add_column('institutions', 
        sa.Column('last_admin_update', sa.DateTime(timezone=True), 
                  nullable=True,
                  comment='Last time admin updated any data'))
    
    op.add_column('institutions', 
        sa.Column('data_quality_notes', sa.String(500), 
                  nullable=True,
                  comment='Admin notes about data quality'))
    
    # Create indexes for performance
    op.create_index('ix_institutions_admin_verified', 
                    'institutions', ['admin_verified'])
    op.create_index('ix_institutions_completeness_score', 
                    'institutions', ['completeness_score'])


def downgrade():
    """Remove verification fields"""
    op.drop_index('ix_institutions_completeness_score', table_name='institutions')
    op.drop_index('ix_institutions_admin_verified', table_name='institutions')
    
    op.drop_column('institutions', 'data_quality_notes')
    op.drop_column('institutions', 'last_admin_update')
    op.drop_column('institutions', 'admissions_data_verified_at')
    op.drop_column('institutions', 'admissions_data_verified')
    op.drop_column('institutions', 'cost_data_verified_at')
    op.drop_column('institutions', 'cost_data_verified')
    op.drop_column('institutions', 'completeness_score')
    op.drop_column('institutions', 'admin_verified')
