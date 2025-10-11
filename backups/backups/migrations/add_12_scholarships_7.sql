-- ============================================================================
-- Add 12 DIVERSITY Scholarships to MagicScholar Database
-- File: add_12_scholarships_7.sql
-- Batch: 7 of 10
-- Created: 2025-10-11
-- Theme: Diversity - Ethnicity, Gender, First-Generation, Underrepresented Groups
-- ============================================================================

-- Start transaction
BEGIN;

-- ============================================================================
-- 1. Point Foundation Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Point Foundation Scholarship',
    'Point Foundation',
    'DIVERSITY',
    'ACTIVE',
    'HARD',
    4800,
    36000,
    true,
    30,
    '2026-01-27',
    '2025-10-01',
    '2026-2027',
    'For LGBTQ students with demonstrated leadership and community involvement. Largest scholarship program for LGBTQ students in nation. Includes mentorship and leadership development.',
    'https://pointfoundation.org/point-apply/scholarship-faqs/',
    3.20,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/point_foundation_scholarship.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 2. American Indian College Fund Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'American Indian College Fund Scholarship',
    'American Indian College Fund',
    'DIVERSITY',
    'ACTIVE',
    'MODERATE',
    1000,
    10000,
    false,
    6000,
    '2026-05-31',
    '2026-01-01',
    '2026-2027',
    'For Native American and Alaska Native students. Over 200 different scholarships available for various majors and tribal affiliations. One application applies for all eligible awards.',
    'https://collegefund.org/students/scholarships/',
    2.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/american_indian_college_fund_scholarship.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 3. Asian & Pacific Islander American Scholarship Fund
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'APIASF Scholarship',
    'Asian & Pacific Islander American Scholarship Fund',
    'DIVERSITY',
    'ACTIVE',
    'MODERATE',
    2500,
    20000,
    false,
    600,
    '2026-01-16',
    '2025-10-01',
    '2026-2027',
    'For students of Asian and Pacific Islander heritage. Based on financial need, academic achievement, and commitment to community service. Multiple scholarship programs available.',
    'https://www.apiasf.org/scholarship.html',
    2.70,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/apiasf_scholarship.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 4. LULAC National Scholarship Fund
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'LULAC National Scholarship Fund',
    'League of United Latin American Citizens',
    'DIVERSITY',
    'ACTIVE',
    'MODERATE',
    500,
    2000,
    false,
    1000,
    '2026-03-31',
    '2026-01-01',
    '2026-2027',
    'For Hispanic students of all majors. Awards based on academic achievement, community involvement, and financial need. Largest Hispanic scholarship program in the United States.',
    'https://lnesc.org/',
    3.25,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/lulac_national_scholarship_fund.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 5. NAACP Scholarships
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'NAACP Scholarships',
    'National Association for the Advancement of Colored People',
    'DIVERSITY',
    'ACTIVE',
    'MODERATE',
    1000,
    5000,
    false,
    50,
    '2026-03-07',
    '2025-12-01',
    '2026-2027',
    'For African American high school seniors and current undergraduates. Multiple scholarships available for various fields. Based on academics, financial need, and commitment to racial justice.',
    'https://naacp.org/find-resources/scholarships',
    2.50,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/naacp_scholarships.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 6. P.E.O. Program for Continuing Education
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'P.E.O. Program for Continuing Education',
    'P.E.O. Sisterhood',
    'DIVERSITY',
    'ACTIVE',
    'MODERATE',
    3000,
    3000,
    false,
    2500,
    '2026-03-01',
    '2025-11-01',
    '2026-2027',
    'For women returning to school to complete their education after interruption. One-time grant to help with tuition, books, and fees. Must be sponsored by local P.E.O. chapter.',
    'https://www.peointernational.org/about-peo-sisterhood',
    NULL,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/peo_program_for_continuing_education.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 7. Jeannette Rankin Women's Scholarship Fund
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Jeannette Rankin Women''s Scholarship Fund',
    'Jeannette Rankin Foundation',
    'DIVERSITY',
    'ACTIVE',
    'MODERATE',
    2000,
    2000,
    false,
    50,
    '2026-03-01',
    '2025-11-01',
    '2026-2027',
    'For low-income women aged 35 and older pursuing undergraduate or technical education. Named after first woman elected to U.S. Congress. Focus on helping women achieve economic security.',
    'https://rankinfoundation.org/students/application-information/',
    2.50,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/jeannette_rankin_womens_scholarship_fund.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 8. Que Llueva Café Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Que Llueva Café Scholarship',
    'Café Bustelo',
    'DIVERSITY',
    'ACTIVE',
    'MODERATE',
    5000,
    5000,
    false,
    10,
    '2026-04-28',
    '2026-02-01',
    '2026-2027',
    'For Latino students demonstrating academic excellence, leadership, and commitment to making positive impact in their communities. Essay required about cultural heritage and aspirations.',
    'https://www.cafebustelo.com/en/scholarship',
    3.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/que_llueva_cafe_scholarship.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 9. First Generation Matching Grant Program
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'First Generation Matching Grant Program',
    'Taco Bell Foundation',
    'DIVERSITY',
    'ACTIVE',
    'MODERATE',
    5000,
    25000,
    false,
    500,
    '2026-01-31',
    '2025-10-01',
    '2026-2027',
    'For first-generation college students ages 16-24 pursuing two or four-year degree. Based on passion, drive, and commitment to education. No minimum GPA requirement.',
    'https://www.tacobellfoundation.org/live-mas-scholarship/',
    NULL,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/first_generation_matching_grant_program.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 10. Dream.US National Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Dream.US National Scholarship',
    'TheDream.US',
    'DIVERSITY',
    'ACTIVE',
    'HARD',
    14000,
    33000,
    true,
    1000,
    '2026-02-28',
    '2025-11-01',
    '2026-2027',
    'For DREAMers (DACA and undocumented students) with significant unmet financial need. Largest college access program for immigrant youth. Covers tuition, fees, and books at partner colleges.',
    'https://www.thedream.us/',
    2.50,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/dream_us_national_scholarship.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 11. LAGRANT Foundation Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'LAGRANT Foundation Scholarship',
    'LAGRANT Foundation',
    'DIVERSITY',
    'ACTIVE',
    'MODERATE',
    2500,
    10000,
    false,
    40,
    '2026-02-28',
    '2025-12-01',
    '2026-2027',
    'For ethnic minority students pursuing careers in advertising, marketing, or public relations. Includes mentorship and internship opportunities. Based on academics, financial need, and career goals.',
    'https://www.lagrantfoundation.org/Scholarship%20Program',
    3.20,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/lagrant_foundation_scholarship.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 12. Thurgood Marshall College Fund Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Thurgood Marshall College Fund Scholarship',
    'Thurgood Marshall College Fund',
    'DIVERSITY',
    'ACTIVE',
    'MODERATE',
    3100,
    6200,
    false,
    500,
    '2026-04-15',
    '2026-01-01',
    '2026-2027',
    'For students attending TMCF member schools (historically Black public colleges and universities). Multiple scholarships available. Based on academics, leadership, and community service.',
    'https://www.tmcf.org/students-alumni/scholarship/',
    3.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/thurgood_marshall_college_fund_scholarship.jpg',
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
-- WHERE id > 78 
-- ORDER BY id;

