# 🧪 MagicScholar Backend Testing Strategy

## Overview

This document outlines the comprehensive testing strategy for the MagicScholar backend (college_backend), mirroring the rigorous approach used in CampusConnect backend with 94+ passing tests.

---

## 🎯 Testing Goals

1. **Comprehensive Coverage** - Test all API endpoints and business logic
2. **User Flow Testing** - Verify complete student journeys
3. **Data Integrity** - Ensure database operations are correct
4. **Security Testing** - Validate authentication and authorization
5. **Integration Testing** - Test interactions between services
6. **Regression Prevention** - Catch bugs before production

---

## 📊 Test Architecture

### Test Structure
```
tests/
├── conftest.py              # Shared fixtures and configuration
├── integration/             # API endpoint integration tests
│   ├── test_auth_flow.py
│   ├── test_institutions.py
│   ├── test_scholarships.py
│   ├── test_college_tracking.py
│   ├── test_scholarship_tracking.py
│   ├── test_profiles.py
│   ├── test_admissions.py
│   ├── test_tuition.py
│   ├── test_enrollment.py
│   └── test_graduation.py
├── unit/                    # Unit tests for core functionality
│   ├── test_services.py
│   ├── test_models.py
│   └── test_security.py
└── README.md               # Testing documentation
```

---

## 🔑 Core Testing Areas

### 1. Authentication & Authorization (OAuth + JWT)

**Google OAuth Flow:**
- ✅ OAuth initiation
- ✅ OAuth callback handling
- ✅ Token generation
- ✅ Token refresh
- ✅ Token validation
- ✅ Invalid token rejection
- ✅ Expired token handling

**Test Files:**
- `tests/integration/test_auth_flow.py`
- `tests/unit/test_security.py`

**Key Scenarios:**
```python
# Happy path
test_google_oauth_callback_success()
test_token_refresh_valid()
test_protected_endpoint_with_valid_token()

# Error cases
test_oauth_callback_invalid_code()
test_expired_token_rejection()
test_missing_token_rejection()
test_malformed_token_rejection()
```

---

### 2. User Profile Management

**Profile Operations:**
- ✅ Create profile on registration
- ✅ Get current user profile
- ✅ Update profile information
- ✅ Upload profile picture
- ✅ Resume upload and parsing
- ✅ Settings management
- ✅ Profile completeness tracking

**Test Files:**
- `tests/integration/test_profiles.py`

**Key Scenarios:**
```python
# Profile CRUD
test_get_my_profile()
test_update_profile_success()
test_profile_created_on_registration()

# Resume handling
test_upload_resume_pdf()
test_upload_resume_docx()
test_resume_parsing_extracts_data()
test_resume_updates_profile()

# Settings
test_update_settings()
test_get_settings()
```

---

### 3. Institution Management

**Institution Operations:**
- ✅ List institutions with pagination
- ✅ Search institutions by name
- ✅ Filter by state
- ✅ Filter by control type
- ✅ Get institution by IPEDS ID
- ✅ Get institution by database ID
- ✅ Get institution details with related data

**Test Files:**
- `tests/integration/test_institutions.py`

**Key Scenarios:**
```python
# Search and filtering
test_list_institutions_paginated()
test_search_institutions_by_name()
test_filter_by_state()
test_filter_by_control_type()

# Detail retrieval
test_get_institution_by_ipeds_id()
test_get_institution_by_id()
test_get_nonexistent_institution_404()

# Related data
test_institution_with_admissions_data()
test_institution_with_enrollment_data()
```

---

### 4. Scholarship Management

**Scholarship Operations:**
- ✅ List scholarships with pagination
- ✅ Search scholarships
- ✅ Filter by award amount
- ✅ Filter by deadline
- ✅ Get scholarship details
- ✅ Scholarship matching based on profile

**Test Files:**
- `tests/integration/test_scholarships.py`

**Key Scenarios:**
```python
# Search and filtering
test_list_scholarships()
test_search_scholarships()
test_filter_by_award_amount()
test_filter_by_deadline()

# Details
test_get_scholarship_by_id()
test_scholarship_not_found_404()
```

---

### 5. College Application Tracking

**Application Tracking:**
- ✅ Get dashboard with summary stats
- ✅ Save/bookmark college
- ✅ Update application status
- ✅ Add/update deadlines
- ✅ Add notes
- ✅ Delete application
- ✅ Deadline reminders
- ✅ Overdue tracking

**Test Files:**
- `tests/integration/test_college_tracking.py`

**Key Scenarios:**
```python
# Dashboard
test_get_empty_dashboard()
test_dashboard_with_applications()
test_dashboard_statistics()
test_upcoming_deadlines()
test_overdue_applications()

# CRUD operations
test_save_college()
test_update_application_status()
test_add_deadline()
test_add_notes()
test_delete_application()

# Application types
test_save_early_decision()
test_save_early_action()
test_save_regular_decision()

# Status transitions
test_status_planning_to_in_progress()
test_status_submitted_to_accepted()
test_status_submitted_to_rejected()
```

