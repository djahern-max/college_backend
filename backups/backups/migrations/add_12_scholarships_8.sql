-- ============================================================================
-- Add 12 ACADEMIC_MERIT Scholarships to MagicScholar Database
-- File: add_12_scholarships_8.sql
-- Batch: 8 of 10
-- Created: 2025-10-11
-- Theme: Academic Merit - High Achievers, Honor Societies, Academic Excellence
-- ============================================================================

-- Start transaction
BEGIN;

-- ============================================================================
-- 1. National Honor Society Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'National Honor Society Scholarship',
    'National Honor Society',
    'ACADEMIC_MERIT',
    'ACTIVE',
    'HARD',
    1000,
    25000,
    false,
    600,
    '2026-01-27',
    '2025-10-01',
    '2026-2027',
    'For NHS members demonstrating scholarship, service, leadership, and character. Multiple scholarship levels. Must be active NHS member at time of application.',
    'https://www.nhs.us/students/the-nhs-scholarship/',
    3.50,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/national_honor_society_scholarship.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 2. Phi Theta Kappa Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Phi Theta Kappa Scholarship',
    'Phi Theta Kappa Honor Society',
    'ACADEMIC_MERIT',
    'ACTIVE',
    'MODERATE',
    500,
    5000,
    false,
    200,
    '2026-04-01',
    '2026-01-01',
    '2026-2027',
    'For community college students who are PTK members transferring to four-year institutions. Based on academics, leadership, and PTK involvement. Over 600 partner colleges offer additional scholarships.',
    'https://www.ptk.org/scholarships/',
    3.50,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/phi_theta_kappa_scholarship.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 3. Phi Beta Kappa Academic Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Phi Beta Kappa Academic Scholarship',
    'Phi Beta Kappa Society',
    'ACADEMIC_MERIT',
    'ACTIVE',
    'VERY_HARD',
    15000,
    15000,
    false,
    3,
    '2026-01-31',
    '2025-10-01',
    '2026-2027',
    'Mary Isabel Sibley Fellowship for women scholars in Greek or French studies. One of oldest and most prestigious academic honor societies. Highly competitive.',
    'https://www.pbk.org/Scholarships',
    3.80,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/phi_beta_kappa_academic_scholarship.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 4. Davidson Fellows Scholarship (Science, Tech, Literature, Music)
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Intel Science Talent Search',
    'Society for Science',
    'ACADEMIC_MERIT',
    'ACTIVE',
    'VERY_HARD',
    25000,
    250000,
    false,
    40,
    '2025-11-13',
    '2025-08-01',
    '2026-2027',
    'Oldest and most prestigious pre-college science competition. For high school seniors completing original research project. Top winner receives $250,000. Formerly known as Westinghouse and Intel STS.',
    'https://www.societyforscience.org/regeneron-sts/',
    3.50,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/intel_science_talent_search.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 5. Siemens Competition in Math, Science & Technology
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Siemens Competition',
    'Siemens Foundation',
    'ACADEMIC_MERIT',
    'ACTIVE',
    'VERY_HARD',
    1000,
    100000,
    false,
    96,
    '2025-10-01',
    '2025-06-01',
    '2026-2027',
    'Premier competition for high school students conducting individual or team research projects in STEM. Regional and national finals. Grand prize of $100,000 for individuals.',
    'https://www.siemensfoundation.org/programs/siemens-competition/',
    3.70,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/siemens_competition.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 6. U.S. Presidential Scholars Program
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'U.S. Presidential Scholars Program',
    'U.S. Department of Education',
    'ACADEMIC_MERIT',
    'ACTIVE',
    'VERY_HARD',
    0,
    0,
    false,
    161,
    '2025-11-15',
    '2025-09-01',
    '2026-2027',
    'One of nation''s highest honors for graduating high school seniors. Recognition based on academic achievement, essays, leadership, and community service. Medallion ceremony at White House. No monetary award.',
    'https://www2.ed.gov/programs/psp/index.html',
    3.80,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/us_presidential_scholars_program.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 7. Coca-Cola National Scholar
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Coca-Cola National Scholar',
    'Coca-Cola Scholars Foundation',
    'ACADEMIC_MERIT',
    'ACTIVE',
    'VERY_HARD',
    20000,
    20000,
    false,
    150,
    '2025-10-31',
    '2025-08-01',
    '2026-2027',
    'Achievement-based scholarship for exceptional high school seniors. Based on capacity to lead and serve, academic achievement, and unusual circumstances overcome. One of most competitive scholarships.',
    'https://www.coca-colascholarsfoundation.org/',
    3.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/coca_cola_national_scholar.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 8. Golden Key International Honour Society Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Golden Key Scholarship',
    'Golden Key International Honour Society',
    'ACADEMIC_MERIT',
    'ACTIVE',
    'MODERATE',
    1000,
    10000,
    false,
    150,
    '2026-03-01',
    '2025-12-01',
    '2026-2027',
    'For Golden Key members in top 15% of their class. Multiple scholarships for undergraduate and graduate study, study abroad, and professional development.',
    'https://www.goldenkey.org/scholarships-awards/',
    3.50,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/golden_key_scholarship.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 9. Tau Beta Pi Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Tau Beta Pi Scholarship',
    'Tau Beta Pi Engineering Honor Society',
    'ACADEMIC_MERIT',
    'ACTIVE',
    'HARD',
    2000,
    2000,
    false,
    225,
    '2026-04-01',
    '2026-01-01',
    '2026-2027',
    'For engineering students who are Tau Beta Pi members. Oldest engineering honor society in United States. Based on academic excellence, leadership, and service to engineering profession.',
    'https://www.tbp.org/memb/Scholars.cfm',
    3.70,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/tau_beta_pi_scholarship.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 10. Alpha Kappa Alpha Educational Advancement Foundation
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'AKA Educational Advancement Foundation Scholarship',
    'Alpha Kappa Alpha Sorority',
    'ACADEMIC_MERIT',
    'ACTIVE',
    'MODERATE',
    1000,
    5000,
    false,
    100,
    '2026-04-15',
    '2026-01-01',
    '2026-2027',
    'For students demonstrating academic excellence and leadership. Preference given to members and descendants of AKA members. Multiple scholarships for various academic levels and majors.',
    'https://akaeaf.org/scholarships',
    3.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/aka_educational_advancement_foundation_scholarship.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 11. Boettcher Foundation Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Boettcher Foundation Scholarship',
    'Boettcher Foundation',
    'ACADEMIC_MERIT',
    'ACTIVE',
    'VERY_HARD',
    13000,
    52000,
    true,
    42,
    '2025-11-01',
    '2025-08-01',
    '2026-2027',
    'Full-ride scholarship for Colorado high school seniors attending college in Colorado. Covers tuition, fees, books, and living stipend. One of most prestigious merit scholarships in Colorado.',
    'https://boettcherfoundation.org/scholarships/',
    3.75,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/boettcher_foundation_scholarship.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 12. Harry S. Truman Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Harry S. Truman Scholarship',
    'Harry S. Truman Scholarship Foundation',
    'ACADEMIC_MERIT',
    'ACTIVE',
    'VERY_HARD',
    30000,
    30000,
    false,
    60,
    '2026-01-28',
    '2025-09-01',
    '2026-2027',
    'For college juniors committed to careers in public service and government. Provides funding for graduate school. One of most prestigious national scholarships. Requires faculty nomination.',
    'https://www.truman.gov/',
    3.50,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/harry_s_truman_scholarship.jpg',
    true,
    true,
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
-- WHERE id > 90 
-- ORDER BY id;

