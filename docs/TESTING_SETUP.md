# 🧪 MagicScholar Testing Setup Guide

Complete guide to set up and run the MagicScholar backend test suite.

---

## ✅ Prerequisites Checklist

Before starting, ensure you have:

- [x] Python 3.11+ installed
- [x] PostgreSQL 14+ running
- [x] Virtual environment activated
- [x] Test database created (`magicscholar_test`)
- [x] DigitalOcean Spaces credentials

---

## 📦 Step 1: Create Test Directory Structure

Run these commands in your `college-backend` directory:

```bash
# Create test directories
mkdir -p tests/integration tests/unit tests/docs

# Create __init__.py files
touch tests/__init__.py
touch tests/integration/__init__.py
touch tests/unit/__init__.py
```

---

## 📄 Step 2: Copy Configuration Files

Copy the following files from the outputs to your project:

```bash
# Copy test environment configuration
cp /path/to/.env.test .env.test

# Copy pytest configuration
cp /path/to/pytest.ini pytest.ini

# Copy test fixtures
cp /path/to/conftest.py tests/conftest.py

# Copy test requirements
cp /path/to/requirements-test.txt requirements-test.txt
```

---

## 🔧 Step 3: Install Testing Dependencies

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Install testing dependencies
pip install -r requirements-test.txt

# Verify installation
pytest --version
# Should show: pytest 7.4.3
```

---

## 🗄️ Step 4: Set Up Test Database

Your test database is already created! Verify it:

```bash
# Connect to PostgreSQL
psql -U postgres

# List databases
\l

# You should see:
# magicscholar_test  | postgres | UTF8 | ...

# Exit psql
\q
```

The test suite will automatically:
- Create all tables before tests run
- Clean up after tests complete
- Use transaction rollback for isolation

---

## 🔐 Step 5: Verify Environment Configuration

Check your `.env.test` file has these critical settings:

```bash
# View the file
cat .env.test

# Critical settings:
✓ TESTING=true
✓ DATABASE_URL=postgresql://postgres:@localhost:5432/magicscholar_test
✓ SECRET_KEY=test-secret-key...
✓ DIGITAL_OCEAN_SPACES_ACCESS_KEY=DO00FHMKUY2X2M8JZHXD
✓ DIGITAL_OCEAN_SPACES_SECRET_KEY=1z6O3nl1nrzlru/...
```

---

## 🧪 Step 6: Run Your First Test

Let's verify everything works:

```bash
# Run pytest with verbose output
pytest tests/ -v

# You should see something like:
# =================== test session starts ====================
# platform darwin -- Python 3.11.x
# collected 0 items (for now - we'll add tests next)
# =================== no tests ran in 0.01s ==================
```

If you see this, **setup is successful!** ✅

---

## 📝 Step 7: Understanding the Test Structure

Your test structure will look like:

```
college-backend/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # ✅ Shared fixtures (done)
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_auth_flow.py    # 🔜 Coming next
│   │   ├── test_profiles.py
│   │   ├── test_institutions.py
│   │   ├── test_scholarships.py
│   │   ├── test_college_tracking.py
│   │   └── test_scholarship_tracking.py
│   └── unit/
│       ├── __init__.py
│       ├── test_services.py
│       └── test_models.py
├── .env.test                    # ✅ Test config (done)
├── pytest.ini                   # ✅ Pytest config (done)
└── requirements-test.txt        # ✅ Test dependencies (done)
```

---

## 🎯 Available Test Fixtures

Your `conftest.py` provides these fixtures:

### Database & HTTP
- `db_session` - Database session with auto-rollback
- `client` - Async HTTP client for API testing

### Authentication (NO OAUTH - Direct Auth Only)
- `test_user` - Regular test user
- `test_user_2` - Second test user
- `admin_user` - Admin user
- `user_token` - JWT token for test user
- `admin_token` - JWT token for admin
- `auth_headers` - Bearer auth headers
- `admin_headers` - Admin auth headers

### Test Data
- `test_profile` - User profile with sample data
- `complete_profile` - Fully completed profile
- `test_institution` - MIT test institution
- `test_institution_2` - Harvard test institution
- `public_institution` - Public university
- `test_scholarship` - STEM scholarship
- `test_scholarship_2` - Need-based scholarship
- `test_admissions_data` - Admissions statistics
- `test_tuition_data` - Tuition information
- `test_college_application` - College app tracking
- `test_scholarship_application` - Scholarship app tracking

### File Handling
- `sample_resume_pdf` - Minimal PDF for testing
- `sample_image_bytes` - 1x1 PNG image
- `sample_image_file` - File-like object

---

## 🚀 Common Test Commands

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=app --cov-report=html
# View report: open htmlcov/index.html

# Run specific test file
pytest tests/integration/test_auth_flow.py -v

# Run specific test
pytest tests/integration/test_auth_flow.py::TestAuthFlow::test_register_new_user -v

# Run tests by marker
pytest tests/ -m "auth" -v
pytest tests/ -m "integration" -v
pytest tests/ -m "unit" -v

# Run in parallel (faster)
pytest tests/ -n auto

# Stop on first failure
pytest tests/ -x

# Run last failed tests
pytest tests/ --lf

# Show test durations
pytest tests/ --durations=10

# Verbose output with full traceback
pytest tests/ -vv --tb=long
```