-- ============================================================================
-- Summary - Batch 7
-- ============================================================================
-- Total scholarships added: 12 (IDs 79-90)
-- Theme: DIVERSITY - Ethnicity, Gender, First-Generation, Underrepresented
-- 
-- Diversity categories covered:
--   - LGBTQ+: 1 (Point Foundation)
--   - Native American: 1 (American Indian College Fund)
--   - Asian/Pacific Islander: 1 (APIASF)
--   - Hispanic/Latino: 3 (LULAC, Que Llueva Café, Dream.US)
--   - African American: 3 (NAACP, LAGRANT, Thurgood Marshall)
--   - Women: 2 (P.E.O., Jeannette Rankin)
--   - First-Generation: 1 (Taco Bell Foundation)
--   - Undocumented/DACA: 1 (Dream.US)
--
-- Scholarship types distribution:
--   - DIVERSITY: 12
-- 
-- Difficulty distribution:
--   - VERY_HARD: 0
--   - HARD: 2 (Point Foundation, Dream.US)
--   - MODERATE: 10
--   - EASY: 0
--
-- Featured scholarships: 4 (Point Foundation, American Indian College Fund, Taco Bell, Dream.US)
-- All verified: Yes
-- Amount range: $500 - $36,000
-- Total scholarships in database after import: 90
-- ============================================================================
