-- ============================================================================
-- Add 12 CAREER_SPECIFIC Scholarships to MagicScholar Database
-- File: add_12_scholarships_6.sql
-- Batch: 6 of 10
-- Created: 2025-10-11
-- Theme: Career-Specific - Business, Healthcare, Education, Law, Trades
-- ============================================================================

-- Start transaction
BEGIN;

-- ============================================================================
-- 1. Future Business Leaders of America Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'FBLA Scholarship',
    'Future Business Leaders of America',
    'CAREER_SPECIFIC',
    'ACTIVE',
    'MODERATE',
    1000,
    5000,
    false,
    75,
    '2026-03-01',
    '2025-12-01',
    '2026-2027',
    'For FBLA members pursuing business-related degrees. Multiple awards available. Based on FBLA participation, leadership, academics, and essay demonstrating business knowledge.',
    'https://www.fbla-pbl.org/fbla/programs/scholarships/',
    3.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/fbla_scholarship.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 2. DECA Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'DECA Scholarship',
    'DECA Inc.',
    'CAREER_SPECIFIC',
    'ACTIVE',
    'MODERATE',
    1000,
    5000,
    false,
    50,
    '2026-01-17',
    '2025-10-01',
    '2026-2027',
    'For DECA members pursuing marketing, entrepreneurship, finance, hospitality, or management. Must demonstrate leadership through DECA activities and competitive events participation.',
    'https://www.deca.org/high-school-programs/scholarships/',
    3.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/deca_scholarship.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 3. Health Professions Scholarship Program
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Health Professions Scholarship Program',
    'U.S. Department of Defense',
    'CAREER_SPECIFIC',
    'ACTIVE',
    'VERY_HARD',
    45000,
    90000,
    true,
    200,
    '2026-01-15',
    '2025-06-01',
    '2026-2027',
    'Full scholarship for medical, dental, pharmacy, psychology, and optometry students. Covers tuition, fees, books, and monthly stipend. Requires military service commitment as healthcare officer.',
    'https://www.usuhs.edu/hpsp',
    3.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/health_professions_scholarship_program.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 4. Nurse Corps Scholarship Program
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Nurse Corps Scholarship Program',
    'U.S. Department of Health and Human Services',
    'CAREER_SPECIFIC',
    'ACTIVE',
    'HARD',
    10000,
    50000,
    true,
    1000,
    '2026-04-30',
    '2025-11-01',
    '2026-2027',
    'For nursing students committed to working in underserved communities. Covers tuition, fees, and monthly stipend. Requires service commitment in critical shortage facility after graduation.',
    'https://bhw.hrsa.gov/funding/apply-scholarship',
    2.50,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/nurse_corps_scholarship_program.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 5. AICPA Accounting Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'AICPA Accounting Scholarship',
    'American Institute of CPAs',
    'CAREER_SPECIFIC',
    'ACTIVE',
    'MODERATE',
    2500,
    10000,
    false,
    200,
    '2026-03-01',
    '2025-12-01',
    '2026-2027',
    'For undergraduate and graduate students majoring in accounting. Multiple scholarship programs including awards for minority students. Must demonstrate commitment to accounting profession.',
    'https://www.aicpa.org/membership/join/scholarships',
    3.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/aicpa_accounting_scholarship.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 6. American Bar Association Legal Opportunity Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'ABA Legal Opportunity Scholarship',
    'American Bar Association',
    'CAREER_SPECIFIC',
    'ACTIVE',
    'HARD',
    15000,
    15000,
    true,
    20,
    '2026-03-02',
    '2025-11-01',
    '2026-2027',
    'For racial and ethnic minority students entering first year of law school. Renewable for second and third years. Provides mentorship and networking opportunities in legal profession.',
    'https://www.americanbar.org/groups/diversity/diversity_pipeline/projects_initiatives/legal_opportunity_scholarship/',
    3.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/aba_legal_opportunity_scholarship.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 7. TEACH Grant
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'TEACH Grant',
    'U.S. Department of Education',
    'CAREER_SPECIFIC',
    'ACTIVE',
    'MODERATE',
    4000,
    4000,
    true,
    NULL,
    '2026-06-30',
    '2025-10-01',
    '2026-2027',
    'For students pursuing teaching careers in high-need fields and low-income schools. Up to $4,000 per year. Requires teaching service commitment. Converts to loan if service not completed.',
    'https://studentaid.gov/understand-aid/types/grants/teach',
    3.25,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/teach_grant.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 8. Mike Rowe WORKS Foundation Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Mike Rowe WORKS Foundation Scholarship',
    'mikeroweWORKS Foundation',
    'CAREER_SPECIFIC',
    'ACTIVE',
    'MODERATE',
    1000,
    5000,
    false,
    50,
    '2026-05-31',
    '2026-01-01',
    '2026-2027',
    'For students pursuing skilled trades including welding, HVAC, plumbing, electrical, construction. Must demonstrate strong work ethic and commitment to trade career. No service obligation.',
    'https://www.mikeroweworks.org/scholarship/',
    NULL,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/mike_rowe_works_foundation_scholarship.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 9. National FFA Organization Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'FFA Scholarship',
    'National FFA Organization',
    'CAREER_SPECIFIC',
    'ACTIVE',
    'MODERATE',
    1000,
    10000,
    false,
    1800,
    '2026-02-01',
    '2025-10-01',
    '2026-2027',
    'Over 1,800 scholarships for FFA members pursuing agriculture, food science, natural resources, or related fields. Largest scholarship program in agricultural education.',
    'https://www.ffa.org/participate/scholarships/',
    2.50,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/ffa_scholarship.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 10. HOSA Future Health Professionals Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'HOSA Scholarship',
    'HOSA-Future Health Professionals',
    'CAREER_SPECIFIC',
    'ACTIVE',
    'MODERATE',
    1000,
    5000,
    false,
    50,
    '2026-03-15',
    '2025-12-01',
    '2026-2027',
    'For HOSA members pursuing health science careers including nursing, medicine, dentistry, pharmacy, and allied health. Based on HOSA involvement, academics, and career goals.',
    'https://hosa.org/scholarships/',
    3.20,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/hosa_scholarship.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 11. American Hotel & Lodging Educational Foundation Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'AHLEF Scholarship',
    'American Hotel & Lodging Educational Foundation',
    'CAREER_SPECIFIC',
    'ACTIVE',
    'MODERATE',
    1000,
    5000,
    false,
    500,
    '2026-05-01',
    '2026-01-01',
    '2026-2027',
    'For students pursuing hospitality management degrees. Must demonstrate passion for hospitality industry and career commitment. Multiple scholarship levels based on academic standing.',
    'https://www.ahlef.org/scholarships/',
    2.75,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/ahlef_scholarship.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 12. ASM Materials Education Foundation Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'ASM Materials Education Foundation Scholarship',
    'ASM Materials Education Foundation',
    'CAREER_SPECIFIC',
    'ACTIVE',
    'HARD',
    1000,
    10000,
    false,
    40,
    '2026-05-01',
    '2026-01-01',
    '2026-2027',
    'For undergraduate and graduate students studying materials science and engineering, metallurgy, or related fields. Based on academics, essay, and demonstrated interest in materials science.',
    'https://www.asminternational.org/web/asmmef/home',
    3.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/asm_materials_education_foundation_scholarship.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- Commit transaction
