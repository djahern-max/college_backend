from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=5,
    max_overflow=0,
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db():
    """
    Database dependency for FastAPI endpoints.
    Provides a database session that is automatically closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables"""
    # Import models to register them with SQLAlchemy
    from app.models.user import User  # noqa

    # Add other model imports as needed:
    # from app.models.profile import UserProfile  # noqa
    # from app.models.oauth import OAuthAccount  # noqa

    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all database tables (for testing)"""
    Base.metadata.drop_all(bind=engine)
