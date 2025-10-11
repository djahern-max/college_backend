-- Arkansas Tuition Data Insert Statements
-- Run these on your LOCAL database (magicscholar_db) first, then copy to production

-- 1. Arkansas State University (IPEDS: 106458)
-- Data: 2024-2025, Semester rates converted to annual (x2)
INSERT INTO tuition_data (
    ipeds_id, academic_year, data_source,
    tuition_in_state, tuition_out_state,
    tuition_fees_in_state, tuition_fees_out_state,
    room_board_on_campus, books_supplies,
    has_tuition_data, has_fees_data, has_living_data,
    data_completeness_score, validation_status,
    created_at, updated_at
) VALUES (
    106458, '2024-2025', 'institution_website',
    10430, 18740,  -- Annual tuition (semester x 2)
    10430, 18740,  -- Combined tuition+fees (same as tuition, fees included)
    6550,          -- Room & board annual (using lower estimate: $3,275 x 2)
    NULL,          -- Books not specified
    true, true, true,
    85, 'VALIDATED',
    NOW(), NOW()
);

-- 2. Arkansas Tech University (IPEDS: 106467)
-- Data: 2025-2026, Semester rates converted to annual
INSERT INTO tuition_data (
    ipeds_id, academic_year, data_source,
    tuition_in_state, tuition_out_state,
    tuition_fees_in_state, tuition_fees_out_state,
    room_board_on_campus, books_supplies,
    has_tuition_data, has_fees_data, has_living_data,
    data_completeness_score, validation_status,
    created_at, updated_at
) VALUES (
    106467, '2025-2026', 'institution_website',
    6174,   -- Annual tuition in-state ($3,087.24 x 2)
    12349,  -- Annual tuition out-state ($6,174.48 x 2)
    6174,   -- Combined (tuition already includes fees)
    12349,  -- Combined (tuition already includes fees)
    9852,   -- Annual room & board
    1240,   -- Annual books & supplies
    true, true, true,
    100, 'VALIDATED',
    NOW(), NOW()
);

-- 3. Harding University (IPEDS: 107044)
-- Data: 2024-2025, Private school (same for in/out of state)
INSERT INTO tuition_data (
    ipeds_id, academic_year, data_source,
    tuition_in_state, tuition_out_state,
    tuition_fees_in_state, tuition_fees_out_state,
    room_board_on_campus, books_supplies,
    has_tuition_data, has_fees_data, has_living_data,
    data_completeness_score, validation_status,
    created_at, updated_at
) VALUES (
    107044, '2024-2025', 'institution_website',
    26490, 26490,  -- Private university, same tuition
    27282, 27282,  -- Tuition + technology fee ($26,490 + $792)
    10124,         -- Housing + food ($4,924 + $5,200)
    NULL,          -- Books vary by program
    true, true, true,
    90, 'VALIDATED',
    NOW(), NOW()
);

-- 4. Henderson State University (IPEDS: 107071)
-- Data: 2025-2026, Per credit hour converted to 30 credit hours annual
INSERT INTO tuition_data (
    ipeds_id, academic_year, data_source,
    tuition_in_state, tuition_out_state,
    tuition_fees_in_state, tuition_fees_out_state,
    room_board_on_campus, books_supplies,
    has_tuition_data, has_fees_data, has_living_data,
    data_completeness_score, validation_status,
    created_at, updated_at
) VALUES (
    107071, '2025-2026', 'institution_website',
    8250,  -- In-state: $275 x 30 credit hours
    11310, -- Out-of-state: $377 x 30 credit hours
    8250,  -- Combined (tuition only, no separate fees listed)
    11310, -- Combined
    NULL,  -- Room & board not specified
    NULL,  -- Books not specified
    true, false, false,
    50, 'VALIDATED',
    NOW(), NOW()
);

-- 5. John Brown University (IPEDS: 107141)
-- Data: Current year, Private school
INSERT INTO tuition_data (
    ipeds_id, academic_year, data_source,
    tuition_in_state, tuition_out_state,
    tuition_fees_in_state, tuition_fees_out_state,
    room_board_on_campus, books_supplies,
    has_tuition_data, has_fees_data, has_living_data,
    data_completeness_score, validation_status,
    created_at, updated_at
) VALUES (
    107141, '2024-2025', 'institution_website',
    32710, 32710,  -- Private university, same rate
    32710, 32710,  -- Tuition+fees combined
    10189,         -- Room & board
    800,           -- Books & supplies
    true, true, true,
    100, 'VALIDATED',
    NOW(), NOW()
);

-- 6. Southern Arkansas University Main Campus (IPEDS: 107983)
-- Data: 2023-2024 (older data available)
INSERT INTO tuition_data (
    ipeds_id, academic_year, data_source,
    tuition_in_state, tuition_out_state,
    tuition_fees_in_state, tuition_fees_out_state,
    room_board_on_campus, books_supplies,
    has_tuition_data, has_fees_data, has_living_data,
    data_completeness_score, validation_status,
    created_at, updated_at
) VALUES (
    107983, '2023-2024', 'institution_website',
    10200, 16080,  -- Tuition & fees
    10200, 16080,  -- Combined
    NULL,          -- Room & board not specified
    NULL,          -- Books not specified
    true, true, false,
    60, 'VALIDATED',
    NOW(), NOW()
);

