"""
Shared test fixtures and configuration for MagicScholar backend tests.
SYNC version - matches sync SQLAlchemy backend.
"""

import os

# 🔐 Force tests to use a dedicated test database
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
from app.models.entity_image import EntityImage


# ===========================
# TEST DATABASE CONFIGURATION
# ===========================

TEST_DATABASE_URL = os.environ["DATABASE_URL"]
test_engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


# ===========================
# SCHEMA SETUP
# ===========================


@pytest.fixture(scope="session", autouse=True)
def setup_test_database() -> Generator[None, None, None]:
    """Set up test database schema."""
    print(f"\n🔧 Setting up test database: unified_test")

    try:
        with test_engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Test database connection verified")

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
        print("Creating tables from scratch...")
        Base.metadata.create_all(bind=test_engine)

    yield

    print("\n🧹 Cleaning up test database...")


# ===========================
# DATABASE SESSION FIXTURE
# ===========================


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Provide a transactional database session that rolls back after each test.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestSessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        if transaction.is_active:
            transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def db(db_session: Session) -> Session:
    """Alias for db_session to support tests expecting 'db' fixture."""
    return db_session


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
    institution = Institution(
        ipeds_id=9999999,
        name="Massachusetts Institute of Testing",
        city="Cambridge",
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
        scholarship_type="stem",
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


@pytest.fixture
def institution_gallery_images(
    db_session: Session, test_institution: Institution
) -> list[EntityImage]:
    images = [
        EntityImage(
            entity_type="institution",
            entity_id=test_institution.id,
            image_url="https://example.com/images/campus1.jpg",
            cdn_url="https://cdn.example.com/images/campus1.jpg",
            filename="campus1.jpg",
            display_order=1,
            is_featured=True,
        ),
        EntityImage(
            entity_type="institution",
            entity_id=test_institution.id,
            image_url="https://example.com/images/campus2.jpg",
            cdn_url="https://cdn.example.com/images/campus2.jpg",
            filename="campus2.jpg",
            display_order=2,
            is_featured=False,
        ),
        EntityImage(
            entity_type="institution",
            entity_id=test_institution.id,
            image_url="https://example.com/images/campus3.jpg",
            cdn_url="https://cdn.example.com/images/campus3.jpg",
            filename="campus3.jpg",
            display_order=3,
            is_featured=False,
        ),
    ]
    for image in images:
        db_session.add(image)
    db_session.commit()
    for image in images:
        db_session.refresh(image)
    return images


@pytest.fixture
def scholarship_gallery_images(
    db_session: Session, test_scholarship: Scholarship
) -> list[EntityImage]:
    images = [
        EntityImage(
            entity_type="scholarship",
            entity_id=test_scholarship.id,
            image_url="https://example.com/images/scholarship1.jpg",
            cdn_url="https://cdn.example.com/images/scholarship1.jpg",
            filename="scholarship1.jpg",
            display_order=1,
            is_featured=True,
        ),
        EntityImage(
            entity_type="scholarship",
            entity_id=test_scholarship.id,
            image_url="https://example.com/images/scholarship2.jpg",
            cdn_url="https://cdn.example.com/images/scholarship2.jpg",
            filename="scholarship2.jpg",
            display_order=2,
            is_featured=False,
        ),
    ]
    for image in images:
        db_session.add(image)
    db_session.commit()
    for image in images:
        db_session.refresh(image)
    return images
