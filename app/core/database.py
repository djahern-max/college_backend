# app/core/database.py - SYNC VERSION
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from app.core.config import settings

# Remove +asyncpg from the URL
DATABASE_URL = settings.DATABASE_URL.replace("+asyncpg", "")

# Create sync engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Create sync session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database sessions.
    Now returns sync Session instead of AsyncSession.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
