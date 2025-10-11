-- ============================================================================
-- Add 12 New Scholarships to MagicScholar Database
-- File: add_12_scholarships.sql
-- Created: 2025-10-11
-- Description: Adds 12 diverse, well-known scholarships with complete data
-- ============================================================================

-- Start transaction
BEGIN;

-- ============================================================================
-- 1. Gates Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Gates Scholarship',
    'Bill & Melinda Gates Foundation',
    'NEED_BASED',
    'ACTIVE',
    'VERY_HARD',
    40000,
    70000,
    true,
    300,
    '2025-09-15',
    '2025-08-01',
    '2026-2027',
    'Full scholarship for exceptional, Pell-eligible minority high school seniors. Covers full cost of attendance not covered by other financial aid. Includes mentoring and academic support.',
    'https://www.thegatesscholarship.org/',
    3.30,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/gates_scholarship.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 2. Dell Scholars Program
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Dell Scholars Program',
    'Michael & Susan Dell Foundation',
    'NEED_BASED',
    'ACTIVE',
    'MODERATE',
    20000,
    20000,
    false,
    500,
    '2025-12-01',
    '2025-10-01',
    '2026-2027',
    'Scholarship for students with financial need who demonstrate determination to succeed. Includes ongoing support, mentorship, textbook credits, and a laptop.',
    'https://www.dellscholars.org/',
    2.40,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/dell_scholars_program.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 3. QuestBridge National College Match
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'QuestBridge National College Match',
    'QuestBridge',
    'NEED_BASED',
    'ACTIVE',
    'VERY_HARD',
    50000,
    85000,
    true,
    1500,
    '2025-09-26',
    '2025-08-01',
    '2026-2027',
    'Full four-year scholarships to top colleges for high-achieving, low-income students. Covers tuition, room, board, books, and travel expenses at partner institutions.',
    'https://www.questbridge.org/',
    3.50,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/questbridge_national_college_match.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 4. Amazon Future Engineer Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Amazon Future Engineer Scholarship',
    'Amazon',
    'STEM',
    'ACTIVE',
    'MODERATE',
    40000,
    40000,
    true,
    100,
    '2026-01-31',
    '2025-10-01',
    '2026-2027',
    'For students pursuing computer science degrees. Includes $10,000 per year for four years plus a guaranteed paid internship at Amazon after freshman year.',
    'https://www.amazonfutureengineer.com/',
    3.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/amazon_future_engineer_scholarship.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 5. Hispanic Scholarship Fund
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Hispanic Scholarship Fund',
    'Hispanic Scholarship Fund',
    'DIVERSITY',
    'ACTIVE',
    'EASY',
    500,
    5000,
    true,
    10000,
    '2026-02-15',
    '2025-11-01',
    '2026-2027',
    'Scholarships for Hispanic/Latino students of any major pursuing higher education. Awards based on merit and financial need. Renewable annually with continued eligibility.',
    'https://www.hsf.net/',
    3.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/hispanic_scholarship_fund.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 6. AXA Achievement Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'AXA Achievement Scholarship',
    'AXA Foundation',
    'LEADERSHIP',
    'ACTIVE',
    'MODERATE',
    2500,
    25000,
    false,
    60,
    '2025-12-15',
    '2025-10-01',
    '2026-2027',
    'For students who demonstrate ambition, drive, determination, and self-discipline to succeed. Recognizes students who have overcome significant obstacles.',
    'https://www.axa-achievement.com/',
    3.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/axa_achievement_scholarship.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 7. Burger King Scholars Program
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Burger King Scholars Program',
    'Burger King Foundation',
    'NEED_BASED',
    'ACTIVE',
    'EASY',
    1000,
    50000,
    false,
    3500,
    '2025-12-15',
    '2025-10-01',
    '2026-2027',
    'Scholarships for high school seniors with demonstrated financial need, work experience, and community service. Award amounts vary based on need and merit.',
    'https://www.burgerkingfoundation.org/',
    2.50,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/burger_king_scholars_program.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 8. Jack Kent Cooke Foundation College Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Jack Kent Cooke Foundation College Scholarship',
    'Jack Kent Cooke Foundation',
    'ACADEMIC_MERIT',
    'ACTIVE',
    'VERY_HARD',
    40000,
    55000,
    true,
    40,
    '2025-11-14',
    '2025-08-01',
    '2026-2027',
    'For high-achieving high school seniors with financial need. Covers tuition, living expenses, books, and fees for up to four years. One of the largest scholarships available.',
    'https://www.jkcf.org/',
    3.50,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/jack_kent_cooke_foundation_college_scholarship.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 9. Ron Brown Scholar Program
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Ron Brown Scholar Program',
    'Ron Brown Scholar Program',
    'DIVERSITY',
    'ACTIVE',
    'VERY_HARD',
    40000,
    40000,
    true,
    10,
    '2026-01-09',
    '2025-09-01',
    '2026-2027',
    'For African American high school seniors who demonstrate academic excellence, leadership, and community service. Provides $10,000 per year for four years plus mentoring.',
    'https://www.ronbrown.org/',
    3.50,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/ron_brown_scholar_program.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 10. Horatio Alger National Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Horatio Alger National Scholarship',
    'Horatio Alger Association',
    'NEED_BASED',
    'ACTIVE',
    'MODERATE',
    25000,
    25000,
    false,
    106,
    '2025-10-25',
    '2025-08-01',
    '2026-2027',
    'For students who have faced and overcome great obstacles, demonstrate perseverance, and have financial need. Recognizes students who exhibit integrity and determination.',
    'https://scholars.horatioalger.org/',
    2.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/horatio_alger_national_scholarship.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 11. Davidson Fellows Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Davidson Fellows Scholarship',
    'Davidson Institute',
    'STEM',
    'ACTIVE',
    'VERY_HARD',
    10000,
    50000,
    false,
    20,
    '2026-02-13',
    '2025-10-01',
    '2026-2027',
    'For students 18 and under who have completed a significant piece of work in STEM, literature, music, or philosophy. Requires submission of an extraordinary project.',
    'https://www.davidsongifted.org/fellows-scholarship',
    NULL,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/davidson_fellows_scholarship.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 12. Foot Locker Scholar Athletes Program
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Foot Locker Scholar Athletes Program',
    'Foot Locker Foundation',
    'ATHLETIC',
    'ACTIVE',
    'MODERATE',
    5000,
    20000,
    false,
    20,
    '2026-01-07',
    '2025-10-01',
    '2026-2027',
    'For student-athletes who demonstrate leadership on and off the field. Must participate in high school sports and maintain strong academics while contributing to community.',
    'https://www.footlockerscholarathletes.com/',
    3.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/foot_locker_scholar_athletes_program.jpg',
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
-- WHERE id > 6 
-- ORDER BY id;

-- ============================================================================
-- Summary
-- ============================================================================
-- Total scholarships added: 12
-- Scholarship types distribution:
--   - NEED_BASED: 5 (Gates, Dell, QuestBridge, Burger King, Horatio Alger)
--   - STEM: 2 (Amazon Future Engineer, Davidson Fellows)
--   - DIVERSITY: 2 (Hispanic Scholarship Fund, Ron Brown)
--   - LEADERSHIP: 1 (AXA Achievement)
--   - ACADEMIC_MERIT: 1 (Jack Kent Cooke)
--   - ATHLETIC: 1 (Foot Locker)
-- 
-- Difficulty distribution:
--   - VERY_HARD: 5
--   - HARD: 0
--   - MODERATE: 5
--   - EASY: 2
--
-- Featured scholarships: 4
-- All verified: Yes
-- ============================================================================
