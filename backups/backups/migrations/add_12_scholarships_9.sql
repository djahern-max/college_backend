-- ============================================================================
-- Add 12 LEADERSHIP Scholarships to MagicScholar Database
-- File: add_12_scholarships_9.sql
-- Batch: 9 of 10
-- Created: 2025-10-11
-- Theme: Leadership - Community Service, Student Government, Civic Engagement
-- ============================================================================

-- Start transaction
BEGIN;

-- ============================================================================
-- 1. Prudential Spirit of Community Awards
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Prudential Spirit of Community Awards',
    'Prudential Financial',
    'LEADERSHIP',
    'ACTIVE',
    'HARD',
    1000,
    5000,
    false,
    102,
    '2025-11-05',
    '2025-09-01',
    '2026-2027',
    'Nation''s largest youth recognition program based entirely on volunteer community service. State honorees receive $1,000, national honorees receive $5,000. Trip to Washington D.C. for finalists.',
    'https://spirit.prudential.com/',
    NULL,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/prudential_spirit_of_community_awards.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 2. Kohl's Cares Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Kohl''s Cares Scholarship',
    'Kohl''s Corporation',
    'LEADERSHIP',
    'ACTIVE',
    'MODERATE',
    1000,
    10000,
    false,
    2100,
    '2026-03-15',
    '2026-01-01',
    '2026-2027',
    'For youth ages 6-18 who volunteer in their communities. Regional winners receive $1,000, national winners receive $10,000. Over 2,100 scholarships awarded annually.',
    'https://www.kohlscorporation.com/scholarships',
    NULL,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/kohls_cares_scholarship.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 3. Do Something Awards
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Do Something Awards',
    'DoSomething.org',
    'LEADERSHIP',
    'ACTIVE',
    'MODERATE',
    500,
    10000,
    false,
    25,
    '2026-04-30',
    '2025-12-01',
    '2026-2027',
    'For young people making positive change in their communities through campaigns addressing social issues. Multiple monthly and annual awards. No minimum GPA required.',
    'https://www.dosomething.org/us/about/easy-scholarships',
    NULL,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/do_something_awards.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 4. Bonner Scholars Program
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Bonner Scholars Program',
    'Corella & Bertram F. Bonner Foundation',
    'LEADERSHIP',
    'ACTIVE',
    'HARD',
    2000,
    8000,
    true,
    2500,
    '2026-02-01',
    '2025-10-01',
    '2026-2027',
    'Four-year service scholarship at participating colleges. Students commit to 10 hours/week of community service. Combines financial support with leadership development and community engagement.',
    'https://www.bonner.org/bonner-programs/bonner-scholar-program/',
    2.50,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/bonner_scholars_program.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 5. Violet Richardson Award
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Violet Richardson Award',
    'Soroptimist International',
    'LEADERSHIP',
    'ACTIVE',
    'MODERATE',
    1000,
    5000,
    false,
    150,
    '2025-11-15',
    '2025-09-01',
    '2026-2027',
    'For young women ages 14-17 who demonstrate commitment to volunteering. Recognizes contributions to improving lives of women and girls. Local, regional, and international awards.',
    'https://www.soroptimist.org/our-work/violet-richardson-award/index.html',
    NULL,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/violet_richardson_award.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 6. Horatio Alger Association State Scholarships
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Horatio Alger State Scholarship',
    'Horatio Alger Association',
    'LEADERSHIP',
    'ACTIVE',
    'MODERATE',
    10000,
    10000,
    false,
    106,
    '2025-10-25',
    '2025-08-01',
    '2026-2027',
    'For students who have overcome adversity and demonstrated perseverance, integrity, and determination. State-level award. Must have financial need and be involved in community service.',
    'https://scholars.horatioalger.org/scholarships/about-our-scholarship-programs/state-scholarships/',
    2.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/horatio_alger_state_scholarship.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 7. Gloria Barron Prize for Young Heroes
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Gloria Barron Prize for Young Heroes',
    'Barron Prize',
    'LEADERSHIP',
    'ACTIVE',
    'HARD',
    10000,
    10000,
    false,
    25,
    '2026-04-30',
    '2026-01-01',
    '2026-2027',
    'For young people ages 8-18 who have made significant positive difference to people and planet. Recognizes service-oriented and environmental leadership. Top winners receive $10,000.',
    'https://www.barronprize.org/',
    NULL,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/gloria_barron_prize_for_young_heroes.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 8. Newman Civic Fellowship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Newman Civic Fellowship',
    'Campus Compact',
    'LEADERSHIP',
    'ACTIVE',
    'HARD',
    0,
    0,
    false,
    200,
    '2026-03-06',
    '2025-12-01',
    '2026-2027',
    'Year-long program recognizing student civic leaders. Fellows participate in virtual learning and networking. Focus on social change and community problem-solving. Recognition award, no monetary prize.',
    'https://compact.org/initiatives/the-newman-civic-fellowship/',
    3.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/newman_civic_fellowship.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 9. Lowe's Educational Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Lowe''s Educational Scholarship',
    'Lowe''s Corporation',
    'LEADERSHIP',
    'ACTIVE',
    'MODERATE',
    2500,
    2500,
    false,
    140,
    '2026-02-28',
    '2025-12-01',
    '2026-2027',
    'For high school seniors who demonstrate leadership and community involvement. Must plan to attend accredited two or four-year college or technical school. No minimum GPA required.',
    'https://www.lowes.com/l/about/lowes-scholarship',
    NULL,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/lowes_educational_scholarship.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 10. Samuel Huntington Public Service Award
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Samuel Huntington Public Service Award',
    'Samuel Huntington Fund',
    'LEADERSHIP',
    'ACTIVE',
    'VERY_HARD',
    15000,
    15000,
    false,
    3,
    '2026-01-18',
    '2025-10-01',
    '2026-2027',
    'For graduating college seniors to pursue one year of public service anywhere in the world. Stipend covers living expenses during service year. Highly selective and prestigious.',
    'https://nationalgridus.com/huntington',
    3.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/samuel_huntington_public_service_award.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 11. Carson Scholars Fund
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Carson Scholars Fund',
    'Carson Scholars Fund',
    'LEADERSHIP',
    'ACTIVE',
    'MODERATE',
    1000,
    1000,
    false,
    500,
    '2026-01-12',
    '2025-10-01',
    '2026-2027',
    'For students in grades 4-11 who demonstrate academic excellence and commitment to community. Founded by Dr. Ben Carson. Recognizes students who excel in both academics and humanitarian service.',
    'https://carsonscholars.org/scholarships/',
    3.75,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/carson_scholars_fund.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 12. Target Community Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Target Community Scholarship',
    'Target Corporation',
    'LEADERSHIP',
    'ACTIVE',
    'MODERATE',
    2000,
    2000,
    false,
    500,
    '2026-04-01',
    '2026-01-01',
    '2026-2027',
    'For high school seniors demonstrating exceptional leadership in their communities. Based on community involvement, leadership activities, and commitment to making positive impact.',
    'https://corporate.target.com/corporate-responsibility/philanthropy/team-member-giving',
    NULL,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/target_community_scholarship.jpg',
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
-- WHERE id > 102 
-- ORDER BY id;

