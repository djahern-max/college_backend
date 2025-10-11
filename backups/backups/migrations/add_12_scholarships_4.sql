-- ============================================================================
-- Add 12 ATHLETIC Scholarships to MagicScholar Database
-- File: add_12_scholarships_4.sql
-- Batch: 4 of 10
-- Created: 2025-10-11
-- Theme: Athletic, Sports, Student-Athletes
-- ============================================================================

-- Start transaction
BEGIN;

-- ============================================================================
-- 1. NCAA Division I Athletic Scholarships
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'NCAA Division I Athletic Scholarships',
    'National Collegiate Athletic Association',
    'ATHLETIC',
    'ACTIVE',
    'VERY_HARD',
    1000,
    70000,
    true,
    NULL,
    '2026-05-01',
    '2025-07-01',
    '2026-2027',
    'Full and partial athletic scholarships for exceptional student-athletes competing at Division I level. Covers tuition, fees, room, board, and books. Must meet NCAA eligibility requirements.',
    'https://www.ncaa.org/sports/2015/6/26/scholarships.aspx',
    2.30,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/ncaa_division_i_athletic_scholarships.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 2. NAIA Athletic Scholarships
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'NAIA Athletic Scholarships',
    'National Association of Intercollegiate Athletics',
    'ATHLETIC',
    'ACTIVE',
    'HARD',
    1000,
    50000,
    true,
    NULL,
    '2026-05-01',
    '2025-07-01',
    '2026-2027',
    'Athletic scholarships for student-athletes at NAIA institutions. More flexible eligibility requirements than NCAA. Scholarships can be combined with academic awards.',
    'https://www.naia.org/',
    2.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/naia_athletic_scholarships.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 3. NCAA Postgraduate Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'NCAA Postgraduate Scholarship',
    'National Collegiate Athletic Association',
    'ATHLETIC',
    'ACTIVE',
    'VERY_HARD',
    10000,
    10000,
    false,
    174,
    '2026-01-15',
    '2025-10-01',
    '2026-2027',
    'For student-athletes in final year of eligibility with strong academic records planning to attend graduate school. Recognizes academic achievement and athletic excellence.',
    'https://www.ncaa.org/sports/2013/11/14/postgraduate-scholarship-program.aspx',
    3.20,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/ncaa_postgraduate_scholarship.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 4. NFHS Spirit of Sport Award
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'NFHS Spirit of Sport Award',
    'National Federation of State High School Associations',
    'ATHLETIC',
    'ACTIVE',
    'MODERATE',
    1000,
    1000,
    false,
    8,
    '2026-03-01',
    '2025-12-01',
    '2026-2027',
    'For high school student-athletes who demonstrate exemplary sportsmanship, ethics, integrity, and character. One winner selected per NFHS section across the country.',
    'https://www.nfhs.org/articles/spirit-of-sport-award/',
    3.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/nfhs_spirit_of_sport_award.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 5. Women's Sports Foundation Travel & Training Fund
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Women''s Sports Foundation Travel & Training Fund',
    'Women''s Sports Foundation',
    'ATHLETIC',
    'ACTIVE',
    'MODERATE',
    1000,
    5000,
    false,
    150,
    '2026-04-01',
    '2025-10-01',
    '2026-2027',
    'Grants for female athletes to help cover training, travel, and competition expenses. For athletes with financial need pursuing competitive sports at national or international level.',
    'https://www.womenssportsfoundation.org/programs/travel-training-grants/',
    2.50,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/womens_sports_foundation_travel_training_fund.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 6. Jackie Robinson Foundation Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Jackie Robinson Foundation Scholarship',
    'Jackie Robinson Foundation',
    'ATHLETIC',
    'ACTIVE',
    'VERY_HARD',
    30000,
    30000,
    true,
    60,
    '2026-01-31',
    '2025-10-01',
    '2026-2027',
    'Four-year scholarship for minority high school seniors demonstrating leadership, financial need, and commitment to community service. Named after baseball legend who broke color barrier.',
    'https://www.jackierobinson.org/',
    3.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/jackie_robinson_foundation_scholarship.jpg',
    true,
    true,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 7. All-American Scholar Award
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'All-American Scholar Award',
    'USAG Gymnastics',
    'ATHLETIC',
    'ACTIVE',
    'HARD',
    1000,
    5000,
    false,
    12,
    '2026-02-15',
    '2025-11-01',
    '2026-2027',
    'For high school senior gymnasts competing at Level 9 or 10 who demonstrate athletic excellence and strong academics. Must be USA Gymnastics member planning to attend four-year institution.',
    'https://usagym.org/pages/education/scholarships/',
    3.50,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/all_american_scholar_award.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 8. National Strength and Conditioning Association Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'NSCA Scholarship',
    'National Strength and Conditioning Association',
    'ATHLETIC',
    'ACTIVE',
    'MODERATE',
    1500,
    2500,
    false,
    10,
    '2026-03-15',
    '2025-12-01',
    '2026-2027',
    'For undergraduate students majoring in strength and conditioning or related field. Must be NSCA member and demonstrate career commitment to strength and conditioning profession.',
    'https://www.nsca.com/membership/scholarships/',
    3.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/nsca_scholarship.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 9. Pop Warner Little Scholars Program
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Pop Warner Little Scholars Program',
    'Pop Warner Little Scholars',
    'ATHLETIC',
    'ACTIVE',
    'MODERATE',
    1000,
    2000,
    false,
    100,
    '2026-02-28',
    '2025-11-01',
    '2026-2027',
    'For graduating high school seniors who participated in Pop Warner youth football or cheerleading. Based on academics, community service, and financial need.',
    'https://www.popwarner.com/Default.aspx?tabid=1476649',
    3.00,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/pop_warner_little_scholars_program.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 10. AAU Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'AAU Scholarship',
    'Amateur Athletic Union',
    'ATHLETIC',
    'ACTIVE',
    'MODERATE',
    500,
    2500,
    false,
    50,
    '2026-04-15',
    '2026-01-01',
    '2026-2027',
    'For high school seniors who participated in AAU sports programs. Recognizes academic achievement, athletic participation, and community involvement. Must have been AAU member.',
    'https://aausports.org/page.php?page_id=119854',
    2.80,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/aau_scholarship.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 11. Abe and Annie Seibel Foundation Scholarship
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'Abe and Annie Seibel Foundation Scholarship',
    'Abe and Annie Seibel Foundation',
    'ATHLETIC',
    'ACTIVE',
    'HARD',
    4000,
    4000,
    true,
    10,
    '2026-03-01',
    '2025-12-01',
    '2026-2027',
    'For student-athletes from Texas attending public universities in Texas. Must demonstrate strong academics and athletic participation. Renewable for up to four years with continued eligibility.',
    'https://www.seibelfoundation.org/',
    3.25,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/abe_and_annie_seibel_foundation_scholarship.jpg',
    true,
    false,
    0,
    0,
    NOW()
);

