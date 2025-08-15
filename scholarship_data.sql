
-- Insert Courage to Grow Scholarship into the scholarships table
INSERT INTO scholarships (
    title,
    description,
    provider,
    amount_exact,
    renewable,
    max_renewals,
    deadline,
    application_url,
    contact_email,
    eligibility_criteria,
    required_documents,
    academic_requirements,
    demographic_criteria,
    categories,
    scholarship_type,
    keywords,
    status,
    external_id,
    source,
    source_url,
    verified,
    last_verified
) VALUES (
    'Courage to Grow Scholarship',
    'The Courage to Grow Scholarship was created to help students realize their college dreams by taking away some of the financial concerns surrounding college. The scholarship evaluates students on their academics and requires a thoughtful essay about why they deserve the scholarship. This monthly scholarship helps students accomplish their higher education goals and wants to shoulder some of the financial burdens that students and their families face so that they can concentrate on their future.',
    'Courage to Grow',
    1000.00,  -- Based on official website showing $1,000 (some sources show $500 monthly)
    false,
    null,
    '2025-09-30',  -- September 30, 2025 deadline from official website
    'https://couragetogrowscholarship.com/',
    'info@couragetogrowscholarship.com',
    '{
        "location": ["United States"],
        "grade_level": ["High School Junior", "High School Senior", "College Student"],
        "requirements": [
            "Must be a U.S. citizen",
            "Must be a junior or senior in high school OR college student",
            "Minimum GPA of 2.5 or better",
            "Must submit 250-word essay explaining why they deserve the scholarship"
        ]
    }'::json,
    '{
        "documents": [
            "Online application form",
            "Essay (250 words maximum) explaining why applicant deserves the scholarship"
        ]
    }'::json,
    '{
        "gpa_minimum": 2.5,
        "academic_focus": "All fields of study",
        "grade_levels": ["High School Junior", "High School Senior", "College Student"]
    }'::json,
    '{
        "citizenship": ["U.S. Citizens only"],
        "age_group": "High school juniors/seniors and college students",
        "special_populations": []
    }'::json,
    '["Merit-Based", "Essay-Based", "General Academic", "Monthly Opportunity", "Low GPA Requirement"]'::json,
    'MERIT',
    '["Courage to Grow", "essay scholarship", "monthly scholarship", "2.5 GPA", "high school", "college", "merit-based", "$1000", "U.S. citizens", "general scholarship", "educational support"]'::json,
    'ACTIVE',
    'CTG-2025',
    'Courage to Grow',
    'https://couragetogrowscholarship.com/',
    true,
    CURRENT_DATE
);


-- Insert Chick-fil-A Community Scholars scholarship into the scholarships table
INSERT INTO scholarships (
    title,
    description,
    provider,
    amount_exact,
    renewable,
    max_renewals,
    deadline,
    start_date,
    end_date,
    application_url,
    contact_email,
    eligibility_criteria,
    required_documents,
    academic_requirements,
    demographic_criteria,
    categories,
    scholarship_type,
    keywords,
    status,
    external_id,
    source,
    source_url,
    verified,
    last_verified,
    application_count
) VALUES (
    'Chick-fil-A Community Scholars',
    'Through the Chick-fil-A Community Scholars program, Chick-fil-A, Inc. helps pay for the education of leaders in our communities who want to continue learning. Every year, at least twelve $25,000 scholarships are awarded to students based on academic success, community service and financial need. The Chick-fil-A Community Scholars also participate in the Chick-fil-A Scholars Program, a one-year engagement that includes mentoring and leadership development alongside Chick-fil-A True Inspiration Scholars. This program recognizes remarkable individuals who share dedication to caring for others and caring for their communities.',
    'Chick-fil-A, Inc.',
    25000.00,
    false,
    null,
    '2025-11-01',  -- November 2025 application deadline
    '2026-07-01',  -- July 2026 award distribution
    '2027-06-30',  -- Estimated one-year scholarship period end
    'https://www.chick-fil-a.com/community-scholars',
    null,  -- No specific contact email provided in sources
    '{
        "location": ["United States", "Puerto Rico", "Canada"],
        "grade_level": ["Undergraduate Student", "Graduate Student", "Planning to Enroll"],
        "requirements": [
            "Must be a resident of the United States, Puerto Rico, or Canada",
            "Must be a postsecondary undergraduate or graduate student OR planning to enroll in undergraduate or graduate study",
            "Must attend accredited two- or four-year college, university or vocational-technical school",
            "Minimum cumulative GPA of 3.0 on a 4.0 scale (or equivalent)",
            "Must demonstrate financial need",
            "Must demonstrate community service and impact over the past 12 months",
            "Must be recommended by a teacher, coach, community leader or mentor",
            "Cannot be employed at Chick-fil-A restaurant or Chick-fil-A, Inc. at time of application",
            "Cannot be dependent or spouse of Chick-fil-A, Inc. employee or operator"
        ]
    }'::json,
    '{
        "documents": [
            "Online application form",
            "Official transcript showing name, school name, GPA, and credit hours for each class",
            "Recommendation from teacher, coach, community leader or mentor addressing personal/professional achievement",
            "Financial need documentation",
            "Community service and impact documentation"
        ]
    }'::json,
    '{
        "gpa_minimum": 3.0,
        "gpa_scale": 4.0,
        "academic_focus": "All fields of study",
        "institution_types": ["Two-year college", "Four-year college", "University", "Vocational-technical school"],
        "accreditation_required": true
    }'::json,
    '{
        "citizenship": ["U.S. residents", "Puerto Rico residents", "Canada residents"],
        "age_group": "Undergraduate and graduate students",
        "employment_restrictions": ["Cannot work at Chick-fil-A", "Cannot be family member of Chick-fil-A employee"],
        "special_populations": ["Community service participants", "Students with financial need"]
    }'::json,
    '["Merit-Based", "Need-Based", "Community Service", "Leadership Development", "High Award Amount", "Mentoring Program", "Corporate Sponsored"]'::json,
    'MERIT',
    '["Chick-fil-A", "community scholars", "leadership", "mentoring", "$25000", "community service", "financial need", "3.0 GPA", "corporate scholarship", "remarkable futures", "academic achievement", "caring for others"]'::json,
    'ACTIVE',
    'CFA-CS-2026',
    'Chick-fil-A, Inc.',
    'https://www.chick-fil-a.com/community-scholars',
    true,
    CURRENT_DATE,
    12  
);