-- ============================================================================
-- Add 12 ARTS Scholarships to MagicScholar Database
-- File: add_12_scholarships_3.sql
-- Batch: 3 of 10
-- Created: 2025-10-11
-- Theme: Arts, Music, Visual Arts, Performing Arts, Creative Fields
-- ============================================================================

-- Start transaction
BEGIN;

-- ============================================================================
-- 1. YoungArts
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'YoungArts',
    'National YoungArts Foundation',
    'ARTS',
    'ACTIVE',
    'VERY_HARD',
    0,
    10000,
    false,
    700,
    '2025-10-14',
    '2025-06-01',
    '2026-2027',
    'For high school seniors and 18-year-olds in visual, literary, design, and performing arts. Winners receive cash awards, mentorship, and performance opportunities. One of most prestigious arts awards.',
    'https://www.youngarts.org/',
    NULL,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/youngarts.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 2. Scholastic Art & Writing Awards
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Scholastic Art & Writing Awards',
    'Alliance for Young Artists & Writers',
    'ARTS',
    'ACTIVE',
    'MODERATE',
    500,
    10000,
    false,
    1000,
    '2026-01-10',
    '2025-09-01',
    '2026-2027',
    'Longest-running recognition program for creative teens in grades 7-12. Portfolio Gold awards receive $10,000. Categories include writing, photography, painting, sculpture, and more.',
    'https://www.artandwriting.org/',
    NULL,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/scholastic_art_writing_awards.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 3. National Association for Music Education Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'NAfME Scholarship',
    'National Association for Music Education',
    'ARTS',
    'ACTIVE',
    'MODERATE',
    1000,
    5000,
    false,
    20,
    '2025-11-15',
    '2025-09-01',
    '2026-2027',
    'For high school seniors planning to major in music education. Requires audition tape, essay, and letters of recommendation demonstrating musical talent and teaching potential.',
    'https://nafme.org/my-classroom/journals-magazines-books/scholarships/',
    3.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/nafme_scholarship.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 4. Princess Grace Awards
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Princess Grace Awards',
    'Princess Grace Foundation',
    'ARTS',
    'ACTIVE',
    'VERY_HARD',
    7500,
    30000,
    false,
    50,
    '2026-03-31',
    '2026-01-01',
    '2026-2027',
    'For emerging artists in theater, dance, and film. Students must be nominated by their institution. Includes scholarships, apprenticeships, and fellowships for exceptional performing artists.',
    'https://www.pgfusa.org/',
    NULL,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/princess_grace_awards.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 5. VSA Playwright Discovery Program
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'VSA Playwright Discovery Program',
    'Kennedy Center',
    'ARTS',
    'ACTIVE',
    'MODERATE',
    2000,
    2000,
    false,
    1,
    '2026-02-01',
    '2025-10-01',
    '2026-2027',
    'For students with disabilities who write plays. Winner receives cash prize and production of their script at Kennedy Center. Open to middle and high school students.',
    'https://www.kennedy-center.org/education/opportunities-for-artists/competitions-and-commissions/vsa-playwright-discovery/',
    NULL,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/vsa_playwright_discovery_program.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 6. ASCAP Foundation Morton Gould Young Composer Awards
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'ASCAP Morton Gould Young Composer Awards',
    'ASCAP Foundation',
    'ARTS',
    'ACTIVE',
    'HARD',
    500,
    5000,
    false,
    40,
    '2026-02-01',
    '2025-11-01',
    '2026-2027',
    'For composers under 30 years old. Submit original concert music composition. One of the longest-running composition competitions. Winners performed at concerts and recognized industry-wide.',
    'https://www.ascapfoundation.org/programs/awards/morton-gould-young-composer-awards',
    NULL,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/ascap_morton_gould_young_composer_awards.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 7. National Endowment for the Arts Creative Writing Fellowship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'NEA Creative Writing Fellowship',
    'National Endowment for the Arts',
    'ARTS',
    'ACTIVE',
    'VERY_HARD',
    25000,
    25000,
    false,
    45,
    '2026-03-01',
    '2025-12-01',
    '2026-2027',
    'For published creative writers demonstrating exceptional talent in prose or poetry. Highly competitive. Provides time and resources for writers to continue their craft.',
    'https://www.arts.gov/grants/creative-writing-fellowships',
    NULL,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/nea_creative_writing_fellowship.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 8. Disney Dreamers Academy
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Disney Dreamers Academy',
    'Walt Disney Company',
    'ARTS',
    'ACTIVE',
    'HARD',
    0,
    5000,
    false,
    100,
    '2025-10-31',
    '2025-08-01',
    '2026-2027',
    'All-expense-paid mentorship program at Walt Disney World for high school students interested in performing arts, animation, media, and entertainment. Includes career workshops and networking.',
    'https://www.disneydreamersacademy.com/',
    2.75,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/disney_dreamers_academy.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 9. AIGA Worldstudio Scholarships
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'AIGA Worldstudio Scholarships',
    'AIGA',
    'ARTS',
    'ACTIVE',
    'MODERATE',
    2000,
    6000,
    false,
    25,
    '2026-04-15',
    '2026-01-01',
    '2026-2027',
    'For minority and economically disadvantaged students pursuing degrees in design and visual arts. Focus on students using design for social good. Portfolio submission required.',
    'https://www.aiga.org/membership-community/worldstudio-scholarship',
    2.50,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/aiga_worldstudio_scholarships.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 10. BMI Student Composer Awards
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'BMI Student Composer Awards',
    'BMI Foundation',
    'ARTS',
    'ACTIVE',
    'HARD',
    500,
    5000,
    false,
    20,
    '2026-02-01',
    '2025-11-01',
    '2026-2027',
    'For young composers under age 28. Submit original classical music composition. One of oldest competitions for student composers. Past winners include many now-famous composers.',
    'https://www.bmifoundation.org/programs/bmi-student-composer-awards',
    NULL,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/bmi_student_composer_awards.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 11. National Federation of Music Clubs Scholarships
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'NFMC Scholarships',
    'National Federation of Music Clubs',
    'ARTS',
    'ACTIVE',
    'MODERATE',
    1000,
    10000,
    false,
    75,
    '2026-03-01',
    '2025-12-01',
    '2026-2027',
    'Multiple scholarships for music students in various categories including vocal, instrumental, and composition. Must be NFMC member. Awards range by competition category and age group.',
    'https://www.nfmc-music.org/competitions-awards/',
    3.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/nfmc_scholarships.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 12. Hagan Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Hagan Scholarship',
    'Hagan Scholarship Foundation',
    'ARTS',
    'ACTIVE',
    'HARD',
    6000,
    48000,
    true,
    600,
    '2025-12-01',
    '2025-09-01',
    '2026-2027',
    'For rural high school graduates pursuing any field including arts. Eight-semester scholarship worth up to $48,000 total. Includes mentorship, career guidance, and enrichment opportunities.',
    'https://haganscholarships.org/',
    3.50,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/hagan_scholarship.jpg',
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
-- WHERE id > 30 
-- ORDER BY id;

-- ============================================================================
-- Summary - Batch 3
-- ============================================================================
-- Total scholarships added: 12 (IDs 31-42)
-- Theme: ARTS - Music, Visual Arts, Performing Arts, Creative Writing
-- 
-- Scholarship types distribution:
--   - ARTS: 12
-- 
-- Difficulty distribution:
--   - VERY_HARD: 3 (YoungArts, Princess Grace, NEA)
--   - HARD: 4 (ASCAP, Disney, BMI, Hagan)
--   - MODERATE: 5 (Scholastic, NAfME, VSA, AIGA, NFMC)
--   - EASY: 0
--
-- Featured scholarships: 4 (YoungArts, Scholastic, Princess Grace, Hagan)
-- All verified: Yes
-- Amount range: $0 - $48,000
-- Total scholarships in database after import: 42
-- ============================================================================
