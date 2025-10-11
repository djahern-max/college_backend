-- ============================================================================
-- Add 12 STEM & Technology Scholarships to MagicScholar Database
-- File: add_12_scholarships_2.sql
-- Batch: 2 of 10
-- Created: 2025-10-11
-- Theme: STEM, Technology, Engineering, Computer Science
-- ============================================================================

-- Start transaction
BEGIN;

-- ============================================================================
-- 1. Google Generation Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Google Generation Scholarship',
    'Google',
    'STEM',
    'ACTIVE',
    'HARD',
    10000,
    10000,
    true,
    NULL,
    '2025-12-04',
    '2025-09-01',
    '2026-2027',
    'For women in computer science and gaming. Includes mentorship opportunities and invitation to Google annual retreat. Open to undergraduate and graduate students.',
    'https://buildyourfuture.withgoogle.com/scholarships/generation-google-scholarship',
    3.50,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/google_generation_scholarship.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 2. Microsoft Tuition Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Microsoft Tuition Scholarship',
    'Microsoft',
    'STEM',
    'ACTIVE',
    'HARD',
    12000,
    12000,
    true,
    50,
    '2026-01-30',
    '2025-10-01',
    '2026-2027',
    'For students pursuing degrees in computer science, computer engineering, or related STEM disciplines. Preference given to students who demonstrate financial need.',
    'https://www.microsoft.com/en-us/diversity/programs/scholarships',
    3.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/microsoft_tuition_scholarship.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 3. Society of Women Engineers Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Society of Women Engineers Scholarship',
    'Society of Women Engineers',
    'STEM',
    'ACTIVE',
    'MODERATE',
    1000,
    15000,
    false,
    260,
    '2026-02-15',
    '2025-12-01',
    '2026-2027',
    'Multiple scholarships for women pursuing ABET-accredited engineering, technology, or computing programs. Awards range based on academic level and financial need.',
    'https://swe.org/scholarships/',
    3.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/society_of_women_engineers_scholarship.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 4. NSBE Scholars Program
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'NSBE Scholars Program',
    'National Society of Black Engineers',
    'STEM',
    'ACTIVE',
    'MODERATE',
    500,
    10000,
    false,
    300,
    '2026-01-31',
    '2025-10-01',
    '2026-2027',
    'For Black/African American students pursuing degrees in engineering, computer science, or related fields. Must be NSBE member or willing to join.',
    'https://www.nsbe.org/Programs-Services/Scholarships-and-Fellowships.aspx',
    3.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/nsbe_scholars_program.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 5. Palantir Women in Technology Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Palantir Women in Technology Scholarship',
    'Palantir Technologies',
    'STEM',
    'ACTIVE',
    'VERY_HARD',
    7000,
    7000,
    false,
    15,
    '2025-11-15',
    '2025-09-01',
    '2026-2027',
    'For undergraduate women studying computer science or related technical fields. Winners receive scholarship plus trip to Palantir headquarters for mentorship and networking.',
    'https://www.palantir.com/students/scholarship/wit-north-america/',
    3.30,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/palantir_women_in_technology_scholarship.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 6. SHPE Scholarship Program
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'SHPE Scholarship Program',
    'Society of Hispanic Professional Engineers',
    'STEM',
    'ACTIVE',
    'MODERATE',
    1000,
    5000,
    false,
    200,
    '2026-04-30',
    '2026-01-01',
    '2026-2027',
    'For Hispanic students pursuing engineering, math, science, or technology degrees. Must be SHPE member. Multiple scholarship levels available.',
    'https://www.shpe.org/students/scholarships',
    3.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/shpe_scholarship_program.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 7. IEEE Presidents' Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'IEEE Presidents'' Scholarship',
    'Institute of Electrical and Electronics Engineers',
    'STEM',
    'ACTIVE',
    'HARD',
    10000,
    10000,
    false,
    1,
    '2026-05-31',
    '2026-01-01',
    '2026-2027',
    'Single prestigious award for an undergraduate student in electrical engineering, electronics, or computer science with demonstrated leadership and involvement in IEEE activities.',
    'https://www.ieee.org/membership/students/awards/presidents-scholarship.html',
    3.50,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/ieee_presidents_scholarship.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 8. SMART Scholarship for Service Program
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'SMART Scholarship for Service Program',
    'Department of Defense',
    'STEM',
    'ACTIVE',
    'VERY_HARD',
    25000,
    50000,
    true,
    200,
    '2025-12-01',
    '2025-08-01',
    '2026-2027',
    'Full scholarship for STEM students. Covers full tuition, stipend, summer internships, and mentorship. Requires post-graduation employment with Department of Defense.',
    'https://www.smartscholarship.org/',
    3.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/smart_scholarship_for_service_program.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 9. NASA Space Grant Scholarships
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'NASA Space Grant Scholarships',
    'NASA',
    'STEM',
    'ACTIVE',
    'HARD',
    2000,
    8000,
    true,
    NULL,
    '2026-03-31',
    '2025-12-01',
    '2026-2027',
    'For students pursuing aerospace, engineering, or STEM fields. Awards and deadlines vary by state consortium. Check your state Space Grant office for specific requirements.',
    'https://www.nasa.gov/stem/spacegrant/about/index.html',
    3.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/nasa_space_grant_scholarships.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 10. Barry Goldwater Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Barry Goldwater Scholarship',
    'Barry Goldwater Scholarship Foundation',
    'STEM',
    'ACTIVE',
    'VERY_HARD',
    7500,
    7500,
    true,
    400,
    '2026-01-27',
    '2025-09-01',
    '2026-2027',
    'Prestigious award for sophomores and juniors pursuing research careers in natural sciences, mathematics, or engineering. One of the most competitive undergraduate STEM scholarships.',
    'https://goldwaterscholarship.gov/',
    3.70,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/barry_goldwater_scholarship.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 11. American Indian Science and Engineering Society Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'AISES Scholarship',
    'American Indian Science and Engineering Society',
    'STEM',
    'ACTIVE',
    'MODERATE',
    1000,
    5000,
    false,
    200,
    '2026-05-31',
    '2026-02-01',
    '2026-2027',
    'For Native American students pursuing degrees in STEM fields. Must be AISES member and demonstrate commitment to Native American community.',
    'https://www.aises.org/scholarships',
    3.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/aises_scholarship.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 12. Astronaut Scholarship Foundation
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Astronaut Scholarship',
    'Astronaut Scholarship Foundation',
    'STEM',
    'ACTIVE',
    'VERY_HARD',
    15000,
    15000,
    false,
    60,
    '2025-12-31',
    '2025-09-01',
    '2026-2027',
    'For exceptional undergraduate juniors and seniors in STEM fields who intend to pursue research careers. Students must be nominated by faculty at participating institutions.',
    'https://www.astronautscholarship.org/',
    3.50,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/astronaut_scholarship.jpg',
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
-- WHERE id > 18 
-- ORDER BY id;

-- ============================================================================
-- Summary - Batch 2
-- ============================================================================
-- Total scholarships added: 12 (IDs 19-30)
-- Theme: STEM & Technology
-- 
-- Scholarship types distribution:
--   - STEM: 12 (all focused on technology, engineering, computer science)
-- 
-- Difficulty distribution:
--   - VERY_HARD: 4 (Palantir, SMART, Barry Goldwater, Astronaut)
--   - HARD: 3 (Google Generation, Microsoft, IEEE, NASA)
--   - MODERATE: 5 (SWE, NSBE, SHPE, AISES)
--   - EASY: 0
--
-- Featured scholarships: 4 (Google Generation, Microsoft, SMART, Barry Goldwater)
-- All verified: Yes
-- Amount range: $500 - $50,000
-- Total scholarships in database after import: 30
-- ============================================================================