-- 7. University of Arkansas (IPEDS: 106397)
-- Data: 2024-2025
INSERT INTO tuition_data (
    ipeds_id, academic_year, data_source,
    tuition_in_state, tuition_out_state,
    tuition_fees_in_state, tuition_fees_out_state,
    room_board_on_campus, books_supplies,
    has_tuition_data, has_fees_data, has_living_data,
    data_completeness_score, validation_status,
    created_at, updated_at
) VALUES (
    106397, '2024-2025', 'institution_website',
    10496, 31550,  -- Tuition (fees included based on description)
    10496, 31550,  -- Combined
    10758,         -- Room & board (double occupancy, Founders Hall)
    NULL,          -- Books not specified
    true, true, true,
    85, 'VALIDATED',
    NOW(), NOW()
);

-- 8. University of Arkansas Community College-Morrilton (IPEDS: 107585)
-- Data: Current year, Per credit hour converted to 30 credit hours
INSERT INTO tuition_data (
    ipeds_id, academic_year, data_source,
    tuition_in_state, tuition_out_state,
    required_fees_in_state, required_fees_out_state,
    tuition_fees_in_state, tuition_fees_out_state,
    room_board_on_campus, books_supplies,
    has_tuition_data, has_fees_data, has_living_data,
    data_completeness_score, validation_status,
    created_at, updated_at
) VALUES (
    107585, '2024-2025', 'institution_website',
    3150,  -- Tuition: $105 x 30 credit hours
    3150,  -- Community college, typically same for in/out (update if you find out-of-state rate)
    1410,  -- Fees: $47 x 30 credit hours
    1410,
    4560,  -- Combined tuition+fees
    4560,
    NULL,  -- Community college typically no on-campus housing
    NULL,  -- Books not specified
    true, true, false,
    70, 'VALIDATED',
    NOW(), NOW()
);

-- 9. University of Arkansas at Little Rock (IPEDS: 106245)
-- Data: 2025-2026, Out-of-state provided, estimated in-state
INSERT INTO tuition_data (
    ipeds_id, academic_year, data_source,
    tuition_in_state, tuition_out_state,
    tuition_fees_in_state, tuition_fees_out_state,
    room_board_on_campus, books_supplies,
    has_tuition_data, has_fees_data, has_living_data,
    data_completeness_score, validation_status,
    created_at, updated_at
) VALUES (
    106245, '2025-2026', 'institution_website',
    NULL,   -- In-state not specified (would need to research)
    22870,  -- Out-of-state tuition & fees
    NULL,
    22870,  -- Combined
    7606,   -- Room & board
    1800,   -- Books & supplies
    true, true, true,
    75, 'NEEDS_REVIEW',  -- Marked for review since in-state missing
    NOW(), NOW()
);

-- 10. University of Arkansas at Pine Bluff (IPEDS: 106412)
-- Data: Current year
INSERT INTO tuition_data (
    ipeds_id, academic_year, data_source,
    tuition_in_state, tuition_out_state,
    tuition_fees_in_state, tuition_fees_out_state,
    room_board_on_campus, books_supplies,
    has_tuition_data, has_fees_data, has_living_data,
    data_completeness_score, validation_status,
    created_at, updated_at
) VALUES (
    106412, '2024-2025', 'institution_website',
    9019,  -- In-state tuition
    17029, -- Out-of-state tuition
    9019,  -- Combined (appears to be tuition+fees already)
    17029,
    NULL,  -- Room & board not specified
    NULL,  -- Books not specified
    true, true, false,
    60, 'VALIDATED',
    NOW(), NOW()
);

-- 11. University of Arkansas-Fort Smith (IPEDS: 108092)
-- Data: 2024-2025
INSERT INTO tuition_data (
    ipeds_id, academic_year, data_source,
    tuition_in_state, tuition_out_state,
    tuition_fees_in_state, tuition_fees_out_state,
    room_board_on_campus, books_supplies,
    has_tuition_data, has_fees_data, has_living_data,
    data_completeness_score, validation_status,
    created_at, updated_at
) VALUES (
    108092, '2024-2025', 'institution_website',
    9826,  -- In-state tuition & fees (30 credit hours)
    15226, -- Out-of-state tuition & fees
    9826,  -- Combined
    15226,
    NULL,  -- Room & board not specified
    NULL,  -- Books not specified
    true, true, false,
    60, 'VALIDATED',
    NOW(), NOW()
);

-- 12. University of Central Arkansas (IPEDS: 106704)
-- Data: 2024-2025
INSERT INTO tuition_data (
    ipeds_id, academic_year, data_source,
    tuition_in_state, tuition_out_state,
    tuition_fees_in_state, tuition_fees_out_state,
    room_board_on_campus, books_supplies,
    has_tuition_data, has_fees_data, has_living_data,
    data_completeness_score, validation_status,
    created_at, updated_at
) VALUES (
    106704, '2024-2025', 'institution_website',
    10523, 18023,  -- Tuition & fees
    10523, 18023,  -- Combined
    9552,          -- Housing & meals
    1216,          -- Books
    true, true, true,
    100, 'VALIDATED',
    NOW(), NOW()
);

-- Verification Query: Run this after inserting to check your data
SELECT 
    i.name,
    t.academic_year,
    t.tuition_fees_in_state,
    t.tuition_fees_out_state,
    t.room_board_on_campus,
    t.books_supplies,
    t.data_completeness_score
FROM institutions i
JOIN tuition_data t ON i.ipeds_id = t.ipeds_id
WHERE i.state = 'AR'
ORDER BY i.name;
