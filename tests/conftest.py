"""
Shared test fixtures and configuration for MagicScholar backend tests.
Configured for SYNC SQLAlchemy (not async).
"""

import os

# 🔐 Force tests to use a dedicated test database
# This overrides whatever is in .env (like unified_db)
os.environ["DATABASE_URL"] = (
    "postgresql://postgres:postgres@localhost:5432/unified_test"
)


import pytest
from typing import Generator, Dict
from starlette.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
from decimal import Decimal

from app.main import app
from app.core.database import get_db, Base
from app.core.security import create_access_token, get_password_hash
from app.models.user import User
from app.models.profile import UserProfile
from app.models.institution import Institution, ControlType
from app.models.scholarship import Scholarship


# ===========================
# TEST DATABASE CONFIGURATION
# ===========================

TEST_DATABASE_URL = os.environ["DATABASE_URL"]

# For Postgres we do NOT need StaticPool; a normal engine is fine
test_engine = create_engine(TEST_DATABASE_URL)

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


# ===========================
# SCHEMA SETUP (ONCE PER TEST RUN)
# ===========================


@pytest.fixture(scope="session", autouse=True)
def setup_test_database() -> Generator[None, None, None]:
    """
    Set up test database - handle both fresh and template-copied databases.

    Since unified_test was created from unified_db template, it already has:
    - All tables created
    - Alembic version history

    We just need to ensure the schema is current without re-running migrations.
    """
    print(f"\n🔧 Setting up test database: unified_test")

    # Option 1: Just use the existing database as-is
    # Since it was copied from unified_db, it should have all tables
    # We'll just verify the connection works
    try:
        with test_engine.connect() as conn:
            # Test connection
            result = conn.execute(text("SELECT 1"))
            print("✅ Test database connection verified")

            # Check if tables exist
            result = conn.execute(
                text(
                    """
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """
                )
            )
            table_count = result.scalar()
            print(f"✅ Found {table_count} tables in database")

    except Exception as e:
        print(f"❌ Database setup error: {e}")
        # If connection fails, try to create tables
        print("Creating tables from scratch...")
        Base.metadata.create_all(bind=test_engine)

    yield

    # Cleanup: Drop all data but keep schema
    # This allows the next test run to start fresh
    print("\n🧹 Cleaning up test database...")
    # We don't drop tables, just truncate them if needed


@pytest.fixture(scope="function", autouse=True)
def cleanup_data(db_session: Session) -> Generator[None, None, None]:
    """
    Clean up test data after each test.
    Since we're using transactions that rollback, this is mostly a safety net.
    """
    yield
    # The transaction rollback in db_session handles cleanup


# ===========================
# DATABASE SESSION FIXTURE
# ===========================


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Provide a transactional database session that rolls back after each test.

    - Starts a transaction at the connection level
    - Yields a Session bound to that connection
    - Rolls back the transaction at the end so the DB is clean for the next test
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestSessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        # Avoid SAWarning: only roll back if still active
        if transaction.is_active:
            transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Provide a TestClient with dependency override so the API uses our test session.
    """

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


# ===========================
# AUTH FIXTURES
# ===========================


@pytest.fixture
def test_user(db_session: Session) -> User:
    user = User(
        email="test@example.com",
        username="testuser",
        first_name="Test",
        last_name="User",
        hashed_password=get_password_hash("TestPassword123!"),
        is_active=True,
        is_superuser=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user_2(db_session: Session) -> User:
    user = User(
        email="test2@example.com",
        username="testuser2",
        first_name="Test",
        last_name="User2",
        hashed_password=get_password_hash("TestPassword123!"),
        is_active=True,
        is_superuser=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_user(db_session: Session) -> User:
    user = User(
        email="admin@example.com",
        username="adminuser",
        first_name="Admin",
        last_name="User",
        hashed_password=get_password_hash("AdminPassword123!"),
        is_active=True,
        is_superuser=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def user_token(test_user: User) -> str:
    return create_access_token(subject=str(test_user.id))


@pytest.fixture
def admin_token(admin_user: User) -> str:
    return create_access_token(subject=str(admin_user.id))


@pytest.fixture
def auth_headers(user_token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def admin_headers(admin_token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {admin_token}"}


# ===========================
# DATA FIXTURES
# ===========================


@pytest.fixture
def test_profile(db_session: Session, test_user: User) -> UserProfile:
    profile = UserProfile(
        user_id=test_user.id,
        high_school="Test High School",
        graduation_year=2025,
        gpa=3.8,
        sat_score=1400,
        act_score=32,
        intended_major="Computer Science",
        state="MA",
        city="Boston",
        zip_code="02101",
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    return profile


@pytest.fixture
def test_institution(db_session: Session) -> Institution:
    """
    Create a test institution with unique IPEDS ID.

    Uses 9999999 to avoid conflicts with real institutions in unified_test.
    Since unified_test was created from unified_db template, it contains
    real institutions like MIT (166027). Using a high test ID prevents
    duplicate key violations.
    """
    institution = Institution(
        ipeds_id=9999999,  # Won't conflict with real institutions (6-digit IDs)
        name="Test University",
        city="Test City",
        state="MA",
        control_type=ControlType.PRIVATE_NONPROFIT,
        student_faculty_ratio=Decimal("3.0"),
        size_category="Medium",
        locale="City: Large",
    )
    db_session.add(institution)
    db_session.commit()
    db_session.refresh(institution)
    return institution


@pytest.fixture
def test_scholarship(db_session: Session) -> Scholarship:
    scholarship = Scholarship(
        title="Test STEM Scholarship",
        organization="Test Foundation",
        scholarship_type="stem",  # must match your actual enum/text values
        amount_min=5000,
        amount_max=10000,
        deadline=datetime.now() + timedelta(days=60),
        description="Scholarship for STEM students",
        status="active",
        difficulty_level="moderate",
        is_renewable=False,
    )
    db_session.add(scholarship)
    db_session.commit()
    db_session.refresh(scholarship)
    return scholarship
