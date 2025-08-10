"""
Script to add the Fisher Cats Foundation Scholar-Athlete Scholarship to the database.
Run this from your FastAPI project root directory.
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


async def add_fisher_cats_scholarship():
    """Add the Fisher Cats Foundation Scholar-Athlete Scholarship to the database."""
    
    async with AsyncSessionLocal() as session:
        try:
            # Create the scholarship record
            fisher_cats_scholarship = Scholarship(
                title="Fisher Cats Foundation Scholar-Athlete Scholarship",
                description=(
                    "The Fisher Cats Foundation annually awards $1,500 scholarships to 15 "
                    "college-bound high school seniors from New Hampshire. Recipients are "
                    "selected based on academic achievement, athletic achievement, and active "
                    "citizenship. Students must submit a Statement of Commitment from a school "
                    "counselor, contact info for two references, and a 2-3 minute video "
                    "answering 'How has participation in high school athletics shaped your life?'"
                ),
                provider="Fisher Cats Foundation",
                amount_exact=Decimal("1500.00"),
                renewable=False,
                deadline=date(2025, 4, 18),
                application_url="https://www.milb.com/new-hampshire/community/scholar-athlete-scholarships",
                contact_email="sfournier@nhfishercats.com",  # Fisher Cats Foundation Executive Director
                eligibility_criteria={
                    "location": ["New Hampshire"],
                    "grade_level": ["High School Senior"],
                    "requirements": [
                        "Must be a New Hampshire high school senior",
                        "Must participate in athletics",
                        "Must demonstrate academic achievement",
                        "Must demonstrate athletic achievement", 
                        "Must demonstrate active citizenship",
                        "Must be college-bound"
                    ]
                },
                required_documents={
                    "documents": [
                        "Statement of Commitment (Academic) from school counselor",
                        "Contact information for two references",
                        "2-3 minute video answering: 'How has participation in high school athletics shaped your life?'"
                    ]
                },
                academic_requirements={
                    "gpa_minimum": None,  # Not specified in the requirements
                    "academic_focus": "General - all academic fields accepted"
                },
                demographic_criteria={
                    "state_residence": ["New Hampshire"],
                    "age_group": "High School Senior",
                    "special_populations": []
                },
                categories=["Athletic", "Academic Merit", "Community Service", "High School Senior"],
                scholarship_type=ScholarshipType.MERIT,
                keywords=["athletics", "sports", "New Hampshire", "high school", "Fisher Cats", 
                         "baseball", "community service", "citizenship", "student athlete"],
                status=ScholarshipStatus.ACTIVE,
                source="Fisher Cats Foundation",
                source_url="https://www.milb.com/new-hampshire/community/scholar-athlete-scholarships",
                verified=True,
                last_verified=date.today(),
                application_count=0
            )
            
            # Add to session and commit
            session.add(fisher_cats_scholarship)
            await session.commit()
            await session.refresh(fisher_cats_scholarship)
            
            print(f"✅ Successfully added Fisher Cats Scholarship with ID: {fisher_cats_scholarship.id}")
            print(f"📅 Deadline: {fisher_cats_scholarship.deadline}")
            print(f"💰 Amount: ${fisher_cats_scholarship.amount_exact}")
            print(f"🎯 Status: {fisher_cats_scholarship.status}")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error adding scholarship: {e}")
            raise
        finally:
            await session.close()


async def verify_scholarship_added():
    """Verify the scholarship was added successfully."""
    
    async with AsyncSessionLocal() as session:
        try:
            # Query for the Fisher Cats scholarship
            result = await session.execute(
                """
                SELECT id, title, provider, amount_exact, deadline, status 
                FROM scholarships 
                WHERE title LIKE '%Fisher Cats%'
                """
            )
            
            scholarship = result.fetchone()
            if scholarship:
                print("\n✅ Scholarship verification:")
                print(f"   ID: {scholarship[0]}")
                print(f"   Title: {scholarship[1]}")
                print(f"   Provider: {scholarship[2]}")
                print(f"   Amount: ${scholarship[3]}")
                print(f"   Deadline: {scholarship[4]}")
                print(f"   Status: {scholarship[5]}")
            else:
                print("❌ Scholarship not found!")
                
        except Exception as e:
            print(f"❌ Error verifying scholarship: {e}")
        finally:
            await session.close()


if __name__ == "__main__":
    print("🏟️ Adding Fisher Cats Foundation Scholar-Athlete Scholarship...")
    
    # Run the async function
    asyncio.run(add_fisher_cats_scholarship())
    
    print("\n🔍 Verifying scholarship was added...")
    asyncio.run(verify_scholarship_added())
    
    print("\n🎉 Done! You can now use this scholarship in your application.")
    print("\nNext steps:")
    print("1. Test the scholarship endpoint: GET /api/v1/scholarships/")
    print("2. Start building the application form features")
    print("3. Add user profile fields for academic/athletic achievements")