---

## 🔍 Debugging Failed Tests

When a test fails:

```bash
# Run with extra verbose output
pytest tests/integration/test_profiles.py -vv

# Show local variables in traceback
pytest tests/integration/test_profiles.py -vv -l

# Drop into debugger on failure
pytest tests/integration/test_profiles.py --pdb

# Print output during tests (normally captured)
pytest tests/integration/test_profiles.py -s
```

---

## 📊 Generating Coverage Reports

```bash
# Generate HTML coverage report
pytest tests/ --cov=app --cov-report=html

# Generate terminal coverage report
pytest tests/ --cov=app --cov-report=term

# Generate XML report (for CI/CD)
pytest tests/ --cov=app --cov-report=xml

# View HTML report
open htmlcov/index.html
```

---

## 🎭 Test Markers

Use markers to organize tests:

```python
@pytest.mark.integration  # Integration test
@pytest.mark.unit        # Unit test
@pytest.mark.auth        # Authentication test
@pytest.mark.profile     # Profile test
@pytest.mark.tracking    # Application tracking test
@pytest.mark.slow        # Slow test
```

Run tests by marker:
```bash
pytest tests/ -m "auth and integration" -v
pytest tests/ -m "not slow" -v
```

---

## 🐛 Common Issues & Solutions

### Issue: `ImportError: No module named 'pytest'`
**Solution:**
```bash
pip install -r requirements-test.txt
```

### Issue: `Database connection error`
**Solution:**
```bash
# Verify database exists
psql -U postgres -c "\l" | grep magicscholar_test

# If not, create it
createdb magicscholar_test
```

### Issue: `asyncpg.exceptions.InvalidCatalogNameError`
**Solution:**
```bash
# Database URL format must be correct
# Check .env.test has:
DATABASE_URL=postgresql://postgres:@localhost:5432/magicscholar_test
```

### Issue: `fixture 'event_loop' not found`
**Solution:**
Already handled! Your `pytest.ini` has:
```ini
asyncio_mode = auto
```

### Issue: Tests pass individually but fail together
**Solution:**
Transaction rollback might not be working. Check:
```python
# In conftest.py, ensure:
async with session.begin():
    try:
        yield session
    finally:
        await session.rollback()
```

---

## ✅ Verification Checklist

Before moving to writing tests, verify:

- [ ] `pytest --version` shows 7.4.3+
- [ ] `.env.test` exists with correct DATABASE_URL
- [ ] Test database `magicscholar_test` exists
- [ ] `pytest tests/ -v` runs without errors
- [ ] Virtual environment is activated
- [ ] All configuration files are in place

---

## 🎯 Next Steps

Now that setup is complete, you're ready to:

1. **Create test files** - Integration tests for each API endpoint
2. **Run tests** - `pytest tests/ -v`
3. **Check coverage** - `pytest tests/ --cov=app`
4. **Write more tests** - Aim for 142+ tests total

---

## 📚 Additional Resources

- **Pytest Documentation:** https://docs.pytest.org/
- **Pytest-asyncio:** https://pytest-asyncio.readthedocs.io/
- **HTTPX Testing:** https://www.python-httpx.org/async/
- **SQLAlchemy Testing:** https://docs.sqlalchemy.org/en/14/orm/session_transaction.html

---

## 🎉 Success!

If you've completed all steps and can run `pytest tests/ -v` successfully, your testing infrastructure is ready!

**Next:** We'll create the actual test files for all your API endpoints.

---

**Last Updated:** November 19, 2025  
**Setup Status:** ✅ Complete  
**Ready for:** Test file creation
