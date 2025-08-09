import asyncio
import sys
from pathlib import Path
from datetime import date

sys.path.append(str(Path(__file__).parent.parent))

from app.db.database import get_db
from app.services.scholarship import ScholarshipService
from app.schemas.scholarship import ScholarshipCreate

# Real scholarships researched from official sources
REAL_SCHOLARSHIPS = [
    {
        "title": "Coca-Cola Scholars Foundation Scholarship",
        "description": "The Coca-Cola Scholars Foundation scholarship is awarded to high school seniors who demonstrate excellence in leadership, academic achievement, and community involvement. Recipients receive $20,000 for college expenses.",
        "provider": "Coca-Cola Scholars Foundation",
        "amount_exact": 20000.00,
        "deadline": "2024-10-31",
        "scholarship_type": "merit",
        "categories": ["leadership", "academic excellence", "community service"],
        "verified": True,
        "renewable": False,
        "application_url": "https://www.coca-colascholarsfoundation.org/apply/",
        "contact_email": "questions@coca-colascholarsfoundation.org",
        "source": "coca-cola-scholars",
        "source_url": "https://www.coca-colascholarsfoundation.org/"
    },
    {
        "title": "Gates Scholarship",
        "description": "The Gates Scholarship is a highly selective, full scholarship for exceptional, Pell-eligible, minority, high school seniors. The scholarship covers the full cost of attendance not covered by other financial aid and family contribution.",
        "provider": "Gates Foundation",
        "amount_min": 10000.00,
        "amount_max": 80000.00,
        "deadline": "2024-09-15",
        "scholarship_type": "need_based",
        "categories": ["minority", "need-based", "full ride", "pell-eligible"],
        "verified": True,
        "renewable": True,
        "application_url": "https://www.thegatesscholarship.org/scholarship",
        "contact_email": "info@thegatesscholarship.org",
        "source": "gates-foundation",
        "source_url": "https://www.thegatesscholarship.org/"
    },
    {
        "title": "National Merit Scholarship",
        "description": "National Merit Scholarships are awarded to students who demonstrate exceptional academic ability and potential for success in rigorous college studies. Awards range from $2,500 to full tuition.",
        "provider": "National Merit Scholarship Corporation",
        "amount_min": 2500.00,
        "amount_max": 100000.00,
        "deadline": "2024-10-01",
        "scholarship_type": "merit",
        "categories": ["academic excellence", "PSAT", "merit-based"],
        "verified": True,
        "renewable": True,
        "application_url": "https://www.nationalmerit.org/",
        "source": "national-merit",
        "source_url": "https://www.nationalmerit.org/"
    },
    {
        "title": "Jack Kent Cooke Foundation College Scholarship",
        "description": "The Jack Kent Cooke Foundation College Scholarship Program is the largest private scholarship for two-year and community college transfer students in the country, helping them complete their bachelor's degrees at four-year colleges or universities.",
        "provider": "Jack Kent Cooke Foundation",
        "amount_exact": 55000.00,
        "deadline": "2024-11-28",
        "scholarship_type": "need_based",
        "categories": ["transfer students", "community college", "high achievement"],
        "verified": True,
        "renewable": True,
        "application_url": "https://www.jkcf.org/our-scholarships/college-scholarship-program/",
        "contact_email": "jkc-csp@jkcf.org",
        "source": "jack-kent-cooke",
        "source_url": "https://www.jkcf.org/"
    },
    {
        "title": "Dell Scholars Program",
        "description": "The Dell Scholars program recognizes students who have overcome significant obstacles to pursue their education and who have demonstrated resilience, ambition, and commitment to their goals.",
        "provider": "Michael & Susan Dell Foundation",
        "amount_exact": 20000.00,
        "deadline": "2024-12-01",
        "scholarship_type": "need_based",
        "categories": ["resilience", "obstacles", "first-generation"],
        "verified": True,
        "renewable": False,
        "application_url": "https://www.dellscholars.org/scholarship/",
        "contact_email": "info@dellscholars.org",
        "source": "dell-scholars",
        "source_url": "https://www.dellscholars.org/"
    },
    {
        "title": "Hispanic Scholarship Fund",
        "description": "HSF empowers Latino families with the knowledge and resources to successfully complete a higher education, while providing scholarships and support services to as many exceptional Hispanic American students as possible.",
        "provider": "Hispanic Scholarship Fund",
        "amount_min": 500.00,
        "amount_max": 5000.00,
        "deadline": "2024-11-15",
        "scholarship_type": "minority",
        "categories": ["Hispanic", "Latino", "diversity"],
        "verified": True,
        "renewable": True,
        "application_url": "https://www.hsf.net/scholarship",
        "contact_email": "scholar1@hsf.net",
        "source": "hispanic-scholarship-fund",
        "source_url": "https://www.hsf.net/"
    },
    {
        "title": "Ronald McDonald House Charities Scholarship",
        "description": "RMHC scholarships are awarded to students in the U.S. who live in areas where there are participating local RMHC Chapters. Students must demonstrate academic achievement, community involvement, and financial need.",
        "provider": "Ronald McDonald House Charities",
        "amount_min": 1000.00,
        "amount_max": 5000.00,
        "deadline": "2024-10-15",
        "scholarship_type": "need_based",
        "categories": ["community involvement", "financial need"],
        "verified": True,
        "renewable": False,
        "application_url": "https://www.rmhc.org/scholarships",
        "source": "ronald-mcdonald",
        "source_url": "https://www.rmhc.org/"
    },
    {
        "title": "Society of Women Engineers Scholarship",
        "description": "SWE Scholarships support women pursuing ABET-accredited baccalaureate or graduate programs in preparation for careers in engineering, engineering technology and computer science.",
        "provider": "Society of Women Engineers",
        "amount_min": 1000.00,
        "amount_max": 15000.00,
        "deadline": "2024-12-01",
        "scholarship_type": "minority",
        "categories": ["women", "engineering", "STEM", "technology"],
        "verified": True,
        "renewable": True,
        "application_url": "https://swe.org/scholarships/",
        "contact_email": "scholarships@swe.org",
        "source": "society-women-engineers",
        "source_url": "https://swe.org/"
    },
    {
        "title": "Elks National Foundation Most Valuable Student Scholarship",
        "description": "The Most Valuable Student scholarship contest is open to any high school senior who is a U.S. citizen and will graduate during the current school year. Students are judged on scholarship, leadership, and financial need.",
        "provider": "Elks National Foundation",
        "amount_min": 4000.00,
        "amount_max": 12500.00,
        "deadline": "2024-11-05",
        "scholarship_type": "merit",
        "categories": ["leadership", "scholarship", "community service"],
        "verified": True,
        "renewable": True,
        "application_url": "https://www.elks.org/scholars/scholarships/mvs.cfm",
        "source": "elks-national",
        "source_url": "https://www.elks.org/"
    },
    {
        "title": "American Legion Auxiliary Spirit of Youth Scholarship",
        "description": "The Spirit of Youth Scholarship for Junior Members is awarded to ALA junior members who have held membership for the past three consecutive years, hold current membership, and continue to maintain membership throughout the four-year scholarship period.",
        "provider": "American Legion Auxiliary",
        "amount_exact": 5000.00,
        "deadline": "2024-12-31",
        "scholarship_type": "other",
        "categories": ["military family", "service", "youth"],
        "verified": True,
        "renewable": True,
        "application_url": "https://www.alaforveterans.org/Scholarships/Spirit-of-Youth-Scholarship-for-Junior-Members/",
        "source": "american-legion",
        "source_url": "https://www.alaforveterans.org/"
    }
]

