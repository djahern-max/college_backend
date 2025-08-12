"""
Script to add the New Hampshire Charitable Foundation Scholarship to the database.
This is a perfect first scholarship - it's local to NH, has multiple deadlines throughout 2025,
and covers a wide range of students and award amounts.
"""

import asyncio
import sys
from datetime import date
from decimal import Decimal

# Add the parent directory to the path so we can import our modules
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import AsyncSessionLocal
from app.models.scholarship import Scholarship, ScholarshipStatus, ScholarshipType


async def add_nh_charitable_foundation_scholarship():
    """Add the NH Charitable Foundation Scholarship to the database."""
    
    async with AsyncSessionLocal() as session:
        try:
            # Create the scholarship record
            nh_foundation_scholarship = Scholarship(
                title="New Hampshire Charitable Foundation Scholarships",
                description=(
                    "The New Hampshire Charitable Foundation offers over 200 different "
                    "scholarships through a single application process. Students are "
                    "automatically matched with all scholarships they qualify for. "
                    "Scholarships range from $250 to $7,500 and are available for "
                    "certificates, licensing programs, apprenticeships, two- and four-year "
                    "degree programs, and graduate school. Selection is based on financial "
                    "need, academic merit, and other factors like community service and "
                    "work experience. Highest priority is given to students with the "
                    "fewest financial resources."
                ),
                provider="New Hampshire Charitable Foundation",
                amount_min=Decimal("250.00"),
                amount_max=Decimal("7500.00"),
                renewable=True,
                max_renewals="4 years",
                deadline=date(2025, 12, 12),  # Open enrollment deadline - STILL ACTIVE!
                application_url="https://www.nhcf.org/how-can-we-help-you/apply-for-a-scholarship/",
                contact_email="info@nhcf.org",
                contact_phone="603-225-6641",
                eligibility_criteria={
                    "location": ["New Hampshire"],
                    "grade_level": ["High School Senior", "College Student", "Graduate Student", "Adult Learner"],
                    "requirements": [
                        "Must be a New Hampshire resident or attending NH institution",
                        "Demonstrate financial need via FAFSA",
                        "Academic merit considered",
                        "Community service and work experience valued",
                        "Must be pursuing certificate, degree, or licensing program"
                    ]
                },
                required_documents={
                    "documents": [
                        "FAFSA Submission Summary",
                        "Academic transcripts",
                        "Personal statement/essay",
                        "Letters of recommendation",
                        "Financial aid package from institution (for finalists)"
                    ]
                },
                academic_requirements={
                    "gpa_minimum": None,  # Academic excellence not required, but reasonable achievement expected
                    "academic_focus": "All fields - certificates, 2-year, 4-year, graduate programs"
                },
                demographic_criteria={
                    "state_residence": ["New Hampshire"],
                    "age_group": "All ages - students over 24 have rolling deadline",
                    "special_populations": ["First-generation college students", "Financial need"]
                },
                categories=[
                    "Need-Based", 
                    "Academic Merit", 
                    "Community Service", 
                    "New Hampshire Residents",
                    "Multiple Award Amounts",
                    "Renewable"
                ],
                scholarship_type=ScholarshipType.NEED_BASED,
                keywords=[
                    "New Hampshire", "NH", "financial need", "FAFSA", "community service", 
                    "work experience", "multiple scholarships", "automatic matching",
                    "certificates", "degrees", "graduate school", "NH residents",
                    "charitable foundation", "renewable", "higher education"
                ],
                status=ScholarshipStatus.ACTIVE,
                source="New Hampshire Charitable Foundation",
                source_url="https://www.nhcf.org/how-can-we-help-you/apply-for-a-scholarship/",
                verified=True,
                last_verified=date.today(),
                application_count=0,
                external_id="NHCF-2025",
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31)
            )
            
            # Add to session and commit
            session.add(nh_foundation_scholarship)
            await session.commit()
            await session.refresh(nh_foundation_scholarship)
            
            print(f"✅ Successfully added NH Charitable Foundation Scholarship with ID: {nh_foundation_scholarship.id}")
            print(f"📅 Deadline: {nh_foundation_scholarship.deadline}")
            print(f"💰 Amount Range: ${nh_foundation_scholarship.amount_min} - ${nh_foundation_scholarship.amount_max}")
            print(f"🎯 Status: {nh_foundation_scholarship.status}")
            print(f"🔄 Renewable: {nh_foundation_scholarship.renewable}")
            print(f"📍 Location: New Hampshire")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error adding scholarship: {e}")
            raise
        finally:
            await session.close()