---

### 6. Scholarship Application Tracking

**Scholarship Tracking:**
- ✅ Get dashboard with summary
- ✅ Save scholarship
- ✅ Update status
- ✅ Track deadlines
- ✅ Add notes
- ✅ Delete application
- ✅ Award tracking

**Test Files:**
- `tests/integration/test_scholarship_tracking.py`

**Key Scenarios:**
```python
# Dashboard
test_get_scholarship_dashboard()
test_scholarship_statistics()
test_upcoming_scholarship_deadlines()

# CRUD
test_save_scholarship()
test_update_scholarship_status()
test_delete_scholarship_application()

# Status tracking
test_status_not_started_to_in_progress()
test_status_submitted_to_awarded()
```

---

### 7. Admissions Data Management

**Admissions Operations:**
- ✅ Get admissions data by institution
- ✅ Get admissions by IPEDS ID
- ✅ Get latest admissions data
- ✅ Historical admissions data
- ✅ Acceptance rate calculations

**Test Files:**
- `tests/integration/test_admissions.py`

**Key Scenarios:**
```python
test_get_admissions_by_institution_id()
test_get_admissions_by_ipeds_id()
test_get_latest_admissions_data()
test_admissions_not_found_returns_404()
test_admissions_acceptance_rate_calculation()
```

---

### 8. Tuition & Financial Data

**Tuition Operations:**
- ✅ Get tuition data by institution
- ✅ Get tuition by IPEDS ID
- ✅ Get latest tuition data
- ✅ In-state vs out-of-state costs
- ✅ Historical tuition trends

**Test Files:**
- `tests/integration/test_tuition.py`

**Key Scenarios:**
```python
test_get_tuition_by_institution_id()
test_get_tuition_by_ipeds_id()
test_get_latest_tuition()
test_tuition_in_state_vs_out_of_state()
test_tuition_historical_data()
```

---

### 9. Enrollment & Graduation Data

**Data Operations:**
- ✅ Get enrollment statistics
- ✅ Get graduation rates
- ✅ Demographic breakdowns
- ✅ Retention rates

**Test Files:**
- `tests/integration/test_enrollment.py`
- `tests/integration/test_graduation.py`

---

### 10. Service Layer Testing

**Service Tests:**
- ✅ ProfileService
- ✅ UserService
- ✅ OAuthService
- ✅ InstitutionService
- ✅ ScholarshipService
- ✅ CollegeTrackingService
- ✅ ScholarshipTrackingService
- ✅ TuitionService
- ✅ AdmissionsService
- ✅ ResumeParser
- ✅ FileExtractor
- ✅ DigitalOceanSpaces

**Test Files:**
- `tests/unit/test_services.py`

---

## 🔧 Test Configuration

### Test Database Setup

**Database:** `magicscholar_test`
**Configuration:** `.env.test`

```env
# .env.test
TESTING=true
DATABASE_URL=postgresql://user:pass@localhost:5432/magicscholar_test
SECRET_KEY=test-secret-key-for-testing-only
GOOGLE_CLIENT_ID=test-google-client-id
GOOGLE_CLIENT_SECRET=test-google-client-secret
SPACES_KEY=test-spaces-key
SPACES_SECRET=test-spaces-secret
```

### Test Isolation Strategy

Each test runs in its own transaction that is rolled back:
```python
@pytest.fixture(scope="function")
async def db_session():
    """Database session with automatic rollback"""
    async with AsyncSession(engine) as session:
        async with session.begin():
            yield session
            await session.rollback()
```

---

## 🎯 Test Fixtures

### Core Fixtures (conftest.py)

```python
# HTTP Client
@pytest.fixture
async def client() -> AsyncClient:
    """Async HTTP client for API testing"""

# Database
@pytest.fixture
async def db_session() -> AsyncSession:
    """Database session with rollback"""

# Authentication
@pytest.fixture
async def test_user(db_session) -> User:
    """Create test user"""

@pytest.fixture
async def user_token(test_user) -> str:
    """Generate JWT token for test user"""

@pytest.fixture
async def auth_headers(user_token) -> dict:
    """Auth headers with Bearer token"""

# Test Data
@pytest.fixture
async def test_institution(db_session) -> Institution:
    """Create test institution"""

@pytest.fixture
async def test_scholarship(db_session) -> Scholarship:
    """Create test scholarship"""

@pytest.fixture
async def test_profile(db_session, test_user) -> UserProfile:
    """Create test user profile"""

# File Handling
@pytest.fixture
def sample_resume_pdf() -> bytes:
    """Sample PDF resume for testing"""

@pytest.fixture
def sample_image_bytes() -> bytes:
    """Sample image for testing"""
```

---

## 📈 Test Metrics & Goals

### Coverage Goals

| Category | Target Coverage | Status |
|----------|----------------|--------|
| API Endpoints | 100% | 🎯 Goal |
| Service Layer | 95%+ | 🎯 Goal |
| Models | 90%+ | 🎯 Goal |
| Authentication | 100% | 🎯 Goal |
| Business Logic | 95%+ | 🎯 Goal |

