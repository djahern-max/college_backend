# 🎓 MagicScholar Backend (college_backend)

**A FastAPI backend powering the student platform for college planning and scholarship discovery**

[![Tests](https://img.shields.io/badge/tests-coming%20soon-yellow)](tests/)
[![Python](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-00a393)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 📊 Project Overview

MagicScholar is a three-part ecosystem connecting students with colleges and scholarships:

1. **CampusConnect** (Admin Portal) - Where institutions manage their data
2. **MagicScholar App** (Student Platform) - Where students discover and track opportunities ← **This Backend**
3. **Marketing Site** - Public-facing website explaining the vision

This repository contains the **student-facing backend** that powers app.magicscholar.com.

---

## 🏗️ Architecture

- **Backend Framework:** FastAPI (async Python web framework)
- **Database:** PostgreSQL with SQLAlchemy ORM
- **Authentication:** Google OAuth + JWT tokens (also supports LinkedIn OAuth)
- **Cloud Storage:** DigitalOcean Spaces for resumes and images
- **File Processing:** Resume parsing (PDF/DOCX)
- **Real-time Data:** IPEDS integration for institution data

---

## 🚀 Key Features

### Student Features
- ✅ Google/LinkedIn OAuth registration and login
- ✅ Comprehensive student profiles
- ✅ Resume upload and automatic parsing
- ✅ College search and discovery (609 institutions)
- ✅ Scholarship search and matching (126+ awards)
- ✅ College application tracking with deadlines
- ✅ Scholarship application tracking
- ✅ Dashboard with statistics and upcoming deadlines
- ✅ Profile-based institution matching

### Data Features
- ✅ IPEDS-integrated institution data
- ✅ Admissions statistics and requirements
- ✅ Tuition and cost information
- ✅ Enrollment and graduation data
- ✅ Real-time data updates

---

## 📚 Complete API Reference

### 🔓 Public Endpoints (No Authentication)

#### **Health & Meta**
```
GET  /                              # Root endpoint
GET  /health                        # Health check
GET  /routes-simple                 # List all routes
```

#### **Institutions**
```
GET  /api/v1/institutions/                    # List institutions (paginated)
GET  /api/v1/institutions/search              # Search institutions
GET  /api/v1/institutions/states              # List available states
GET  /api/v1/institutions/{institution_id}    # Get institution by ID
GET  /api/v1/institutions/ipeds/{ipeds_id}    # Get by IPEDS ID
GET  /api/v1/institutions/stats/summary       # Institution statistics
```

#### **Scholarships**
```
GET  /api/v1/scholarships/                    # List scholarships (paginated)
GET  /api/v1/scholarships/list                # Simple list
GET  /api/v1/scholarships/{scholarship_id}    # Get scholarship details
GET  /api/v1/scholarships/upcoming-deadlines  # Upcoming scholarship deadlines
```

#### **Costs & Financial Data**
```
GET  /api/v1/costs/institution/{ipeds_id}         # Get cost data
GET  /api/v1/costs/institution/{ipeds_id}/summary # Cost summary
GET  /api/v1/costs/compare                        # Compare multiple institutions
```

#### **Admissions Data**
```
GET  /api/v1/admissions/institution/{ipeds_id}                    # Latest admissions
GET  /api/v1/admissions/institution/{ipeds_id}/all                # All years
GET  /api/v1/admissions/institution/{ipeds_id}/year/{academic_year} # Specific year
```

---

### 🔐 Protected Endpoints (Authentication Required)

#### **Authentication & OAuth**
```
POST   /api/v1/auth/register                  # Register new user
POST   /api/v1/auth/login                     # Login (OAuth2 form)
POST   /api/v1/auth/login-json                # Login (JSON format)
GET    /api/v1/auth/me                        # Get current user info
POST   /api/v1/auth/logout                    # Logout

GET    /api/v1/oauth/google/url               # Get Google OAuth URL
GET    /api/v1/oauth/google/callback          # Google OAuth callback
GET    /api/v1/oauth/linkedin/url             # Get LinkedIn OAuth URL
GET    /api/v1/oauth/linkedin/callback        # LinkedIn OAuth callback
DELETE /api/v1/oauth/cleanup-expired-states   # Cleanup expired OAuth states
```

#### **Student Profiles**
```
GET    /api/v1/profiles/me                           # Get my profile
PUT    /api/v1/profiles/me                           # Update my profile
GET    /api/v1/profiles/me/matching-institutions     # Get matching colleges
GET    /api/v1/profiles/me/settings                  # Get profile settings
PATCH  /api/v1/profiles/me/settings                  # Update settings
POST   /api/v1/profiles/me/upload-headshot           # Upload profile picture
POST   /api/v1/profiles/me/upload-resume-and-update  # Upload & parse resume
```

#### **College Application Tracking**
```
GET    /api/v1/college-tracking/dashboard                                # Dashboard with stats
POST   /api/v1/college-tracking/applications                             # Save college
GET    /api/v1/college-tracking/applications                             # List applications
GET    /api/v1/college-tracking/applications/{application_id}            # Get application
PUT    /api/v1/college-tracking/applications/{application_id}            # Update application
DELETE /api/v1/college-tracking/applications/{application_id}            # Delete application

# Quick Status Updates
POST   /api/v1/college-tracking/applications/{application_id}/mark-submitted   # Mark submitted
POST   /api/v1/college-tracking/applications/{application_id}/mark-accepted    # Mark accepted
POST   /api/v1/college-tracking/applications/{application_id}/mark-rejected    # Mark rejected
POST   /api/v1/college-tracking/applications/{application_id}/mark-waitlisted  # Mark waitlisted
```

#### **Scholarship Application Tracking**
```
GET    /api/v1/scholarship-tracking/dashboard                             # Dashboard with stats
POST   /api/v1/scholarship-tracking/applications                          # Save scholarship
GET    /api/v1/scholarship-tracking/applications                          # List applications
GET    /api/v1/scholarship-tracking/applications/{application_id}         # Get application
PUT    /api/v1/scholarship-tracking/applications/{application_id}         # Update application
DELETE /api/v1/scholarship-tracking/applications/{application_id}         # Delete application

# Quick Status Updates
POST   /api/v1/scholarship-tracking/applications/{application_id}/mark-submitted # Mark submitted
POST   /api/v1/scholarship-tracking/applications/{application_id}/mark-accepted  # Mark accepted
POST   /api/v1/scholarship-tracking/applications/{application_id}/mark-rejected  # Mark rejected
```

#### **Admin-Only Scholarship Management**
```
POST   /api/v1/scholarships/                         # Create scholarship
PATCH  /api/v1/scholarships/{scholarship_id}         # Update scholarship
DELETE /api/v1/scholarships/{scholarship_id}         # Delete scholarship
POST   /api/v1/scholarships/bulk                     # Bulk create scholarships
```

---

## 🧪 Testing Plan

### Test Coverage Goals

We're building a comprehensive test suite similar to CampusConnect (94+ passing tests):

| Category | Estimated Tests | Status |
|----------|----------------|--------|
| Authentication & OAuth | 15 tests | 📋 Planned |
| Student Profiles | 18 tests | 📋 Planned |
| Institutions | 12 tests | 📋 Planned |
| Scholarships | 12 tests | 📋 Planned |
| College Tracking | 25 tests | 📋 Planned |
| Scholarship Tracking | 20 tests | 📋 Planned |
| Admissions Data | 10 tests | 📋 Planned |
| Costs & Financial | 10 tests | 📋 Planned |
| Unit Tests | 20 tests | 📋 Planned |
| **TOTAL TARGET** | **142+ tests** | 🎯 Goal |

### Running Tests (Coming Soon)

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest tests/ -v

# Run specific categories
pytest tests/integration/test_auth_flow.py -v
pytest tests/integration/test_college_tracking.py -v
pytest tests/integration/test_profiles.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run in parallel
pytest tests/ -n auto
```

---

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Virtual environment tool

### Installation Steps

1. **Clone the repository**
```bash
git clone https://github.com/djahern-max/college_backend.git
cd college_backend
```

2. **Create and activate virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

Required environment variables:
```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/magicscholar_db

# Security
SECRET_KEY=your-secret-key-here-32-chars-minimum
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/callback

# LinkedIn OAuth (optional)
LINKEDIN_CLIENT_ID=your-linkedin-client-id
LINKEDIN_CLIENT_SECRET=your-linkedin-client-secret

# DigitalOcean Spaces
SPACES_KEY=your-spaces-key
SPACES_SECRET=your-spaces-secret
SPACES_BUCKET=magicscholar
SPACES_REGION=nyc3

# Frontend URL
FRONTEND_URL=http://localhost:3000
CORS_ORIGINS=["http://localhost:3000"]
```

5. **Set up test database**
```bash
# Create test database
createdb magicscholar_test

# Copy test environment
cp .env.test.example .env.test

# Edit .env.test with test database configuration
nano .env.test
```

6. **Run database migrations**
```bash
alembic upgrade head
```

7. **Start the development server**
```bash
uvicorn app.main:app --reload
# Or use the run script
python run.py
```

The API will be available at `http://localhost:8000`

8. **Verify installation**
```bash
# Check API health
curl http://localhost:8000/health

# View all routes
curl http://localhost:8000/routes-simple

# Access interactive docs
open http://localhost:8000/docs
```

---

## 📖 API Documentation

### Interactive Documentation

Once the server is running, access:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **Simple Route List:** `http://localhost:8000/routes-simple`

### Authentication Flow

**Google OAuth (Primary Method):**

1. Frontend requests OAuth URL:
   ```bash
   GET /api/v1/oauth/google/url
   ```

2. User completes Google OAuth flow

3. Google redirects to callback:
   ```bash
   GET /api/v1/oauth/google/callback?code=AUTH_CODE&state=STATE
   ```

4. Backend returns JWT token:
   ```json
   {
     "access_token": "eyJ...",
     "token_type": "bearer",
     "user": {
       "id": 1,
       "email": "student@example.com",
       "username": "student123"
     }
   }
   ```

5. Use JWT for authenticated requests:
   ```bash
   GET /api/v1/profiles/me
   Authorization: Bearer eyJ...
   ```

**Alternative: Email/Password (Development):**

```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "student@example.com",
  "username": "student123",
  "password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

---

## 📊 Database Schema

### Core Models

**User**
- Email and username authentication
- OAuth provider tracking
- Profile relationship

**UserProfile**
- Comprehensive student information
- Academic details (GPA, test scores)
- Geographic preferences
- Career interests
- Resume storage

**Institution**
- IPEDS ID integration
- Geographic information
- Control type (Public/Private)
- Static characteristics

**Scholarship**
- Award amount ranges
- Eligibility criteria
- Deadline tracking
- Application requirements

**CollegeApplication**
- Application tracking
- Status management
- Deadline monitoring
- Notes and timeline

**ScholarshipApplication**
- Similar tracking for scholarships
- Award amount tracking
- Decision dates

**Supporting Data:**
- AdmissionsData
- TuitionData
- EnrollmentData
- GraduationData

---

## 🔐 Security Features

- **OAuth 2.0:** Google and LinkedIn authentication
- **JWT Tokens:** Secure stateless authentication
- **Password Hashing:** PBKDF2 with secure salts
- **CORS Protection:** Configurable cross-origin policies
- **SQL Injection Protection:** SQLAlchemy ORM
- **Environment Variables:** Sensitive data protection

---

## 🎯 Key User Journeys

### Journey 1: New Student Onboarding
```
1. Register via Google OAuth → /api/v1/oauth/google/callback
2. Profile auto-created → /api/v1/profiles/me
3. Upload resume → /api/v1/profiles/me/upload-resume-and-update
4. Profile enriched with parsed data
5. Discover matching institutions → /api/v1/profiles/me/matching-institutions
```

### Journey 2: College Application Management
```
1. Search colleges → /api/v1/institutions/search
2. Save to tracker → POST /api/v1/college-tracking/applications
3. View dashboard → /api/v1/college-tracking/dashboard
4. Update status → PUT /api/v1/college-tracking/applications/{id}
5. Mark submitted → POST /api/v1/college-tracking/applications/{id}/mark-submitted
6. Track decisions → Dashboard shows accepted/rejected
```

### Journey 3: Scholarship Discovery & Application
```
1. Browse scholarships → /api/v1/scholarships/
2. Check upcoming deadlines → /api/v1/scholarships/upcoming-deadlines
3. Save scholarship → POST /api/v1/scholarship-tracking/applications
4. View dashboard → /api/v1/scholarship-tracking/dashboard
5. Submit application → POST /api/v1/scholarship-tracking/applications/{id}/mark-submitted
6. Track awards → Monitor status changes
```

---

## 🧩 Service Layer

The backend uses a service-oriented architecture:

**Services:**
- `UserService` - User management
- `ProfileService` - Profile operations
- `OAuthService` - OAuth handling
- `InstitutionService` - Institution search and filtering
- `ScholarshipService` - Scholarship management
- `CollegeTrackingService` - Application tracking
- `ScholarshipTrackingService` - Scholarship tracking
- `TuitionService` - Cost data
- `AdmissionsService` - Admissions statistics
- `ResumeParser` - PDF/DOCX parsing
- `FileExtractor` - File content extraction
- `DigitalOceanSpaces` - Cloud storage

---

## 📈 Performance & Optimization

- **Async/Await:** Non-blocking I/O throughout
- **Connection Pooling:** Efficient database connections
- **Lazy Loading:** Optimized SQLAlchemy queries
- **CDN Integration:** DigitalOcean Spaces for static assets
- **Indexed Queries:** Database optimization
- **Pagination:** Large result set handling

---

## 🚀 Deployment

### Production Environment

Currently deployed on DigitalOcean:
- **Backend:** Docker container on droplet
- **Database:** Managed PostgreSQL
- **CDN:** DigitalOcean Spaces
- **SSL:** Let's Encrypt via nginx

### Deployment Checklist

- [ ] Set production environment variables
- [ ] Configure production database
- [ ] Set up Google OAuth credentials (production)
- [ ] Configure DigitalOcean Spaces
- [ ] Set up CORS for production frontend
- [ ] Enable HTTPS
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy
- [ ] Run database migrations
- [ ] Verify all endpoints
- [ ] Load test critical paths

---

## 🗺️ Roadmap

### Current Phase (Q4 2025)
- [x] Core API operational
- [x] OAuth authentication
- [x] Institution data (609 schools)
- [x] Scholarship database (126+ awards)
- [x] Application tracking
- [ ] **Complete test suite** ← Current Focus
- [ ] Frontend integration refinement

### Next Phase (Q1 2026)
- [ ] Enhanced matching algorithms
- [ ] AI-powered recommendations (RAG)
- [ ] Mobile app backend support
- [ ] Common App integration
- [ ] Real-time notifications
- [ ] Analytics dashboard

### Future Vision (2026+)
- [ ] Conversational AI assistant
- [ ] Vector database for semantic search
- [ ] Essay review AI
- [ ] Predictive analytics
- [ ] White-label solution
- [ ] Voice interface

---

## 📝 Project Structure

```
college_backend/
├── app/
│   ├── api/
│   │   └── v1/                  # API endpoints
│   │       ├── user.py          # Auth endpoints
│   │       ├── oauth.py         # OAuth endpoints
│   │       ├── profiles.py      # Profile management
│   │       ├── institution.py   # Institution endpoints
│   │       ├── scholarships.py  # Scholarship endpoints
│   │       ├── college_tracking.py    # College tracking
│   │       ├── scholarship_tracking.py # Scholarship tracking
│   │       ├── admissions.py    # Admissions data
│   │       └── costs.py         # Cost/tuition data
│   ├── core/                    # Core functionality
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   ├── models/                  # SQLAlchemy models
│   │   ├── user.py
│   │   ├── profile.py
│   │   ├── institution.py
│   │   ├── scholarship.py
│   │   ├── college_applications.py
│   │   ├── scholarship_applications.py
│   │   ├── admissions.py
│   │   ├── tuition.py
│   │   ├── enrollment.py
│   │   └── graduation.py
│   ├── schemas/                 # Pydantic schemas
│   ├── services/                # Business logic
│   │   ├── user.py
│   │   ├── profile.py
│   │   ├── oauth.py
│   │   ├── institution.py
│   │   ├── scholarship.py
│   │   ├── college_tracking.py
│   │   ├── scholarship_tracking.py
│   │   ├── resume_parser.py
│   │   ├── file_extractor.py
│   │   └── digitalocean_spaces.py
│   └── main.py                  # FastAPI application
├── tests/                       # Test suite (coming soon)
│   ├── integration/
│   ├── unit/
│   └── conftest.py
├── alembic/                     # Database migrations
├── scripts/                     # Utility scripts
├── .env                         # Environment variables
├── requirements.txt             # Python dependencies
├── run.py                       # Development runner
└── README.md                    # This file
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Ensure all tests pass (`pytest tests/ -v`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## 📞 Contact & Resources

**Developer:** Danny Ahern  
**Email:** contact@magicscholar.com  
**GitHub:** @djahern-max

**Live Sites:**
- Student App: https://app.magicscholar.com
- Marketing: https://www.magicscholar.com

**Repositories:**
- This Backend: github.com/djahern-max/college_backend
- Student Frontend: github.com/djahern-max/magicscholar_frontend
- Admin Backend: github.com/djahern-max/campusconnect_backend
- Admin Frontend: github.com/djahern-max/campusconnect_frontend
- Marketing: github.com/djahern-max/magicscholar-marketing

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- FastAPI for the excellent framework
- SQLAlchemy for powerful ORM
- Google & LinkedIn for OAuth support
- DigitalOcean for hosting infrastructure
- The Python async community

---

**Built with ❤️ for students everywhere**

*Democratizing access to college planning through technology*
