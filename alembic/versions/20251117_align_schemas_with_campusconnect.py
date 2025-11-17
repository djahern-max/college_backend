"""Add institution_id and is_admin_verified to align with CampusConnect

Revision ID: align_schemas_cc
Revises: 57895a2df522
Create Date: 2025-11-17 12:00:00.000000

This migration adds fields to match CampusConnect schema:
1. Add institution_id to admissions_data
2. Add is_admin_verified to admissions_data
3. Add institution_id to tuition_data
4. Add is_admin_verified to tuition_data
5. Populate institution_id from existing ipeds_id relationships
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'align_schemas_cc'
down_revision = '57895a2df522'  # Your most recent migration
branch_labels = None
depends_on = None


def upgrade():
    """Add institution_id and is_admin_verified fields"""
    
    # ==========================================
    # 1. ADD COLUMNS TO admissions_data
    # ==========================================
    print("Adding institution_id to admissions_data...")
    op.add_column('admissions_data', 
        sa.Column('institution_id', sa.Integer(), nullable=True)
    )
    
    print("Adding is_admin_verified to admissions_data...")
    op.add_column('admissions_data',
        sa.Column('is_admin_verified', sa.Boolean(), server_default='false', nullable=False)
    )
    
    # ==========================================
    # 2. ADD COLUMNS TO tuition_data
    # ==========================================
    print("Adding institution_id to tuition_data...")
    op.add_column('tuition_data',
        sa.Column('institution_id', sa.Integer(), nullable=True)
    )
    
    print("Adding is_admin_verified to tuition_data...")
    op.add_column('tuition_data',
        sa.Column('is_admin_verified', sa.Boolean(), server_default='false', nullable=False)
    )
    
    # ==========================================
    # 3. POPULATE institution_id FROM ipeds_id
    # ==========================================
    print("Populating institution_id in admissions_data...")
    op.execute("""
        UPDATE admissions_data ad
        SET institution_id = i.id
        FROM institutions i
        WHERE ad.ipeds_id = i.ipeds_id
    """)
    
    print("Populating institution_id in tuition_data...")
    op.execute("""
        UPDATE tuition_data td
        SET institution_id = i.id
        FROM institutions i
        WHERE td.ipeds_id = i.ipeds_id
    """)
    
    # ==========================================
    # 4. ADD NOT NULL CONSTRAINT (after populating)
    # ==========================================
    print("Making institution_id NOT NULL in admissions_data...")
    op.alter_column('admissions_data', 'institution_id',
        existing_type=sa.Integer(),
        nullable=False
    )
    
    print("Making institution_id NOT NULL in tuition_data...")
    op.alter_column('tuition_data', 'institution_id',
        existing_type=sa.Integer(),
        nullable=False
    )
    
    # ==========================================
    # 5. ADD FOREIGN KEY CONSTRAINTS
    # ==========================================
    print("Adding foreign key constraint to admissions_data...")
    op.create_foreign_key(
        'admissions_data_institution_id_fkey',
        'admissions_data', 'institutions',
        ['institution_id'], ['id'],
        ondelete='CASCADE'
    )
    
    print("Adding foreign key constraint to tuition_data...")
    op.create_foreign_key(
        'tuition_data_institution_id_fkey',
        'tuition_data', 'institutions',
        ['institution_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # ==========================================
    # 6. ADD INDEXES
    # ==========================================
    print("Adding index to admissions_data.institution_id...")
    op.create_index(
        'ix_admissions_data_institution_id',
        'admissions_data',
        ['institution_id']
    )
    
    print("Adding index to tuition_data.institution_id...")
    op.create_index(
        'ix_tuition_data_institution_id',
        'tuition_data',
        ['institution_id']
    )
    
    print("✅ Migration complete! Schemas now aligned with CampusConnect.")


def downgrade():
    """Remove institution_id and is_admin_verified fields"""
    
    print("Removing indexes...")
    op.drop_index('ix_tuition_data_institution_id', table_name='tuition_data')
    op.drop_index('ix_admissions_data_institution_id', table_name='admissions_data')
    
    print("Removing foreign keys...")
    op.drop_constraint('tuition_data_institution_id_fkey', 'tuition_data', type_='foreignkey')
    op.drop_constraint('admissions_data_institution_id_fkey', 'admissions_data', type_='foreignkey')
    
    print("Removing columns from tuition_data...")
    op.drop_column('tuition_data', 'is_admin_verified')
    op.drop_column('tuition_data', 'institution_id')
    
    print("Removing columns from admissions_data...")
    op.drop_column('admissions_data', 'is_admin_verified')
    op.drop_column('admissions_data', 'institution_id')
    
    print("✅ Downgrade complete!")
