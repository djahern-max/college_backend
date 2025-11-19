# tests/conftest.py
"""
Shared test fixtures and configuration for MagicScholar backend tests.

This file provides reusable fixtures for:
- HTTP clients
- Database sessions with transaction rollback
- Authentication (users, tokens, headers) - NO OAUTH, direct auth only
- Test data (institutions, scholarships, profiles)
- File handling (resumes, images)
"""

import pytest
import pytest_asyncio
from typing import AsyncGenerator, Dict, Any
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text
from datetime import datetime, timedelta
import os
from io import BytesIO
from decimal import Decimal

from app.main import app
from app.core.database import get_db, Base
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
from app.models.user import User
from app.models.profile import UserProfile
from app.models.institution import Institution
from app.models.scholarship import Scholarship
from app.models.college_applications import CollegeApplication
from app.models.scholarship_applications import ScholarshipApplication
from app.models.admissions import AdmissionsData
from app.models.tuition import TuitionData


# ===========================
# TEST DATABASE CONFIGURATION
# ===========================

# Use test database URL from environment
TEST_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:@localhost:5432/magicscholar_test"
)

# Convert to async URL if needed
if not TEST_DATABASE_URL.startswith("postgresql+asyncpg://"):
    TEST_DATABASE_URL = TEST_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create async engine for testing
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=NullPool,  # Disable connection pooling for tests
)

# Create session maker
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# ===========================
# DATABASE FIXTURES
# ===========================

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database():
    """
    Create all tables before running tests and drop them after.
    Runs once per test session.
    """
    async with test_engine.begin() as conn:
        # Drop all tables first (clean slate)
        await conn.run_sync(Base.metadata.drop_all)
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Cleanup after all tests
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a database session for each test with automatic rollback.
    Each test gets a clean database state.
    """
    async with TestSessionLocal() as session:
        async with session.begin():
            try:
                yield session
            finally:
                await session.rollback()
                await session.close()


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Provide an async HTTP client for testing API endpoints.
    Overrides the database dependency to use the test session.
    """
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()


# ===========================
# AUTHENTICATION FIXTURES
# ===========================

