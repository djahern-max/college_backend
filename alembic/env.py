# alembic/env.py for MagicScholar
# This tells Alembic to IGNORE CampusConnect tables (not drop them)
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import Base
from app.core.database import Base

# Import ALL MagicScholar models (including shared models)
from app.models.user import User
from app.models.profile import UserProfile
from app.models.institution import Institution
from app.models.scholarship import Scholarship

from app.models.oauth import OAuthAccount, OAuthState


from app.models.scholarship_applications import ScholarshipApplication
from app.models.college_applications import CollegeApplication
from app.models.entity_image import EntityImage

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def include_object(object, name, type_, reflected, compare_to):
    """
    Control which database objects Alembic should manage.

    - Exclude alembic_version table
    - IGNORE (don't drop) CampusConnect-specific tables that exist in unified_db
    """
    # Always exclude alembic_version
    if type_ == "table" and name == "alembic_version":
        return False

    # CampusConnect tables that MagicScholar should IGNORE
    # These exist in unified_db but are managed by CampusConnect
    campusconnect_tables = {
        "admin_users",
        "invitation_codes",
        "subscriptions",
        "display_settings",
        "contact_inquiries",
        "outreach_activities",
        "outreach_tracking",
        "message_templates",
    }

    if type_ == "table" and name in campusconnect_tables:
        # If compare_to is None, it means the table exists in DB but not in our models
        # We want to IGNORE it (return False) so Alembic doesn't try to drop it
        return False

    # For indexes and constraints on CampusConnect tables
    if type_ in ("index", "unique_constraint", "foreign_key"):
        # Get the table name from the object
        table_name = None
        if hasattr(object, "table"):
            table_name = object.table.name
        elif hasattr(object, "parent"):
            table_name = object.parent.name

        if table_name in campusconnect_tables:
            return False

    return True


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
        compare_type=True,
        version_table="alembic_version_magicscholar",  # ADD THIS LINE
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # Try environment variable first (production), fall back to alembic.ini (local)
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        # Production: use DATABASE_URL environment variable
        from sqlalchemy import create_engine

        connectable = create_engine(database_url, poolclass=pool.NullPool)
    else:
        # Local development: use alembic.ini
        connectable = engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
            compare_type=True,
            version_table="alembic_version_magicscholar",  # ADD THIS LINE
        )

        with context.begin_transaction():
            context.run_migrations()
