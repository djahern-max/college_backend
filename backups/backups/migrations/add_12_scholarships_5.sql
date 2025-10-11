-- ============================================================================
-- Add 12 MILITARY Scholarships to MagicScholar Database
-- File: add_12_scholarships_5.sql
-- Batch: 5 of 10
-- Created: 2025-10-11
-- Theme: Military, Veterans, Service Members, Military Families
-- ============================================================================

-- Start transaction
BEGIN;

-- ============================================================================
-- 1. Army ROTC Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Army ROTC Scholarship',
    'U.S. Army',
    'MILITARY',
    'ACTIVE',
    'HARD',
    10000,
    80000,
    true,
    4000,
    '2026-01-10',
    '2025-06-01',
    '2026-2027',
    'Full tuition or room and board plus monthly stipend for students participating in Army ROTC. Requires military service commitment after graduation. Available at over 1,100 colleges nationwide.',
    'https://www.goarmy.com/careers-and-jobs/find-your-path/army-officers/rotc/scholarships.html',
    2.50,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/army_rotc_scholarship.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 2. Navy ROTC Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Navy ROTC Scholarship',
    'U.S. Navy',
    'MILITARY',
    'ACTIVE',
    'HARD',
    15000,
    80000,
    true,
    2400,
    '2026-01-31',
    '2025-07-01',
    '2026-2027',
    'Covers full tuition and fees or room and board, plus monthly stipend and book allowance. For students pursuing technical majors or nursing. Requires service commitment as Navy officer.',
    'https://www.navy.com/education-opportunities/nrotc-scholarships',
    2.50,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/navy_rotc_scholarship.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 3. Air Force ROTC Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Air Force ROTC Scholarship',
    'U.S. Air Force',
    'MILITARY',
    'ACTIVE',
    'HARD',
    9000,
    54000,
    true,
    2000,
    '2026-01-16',
    '2025-06-01',
    '2026-2027',
    'Type 1, 2, and 7 scholarships covering full or partial tuition plus monthly stipend. Preference for STEM and critical foreign language majors. Requires service as Air Force officer.',
    'https://www.afrotc.com/scholarships/',
    3.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/air_force_rotc_scholarship.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 4. Marine Corps Scholarship Foundation
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Marine Corps Scholarship Foundation',
    'Marine Corps Scholarship Foundation',
    'MILITARY',
    'ACTIVE',
    'MODERATE',
    1500,
    10000,
    true,
    3300,
    '2026-03-01',
    '2026-01-01',
    '2026-2027',
    'For children of Marines and Navy Corpsmen. Based on financial need and merit. No service obligation. One of largest providers of need-based scholarships for military children.',
    'https://www.mcsf.org/',
    2.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/marine_corps_scholarship_foundation.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 5. Veterans of Foreign Wars Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'VFW Voice of Democracy Scholarship',
    'Veterans of Foreign Wars',
    'MILITARY',
    'ACTIVE',
    'MODERATE',
    1000,
    35000,
    false,
    54,
    '2025-10-31',
    '2025-08-01',
    '2026-2027',
    'Audio essay competition for high school students on patriotic theme. Top national winner receives $35,000. Open to all students grades 9-12. Theme changes annually.',
    'https://www.vfw.org/community/youth-and-education/youth-scholarships',
    NULL,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/vfw_voice_of_democracy_scholarship.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 6. American Legion Auxiliary Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'American Legion Auxiliary Scholarship',
    'American Legion Auxiliary',
    'MILITARY',
    'ACTIVE',
    'MODERATE',
    1000,
    5000,
    false,
    100,
    '2026-03-01',
    '2025-12-01',
    '2026-2027',
    'For children or grandchildren of veterans who served during wartime. Multiple scholarships available. Based on academics, financial need, and commitment to serving community.',
    'https://www.alaforveterans.org/Scholarships/',
    3.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/american_legion_auxiliary_scholarship.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 7. Pat Tillman Foundation Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Pat Tillman Foundation Scholarship',
    'Pat Tillman Foundation',
    'MILITARY',
    'ACTIVE',
    'VERY_HARD',
    5000,
    10000,
    false,
    60,
    '2026-02-28',
    '2025-12-01',
    '2026-2027',
    'For active-duty service members, veterans, and military spouses pursuing higher education. Focuses on academic excellence, leadership, and service. Named after NFL player who died in service.',
    'https://pattillmanfoundation.org/apply-for-a-scholarship/',
    3.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/pat_tillman_foundation_scholarship.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 8. Military Order of the Purple Heart Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Military Order of the Purple Heart Scholarship',
    'Military Order of the Purple Heart',
    'MILITARY',
    'ACTIVE',
    'MODERATE',
    5000,
    5000,
    false,
    83,
    '2026-02-17',
    '2025-11-01',
    '2026-2027',
    'For children, grandchildren, great-grandchildren, or spouses of Purple Heart recipients. Recognizes sacrifice of wounded and killed service members and their families.',
    'https://www.purpleheart.org/scholarships/',
    2.75,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/military_order_of_the_purple_heart_scholarship.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 9. AMVETS National Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'AMVETS National Scholarship',
    'AMVETS',
    'MILITARY',
    'ACTIVE',
    'MODERATE',
    1000,
    4000,
    false,
    7,
    '2026-04-30',
    '2026-01-01',
    '2026-2027',
    'For veterans, active-duty military, National Guard, Reserves, and their dependents. Must be graduating high school senior or current college student pursuing undergraduate degree.',
    'https://www.amvets.org/scholarships/',
    2.50,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/amvets_national_scholarship.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 10. Daughters of the American Revolution Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'DAR Scholarship',
    'Daughters of the American Revolution',
    'MILITARY',
    'ACTIVE',
    'MODERATE',
    1000,
    5000,
    false,
    50,
    '2026-02-15',
    '2025-11-01',
    '2026-2027',
    'Multiple scholarships for various fields including nursing, education, and general studies. Some specifically for children of veterans or ROTC participants. Each scholarship has specific requirements.',
    'https://www.dar.org/national-society/scholarships',
    3.25,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/dar_scholarship.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 11. Chief Petty Officer Scholarship Fund
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Chief Petty Officer Scholarship Fund',
    'Chief Petty Officer Scholarship Fund',
    'MILITARY',
    'ACTIVE',
    'MODERATE',
    1000,
    5000,
    false,
    100,
    '2026-04-01',
    '2026-01-01',
    '2026-2027',
    'For dependents of active duty, reserve, or retired Navy and Coast Guard personnel. Must be high school senior or current college student. Based on academics, character, and financial need.',
    'https://www.cposcholarshipfund.org/',
    2.50,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/chief_petty_officer_scholarship_fund.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 12. Fisher House Foundation Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Fisher House Foundation Scholarship',
    'Fisher House Foundation',
    'MILITARY',
    'ACTIVE',
    'MODERATE',
    2000,
    5000,
    false,
    100,
    '2026-03-15',
    '2025-12-01',
    '2026-2027',
    'For children of service members who are receiving or have received medical care at military or VA medical centers. Recognizes families supporting wounded, ill, and injured service members.',
    'https://www.fisherhouse.org/programs/scholarships-for-military-children/',
    3.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/fisher_house_foundation_scholarship.jpg',
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
-- WHERE id > 54 
-- ORDER BY id;

-- ============================================================================
-- Summary - Batch 5
-- ============================================================================
-- Total scholarships added: 12 (IDs 55-66)
-- Theme: MILITARY - Veterans, Service Members, Military Families
-- 
-- Scholarship types distribution:
--   - MILITARY: 12
-- 
-- Difficulty distribution:
--   - VERY_HARD: 1 (Pat Tillman)
--   - HARD: 3 (Army ROTC, Navy ROTC, Air Force ROTC)
--   - MODERATE: 8 (Marine Corps, VFW, American Legion, Purple Heart, AMVETS, DAR, CPO, Fisher House)
--   - EASY: 0
--
-- ROTC vs Non-ROTC:
--   - ROTC (service commitment): 3
--   - Non-ROTC (no service): 9
--
-- Featured scholarships: 5 (Army ROTC, Navy ROTC, Air Force ROTC, Marine Corps, Pat Tillman)
-- All verified: Yes
-- Amount range: $1,000 - $80,000
-- Total scholarships in database after import: 66
-- ============================================================================