@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """
    Create a test user with email/password authentication.
    No OAuth - direct registration for testing.
    """
    user = User(
        email="test@example.com",
        username="testuser",
        first_name="Test",
        last_name="User",
        hashed_password=get_password_hash("TestPassword123!"),
        is_active=True,
        is_superuser=False
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_user_2(db_session: AsyncSession) -> User:
    """Create a second test user for multi-user tests"""
    user = User(
        email="test2@example.com",
        username="testuser2",
        first_name="Test",
        last_name="User2",
        hashed_password=get_password_hash("TestPassword123!"),
        is_active=True,
        is_superuser=False
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Create an admin/superuser for admin-only tests"""
    user = User(
        email="admin@example.com",
        username="adminuser",
        first_name="Admin",
        last_name="User",
        hashed_password=get_password_hash("AdminPassword123!"),
        is_active=True,
        is_superuser=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def user_token(test_user: User) -> str:
    """Generate JWT token for test user"""
    return create_access_token(data={"sub": str(test_user.id)})


@pytest.fixture
def admin_token(admin_user: User) -> str:
    """Generate JWT token for admin user"""
    return create_access_token(data={"sub": str(admin_user.id)})


@pytest.fixture
def auth_headers(user_token: str) -> Dict[str, str]:
    """Auth headers with Bearer token for regular user"""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def admin_headers(admin_token: str) -> Dict[str, str]:
    """Auth headers with Bearer token for admin user"""
    return {"Authorization": f"Bearer {admin_token}"}


# ===========================
# PROFILE FIXTURES
# ===========================

@pytest_asyncio.fixture
async def test_profile(db_session: AsyncSession, test_user: User) -> UserProfile:
    """Create a test user profile with sample data"""
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
        biography="Test student interested in STEM",
        extracurriculars="Robotics Club, Math Team",
        awards="National Merit Semifinalist",
        interests="AI, Machine Learning, Sustainability"
    )
    db_session.add(profile)
    await db_session.commit()
    await db_session.refresh(profile)
    return profile


@pytest_asyncio.fixture
async def complete_profile(db_session: AsyncSession, test_user: User) -> UserProfile:
    """Create a fully completed profile for matching tests"""
    profile = UserProfile(
        user_id=test_user.id,
        high_school="Boston Latin School",
        graduation_year=2025,
        gpa=3.9,
        sat_score=1500,
        act_score=34,
        intended_major="Engineering",
        state="MA",
        city="Boston",
        zip_code="02101",
        biography="Passionate about engineering and innovation",
        extracurriculars="Robotics Captain, Science Olympiad, Volunteering",
        awards="Intel Science Fair Finalist, National Merit Scholar",
        interests="Renewable Energy, AI, Environmental Engineering",
        career_goals="Environmental Engineer",
        preferred_college_size="Medium",
        preferred_location="Northeast",
        financial_aid_needed=True,
        max_tuition_budget=50000
    )
    db_session.add(profile)
    await db_session.commit()
    await db_session.refresh(profile)
    return profile


# ===========================
# INSTITUTION FIXTURES
# ===========================

@pytest_asyncio.fixture
async def test_institution(db_session: AsyncSession) -> Institution:
    """Create a test institution (MIT)"""
    institution = Institution(
        ipeds_id=166027,  # MIT's real IPEDS ID
        name="Massachusetts Institute of Technology",
        city="Cambridge",
        state="MA",
        zip_code="02139",
        control_type="Private",
        latitude=Decimal("42.3601"),
        longitude=Decimal("-71.0942"),
        student_faculty_ratio=Decimal("3.0"),
        size_category="Medium",
        locale="City: Large"
    )
    db_session.add(institution)
    await db_session.commit()
    await db_session.refresh(institution)
    return institution


@pytest_asyncio.fixture
async def test_institution_2(db_session: AsyncSession) -> Institution:
    """Create a second test institution (Harvard)"""
    institution = Institution(
        ipeds_id=166027,  # Harvard's IPEDS ID
        name="Harvard University",
        city="Cambridge",
        state="MA",
        zip_code="02138",
        control_type="Private",
        latitude=Decimal("42.3770"),
        longitude=Decimal("-71.1167"),
        student_faculty_ratio=Decimal("5.0"),
        size_category="Large",
        locale="City: Large"
    )
    db_session.add(institution)
    await db_session.commit()
    await db_session.refresh(institution)
    return institution


@pytest_asyncio.fixture
async def public_institution(db_session: AsyncSession) -> Institution:
    """Create a public institution for filtering tests"""
    institution = Institution(
        ipeds_id=190415,  # Example IPEDS ID
        name="University of Massachusetts Amherst",
        city="Amherst",
        state="MA",
        zip_code="01003",
        control_type="Public",
        latitude=Decimal("42.3868"),
        longitude=Decimal("-72.5301"),
        student_faculty_ratio=Decimal("18.0"),
        size_category="Large",
        locale="Town: Fringe"
    )
    db_session.add(institution)
    await db_session.commit()
    await db_session.refresh(institution)
    return institution


# ===========================
# ADMISSIONS DATA FIXTURES
# ===========================

@pytest_asyncio.fixture
async def test_admissions_data(
    db_session: AsyncSession,
    test_institution: Institution
) -> AdmissionsData:
    """Create test admissions data for an institution"""
    admissions = AdmissionsData(
        ipeds_id=test_institution.ipeds_id,
        academic_year="2023-24",
        applications_total=20000,
        admissions_total=800,
        enrolled_total=400,
        acceptance_rate="4.0",
        yield_rate="50.0",
        sat_reading_25th=730,
        sat_reading_50th=770,
        sat_reading_75th=800,
        sat_math_25th=760,
        sat_math_50th=790,
        sat_math_75th=800,
        percent_submitting_sat="75.0"
    )
    db_session.add(admissions)
    await db_session.commit()
    await db_session.refresh(admissions)
    return admissions


# ===========================
# TUITION DATA FIXTURES
# ===========================

@pytest_asyncio.fixture
async def test_tuition_data(
    db_session: AsyncSession,
    test_institution: Institution
) -> TuitionData:
    """Create test tuition data for an institution"""
    tuition = TuitionData(
        ipeds_id=test_institution.ipeds_id,
        academic_year="2023-24",
        tuition_in_state=55878,
        tuition_out_state=55878,
        fees=368,
        room_and_board=19110,
        books_and_supplies=1000,
        total_in_state=76356,
        total_out_state=76356
    )
    db_session.add(tuition)
    await db_session.commit()
    await db_session.refresh(tuition)
    return tuition


# ===========================
# SCHOLARSHIP FIXTURES
# ===========================

@pytest_asyncio.fixture
async def test_scholarship(db_session: AsyncSession) -> Scholarship:
    """Create a test scholarship"""
    scholarship = Scholarship(
        name="Test STEM Scholarship",
        organization="Test Foundation",
        amount_min=5000,
        amount_max=10000,
        deadline=datetime.now() + timedelta(days=60),
        description="Scholarship for STEM students",
        eligibility_requirements="Must be pursuing STEM degree, 3.5+ GPA",
        application_url="https://example.com/apply",
        essay_required=True,
        letters_of_recommendation_required=2,
        is_renewable=True,
        award_type="Merit-based"
    )
    db_session.add(scholarship)
    await db_session.commit()
    await db_session.refresh(scholarship)
    return scholarship


@pytest_asyncio.fixture
async def test_scholarship_2(db_session: AsyncSession) -> Scholarship:
    """Create a second test scholarship with different criteria"""
    scholarship = Scholarship(
        name="Need-Based Scholarship",
        organization="Community Foundation",
        amount_min=2000,
        amount_max=5000,
        deadline=datetime.now() + timedelta(days=30),
        description="Scholarship for students with financial need",
        eligibility_requirements="Must demonstrate financial need",
        application_url="https://example.com/need-based",
        essay_required=True,
        letters_of_recommendation_required=1,
        is_renewable=False,
        award_type="Need-based"
    )
    db_session.add(scholarship)
    await db_session.commit()
    await db_session.refresh(scholarship)
    return scholarship


# ===========================
# APPLICATION TRACKING FIXTURES
# ===========================

@pytest_asyncio.fixture
async def test_college_application(
    db_session: AsyncSession,
    test_user: User,
    test_institution: Institution
) -> CollegeApplication:
    """Create a test college application"""
    application = CollegeApplication(
        user_id=test_user.id,
        institution_id=test_institution.id,
        status="planning",
        application_type="regular_decision",
        deadline=datetime.now() + timedelta(days=90),
        notes="Reach school, strong engineering program"
    )
    db_session.add(application)
    await db_session.commit()
    await db_session.refresh(application)
    return application


@pytest_asyncio.fixture
async def test_scholarship_application(
    db_session: AsyncSession,
    test_user: User,
    test_scholarship: Scholarship
) -> ScholarshipApplication:
    """Create a test scholarship application"""
    application = ScholarshipApplication(
        user_id=test_user.id,
        scholarship_id=test_scholarship.id,
        status="interested",
        notes="Good fit for my major and GPA"
    )
    db_session.add(application)
    await db_session.commit()
    await db_session.refresh(application)
    return application


# ===========================
# FILE HANDLING FIXTURES
# ===========================

@pytest.fixture
def sample_resume_pdf() -> bytes:
    """
    Generate a minimal valid PDF for testing resume uploads.
    This is a simple PDF that parsers can handle.
    """
    # Minimal PDF structure
    pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >>
   /MediaBox [0 0 612 792] /Contents 5 0 R >>
endobj
4 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
5 0 obj
<< /Length 44 >>
stream
BT
/F1 12 Tf
100 700 Td
(Test Resume) Tj
ET
endstream
endobj
xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000261 00000 n
0000000340 00000 n
trailer
<< /Size 6 /Root 1 0 R >>
startxref
433
%%EOF"""
    return pdf_content


@pytest.fixture
def sample_resume_docx() -> bytes:
    """
    Generate a minimal DOCX file for testing.
    Note: This is a simplified version. For real tests, you might want to use python-docx.
    """
    # For now, return empty bytes - implement with python-docx if needed
    return b""


@pytest.fixture
def sample_image_bytes() -> bytes:
    """
    Generate a minimal valid PNG image for testing image uploads.
    1x1 pixel transparent PNG.
    """
    # Minimal 1x1 transparent PNG
    png_bytes = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00'
        b'\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx'
        b'\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    return png_bytes


@pytest.fixture
def sample_image_file(sample_image_bytes: bytes):
    """Create a file-like object from image bytes"""
    return BytesIO(sample_image_bytes)


# ===========================
# HELPER FIXTURES
# ===========================

@pytest.fixture
def sample_user_data() -> Dict[str, Any]:
    """Sample user registration data"""
    return {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "NewUserPassword123!",
        "first_name": "New",
        "last_name": "User"
    }


@pytest.fixture
def sample_profile_data() -> Dict[str, Any]:
    """Sample profile update data"""
    return {
        "high_school": "Sample High School",
        "graduation_year": 2025,
        "gpa": 3.7,
        "sat_score": 1350,
        "intended_major": "Biology",
        "state": "CA",
        "city": "Los Angeles",
        "biography": "Aspiring biologist interested in research"
    }


@pytest.fixture
def sample_college_application_data(test_institution: Institution) -> Dict[str, Any]:
    """Sample college application creation data"""
    return {
        "institution_id": test_institution.id,
        "status": "planning",
        "application_type": "early_action",
        "deadline": (datetime.now() + timedelta(days=60)).isoformat(),
        "notes": "Strong safety school"
    }


@pytest.fixture
def sample_scholarship_application_data(test_scholarship: Scholarship) -> Dict[str, Any]:
    """Sample scholarship application creation data"""
    return {
        "scholarship_id": test_scholarship.id,
        "status": "planning",
        "notes": "Meets all eligibility requirements"
    }


# ===========================
# SESSION SCOPED FIXTURES
# ===========================

@pytest.fixture(scope="session")
def anyio_backend():
    """Configure anyio backend for pytest-asyncio"""
    return "asyncio"