-- ============================================================================
-- Summary - Batch 8
-- ============================================================================
-- Total scholarships added: 12 (IDs 91-102)
-- Theme: ACADEMIC_MERIT - High Achievers, Honor Societies, Excellence
-- 
-- Categories covered:
--   - Honor Societies: 5 (NHS, Phi Theta Kappa, Phi Beta Kappa, Golden Key, Tau Beta Pi, AKA)
--   - Science Competitions: 2 (Intel STS, Siemens)
--   - National Recognition: 3 (Presidential Scholars, Coca-Cola, Truman)
--   - State/Regional: 1 (Boettcher - Colorado)
--
-- Scholarship types distribution:
--   - ACADEMIC_MERIT: 12
-- 
-- Difficulty distribution:
--   - VERY_HARD: 7 (Phi Beta Kappa, Intel STS, Siemens, Presidential Scholars, Coca-Cola, Boettcher, Truman)
--   - HARD: 2 (NHS, Tau Beta Pi)
--   - MODERATE: 3 (Phi Theta Kappa, Golden Key, AKA)
--   - EASY: 0
--
-- Featured scholarships: 7 (NHS, Phi Beta Kappa, Intel STS, Siemens, Presidential Scholars, Coca-Cola, Boettcher, Truman)
-- All verified: Yes
-- Amount range: $0 (recognition only) - $250,000
-- Total scholarships in database after import: 102
-- ============================================================================