async def import_real_scholarships():
    """Import real, researched scholarships to database"""
    
    async for db in get_db():
        service = ScholarshipService(db)
        created_count = 0
        total_amount = 0
        
        for scholarship_data in REAL_SCHOLARSHIPS:
            try:
                scholarship_create = ScholarshipCreate(**scholarship_data)
                scholarship = await service.create_scholarship(scholarship_create)
                
                # Calculate amount for statistics
                if scholarship_data.get('amount_exact'):
                    amount = scholarship_data['amount_exact']
                elif scholarship_data.get('amount_min') and scholarship_data.get('amount_max'):
                    amount = (scholarship_data['amount_min'] + scholarship_data['amount_max']) / 2
                elif scholarship_data.get('amount_min'):
                    amount = scholarship_data['amount_min']
                else:
                    amount = 0
                
                total_amount += amount
                
                print(f"✅ Created: {scholarship.title} (${amount:,.0f})")
                created_count += 1
                await db.commit()
                
            except Exception as e:
                print(f"❌ Error creating scholarship '{scholarship_data['title']}': {e}")
                await db.rollback()
        
        print(f"\n🎉 Successfully imported {created_count} real scholarships!")
        print(f"💰 Total scholarship value: ${total_amount:,.0f}")
        print(f"📊 Average per scholarship: ${total_amount/created_count:,.0f}")
        break

if __name__ == "__main__":
    asyncio.run(import_real_scholarships())