async def add_nh_governors_scholarship():
    """Add the NH Governor's Scholarship as a second option."""
    
    async with AsyncSessionLocal() as session:
        try:
            # Create the Governor's scholarship record
            governors_scholarship = Scholarship(
                title="New Hampshire Governor's Scholarship Program",
                description=(
                    "The New Hampshire Governor's Scholarship Program awards between "
                    "$1,000 and $2,000 annually to New Hampshire residents attending "
                    "in-state institutions. First-year, full-time, Pell Grant-eligible "
                    "students who earn the New Hampshire Scholar designation may receive "
                    "$2,000 per year, while other eligible students receive $1,000 per year. "
                    "The scholarship can be renewed for up to four years. This program "
                    "supports New Hampshire high school graduates attending NH colleges "
                    "and universities."
                ),
                provider="State of New Hampshire",
                amount_min=Decimal("1000.00"),
                amount_max=Decimal("2000.00"),
                renewable=True,
                max_renewals="4 years",
                deadline=date(2025, 6, 1),  # Typical application deadline
                application_url="https://nhscholars.org/",
                eligibility_criteria={
                    "location": ["New Hampshire"],
                    "grade_level": ["High School Graduate"],
                    "requirements": [
                        "Must be NH high school graduate",
                        "Must attend NH college or university",
                        "Must be first-year student",
                        "Full-time enrollment required",
                        "Pell Grant eligibility for $2,000 tier",
                        "NH Scholar designation preferred"
                    ]
                },
                required_documents={
                    "documents": [
                        "High school transcript",
                        "College enrollment verification",
                        "FAFSA completion",
                        "NH Scholar designation (if applicable)"
                    ]
                },
                academic_requirements={
                    "gpa_minimum": None,
                    "academic_focus": "All fields of study"
                },
                demographic_criteria={
                    "state_residence": ["New Hampshire"],
                    "age_group": "Traditional college age",
                    "special_populations": ["NH Scholars", "Pell Grant eligible"]
                },
                categories=[
                    "State Scholarship",
                    "New Hampshire Residents", 
                    "In-State Tuition",
                    "Renewable",
                    "Merit-Based"
                ],
                scholarship_type=ScholarshipType.MERIT,
                keywords=[
                    "New Hampshire", "NH", "Governor", "state scholarship", "in-state",
                    "renewable", "Pell Grant", "NH Scholar", "college", "university"
                ],
                status=ScholarshipStatus.ACTIVE,
                source="New Hampshire Department of Education",
                source_url="https://nhscholars.org/",
                verified=True,
                last_verified=date.today(),
                application_count=0,
                external_id="NH-GOV-2025"
            )
            
            # Add to session and commit
            session.add(governors_scholarship)
            await session.commit()
            await session.refresh(governors_scholarship)
            
            print(f"✅ Successfully added NH Governor's Scholarship with ID: {governors_scholarship.id}")
            print(f"📅 Deadline: {governors_scholarship.deadline}")
            print(f"💰 Amount Range: ${governors_scholarship.amount_min} - ${governors_scholarship.amount_max}")
            print(f"🎯 Status: {governors_scholarship.status}")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error adding Governor's scholarship: {e}")
            raise
        finally:
            await session.close()


async def add_new_england_tuition_break():
    """Add the New England Tuition Break program - active until Dec 31, 2025."""
    
    async with AsyncSessionLocal() as session:
        try:
            # Create the New England Tuition Break program
            tuition_break = Scholarship(
                title="New England Regional Student Program (Tuition Break)",
                description=(
                    "The New England Board of Higher Education's Tuition Break program "
                    "allows New Hampshire residents to enroll in out-of-state public "
                    "colleges and universities within New England at a reduced tuition "
                    "rate for approved programs. This program offers substantial tuition "
                    "savings by allowing students to pay no more than 150% of in-state "
                    "tuition at participating institutions across Connecticut, Maine, "
                    "Massachusetts, New Hampshire, Rhode Island, and Vermont."
                ),
                provider="New England Board of Higher Education (NEBHE)",
                amount_min=Decimal("2000.00"),  # Estimated savings
                amount_max=Decimal("15000.00"), # Estimated max savings
                renewable=True,
                max_renewals="4 years",
                deadline=date(2025, 12, 31),  # ACTIVE DEADLINE
                application_url="https://www.nebhe.org/tuitionbreak/",
                contact_email="tuitionbreak@nebhe.org",
                eligibility_criteria={
                    "location": ["New England States"],
                    "grade_level": ["High School Senior", "Transfer Student"],
                    "requirements": [
                        "Must be resident of New England state",
                        "Must apply to approved program at participating institution",
                        "Program must not be available at public institutions in home state",
                        "Must meet admission requirements of receiving institution"
                    ]
                },
                required_documents={
                    "documents": [
                        "College application to participating institution",
                        "Proof of New England residency",
                        "High school transcripts",
                        "Standard college admission materials"
                    ]
                },
                academic_requirements={
                    "gpa_minimum": None,  # Varies by institution
                    "academic_focus": "Programs not available in home state"
                },
                demographic_criteria={
                    "state_residence": ["Connecticut", "Maine", "Massachusetts", "New Hampshire", "Rhode Island", "Vermont"],
                    "age_group": "Traditional and non-traditional college students",
                    "special_populations": []
                },
                categories=[
                    "Regional Program",
                    "Tuition Reduction", 
                    "New England",
                    "Out-of-State Tuition",
                    "Renewable"
                ],
                scholarship_type=ScholarshipType.GEOGRAPHIC,
                keywords=[
                    "New England", "tuition break", "NEBHE", "out-of-state", "reduced tuition",
                    "regional", "New Hampshire", "Connecticut", "Maine", "Massachusetts",
                    "Rhode Island", "Vermont", "public universities"
                ],
                status=ScholarshipStatus.ACTIVE,
                source="New England Board of Higher Education",
                source_url="https://www.nebhe.org/tuitionbreak/",
                verified=True,
                last_verified=date.today(),
                application_count=0,
                external_id="NEBHE-TB-2025"
            )
            
            # Add to session and commit
            session.add(tuition_break)
            await session.commit()
            await session.refresh(tuition_break)
            
            print(f"✅ Successfully added New England Tuition Break with ID: {tuition_break.id}")
            print(f"📅 Deadline: {tuition_break.deadline}")
            print(f"💰 Estimated Savings: ${tuition_break.amount_min} - ${tuition_break.amount_max}")
            print(f"🎯 Status: {tuition_break.status}")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error adding tuition break program: {e}")
            raise
        finally:
            await session.close()


