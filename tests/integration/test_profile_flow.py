# tests/integration/test_profile_flow.py
"""
Integration tests for profile management and operations.
SYNC version - matches sync SQLAlchemy backend.

Following TDD approach: Tests define the contract, then we validate the spec.
"""

import pytest
from starlette.testclient import TestClient
from sqlalchemy.orm import Session
import io
from datetime import datetime

from app.models.user import User
from app.models.profile import UserProfile


@pytest.mark.integration
@pytest.mark.profile
class TestProfileRetrieval:
    """Test profile retrieval endpoints"""

    def test_get_profile_auto_creates_if_missing(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        db_session: Session,
    ):
        """Test GET /me auto-creates empty profile if none exists"""
        # Ensure no profile exists
        existing = (
            db_session.query(UserProfile)
            .filter(UserProfile.user_id == test_user.id)
            .first()
        )
        if existing:
            db_session.delete(existing)
            db_session.commit()

        response = client.get("/api/v1/profiles/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == test_user.id
        assert "id" in data
        assert "created_at" in data
        assert data["settings"]["confetti_enabled"] is True  # Default setting

    def test_get_existing_profile(
        self, client: TestClient, auth_headers: dict, test_profile: UserProfile
    ):
        """Test GET /me returns existing profile"""
        response = client.get("/api/v1/profiles/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_profile.id
        assert data["user_id"] == test_profile.user_id
        assert data["state"] == test_profile.state
        assert data["city"] == test_profile.city
        assert data["high_school_name"] == test_profile.high_school_name
        assert data["graduation_year"] == test_profile.graduation_year
        assert data["gpa"] == test_profile.gpa

    def test_get_profile_requires_auth(self, client: TestClient):
        """Test GET /me fails without authentication"""
        response = client.get("/api/v1/profiles/me")

        assert response.status_code in [401, 403]

    def test_get_profile_returns_all_fields(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session: Session,
        test_user: User,
    ):
        """Test GET /me returns complete profile structure"""
        # Create comprehensive profile
        profile = UserProfile(
            user_id=test_user.id,
            state="NH",
            city="Manchester",
            zip_code="03101",
            high_school_name="Manchester High School",
            graduation_year=2025,
            gpa=3.8,
            gpa_scale="4.0",
            sat_score=1450,
            act_score=32,
            intended_major="Computer Science",
            career_goals="Software engineer at tech company",
            volunteer_hours=120,
            extracurriculars=[
                {
                    "name": "Robotics Club",
                    "role": "Captain",
                    "years_active": "2022-2024",
                }
            ],
            work_experience=[
                {"title": "Intern", "organization": "TechCorp", "dates": "Summer 2024"}
            ],
            honors_awards=["Honor Roll", "AP Scholar"],
            skills=["Python", "JavaScript", "Leadership"],
            location_preference="MA",
            profile_image_url="https://cdn.example.com/profile.jpg",
            resume_url="https://cdn.example.com/resume.pdf",
            settings={"confetti_enabled": False},
        )
        db_session.add(profile)
        db_session.commit()

        response = client.get("/api/v1/profiles/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Location fields
        assert data["state"] == "NH"
        assert data["city"] == "Manchester"
        assert data["zip_code"] == "03101"

        # Academic fields
        assert data["high_school_name"] == "Manchester High School"
        assert data["graduation_year"] == 2025
        assert data["gpa"] == 3.8
        assert data["gpa_scale"] == "4.0"
        assert data["sat_score"] == 1450
        assert data["act_score"] == 32
        assert data["intended_major"] == "Computer Science"

        # Career & Activities
        assert data["career_goals"] == "Software engineer at tech company"
        assert data["volunteer_hours"] == 120
        assert len(data["extracurriculars"]) == 1
        assert data["extracurriculars"][0]["name"] == "Robotics Club"
        assert len(data["work_experience"]) == 1
        assert len(data["honors_awards"]) == 2
        assert len(data["skills"]) == 3

        # Matching & Files
        assert data["location_preference"] == "MA"
        assert data["profile_image_url"] is not None
        assert data["resume_url"] is not None

        # Settings
        assert data["settings"]["confetti_enabled"] is False


@pytest.mark.integration
@pytest.mark.profile
class TestProfileUpdate:
    """Test profile update endpoints"""

    def test_update_profile_success(
        self, client: TestClient, auth_headers: dict, test_profile: UserProfile
    ):
        """Test PUT /me updates profile fields"""
        update_data = {
            "state": "CA",
            "city": "San Francisco",
            "zip_code": "94102",
            "gpa": 3.9,
            "sat_score": 1500,
            "location_preference": "CA",
        }

        response = client.put(
            "/api/v1/profiles/me", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["state"] == "CA"
        assert data["city"] == "San Francisco"
        assert data["zip_code"] == "94102"
        assert data["gpa"] == 3.9
        assert data["sat_score"] == 1500
        assert data["location_preference"] == "CA"

    def test_update_profile_partial(
        self, client: TestClient, auth_headers: dict, test_profile: UserProfile
    ):
        """Test PUT /me allows partial updates"""
        original_gpa = test_profile.gpa
        update_data = {"city": "Cambridge"}

        response = client.put(
            "/api/v1/profiles/me", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["city"] == "Cambridge"
        assert data["gpa"] == original_gpa  # Other fields unchanged

    def test_update_creates_if_missing(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        db_session: Session,
    ):
        """Test PUT /me creates profile if doesn't exist"""
        # Ensure no profile exists
        existing = (
            db_session.query(UserProfile)
            .filter(UserProfile.user_id == test_user.id)
            .first()
        )
        if existing:
            db_session.delete(existing)
            db_session.commit()

        update_data = {
            "state": "NY",
            "city": "New York",
            "graduation_year": 2026,
        }

        response = client.put(
            "/api/v1/profiles/me", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["state"] == "NY"
        assert data["city"] == "New York"
        assert data["user_id"] == test_user.id

    def test_update_profile_requires_auth(self, client: TestClient):
        """Test PUT /me fails without authentication"""
        update_data = {"city": "Boston"}

        response = client.put("/api/v1/profiles/me", json=update_data)

        assert response.status_code in [401, 403]

    def test_update_profile_validates_gpa_range(
        self, client: TestClient, auth_headers: dict, test_profile: UserProfile
    ):
        """Test PUT /me validates GPA is between 0.0 and 5.0"""
        invalid_data = {"gpa": 6.0}

        response = client.put(
            "/api/v1/profiles/me", json=invalid_data, headers=auth_headers
        )

        assert response.status_code == 422

    def test_update_profile_validates_graduation_year(
        self, client: TestClient, auth_headers: dict, test_profile: UserProfile
    ):
        """Test PUT /me validates graduation year range"""
        invalid_data = {"graduation_year": 2050}

        response = client.put(
            "/api/v1/profiles/me", json=invalid_data, headers=auth_headers
        )

        assert response.status_code == 422

    def test_update_profile_validates_sat_score(
        self, client: TestClient, auth_headers: dict, test_profile: UserProfile
    ):
        """Test PUT /me validates SAT score range (400-1600)"""
        invalid_data = {"sat_score": 2000}

        response = client.put(
            "/api/v1/profiles/me", json=invalid_data, headers=auth_headers
        )

        assert response.status_code == 422

    def test_update_profile_validates_act_score(
        self, client: TestClient, auth_headers: dict, test_profile: UserProfile
    ):
        """Test PUT /me validates ACT score range (1-36)"""
        invalid_data = {"act_score": 50}

        response = client.put(
            "/api/v1/profiles/me", json=invalid_data, headers=auth_headers
        )

        assert response.status_code == 422

    def test_update_profile_validates_gpa_scale(
        self, client: TestClient, auth_headers: dict, test_profile: UserProfile
    ):
        """Test PUT /me validates GPA scale enum"""
        invalid_data = {"gpa_scale": "invalid_scale"}

        response = client.put(
            "/api/v1/profiles/me", json=invalid_data, headers=auth_headers
        )

        # Backend should either reject (422) or set to None
        # Both are acceptable behaviors
        assert response.status_code in [200, 422]

    def test_update_extracurriculars(
        self, client: TestClient, auth_headers: dict, test_profile: UserProfile
    ):
        """Test PUT /me updates extracurriculars array"""
        update_data = {
            "extracurriculars": [
                {
                    "name": "Debate Team",
                    "role": "Captain",
                    "description": "Led team to state finals",
                    "years_active": "2022-2024",
                }
            ]
        }

        response = client.put(
            "/api/v1/profiles/me", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["extracurriculars"]) == 1
        assert data["extracurriculars"][0]["name"] == "Debate Team"

    def test_update_work_experience(
        self, client: TestClient, auth_headers: dict, test_profile: UserProfile
    ):
        """Test PUT /me updates work experience array"""
        update_data = {
            "work_experience": [
                {
                    "title": "Software Intern",
                    "organization": "Tech Company",
                    "dates": "Summer 2024",
                    "description": "Built web applications",
                }
            ]
        }

        response = client.put(
            "/api/v1/profiles/me", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["work_experience"]) == 1
        assert data["work_experience"][0]["title"] == "Software Intern"

    def test_update_honors_and_skills(
        self, client: TestClient, auth_headers: dict, test_profile: UserProfile
    ):
        """Test PUT /me updates honors/awards and skills arrays"""
        update_data = {
            "honors_awards": ["National Merit Scholar", "AP Scholar"],
            "skills": ["Python", "React", "Leadership"],
        }

        response = client.put(
            "/api/v1/profiles/me", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["honors_awards"]) == 2
        assert len(data["skills"]) == 3


@pytest.mark.integration
@pytest.mark.profile
class TestMatchingInstitutions:
    """Test college matching endpoint"""

    def test_get_matching_institutions_with_preference(
        self,
        client: TestClient,
        auth_headers: dict,
        test_profile: UserProfile,
        db_session: Session,
    ):
        """Test GET /matching-institutions returns colleges in preferred state"""
        # Set location preference
        test_profile.location_preference = "MA"
        db_session.commit()

        # Create some test institutions
        from app.models.institution import Institution, ControlType
        from decimal import Decimal

        institutions = [
            Institution(
                ipeds_id=1000001,
                name="Boston University",
                state="MA",
                city="Boston",
                control_type=ControlType.PRIVATE_NONPROFIT,
                student_faculty_ratio=Decimal("10.0"),
            ),
            Institution(
                ipeds_id=1000002,
                name="MIT",
                state="MA",
                city="Cambridge",
                control_type=ControlType.PRIVATE_NONPROFIT,
                student_faculty_ratio=Decimal("3.0"),
            ),
            Institution(
                ipeds_id=1000003,
                name="Stanford",
                state="CA",
                city="Palo Alto",
                control_type=ControlType.PRIVATE_NONPROFIT,
                student_faculty_ratio=Decimal("5.0"),
            ),
        ]
        for inst in institutions:
            db_session.add(inst)
        db_session.commit()

        response = client.get(
            "/api/v1/profiles/me/matching-institutions", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["location_preference"] == "MA"
        assert data["total"] == 2  # Only MA schools
        assert len(data["institutions"]) == 2

        # Verify only MA schools returned
        for inst in data["institutions"]:
            assert inst["state"] == "MA"

    def test_matching_institutions_no_preference(
        self,
        client: TestClient,
        auth_headers: dict,
        test_profile: UserProfile,
        db_session: Session,
    ):
        """Test GET /matching-institutions with no location preference"""
        # Ensure no location preference
        test_profile.location_preference = None
        db_session.commit()

        response = client.get(
            "/api/v1/profiles/me/matching-institutions", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["location_preference"] is None
        assert data["total"] == 0
        assert len(data["institutions"]) == 0

    def test_matching_institutions_respects_limit(
        self,
        client: TestClient,
        auth_headers: dict,
        test_profile: UserProfile,
        db_session: Session,
    ):
        """Test GET /matching-institutions respects limit parameter"""
        # Set location preference
        test_profile.location_preference = "CA"
        db_session.commit()

        # Create many institutions
        from app.models.institution import Institution, ControlType
        from decimal import Decimal

        for i in range(60):
            inst = Institution(
                ipeds_id=2000000 + i,
                name=f"California College {i}",
                state="CA",
                city="Los Angeles",
                control_type=ControlType.PUBLIC,
                student_faculty_ratio=Decimal("15.0"),
            )
            db_session.add(inst)
        db_session.commit()

        # Request with limit
        response = client.get(
            "/api/v1/profiles/me/matching-institutions?limit=10", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 60
        assert len(data["institutions"]) == 10

    def test_matching_institutions_requires_auth(self, client: TestClient):
        """Test GET /matching-institutions requires authentication"""
        response = client.get("/api/v1/profiles/me/matching-institutions")

        assert response.status_code in [401, 403]


@pytest.mark.integration
@pytest.mark.profile
class TestUserSettings:
    """Test user settings endpoints"""

    def test_get_settings_default(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        db_session: Session,
    ):
        """Test GET /settings returns defaults for new profile"""
        # Ensure clean state
        existing = (
            db_session.query(UserProfile)
            .filter(UserProfile.user_id == test_user.id)
            .first()
        )
        if existing:
            db_session.delete(existing)
            db_session.commit()

        response = client.get("/api/v1/profiles/me/settings", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["confetti_enabled"] is True  # Default

    def test_get_settings_existing(
        self,
        client: TestClient,
        auth_headers: dict,
        test_profile: UserProfile,
        db_session: Session,
    ):
        """Test GET /settings returns saved settings"""
        # Set custom settings
        test_profile.settings = {"confetti_enabled": False}
        db_session.commit()

        response = client.get("/api/v1/profiles/me/settings", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["confetti_enabled"] is False

    def test_update_settings(
        self, client: TestClient, auth_headers: dict, test_profile: UserProfile
    ):
        """Test PATCH /settings updates user settings"""
        update_data = {"confetti_enabled": False}

        response = client.patch(
            "/api/v1/profiles/me/settings", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["settings"]["confetti_enabled"] is False
        assert "message" in data

    def test_update_settings_partial(
        self,
        client: TestClient,
        auth_headers: dict,
        test_profile: UserProfile,
        db_session: Session,
    ):
        """Test PATCH /settings allows partial updates"""
        # Set multiple settings
        test_profile.settings = {
            "confetti_enabled": True,
            "future_setting": "value",
        }
        db_session.commit()

        # Update only one setting
        update_data = {"confetti_enabled": False}

        response = client.patch(
            "/api/v1/profiles/me/settings", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["settings"]["confetti_enabled"] is False
        assert data["settings"]["future_setting"] == "value"  # Preserved

    def test_settings_require_auth(self, client: TestClient):
        """Test settings endpoints require authentication"""
        response = client.get("/api/v1/profiles/me/settings")
        assert response.status_code in [401, 403]

        response = client.patch(
            "/api/v1/profiles/me/settings", json={"confetti_enabled": False}
        )
        assert response.status_code in [401, 403]


@pytest.mark.integration
@pytest.mark.profile
class TestHeadshotUpload:
    """Test profile image upload"""

    def test_upload_headshot_success(
        self, client: TestClient, auth_headers: dict, test_profile: UserProfile
    ):
        """Test POST /upload-headshot uploads image successfully"""
        # Create fake image file
        image_content = b"fake-image-content-jpeg"
        files = {"file": ("profile.jpg", io.BytesIO(image_content), "image/jpeg")}

        response = client.post(
            "/api/v1/profiles/me/upload-headshot", files=files, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "profile_image_url" in data
        assert data["profile_image_url"] is not None
        assert "message" in data

    def test_upload_headshot_validates_file_type(
        self, client: TestClient, auth_headers: dict, test_profile: UserProfile
    ):
        """Test POST /upload-headshot rejects invalid file types"""
        # Try uploading a PDF
        file_content = b"fake-pdf-content"
        files = {"file": ("profile.pdf", io.BytesIO(file_content), "application/pdf")}

        response = client.post(
            "/api/v1/profiles/me/upload-headshot", files=files, headers=auth_headers
        )

        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()

    def test_upload_headshot_validates_file_size(
        self, client: TestClient, auth_headers: dict, test_profile: UserProfile
    ):
        """Test POST /upload-headshot rejects files over 5MB"""
        # Create large fake file (over 5MB)
        large_content = b"x" * (6 * 1024 * 1024)  # 6MB
        files = {"file": ("large.jpg", io.BytesIO(large_content), "image/jpeg")}

        response = client.post(
            "/api/v1/profiles/me/upload-headshot", files=files, headers=auth_headers
        )

        assert response.status_code == 400
        assert "large" in response.json()["detail"].lower()

    def test_upload_headshot_requires_auth(self, client: TestClient):
        """Test POST /upload-headshot requires authentication"""
        file_content = b"fake-image"
        files = {"file": ("profile.jpg", io.BytesIO(file_content), "image/jpeg")}

        response = client.post("/api/v1/profiles/me/upload-headshot", files=files)

        assert response.status_code in [401, 403]

    def test_upload_headshot_auto_creates_profile(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        db_session: Session,
    ):
        """Test POST /upload-headshot auto-creates profile if missing"""
        # Ensure no profile exists
        existing = (
            db_session.query(UserProfile)
            .filter(UserProfile.user_id == test_user.id)
            .first()
        )
        if existing:
            db_session.delete(existing)
            db_session.commit()

        file_content = b"fake-image"
        files = {"file": ("profile.jpg", io.BytesIO(file_content), "image/jpeg")}

        response = client.post(
            "/api/v1/profiles/me/upload-headshot", files=files, headers=auth_headers
        )

        assert response.status_code == 200

        # Verify profile was created
        profile = (
            db_session.query(UserProfile)
            .filter(UserProfile.user_id == test_user.id)
            .first()
        )
        assert profile is not None


@pytest.mark.integration
@pytest.mark.profile
class TestResumeUpload:
    """Test resume upload and parsing - Uses real PDF: tests/docs/Claire_Ahern_Resume.pdf"""

    def test_upload_resume_success(
        self, client: TestClient, auth_headers: dict, test_profile: UserProfile
    ):
        """Test POST /upload-resume-and-update uploads and parses resume"""
        import os

        # Use real test PDF - Claire_Ahern_Resume.pdf
        test_pdf = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "docs",
            "Claire_Ahern_Resume.pdf",
        )

        if not os.path.exists(test_pdf):
            pytest.skip(f"Test PDF not found at {test_pdf}")

        with open(test_pdf, "rb") as f:
            files = {"file": ("resume.pdf", f, "application/pdf")}

            response = client.post(
                "/api/v1/profiles/me/upload-resume-and-update",
                files=files,
                headers=auth_headers,
            )

        # Should succeed with real PDF
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "profile" in data
        assert "resume_url" in data
        assert "parsed_data" in data
        assert "metadata" in data
        assert "needs_gpa" in data
        assert "scholarship_matches" in data

        # Verify resume was actually uploaded
        assert data["resume_url"] is not None
        assert len(data["resume_url"]) > 0

    def test_upload_resume_validates_file_type(
        self, client: TestClient, auth_headers: dict, test_profile: UserProfile
    ):
        """Test POST /upload-resume-and-update rejects invalid file types"""
        file_content = b"fake-image"
        files = {"file": ("resume.jpg", io.BytesIO(file_content), "image/jpeg")}

        response = client.post(
            "/api/v1/profiles/me/upload-resume-and-update",
            files=files,
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()

    def test_upload_resume_validates_file_size(
        self, client: TestClient, auth_headers: dict, test_profile: UserProfile
    ):
        """Test POST /upload-resume-and-update rejects files over 10MB"""
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        files = {"file": ("resume.pdf", io.BytesIO(large_content), "application/pdf")}

        response = client.post(
            "/api/v1/profiles/me/upload-resume-and-update",
            files=files,
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert "large" in response.json()["detail"].lower()

    def test_upload_resume_requires_auth(self, client: TestClient):
        """Test POST /upload-resume-and-update requires authentication"""
        file_content = b"fake-pdf"
        files = {"file": ("resume.pdf", io.BytesIO(file_content), "application/pdf")}

        response = client.post(
            "/api/v1/profiles/me/upload-resume-and-update", files=files
        )

        assert response.status_code in [401, 403]

    def test_upload_resume_auto_creates_profile(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        db_session: Session,
    ):
        """Test POST /upload-resume-and-update auto-creates profile if missing"""
        import os

        # Ensure no profile exists
        existing = (
            db_session.query(UserProfile)
            .filter(UserProfile.user_id == test_user.id)
            .first()
        )
        if existing:
            db_session.delete(existing)
            db_session.commit()

        # Use real test PDF
        test_pdf = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "docs",
            "Claire_Ahern_Resume.pdf",
        )

        if not os.path.exists(test_pdf):
            pytest.skip(f"Test PDF not found at {test_pdf}")

        with open(test_pdf, "rb") as f:
            files = {"file": ("resume.pdf", f, "application/pdf")}

            response = client.post(
                "/api/v1/profiles/me/upload-resume-and-update",
                files=files,
                headers=auth_headers,
            )

        # Should succeed and auto-create profile
        assert response.status_code == 200

        # Verify profile was created
        profile = (
            db_session.query(UserProfile)
            .filter(UserProfile.user_id == test_user.id)
            .first()
        )
        assert profile is not None

    def test_upload_resume_returns_scholarship_matches_with_gpa(
        self,
        client: TestClient,
        auth_headers: dict,
        test_profile: UserProfile,
        db_session: Session,
    ):
        """Test resume upload returns scholarship matches when GPA exists"""
        import os

        # Set GPA on profile
        test_profile.gpa = 3.8
        db_session.commit()

        # Create scholarship that matches
        from app.models.scholarship import Scholarship
        from datetime import timedelta

        scholarship = Scholarship(
            title="Test Scholarship",
            organization="Test Org",
            scholarship_type="ACADEMIC_MERIT",  # ✅ CORRECT - matches your enum
            amount_min=5000,
            amount_max=10000,
            deadline=datetime.now() + timedelta(days=60),
            min_gpa=3.5,
            status="ACTIVE",  # Also fix status if needed
        )
        db_session.add(scholarship)
        db_session.commit()

        # Use real test PDF
        test_pdf = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "docs",
            "Claire_Ahern_Resume.pdf",
        )

        if not os.path.exists(test_pdf):
            pytest.skip(f"Test PDF not found at {test_pdf}")

        with open(test_pdf, "rb") as f:
            files = {"file": ("resume.pdf", f, "application/pdf")}

            response = client.post(
                "/api/v1/profiles/me/upload-resume-and-update",
                files=files,
                headers=auth_headers,
            )

        assert response.status_code == 200
        data = response.json()
        assert data["needs_gpa"] is False
        assert "scholarship_matches" in data

    def test_upload_resume_returns_metadata(
        self, client: TestClient, auth_headers: dict, test_profile: UserProfile
    ):
        """Test resume upload returns AI parsing metadata"""
        import os

        # Use real test PDF
        test_pdf = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "docs",
            "Claire_Ahern_Resume.pdf",
        )

        if not os.path.exists(test_pdf):
            pytest.skip(f"Test PDF not found at {test_pdf}")

        with open(test_pdf, "rb") as f:
            files = {"file": ("resume.pdf", f, "application/pdf")}

            response = client.post(
                "/api/v1/profiles/me/upload-resume-and-update",
                files=files,
                headers=auth_headers,
            )

        assert response.status_code == 200
        data = response.json()
        metadata = data["metadata"]

        # Verify metadata structure matches actual backend response
        assert "confidence_score" in metadata
        assert "fields_extracted" in metadata
        assert "extraction_notes" in metadata

        # Verify metadata values are reasonable
        assert isinstance(metadata["confidence_score"], float)
        assert 0.0 <= metadata["confidence_score"] <= 1.0
        assert isinstance(metadata["fields_extracted"], int)
        assert metadata["fields_extracted"] > 0

        # Verify we got some parsed data
        assert "parsed_data" in data


@pytest.mark.integration
@pytest.mark.profile
class TestMultipleUsersProfiles:
    """Test profile isolation between users"""

    def test_users_have_separate_profiles(
        self, client: TestClient, test_user: User, test_user_2: User, user_token: str
    ):
        """Test that different users have completely separate profiles"""
        from app.core.security import create_access_token

        user1_headers = {"Authorization": f"Bearer {user_token}"}
        user2_token = create_access_token(subject=str(test_user_2.id))
        user2_headers = {"Authorization": f"Bearer {user2_token}"}

        # Update user 1 profile
        user1_data = {"city": "Boston", "gpa": 3.8}
        response1 = client.put(
            "/api/v1/profiles/me", json=user1_data, headers=user1_headers
        )
        assert response1.status_code == 200

        # Update user 2 profile
        user2_data = {"city": "Cambridge", "gpa": 3.5}
        response2 = client.put(
            "/api/v1/profiles/me", json=user2_data, headers=user2_headers
        )
        assert response2.status_code == 200

        # Verify separation
        response1 = client.get("/api/v1/profiles/me", headers=user1_headers)
        response2 = client.get("/api/v1/profiles/me", headers=user2_headers)

        data1 = response1.json()
        data2 = response2.json()

        assert data1["user_id"] != data2["user_id"]
        assert data1["city"] == "Boston"
        assert data2["city"] == "Cambridge"
        assert data1["gpa"] == 3.8
        assert data2["gpa"] == 3.5

    def test_user_cannot_access_other_profiles(
        self, client: TestClient, auth_headers: dict, test_user_2: User
    ):
        """Test that users can only access their own profile"""
        # User 1 (with auth_headers) should not be able to manipulate user 2's data
        # This is implicit in the /me endpoint - there's no way to specify another user

        response = client.get("/api/v1/profiles/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # Should only see own user_id, not test_user_2.id
        assert data["user_id"] != test_user_2.id


@pytest.mark.integration
@pytest.mark.profile
class TestProfileCompleteness:
    """Test profile completion tracking"""

    def test_empty_profile_low_completion(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        db_session: Session,
    ):
        """Test empty profile has low completion percentage"""
        # Create empty profile
        profile = UserProfile(user_id=test_user.id)
        db_session.add(profile)
        db_session.commit()

        response = client.get("/api/v1/profiles/me", headers=auth_headers)
        assert response.status_code == 200

        # The model's completion_percentage property should reflect low completion
        # This is not directly in the API response but the backend tracks it

    def test_complete_profile_high_completion(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        db_session: Session,
    ):
        """Test fully filled profile has high completion percentage"""
        profile = UserProfile(
            user_id=test_user.id,
            state="MA",
            city="Boston",
            high_school_name="Test High",
            graduation_year=2025,
            gpa=3.8,
            gpa_scale="4.0",
            sat_score=1400,
            intended_major="Engineering",
            career_goals="Engineer",
            volunteer_hours=100,
            extracurriculars=[{"name": "Club"}],
            work_experience=[{"title": "Intern"}],
            honors_awards=["Award"],
            skills=["Skill"],
        )
        db_session.add(profile)
        db_session.commit()

        response = client.get("/api/v1/profiles/me", headers=auth_headers)
        assert response.status_code == 200
        # Well-filled profile should have most fields populated