-- ============================================================================
-- 12. NCSAA Scholarship Program
-- ============================================================================
INSERT INTO scholarships (
    title, organization, scholarship_type, status, difficulty_level,
    amount_min, amount_max, is_renewable, number_of_awards,
    deadline, application_opens, for_academic_year,
    description, website_url, min_gpa,
    primary_image_url, verified, featured,
    views_count, applications_count, created_at
) VALUES (
    'NCSAA Scholarship Program',
    'National Christian College Athletic Association',
    'ATHLETIC',
    'ACTIVE',
    'MODERATE',
    1000,
    3000,
    false,
    25,
    '2026-02-01',
    '2025-11-01',
    '2026-2027',
    'For Christian student-athletes attending NCCAA member institutions. Based on athletic ability, academic achievement, Christian character, and financial need.',
    'https://www.thenccaa.org/',
    2.75,
    'https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/ncsaa_scholarship_program.jpg',
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
-- WHERE id > 42 
-- ORDER BY id;

-- ============================================================================
-- Summary - Batch 4
-- ============================================================================
-- Total scholarships added: 12 (IDs 43-54)
-- Theme: ATHLETIC - Sports, Student-Athletes, Athletic Achievement
-- 
-- Scholarship types distribution:
--   - ATHLETIC: 12
-- 
-- Difficulty distribution:
--   - VERY_HARD: 3 (NCAA D1, NCAA Postgrad, Jackie Robinson)
--   - HARD: 3 (NAIA, All-American, Seibel)
--   - MODERATE: 6 (NFHS, WSF, NSCA, Pop Warner, AAU, NCSAA)
--   - EASY: 0
--
-- Featured scholarships: 3 (NCAA D1, NCAA Postgrad, Jackie Robinson)
-- All verified: Yes
-- Amount range: $500 - $70,000
-- Total scholarships in database after import: 54
-- ============================================================================