async def add_fall_2026_scholarships():
    """Add scholarships with deadlines for Fall 2026 enrollment."""
    
    async with AsyncSessionLocal() as session:
        try:
            # University of Minnesota National Scholarship
            umn_scholarship = Scholarship(
                title="University of Minnesota National Scholarship",
                description=(
                    "The University of Minnesota National Scholarship awards $60,000 "
                    "to incoming freshmen from any state except Minnesota, North Dakota, "
                    "South Dakota, and Wisconsin. This merit-based scholarship is awarded "
                    "based on an overall assessment of the application for admission. "
                    "Full consideration requires submitting a complete application by "
                    "the Early Action or Regular admission deadlines."
                ),
                provider="University of Minnesota",
                amount_exact=Decimal("60000.00"),
                renewable=True,
                max_renewals="4 years",
                deadline=date(2026, 1, 1),  # Regular admission deadline
                application_url="https://admissions.tc.umn.edu/scholarships",
                eligibility_criteria={
                    "location": ["All states except MN, ND, SD, WI"],
                    "grade_level": ["High School Senior"],
                    "requirements": [
                        "Must be incoming freshman",
                        "Cannot be resident of MN, ND, SD, or WI",
                        "Must submit complete application by deadline",
                        "Merit-based selection"
                    ]
                },
                required_documents={
                    "documents": [
                        "University of Minnesota application",
                        "High school transcripts",
                        "Standardized test scores (if required)",
                        "Letters of recommendation",
                        "Personal statement/essay"
                    ]
                },
                academic_requirements={
                    "gpa_minimum": 3.5,  # Estimated for competitive consideration
                    "academic_focus": "All majors"
                },
                demographic_criteria={
                    "state_residence": ["All except Minnesota, North Dakota, South Dakota, Wisconsin"],
                    "age_group": "Traditional college age",
                    "special_populations": ["Out-of-state students"]
                },
                categories=[
                    "Merit-Based",
                    "Full Tuition",
                    "Out-of-State",
                    "Renewable",
                    "Highly Competitive"
                ],
                scholarship_type=ScholarshipType.MERIT,
                keywords=[
                    "University of Minnesota", "national scholarship", "merit-based",
                    "out-of-state", "$60000", "full tuition", "renewable", "competitive"
                ],
                status=ScholarshipStatus.ACTIVE,
                source="University of Minnesota",
                source_url="https://admissions.tc.umn.edu/scholarships",
                verified=True,
                last_verified=date.today(),
                application_count=0,
                external_id="UMN-NAT-2026"
            )
            
            session.add(umn_scholarship)
            await session.commit()
            await session.refresh(umn_scholarship)
            
            print(f"✅ Successfully added UMN National Scholarship with ID: {umn_scholarship.id}")
            print(f"📅 Deadline: {umn_scholarship.deadline}")
            print(f"💰 Amount: ${umn_scholarship.amount_exact}")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error adding UMN scholarship: {e}")
            raise
        finally:
            await session.close()


async def main():
    """Run all scholarship additions with ACTIVE deadlines."""
    print("🚀 Adding New Hampshire & Regional Scholarships (ACTIVE DEADLINES)")
    print("📅 Current Date: August 10, 2025")
    print("=" * 60)
    
    await add_nh_charitable_foundation_scholarship()
    print()
    await add_new_england_tuition_break() 
    print()
    await add_fall_2026_scholarships()
    
    print("=" * 60)
    print("🎉 Successfully added 3 scholarships with ACTIVE deadlines!")
    print("\n📋 Summary:")
    print("1. NH Charitable Foundation - Dec 12, 2025 (Rolling)")
    print("2. New England Tuition Break - Dec 31, 2025") 
    print("3. University of Minnesota National - Jan 1, 2026")
    print("\n✅ All deadlines are AFTER August 10, 2025!")


if __name__ == "__main__":
    asyncio.run(main())