### Test Count Goals

| Category | Estimated Tests |
|----------|----------------|
| Authentication | 12 tests |
| Profiles | 15 tests |
| Institutions | 12 tests |
| Scholarships | 10 tests |
| College Tracking | 20 tests |
| Scholarship Tracking | 15 tests |
| Admissions | 8 tests |
| Tuition | 8 tests |
| Enrollment | 6 tests |
| Graduation | 6 tests |
| Unit Tests | 20 tests |
| **TOTAL** | **132+ tests** |

---

## 🚀 Test Execution Commands

### Basic Commands
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific category
pytest tests/integration/ -v
pytest tests/unit/ -v

# Run specific file
pytest tests/integration/test_auth_flow.py -v
pytest tests/integration/test_college_tracking.py -v
```

### Advanced Commands
```bash
# Parallel execution
pytest tests/ -n auto

# Stop on first failure
pytest tests/ -x

# Run last failed tests
pytest tests/ --lf

# Show test durations
pytest tests/ --durations=10

# Run with markers
pytest tests/ -m "auth" -v
pytest tests/ -m "slow" -v
```

---

## 🏷️ Test Markers

```python
@pytest.mark.integration  # Integration tests
@pytest.mark.unit         # Unit tests
@pytest.mark.auth         # Authentication tests
@pytest.mark.tracking     # Application tracking tests
@pytest.mark.slow         # Slow-running tests
@pytest.mark.external     # Tests requiring external services
```

---

## 📝 Writing New Tests

### Integration Test Template
```python
import pytest
from httpx import AsyncClient

@pytest.mark.integration
class TestMyFeature:
    
    @pytest.mark.asyncio
    async def test_my_endpoint(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_institution: Institution
    ):
        """Test description"""
        # Arrange
        endpoint = f"/api/v1/institutions/{test_institution.id}"
        
        # Act
        response = await client.get(endpoint, headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_institution.id
```

### Unit Test Template
```python
import pytest
from app.services.profile import ProfileService

@pytest.mark.unit
class TestProfileService:
    
    def test_create_profile(self, db_session, test_user):
        """Test profile creation"""
        # Arrange
        service = ProfileService(db_session)
        
        # Act
        profile = service.create_profile(test_user.id)
        
        # Assert
        assert profile.user_id == test_user.id
        assert profile.id is not None
```

---

## 🔍 Test Data Strategy

### Realistic Test Data
- Use real IPEDS IDs for institutions (e.g., 186131 for MIT)
- Realistic student profiles
- Valid scholarship criteria
- Proper date ranges for deadlines

### Data Factories
```python
def create_test_institution(**kwargs):
    """Factory for creating test institutions"""
    defaults = {
        "ipeds_id": 186131,
        "name": "Test University",
        "city": "Boston",
        "state": "MA",
        "control_type": "Public"
    }
    defaults.update(kwargs)
    return Institution(**defaults)
```

---

## 🎭 Test Scenarios

### Critical User Journeys

**Journey 1: New Student Onboarding**
1. Register via Google OAuth
2. Create profile
3. Upload resume
4. Browse institutions
5. Save colleges to tracker
6. Discover scholarships
7. Save scholarships

**Journey 2: Application Management**
1. View dashboard
2. Update application status
3. Add deadlines
4. Track progress
5. Submit applications
6. Receive acceptance
7. Make final decision

**Journey 3: Scholarship Hunt**
1. Search scholarships
2. Filter by eligibility
3. Save to tracker
4. Track deadlines
5. Submit applications
6. Monitor awards

---

## 🐛 Common Test Pitfalls to Avoid

1. **Database State Pollution** - Always use transaction rollback
2. **Hard-coded IDs** - Use fixtures and factories
3. **Flaky Tests** - Avoid time-dependent tests
4. **Missing Edge Cases** - Test error paths
5. **Slow Tests** - Mock external services
6. **Incomplete Cleanup** - Ensure fixtures clean up

---

## 📊 CI/CD Integration

### GitHub Actions Workflow
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
    
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      
      - name: Run tests
        run: pytest tests/ -v --cov=app
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## 🎯 Success Criteria

### Definition of Done for Testing

- [ ] All API endpoints have integration tests
- [ ] All services have unit tests
- [ ] Test coverage > 90%
- [ ] All tests pass consistently
- [ ] Documentation is complete
- [ ] CI/CD pipeline is green
- [ ] No flaky tests
- [ ] Performance benchmarks met

---

## 📚 Resources

### FastAPI Testing
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [Async Testing with HTTPX](https://www.python-httpx.org/async/)

### Pytest
- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-asyncio](https://pytest-asyncio.readthedocs.io/)

### SQLAlchemy
- [Testing with SQLAlchemy](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html)

---

**Last Updated:** November 19, 2025
**Status:** Implementation Ready
**Target:** 132+ passing tests