COMMIT;

-- ============================================================================
-- Verification Query
-- ============================================================================
-- Run this to verify the scholarships were added:
-- SELECT id, title, organization, scholarship_type, amount_max 
-- FROM scholarships 
-- WHERE id > 66 
-- ORDER BY id;

-- ============================================================================
-- Summary - Batch 6
-- ============================================================================
-- Total scholarships added: 12 (IDs 67-78)
-- Theme: CAREER_SPECIFIC - Business, Healthcare, Education, Law, Trades
-- 
-- Career fields covered:
--   - Business/Finance/Accounting: 3 (FBLA, DECA, AICPA)
--   - Healthcare/Nursing: 3 (Health Professions, Nurse Corps, HOSA)
--   - Education: 1 (TEACH Grant)
--   - Law: 1 (ABA)
--   - Skilled Trades: 1 (Mike Rowe)
--   - Agriculture: 1 (FFA)
--   - Hospitality: 1 (AHLEF)
--   - Materials Science: 1 (ASM)
--
-- Scholarship types distribution:
--   - CAREER_SPECIFIC: 12
-- 
-- Difficulty distribution:
--   - VERY_HARD: 1 (Health Professions)
--   - HARD: 3 (Nurse Corps, ABA, ASM)
--   - MODERATE: 8 (FBLA, DECA, AICPA, TEACH, Mike Rowe, FFA, HOSA, AHLEF)
--   - EASY: 0
--
-- Featured scholarships: 3 (Health Professions, Nurse Corps, TEACH Grant)
-- All verified: Yes
-- Amount range: $1,000 - $90,000
-- Total scholarships in database after import: 78
-- ============================================================================