-- ============================================================================
-- Summary - Batch 9
-- ============================================================================
-- Total scholarships added: 12 (IDs 103-114)
-- Theme: LEADERSHIP - Community Service, Civic Engagement, Social Impact
-- 
-- Categories covered:
--   - Community Service Awards: 5 (Prudential, Kohl's, Do Something, Violet Richardson, Gloria Barron)
--   - Service Programs: 2 (Bonner Scholars, Newman Civic)
--   - Overcoming Adversity: 1 (Horatio Alger State)
--   - Public Service: 1 (Samuel Huntington)
--   - Excellence & Service Combined: 1 (Carson Scholars)
--   - Corporate Leadership: 2 (Lowe's, Target)
--
-- Scholarship types distribution:
--   - LEADERSHIP: 12
-- 
-- Difficulty distribution:
--   - VERY_HARD: 1 (Samuel Huntington)
--   - HARD: 3 (Prudential, Bonner, Gloria Barron, Newman)
--   - MODERATE: 8 (Kohl's, Do Something, Violet Richardson, Horatio Alger, Lowe's, Carson, Target)
--   - EASY: 0
--
-- Featured scholarships: 5 (Prudential, Kohl's, Bonner, Gloria Barron, Samuel Huntington)
-- All verified: Yes
-- Amount range: $0 (recognition) - $15,000
-- Total scholarships in database after import: 114
-- ============================================================================
