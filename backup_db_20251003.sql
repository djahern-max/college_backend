--
-- PostgreSQL database dump
--

-- Dumped from database version 16.9 (Homebrew)
-- Dumped by pg_dump version 16.9 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: collegesize; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.collegesize AS ENUM (
    'VERY_SMALL',
    'SMALL',
    'MEDIUM',
    'LARGE',
    'VERY_LARGE',
    'NO_PREFERENCE'
);


ALTER TYPE public.collegesize OWNER TO postgres;

--
-- Name: controltype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.controltype AS ENUM (
    'PUBLIC',
    'PRIVATE_NONPROFIT',
    'PRIVATE_FOR_PROFIT'
);


ALTER TYPE public.controltype OWNER TO postgres;

--
-- Name: difficultylevel; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.difficultylevel AS ENUM (
    'EASY',
    'MODERATE',
    'HARD',
    'VERY_HARD'
);


ALTER TYPE public.difficultylevel OWNER TO postgres;

--
-- Name: essaystatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.essaystatus AS ENUM (
    'DRAFT',
    'IN_PROGRESS',
    'AI_REVIEW_REQUESTED',
    'AI_REVIEWED',
    'PEER_REVIEW',
    'MENTOR_REVIEW',
    'FINAL',
    'SUBMITTED'
);


ALTER TYPE public.essaystatus OWNER TO postgres;

--
-- Name: essaytype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.essaytype AS ENUM (
    'PERSONAL_STATEMENT',
    'SUPPLEMENTAL',
    'SCHOLARSHIP_SPECIFIC',
    'LEADERSHIP',
    'CHALLENGES_OVERCOME',
    'WHY_MAJOR',
    'WHY_SCHOOL',
    'COMMUNITY_SERVICE',
    'DIVERSITY',
    'CUSTOM'
);


ALTER TYPE public.essaytype OWNER TO postgres;

--
-- Name: imageextractionstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.imageextractionstatus AS ENUM (
    'PENDING',
    'PROCESSING',
    'SUCCESS',
    'FAILED',
    'NEEDS_REVIEW',
    'FALLBACK_APPLIED'
);


ALTER TYPE public.imageextractionstatus OWNER TO postgres;

--
-- Name: incomerange; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.incomerange AS ENUM (
    'UNDER_30K',
    'RANGE_30K_50K',
    'RANGE_50K_75K',
    'RANGE_75K_100K',
    'RANGE_100K_150K',
    'OVER_150K',
    'PREFER_NOT_TO_SAY'
);


ALTER TYPE public.incomerange OWNER TO postgres;

--
-- Name: scholarshipstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.scholarshipstatus AS ENUM (
    'ACTIVE',
    'INACTIVE',
    'EXPIRED',
    'DRAFT',
    'PENDING_REVIEW'
);


ALTER TYPE public.scholarshipstatus OWNER TO postgres;

--
-- Name: scholarshiptype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.scholarshiptype AS ENUM (
    'ACADEMIC_MERIT',
    'NEED_BASED',
    'ATHLETIC',
    'STEM',
    'ARTS',
    'DIVERSITY',
    'FIRST_GENERATION',
    'COMMUNITY_SERVICE',
    'LEADERSHIP',
    'LOCAL_COMMUNITY',
    'EMPLOYER_SPONSORED',
    'MILITARY',
    'RELIGIOUS',
    'CAREER_SPECIFIC',
    'ESSAY_BASED',
    'RENEWABLE'
);


ALTER TYPE public.scholarshiptype OWNER TO postgres;

--
-- Name: sizecategory; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.sizecategory AS ENUM (
    'VERY_SMALL',
    'SMALL',
    'MEDIUM',
    'LARGE',
    'VERY_LARGE'
);


ALTER TYPE public.sizecategory OWNER TO postgres;

--
-- Name: usregion; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.usregion AS ENUM (
    'NEW_ENGLAND',
    'MID_ATLANTIC',
    'EAST_NORTH_CENTRAL',
    'WEST_NORTH_CENTRAL',
    'SOUTH_ATLANTIC',
    'EAST_SOUTH_CENTRAL',
    'WEST_SOUTH_CENTRAL',
    'MOUNTAIN',
    'PACIFIC'
);


ALTER TYPE public.usregion OWNER TO postgres;

--
-- Name: validationstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.validationstatus AS ENUM (
    'PENDING',
    'VALIDATED',
    'NEEDS_REVIEW',
    'FAILED'
);


ALTER TYPE public.validationstatus OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: essay_ai_interactions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.essay_ai_interactions (
    id integer NOT NULL,
    essay_id integer NOT NULL,
    user_id integer NOT NULL,
    interaction_type character varying(50) NOT NULL,
    ai_model character varying(50),
    user_request text,
    ai_response json,
    processing_time_ms integer,
    user_rating integer,
    was_helpful boolean,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.essay_ai_interactions OWNER TO postgres;

--
-- Name: essay_ai_interactions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.essay_ai_interactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.essay_ai_interactions_id_seq OWNER TO postgres;

--
-- Name: essay_ai_interactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.essay_ai_interactions_id_seq OWNED BY public.essay_ai_interactions.id;


--
-- Name: essay_templates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.essay_templates (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    essay_type public.essaytype NOT NULL,
    prompt_text text NOT NULL,
    word_limit integer,
    character_limit integer,
    school_name character varying(255),
    scholarship_name character varying(255),
    application_year integer,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone
);


ALTER TABLE public.essay_templates OWNER TO postgres;

--
-- Name: essay_templates_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.essay_templates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.essay_templates_id_seq OWNER TO postgres;

--
-- Name: essay_templates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.essay_templates_id_seq OWNED BY public.essay_templates.id;


--
-- Name: essays; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.essays (
    id integer NOT NULL,
    user_id integer NOT NULL,
    title character varying(255) NOT NULL,
    essay_type public.essaytype NOT NULL,
    prompt text,
    word_limit integer,
    content text,
    word_count integer,
    status public.essaystatus NOT NULL,
    is_primary boolean,
    ai_feedback_count integer,
    last_ai_review_at timestamp with time zone,
    ai_suggestions json,
    ai_score integer,
    version integer,
    parent_essay_id integer,
    target_schools json,
    target_scholarships json,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone,
    submitted_at timestamp with time zone,
    deadline timestamp with time zone
);


ALTER TABLE public.essays OWNER TO postgres;

--
-- Name: essays_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.essays_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.essays_id_seq OWNER TO postgres;

--
-- Name: essays_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.essays_id_seq OWNED BY public.essays.id;


--
-- Name: institution_matches; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.institution_matches (
    id integer NOT NULL,
    user_id integer NOT NULL,
    institution_id integer NOT NULL,
    match_score double precision NOT NULL,
    match_reasons json,
    mismatch_reasons json,
    interested boolean,
    applied boolean,
    admitted boolean,
    enrolled boolean,
    visited boolean,
    application_status character varying(50),
    notes text,
    match_date timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone
);


ALTER TABLE public.institution_matches OWNER TO postgres;

--
-- Name: institution_matches_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.institution_matches_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.institution_matches_id_seq OWNER TO postgres;

--
-- Name: institution_matches_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.institution_matches_id_seq OWNED BY public.institution_matches.id;


--
-- Name: institutions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.institutions (
    id integer NOT NULL,
    ipeds_id integer NOT NULL,
    name character varying(255) NOT NULL,
    address character varying(500),
    city character varying(100) NOT NULL,
    state character varying(2) NOT NULL,
    zip_code character varying(10),
    region public.usregion,
    website character varying(500),
    phone character varying(20),
    president_name character varying(255),
    president_title character varying(100),
    control_type public.controltype NOT NULL,
    size_category public.sizecategory,
    primary_image_url character varying(500),
    primary_image_quality_score integer,
    customer_rank integer,
    logo_image_url character varying(500),
    image_extraction_status public.imageextractionstatus,
    image_extraction_date timestamp without time zone,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.institutions OWNER TO postgres;

--
-- Name: COLUMN institutions.primary_image_url; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.institutions.primary_image_url IS 'CDN URL to standardized 400x300px image for school cards';


--
-- Name: COLUMN institutions.primary_image_quality_score; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.institutions.primary_image_quality_score IS 'Quality score 0-100 for ranking schools by image quality';


--
-- Name: COLUMN institutions.customer_rank; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.institutions.customer_rank IS 'Customer ranking for advertising priority (higher = better placement)';


--
-- Name: COLUMN institutions.logo_image_url; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.institutions.logo_image_url IS 'CDN URL to school logo for headers/search results';


--
-- Name: COLUMN institutions.image_extraction_status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.institutions.image_extraction_status IS 'Status of image extraction process';


--
-- Name: COLUMN institutions.image_extraction_date; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.institutions.image_extraction_date IS 'When images were last extracted/updated';


--
-- Name: institutions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.institutions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.institutions_id_seq OWNER TO postgres;

--
-- Name: institutions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.institutions_id_seq OWNED BY public.institutions.id;


--
-- Name: oauth_accounts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.oauth_accounts (
    id integer NOT NULL,
    user_id integer NOT NULL,
    provider character varying(50) NOT NULL,
    provider_user_id character varying(255) NOT NULL,
    email character varying(255),
    access_token text,
    refresh_token text,
    expires_at timestamp with time zone,
    profile_data json,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.oauth_accounts OWNER TO postgres;

--
-- Name: oauth_accounts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.oauth_accounts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.oauth_accounts_id_seq OWNER TO postgres;

--
-- Name: oauth_accounts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.oauth_accounts_id_seq OWNED BY public.oauth_accounts.id;


--
-- Name: oauth_states; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.oauth_states (
    id integer NOT NULL,
    state character varying(255) NOT NULL,
    provider character varying(50) NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    expires_at timestamp with time zone NOT NULL,
    used boolean
);


ALTER TABLE public.oauth_states OWNER TO postgres;

--
-- Name: oauth_states_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.oauth_states_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.oauth_states_id_seq OWNER TO postgres;

--
-- Name: oauth_states_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.oauth_states_id_seq OWNED BY public.oauth_states.id;


--
-- Name: scholarship_matches; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.scholarship_matches (
    id integer NOT NULL,
    user_id integer NOT NULL,
    scholarship_id integer NOT NULL,
    match_score double precision NOT NULL,
    match_reasons json,
    mismatch_reasons json,
    viewed boolean,
    interested boolean,
    applied boolean,
    bookmarked boolean,
    application_status character varying(50),
    notes text,
    match_date timestamp with time zone DEFAULT now() NOT NULL,
    viewed_at timestamp with time zone,
    applied_at timestamp with time zone
);


ALTER TABLE public.scholarship_matches OWNER TO postgres;

--
-- Name: scholarship_matches_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.scholarship_matches_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.scholarship_matches_id_seq OWNER TO postgres;

--
-- Name: scholarship_matches_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.scholarship_matches_id_seq OWNED BY public.scholarship_matches.id;


--
-- Name: scholarships; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.scholarships (
    id integer NOT NULL,
    title character varying(255) NOT NULL,
    description text,
    organization character varying(255) NOT NULL,
    website_url character varying(500),
    application_url character varying(500),
    scholarship_type public.scholarshiptype NOT NULL,
    categories character varying[],
    status public.scholarshipstatus NOT NULL,
    difficulty_level public.difficultylevel NOT NULL,
    amount_min integer,
    amount_max integer,
    amount_exact integer,
    is_renewable boolean,
    renewal_years integer,
    number_of_awards integer,
    min_gpa double precision,
    max_gpa double precision,
    min_sat_score integer,
    min_act_score integer,
    required_majors character varying[],
    excluded_majors character varying[],
    academic_level character varying[],
    eligible_ethnicities character varying[],
    gender_requirements character varying[],
    first_generation_college_required boolean,
    income_max integer,
    income_min integer,
    need_based_required boolean,
    eligible_states character varying[],
    eligible_cities character varying[],
    eligible_counties character varying[],
    zip_codes character varying[],
    international_students_eligible boolean,
    eligible_schools character varying[],
    high_school_names character varying[],
    graduation_year_min integer,
    graduation_year_max integer,
    required_activities character varying[],
    volunteer_hours_min integer,
    leadership_required boolean,
    work_experience_required boolean,
    special_talents character varying[],
    essay_required boolean,
    essay_topics character varying[],
    essay_word_limit integer,
    transcript_required boolean,
    recommendation_letters_required integer,
    portfolio_required boolean,
    interview_required boolean,
    personal_statement_required boolean,
    leadership_essay_required boolean,
    community_service_essay_required boolean,
    application_opens timestamp with time zone,
    deadline timestamp with time zone,
    award_date timestamp with time zone,
    is_rolling_deadline boolean,
    languages_preferred character varying[],
    military_affiliation_required boolean,
    employer_affiliation character varying(255),
    primary_image_url character varying(500),
    primary_image_quality_score integer,
    logo_image_url character varying(500),
    image_extraction_status public.imageextractionstatus,
    image_extraction_date timestamp with time zone,
    verified boolean,
    featured boolean,
    views_count integer,
    applications_count integer,
    ai_generated_summary text,
    matching_keywords character varying[],
    created_by integer,
    last_verified_at timestamp with time zone,
    verification_notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone
);


ALTER TABLE public.scholarships OWNER TO postgres;

--
-- Name: COLUMN scholarships.primary_image_url; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.scholarships.primary_image_url IS 'CDN URL to standardized scholarship card image';


--
-- Name: COLUMN scholarships.primary_image_quality_score; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.scholarships.primary_image_quality_score IS 'Quality score 0-100 for ranking scholarships by image quality';


--
-- Name: COLUMN scholarships.logo_image_url; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.scholarships.logo_image_url IS 'CDN URL to organization logo';


--
-- Name: COLUMN scholarships.image_extraction_status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.scholarships.image_extraction_status IS 'Status of image extraction process';


--
-- Name: COLUMN scholarships.image_extraction_date; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.scholarships.image_extraction_date IS 'When images were last extracted/updated';


--
-- Name: scholarships_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.scholarships_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.scholarships_id_seq OWNER TO postgres;

--
-- Name: scholarships_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.scholarships_id_seq OWNED BY public.scholarships.id;


--
-- Name: tuition_data; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tuition_data (
    id integer NOT NULL,
    ipeds_id integer NOT NULL,
    academic_year character varying(10) NOT NULL,
    data_source character varying(50) NOT NULL,
    tuition_in_state double precision,
    tuition_out_state double precision,
    required_fees_in_state double precision,
    required_fees_out_state double precision,
    tuition_fees_in_state double precision,
    tuition_fees_out_state double precision,
    room_board_on_campus double precision,
    room_board_off_campus double precision,
    room_board_breakdown jsonb,
    books_supplies double precision,
    personal_expenses double precision,
    transportation double precision,
    has_tuition_data boolean NOT NULL,
    has_fees_data boolean NOT NULL,
    has_living_data boolean NOT NULL,
    data_completeness_score integer NOT NULL,
    validation_status public.validationstatus NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.tuition_data OWNER TO postgres;

--
-- Name: TABLE tuition_data; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.tuition_data IS 'Tuition and financial data for institutions';


--
-- Name: COLUMN tuition_data.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tuition_data.id IS 'Primary key';


--
-- Name: COLUMN tuition_data.ipeds_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tuition_data.ipeds_id IS 'Institution IPEDS ID (foreign key)';


--
-- Name: COLUMN tuition_data.academic_year; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tuition_data.academic_year IS 'Academic year (e.g., "2023-24")';


--
-- Name: COLUMN tuition_data.data_source; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tuition_data.data_source IS 'Source of the data (e.g., "IPEDS", "Manual")';


--
-- Name: COLUMN tuition_data.tuition_in_state; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tuition_data.tuition_in_state IS 'In-state tuition cost';


--
-- Name: COLUMN tuition_data.tuition_out_state; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tuition_data.tuition_out_state IS 'Out-of-state tuition cost';


--
-- Name: COLUMN tuition_data.required_fees_in_state; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tuition_data.required_fees_in_state IS 'Required fees for in-state students';


--
-- Name: COLUMN tuition_data.required_fees_out_state; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tuition_data.required_fees_out_state IS 'Required fees for out-of-state students';


--
-- Name: COLUMN tuition_data.tuition_fees_in_state; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tuition_data.tuition_fees_in_state IS 'Total tuition + fees for in-state';


--
-- Name: COLUMN tuition_data.tuition_fees_out_state; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tuition_data.tuition_fees_out_state IS 'Total tuition + fees for out-of-state';


--
-- Name: COLUMN tuition_data.room_board_on_campus; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tuition_data.room_board_on_campus IS 'Room and board costs on campus';


--
-- Name: COLUMN tuition_data.room_board_off_campus; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tuition_data.room_board_off_campus IS 'Room and board costs off campus';


--
-- Name: COLUMN tuition_data.room_board_breakdown; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tuition_data.room_board_breakdown IS 'JSON breakdown of room/board costs: {"housing": 9346, "meals": 5358, "total": 14704}';


--
-- Name: COLUMN tuition_data.books_supplies; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tuition_data.books_supplies IS 'Books and supplies cost';


--
-- Name: COLUMN tuition_data.personal_expenses; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tuition_data.personal_expenses IS 'Personal/miscellaneous expenses';


--
-- Name: COLUMN tuition_data.transportation; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tuition_data.transportation IS 'Transportation costs';


--
-- Name: COLUMN tuition_data.has_tuition_data; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tuition_data.has_tuition_data IS 'Whether tuition data is available';


--
-- Name: COLUMN tuition_data.has_fees_data; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tuition_data.has_fees_data IS 'Whether fee data is available';


--
-- Name: COLUMN tuition_data.has_living_data; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tuition_data.has_living_data IS 'Whether living expense data is available';


--
-- Name: COLUMN tuition_data.data_completeness_score; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tuition_data.data_completeness_score IS 'Data completeness score (0-100)';


--
-- Name: COLUMN tuition_data.validation_status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tuition_data.validation_status IS 'Data validation status';


--
-- Name: COLUMN tuition_data.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tuition_data.created_at IS 'Record creation timestamp';


--
-- Name: COLUMN tuition_data.updated_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tuition_data.updated_at IS 'Record last update timestamp';


--
-- Name: tuition_data_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tuition_data_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tuition_data_id_seq OWNER TO postgres;

--
-- Name: tuition_data_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tuition_data_id_seq OWNED BY public.tuition_data.id;


--
-- Name: user_profiles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_profiles (
    id integer NOT NULL,
    user_id integer NOT NULL,
    high_school_name character varying(255),
    graduation_year integer,
    gpa double precision,
    gpa_scale character varying(10),
    intended_major character varying(255),
    state character varying(50),
    sat_score integer,
    act_score integer,
    academic_interests character varying[],
    date_of_birth character varying,
    phone_number character varying(20),
    city character varying(100),
    zip_code character varying(10),
    sat_math integer,
    sat_verbal integer,
    act_math integer,
    act_english integer,
    act_science integer,
    act_reading integer,
    secondary_major character varying(255),
    minor_interests character varying[],
    career_goals character varying[],
    ap_courses character varying[],
    honors_courses character varying[],
    dual_enrollment boolean,
    class_rank integer,
    class_size integer,
    extracurricular_activities json,
    volunteer_experience json,
    volunteer_hours integer,
    work_experience json,
    leadership_positions json,
    awards_honors character varying[],
    competitions json,
    sports_activities json,
    arts_activities json,
    musical_instruments character varying[],
    ethnicity character varying[],
    gender character varying(50),
    first_generation_college boolean,
    household_income_range public.incomerange,
    family_size integer,
    military_connection boolean,
    disability_status boolean,
    lgbtq_identification boolean,
    rural_background boolean,
    preferred_college_size public.collegesize,
    preferred_states character varying[],
    college_application_status character varying(50),
    max_tuition_budget integer,
    financial_aid_needed boolean,
    work_study_interest boolean,
    campus_setting character varying[],
    religious_affiliation character varying(100),
    greek_life_interest boolean,
    research_opportunities_important boolean,
    study_abroad_interest boolean,
    has_personal_statement boolean,
    has_leadership_essay boolean,
    has_challenges_essay boolean,
    has_diversity_essay boolean,
    has_community_service_essay boolean,
    has_academic_interest_essay boolean,
    scholarship_types_interested character varying[],
    application_deadline_preference character varying(50),
    min_scholarship_amount integer,
    renewable_scholarships_only boolean,
    local_scholarships_priority boolean,
    languages_spoken character varying[],
    special_talents character varying[],
    certifications character varying[],
    additional_notes text,
    parent_education_level character varying(100),
    parent_occupation character varying(100),
    parent_employer character varying(255),
    profile_tier character varying(20) DEFAULT 'basic'::character varying NOT NULL,
    profile_completed boolean NOT NULL,
    completion_percentage integer NOT NULL,
    last_matching_update timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone,
    completed_at timestamp with time zone,
    CONSTRAINT valid_profile_tier CHECK (((profile_tier)::text = ANY ((ARRAY['basic'::character varying, 'enhanced'::character varying, 'complete'::character varying, 'optimized'::character varying])::text[])))
);


ALTER TABLE public.user_profiles OWNER TO postgres;

--
-- Name: user_profiles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_profiles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_profiles_id_seq OWNER TO postgres;

--
-- Name: user_profiles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_profiles_id_seq OWNED BY public.user_profiles.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying NOT NULL,
    username character varying NOT NULL,
    hashed_password character varying,
    first_name character varying,
    last_name character varying,
    is_active boolean NOT NULL,
    is_superuser boolean NOT NULL,
    is_verified boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone,
    last_login_at timestamp with time zone
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: essay_ai_interactions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.essay_ai_interactions ALTER COLUMN id SET DEFAULT nextval('public.essay_ai_interactions_id_seq'::regclass);


--
-- Name: essay_templates id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.essay_templates ALTER COLUMN id SET DEFAULT nextval('public.essay_templates_id_seq'::regclass);


--
-- Name: essays id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.essays ALTER COLUMN id SET DEFAULT nextval('public.essays_id_seq'::regclass);


--
-- Name: institution_matches id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.institution_matches ALTER COLUMN id SET DEFAULT nextval('public.institution_matches_id_seq'::regclass);


--
-- Name: institutions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.institutions ALTER COLUMN id SET DEFAULT nextval('public.institutions_id_seq'::regclass);


--
-- Name: oauth_accounts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.oauth_accounts ALTER COLUMN id SET DEFAULT nextval('public.oauth_accounts_id_seq'::regclass);


--
-- Name: oauth_states id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.oauth_states ALTER COLUMN id SET DEFAULT nextval('public.oauth_states_id_seq'::regclass);


--
-- Name: scholarship_matches id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scholarship_matches ALTER COLUMN id SET DEFAULT nextval('public.scholarship_matches_id_seq'::regclass);


--
-- Name: scholarships id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scholarships ALTER COLUMN id SET DEFAULT nextval('public.scholarships_id_seq'::regclass);


--
-- Name: tuition_data id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tuition_data ALTER COLUMN id SET DEFAULT nextval('public.tuition_data_id_seq'::regclass);


--
-- Name: user_profiles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_profiles ALTER COLUMN id SET DEFAULT nextval('public.user_profiles_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
e522998fd68b
\.


--
-- Data for Name: essay_ai_interactions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.essay_ai_interactions (id, essay_id, user_id, interaction_type, ai_model, user_request, ai_response, processing_time_ms, user_rating, was_helpful, created_at) FROM stdin;
\.


--
-- Data for Name: essay_templates; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.essay_templates (id, name, essay_type, prompt_text, word_limit, character_limit, school_name, scholarship_name, application_year, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: essays; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.essays (id, user_id, title, essay_type, prompt, word_limit, content, word_count, status, is_primary, ai_feedback_count, last_ai_review_at, ai_suggestions, ai_score, version, parent_essay_id, target_schools, target_scholarships, created_at, updated_at, submitted_at, deadline) FROM stdin;
\.


--
-- Data for Name: institution_matches; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.institution_matches (id, user_id, institution_id, match_score, match_reasons, mismatch_reasons, interested, applied, admitted, enrolled, visited, application_status, notes, match_date, updated_at) FROM stdin;
\.


--
-- Data for Name: institutions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.institutions (id, ipeds_id, name, address, city, state, zip_code, region, website, phone, president_name, president_title, control_type, size_category, primary_image_url, primary_image_quality_score, customer_rank, logo_image_url, image_extraction_status, image_extraction_date, created_at, updated_at) FROM stdin;
1	164465	Amherst College	\N	Amherst	MA	\N	\N	\N	\N	\N	\N	PRIVATE_NONPROFIT	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ma/ma_curated_164465_amherst_college_optimized.jpg	\N	\N	\N	\N	\N	2025-10-01 01:45:18.542629	2025-10-01 01:45:18.542629
2	164924	Boston College	\N	Boston	MA	\N	\N	\N	\N	\N	\N	PRIVATE_NONPROFIT	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ma/ma_curated_164924_Boston_College_optimized.jpg	\N	\N	\N	\N	\N	2025-10-01 01:45:18.542629	2025-10-01 01:45:18.542629
3	164988	Boston University	\N	Boston	MA	\N	\N	\N	\N	\N	\N	PRIVATE_NONPROFIT	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ma/ma_curated_164988_Boston_University_optimized.jpg	\N	\N	\N	\N	\N	2025-10-01 01:45:18.542629	2025-10-01 01:45:18.542629
4	165015	Brandeis University	\N	Waltham	MA	\N	\N	\N	\N	\N	\N	PRIVATE_NONPROFIT	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ma/ma_curated_165015_BrandeisUniversity_optimized.jpg	\N	\N	\N	\N	\N	2025-10-01 01:45:18.542629	2025-10-01 01:45:18.542629
5	166027	Harvard University	\N	Cambridge	MA	\N	\N	\N	\N	\N	\N	PRIVATE_NONPROFIT	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ma/ma_curated_166027_Harvard_optimized.jpg	\N	\N	\N	\N	\N	2025-10-01 01:45:18.542629	2025-10-01 01:45:18.542629
6	166629	University of Massachusetts Amherst	\N	Amherst	MA	\N	\N	\N	\N	\N	\N	PUBLIC	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ma/ma_curated_166629_UMASS_amherst_optimized.jpg	\N	\N	\N	\N	\N	2025-10-01 01:45:18.542629	2025-10-01 01:45:18.542629
7	166683	MIT	\N	Cambridge	MA	\N	\N	\N	\N	\N	\N	PRIVATE_NONPROFIT	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ma/ma_curated_166683_MIT_optimized.jpg	\N	\N	\N	\N	\N	2025-10-01 01:45:18.542629	2025-10-01 01:45:18.542629
8	167358	Northeastern University	\N	Boston	MA	\N	\N	\N	\N	\N	\N	PRIVATE_NONPROFIT	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ma/ma_curated_167358_Northeastern_optimized.jpg	\N	\N	\N	\N	\N	2025-10-01 01:45:18.542629	2025-10-01 01:45:18.542629
9	167835	Smith College	\N	Northampton	MA	\N	\N	\N	\N	\N	\N	PRIVATE_NONPROFIT	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ma/ma_curated_167835_SmithCollege_optimized.jpg	\N	\N	\N	\N	\N	2025-10-01 01:45:18.542629	2025-10-01 01:45:18.542629
10	168148	Tufts University	\N	Medford	MA	\N	\N	\N	\N	\N	\N	PRIVATE_NONPROFIT	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ma/ma_curated_168148_Tufts_University_optimized.jpg	\N	\N	\N	\N	\N	2025-10-01 01:45:18.542629	2025-10-01 01:45:18.542629
11	168218	Wellesley College	\N	Wellesley	MA	\N	\N	\N	\N	\N	\N	PRIVATE_NONPROFIT	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ma/ma_curated_168218_Wellesley_College_optimized.jpg	\N	\N	\N	\N	\N	2025-10-01 01:45:18.542629	2025-10-01 01:45:18.542629
12	168342	Williams College	\N	Williamstown	MA	\N	\N	\N	\N	\N	\N	PRIVATE_NONPROFIT	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ma/ma_curated_168342_Williams_optimized.jpg	\N	\N	\N	\N	\N	2025-10-01 01:45:18.542629	2025-10-01 01:45:18.542629
14	182670	Dartmouth College	\N	Hanover	NH	\N	\N	\N	\N	\N	\N	PRIVATE_NONPROFIT	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/nh/nh_institution_1887_manual_images/institution_1887_dartmouth_optimized.jpg	\N	\N	\N	\N	\N	2025-10-01 02:17:57.181804	2025-10-01 02:17:57.181804
23	182917	Magdalen College	\N	Warner	NH	\N	\N	\N	\N	\N	\N	PRIVATE_NONPROFIT	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/nh/nh_institution_1893_manual_images/institution_1893_magdalen_optimized.jpg	\N	\N	\N	\N	\N	2025-10-01 02:17:57.181804	2025-10-01 02:17:57.181804
18	183239	Saint Anselm College	\N	Manchester	NH	\N	\N	\N	\N	\N	\N	PRIVATE_NONPROFIT	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/nh/nh_institution_1911_manual_images/institution_1911_saint_anselm_optimized.jpg	\N	\N	\N	\N	\N	2025-10-01 02:17:57.181804	2025-10-01 02:17:57.181804
16	183080	Plymouth State University	\N	Plymouth	NH	\N	\N	\N	\N	\N	\N	PUBLIC	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/nh/nh_institution_1901_manual_images/institution_1901_plymouth_state_optimized.jpg	\N	\N	\N	\N	\N	2025-10-01 02:17:57.181804	2025-10-01 02:17:57.181804
20	182795	Franklin Pierce University	\N	Rindge	NH	\N	\N	\N	\N	\N	\N	PRIVATE_NONPROFIT	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/nh/nh_institution_1890_manual_images/institution_1890_franklin_pierce_optimized.jpg	\N	\N	\N	\N	\N	2025-10-01 02:17:57.181804	2025-10-01 02:17:57.181804
21	182634	Colby-Sawyer College	\N	New London	NH	\N	\N	\N	\N	\N	\N	PRIVATE_NONPROFIT	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/nh/nh_institution_1886_manual_images/institution_1886_colby_sawyer_optimized.jpg	\N	\N	\N	\N	\N	2025-10-01 02:17:57.181804	2025-10-01 02:17:57.181804
24	183150	Great Bay Community College	\N	Portsmouth	NH	\N	\N	\N	\N	\N	\N	PUBLIC	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/nh/nh_institution_1908_manual_images/institution_1908_great_bay_optimized.jpg	\N	\N	\N	\N	\N	2025-10-01 02:17:57.181804	2025-10-01 02:17:57.181804
22	183071	University of New Hampshire at Manchester	\N	Manchester	NH	\N	\N	\N	\N	\N	\N	PUBLIC	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/nh/nh_institution_1905_manual_images/institution_1905_lakes_region_optimized.jpg	\N	\N	\N	\N	\N	2025-10-01 02:17:57.181804	2025-10-01 02:17:57.181804
17	183062	Keene State College	\N	Keene	NH	\N	\N	\N	\N	\N	\N	PUBLIC	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/nh/nh_institution_1899_manual_images/institution_1899_keene_state_optimized.jpg	\N	\N	\N	\N	\N	2025-10-01 02:17:57.181804	2025-10-01 02:17:57.181804
13	183044	University of New Hampshire-Main Campus	\N	Durham	NH	\N	\N	\N	\N	\N	\N	PUBLIC	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/nh/nh_institution_1898_manual_images/institution_1898_unh_main_optimized.jpg	\N	\N	\N	\N	\N	2025-10-01 02:17:57.181804	2025-10-01 02:17:57.181804
15	183026	Southern New Hampshire University	\N	Manchester	NH	\N	\N	\N	\N	\N	\N	PRIVATE_NONPROFIT	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/nh/nh_institution_1896_manual_images/institution_1896_snhu_optimized.jpg	\N	\N	\N	\N	\N	2025-10-01 02:17:57.181804	2025-10-01 02:17:57.181804
19	182980	New England College	\N	Henniker	NH	\N	\N	\N	\N	\N	\N	PRIVATE_NONPROFIT	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/nh/nh_institution_1894_manual_images/institution_1894_new_england_optimized.jpg	\N	\N	\N	\N	\N	2025-10-01 02:17:57.181804	2025-10-01 02:17:57.181804
\.


--
-- Data for Name: oauth_accounts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.oauth_accounts (id, user_id, provider, provider_user_id, email, access_token, refresh_token, expires_at, profile_data, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: oauth_states; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.oauth_states (id, state, provider, created_at, expires_at, used) FROM stdin;
1	nBH4dvIfzIkshp-2US94luVj0FdmJyyt4J1bM1_y7Lw	google	2025-10-01 06:56:31.442682-07	2025-10-01 07:06:31.442691-07	f
\.


--
-- Data for Name: scholarship_matches; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.scholarship_matches (id, user_id, scholarship_id, match_score, match_reasons, mismatch_reasons, viewed, interested, applied, bookmarked, application_status, notes, match_date, viewed_at, applied_at) FROM stdin;
\.


--
-- Data for Name: scholarships; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.scholarships (id, title, description, organization, website_url, application_url, scholarship_type, categories, status, difficulty_level, amount_min, amount_max, amount_exact, is_renewable, renewal_years, number_of_awards, min_gpa, max_gpa, min_sat_score, min_act_score, required_majors, excluded_majors, academic_level, eligible_ethnicities, gender_requirements, first_generation_college_required, income_max, income_min, need_based_required, eligible_states, eligible_cities, eligible_counties, zip_codes, international_students_eligible, eligible_schools, high_school_names, graduation_year_min, graduation_year_max, required_activities, volunteer_hours_min, leadership_required, work_experience_required, special_talents, essay_required, essay_topics, essay_word_limit, transcript_required, recommendation_letters_required, portfolio_required, interview_required, personal_statement_required, leadership_essay_required, community_service_essay_required, application_opens, deadline, award_date, is_rolling_deadline, languages_preferred, military_affiliation_required, employer_affiliation, primary_image_url, primary_image_quality_score, logo_image_url, image_extraction_status, image_extraction_date, verified, featured, views_count, applications_count, ai_generated_summary, matching_keywords, created_by, last_verified_at, verification_notes, created_at, updated_at) FROM stdin;
5	National Merit Scholarship	\N	NMSC	\N	\N	ACADEMIC_MERIT	\N	ACTIVE	HARD	\N	\N	2500	f	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	f	f	\N	f	\N	\N	t	0	f	f	f	f	f	\N	\N	\N	f	\N	f	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/optimized/scholarship_3_National_Merit_Scholarship_Program_optimized.jpg	\N	\N	\N	\N	f	f	2	0	\N	\N	\N	\N	\N	2025-10-01 01:45:08.850423-07	2025-10-01 01:56:19.203854-07
2	Davidson Fellows Scholarship	\N	Davidson Institute	\N	\N	ACADEMIC_MERIT	\N	ACTIVE	VERY_HARD	\N	\N	50000	f	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	f	f	\N	f	\N	\N	t	0	f	f	f	f	f	\N	\N	\N	f	\N	f	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/optimized/scholarship_13_Davidson_Fellows_Scholarshi_optimized.jpg	\N	\N	\N	\N	f	f	0	0	\N	\N	\N	\N	\N	2025-10-01 01:45:08.850423-07	\N
1	QuestBridge National College Match	\N	QuestBridge	\N	\N	ACADEMIC_MERIT	\N	ACTIVE	VERY_HARD	\N	\N	200000	f	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	f	f	\N	f	\N	\N	t	0	f	f	f	f	f	\N	\N	\N	f	\N	f	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/optimized/scholarship_11_QuestBridge_National_College_Match_optimized.jpg	\N	\N	\N	\N	f	f	0	0	\N	\N	\N	\N	\N	2025-10-01 01:45:08.850423-07	\N
3	Hispanic Scholarship Fund	\N	HSF	\N	\N	NEED_BASED	\N	ACTIVE	MODERATE	\N	\N	5000	f	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	f	f	\N	f	\N	\N	t	0	f	f	f	f	f	\N	\N	\N	f	\N	f	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/optimized/scholarship_13_Hispanic_Scholarship_Fund_General_Scholarship_optimized.jpg	\N	\N	\N	\N	f	f	0	0	\N	\N	\N	\N	\N	2025-10-01 01:45:08.850423-07	\N
4	Gates Millennium Scholars Program	\N	Gates Foundation	\N	\N	ACADEMIC_MERIT	\N	ACTIVE	HARD	\N	\N	10000	f	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	f	f	\N	f	\N	\N	t	0	f	f	f	f	f	\N	\N	\N	f	\N	f	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/optimized/scholarship_2_Gates_Millennium_Scholars_Program_optimized.jpg	\N	\N	\N	\N	f	f	0	0	\N	\N	\N	\N	\N	2025-10-01 01:45:08.850423-07	\N
6	Google Lime Scholarship	\N	Google	\N	\N	STEM	\N	ACTIVE	HARD	\N	\N	10000	f	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	f	f	\N	f	\N	\N	t	0	f	f	f	f	f	\N	\N	\N	f	\N	f	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/optimized/scholarship_4_Google_Lime_Scholarship_for_Students_with_Disabilities_optimized.jpg	\N	\N	\N	\N	f	f	0	0	\N	\N	\N	\N	\N	2025-10-01 01:45:08.850423-07	\N
7	Coca-Cola Scholars Foundation	\N	Coca-Cola	\N	\N	LEADERSHIP	\N	ACTIVE	HARD	\N	\N	20000	f	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	f	f	\N	f	\N	\N	t	0	f	f	f	f	f	\N	\N	\N	f	\N	f	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/optimized/scholarship_6_Coca-Cola_Scholars_Foundation_Scholarship_optimized.jpg	\N	\N	\N	\N	f	f	0	0	\N	\N	\N	\N	\N	2025-10-01 01:45:08.850423-07	\N
8	Dell Scholars Program	\N	Dell	\N	\N	NEED_BASED	\N	ACTIVE	MODERATE	\N	\N	20000	f	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	f	f	\N	f	\N	\N	t	0	f	f	f	f	f	\N	\N	\N	f	\N	f	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/optimized/scholarship_7_Dell_Scholars_Program_optimized.jpg	\N	\N	\N	\N	f	f	0	0	\N	\N	\N	\N	\N	2025-10-01 01:45:08.850423-07	\N
9	Ron Brown Scholar Program	\N	Ron Brown Foundation	\N	\N	ACADEMIC_MERIT	\N	ACTIVE	VERY_HARD	\N	\N	40000	f	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	f	f	\N	f	\N	\N	t	0	f	f	f	f	f	\N	\N	\N	f	\N	f	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/optimized/scholarship_9_Ron_Brown_Scholar_Program_optimized.jpg	\N	\N	\N	\N	f	f	0	0	\N	\N	\N	\N	\N	2025-10-01 01:45:08.850423-07	\N
10	Horatio Alger National Scholarship	\N	Horatio Alger Association	\N	\N	NEED_BASED	\N	ACTIVE	MODERATE	\N	\N	25000	f	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	f	f	\N	t	\N	\N	t	2	f	f	t	f	f	\N	\N	\N	f	\N	f	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/optimized/scholarship_10_Horatio_Alger_National_Scholarship_optimized.jpg	\N	\N	\N	\N	f	f	2	0	\N	\N	\N	\N	\N	2025-10-01 01:57:48.195049-07	2025-10-01 08:13:50.824525-07
12	Regeneron Science Talent Search	\N	Regeneron	\N	\N	STEM	\N	ACTIVE	VERY_HARD	\N	\N	250000	f	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	t	\N	\N	\N	\N	\N	\N	t	f	\N	t	\N	\N	t	3	t	t	t	f	f	\N	\N	\N	f	\N	f	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/optimized/scholarship_8_Regeneron_Science_Talent_Search_optimized.jpg	\N	\N	\N	\N	f	f	3	0	\N	\N	\N	\N	\N	2025-10-01 01:57:48.195049-07	2025-10-01 08:15:41.64445-07
11	Jackie Robinson Foundation Scholarship	\N	Jackie Robinson Foundation	\N	\N	LEADERSHIP	\N	ACTIVE	HARD	\N	\N	30000	t	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	t	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	t	f	\N	t	\N	\N	t	3	f	t	t	t	t	\N	\N	\N	f	\N	f	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/optimized/scholarship_5_Jackie_Robinson_Foundation_Scholarship__optimized.jpg	\N	\N	\N	\N	f	f	2	0	\N	\N	\N	\N	\N	2025-10-01 01:57:48.195049-07	2025-10-01 08:17:54.860327-07
\.


--
-- Data for Name: tuition_data; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tuition_data (id, ipeds_id, academic_year, data_source, tuition_in_state, tuition_out_state, required_fees_in_state, required_fees_out_state, tuition_fees_in_state, tuition_fees_out_state, room_board_on_campus, room_board_off_campus, room_board_breakdown, books_supplies, personal_expenses, transportation, has_tuition_data, has_fees_data, has_living_data, data_completeness_score, validation_status, created_at, updated_at) FROM stdin;
1	166683	2024-25	manual	62000	62000	\N	\N	62400	62400	20300	\N	\N	1000	\N	\N	t	t	t	85	VALIDATED	2025-10-01 02:12:31.351575	2025-10-01 02:12:31.351575
2	166027	2024-25	manual	56000	56000	\N	\N	57000	57000	19500	\N	\N	1000	\N	\N	t	t	t	85	VALIDATED	2025-10-01 02:12:31.351575	2025-10-01 02:12:31.351575
3	164465	2024-25	manual	66000	66000	\N	\N	66800	66800	19000	\N	\N	1000	\N	\N	t	t	t	85	VALIDATED	2025-10-01 02:12:31.351575	2025-10-01 02:12:31.351575
4	168342	2024-25	manual	65000	65000	\N	\N	65800	65800	18500	\N	\N	1000	\N	\N	t	t	t	85	VALIDATED	2025-10-01 02:12:31.351575	2025-10-01 02:12:31.351575
5	164924	2024-25	manual	67000	67000	\N	\N	68000	68000	19000	\N	\N	1000	\N	\N	t	t	t	85	VALIDATED	2025-10-01 02:12:31.351575	2025-10-01 02:12:31.351575
6	164988	2024-25	manual	65000	65000	\N	\N	66000	66000	20000	\N	\N	1000	\N	\N	t	t	t	85	VALIDATED	2025-10-01 02:12:31.351575	2025-10-01 02:12:31.351575
7	165015	2024-25	manual	65000	65000	\N	\N	66000	66000	19500	\N	\N	1000	\N	\N	t	t	t	85	VALIDATED	2025-10-01 02:12:31.351575	2025-10-01 02:12:31.351575
8	167358	2024-25	manual	62000	62000	\N	\N	63000	63000	20500	\N	\N	1000	\N	\N	t	t	t	85	VALIDATED	2025-10-01 02:12:31.351575	2025-10-01 02:12:31.351575
9	167835	2024-25	manual	62000	62000	\N	\N	63000	63000	19000	\N	\N	1000	\N	\N	t	t	t	85	VALIDATED	2025-10-01 02:12:31.351575	2025-10-01 02:12:31.351575
10	168148	2024-25	manual	68000	68000	\N	\N	69000	69000	20000	\N	\N	1000	\N	\N	t	t	t	85	VALIDATED	2025-10-01 02:12:31.351575	2025-10-01 02:12:31.351575
11	168218	2024-25	manual	64000	64000	\N	\N	65000	65000	19500	\N	\N	1000	\N	\N	t	t	t	85	VALIDATED	2025-10-01 02:12:31.351575	2025-10-01 02:12:31.351575
12	166629	2024-25	manual	17000	39000	\N	\N	18500	40500	15000	\N	\N	1000	\N	\N	t	t	t	85	VALIDATED	2025-10-01 02:12:31.351575	2025-10-01 02:12:31.351575
13	183044	2024-25	manual	18500	35500	\N	\N	19500	36500	14000	\N	\N	1000	\N	\N	t	t	t	85	VALIDATED	2025-10-01 02:24:24.440567	2025-10-01 02:24:24.440567
14	182670	2024-25	manual	65000	65000	\N	\N	66000	66000	20000	\N	\N	1000	\N	\N	t	t	t	85	VALIDATED	2025-10-01 02:24:24.440567	2025-10-01 02:24:24.440567
15	183026	2024-25	manual	32000	32000	\N	\N	33000	33000	13500	\N	\N	1000	\N	\N	t	t	t	85	VALIDATED	2025-10-01 02:24:24.440567	2025-10-01 02:24:24.440567
16	183080	2024-25	manual	15000	28000	\N	\N	16000	29000	13000	\N	\N	1000	\N	\N	t	t	t	85	VALIDATED	2025-10-01 02:24:24.440567	2025-10-01 02:24:24.440567
17	183062	2024-25	manual	15000	27000	\N	\N	16000	28000	13500	\N	\N	1000	\N	\N	t	t	t	85	VALIDATED	2025-10-01 02:24:24.440567	2025-10-01 02:24:24.440567
18	183239	2024-25	manual	45000	45000	\N	\N	46000	46000	16000	\N	\N	1000	\N	\N	t	t	t	85	VALIDATED	2025-10-01 02:24:24.440567	2025-10-01 02:24:24.440567
19	182980	2024-25	manual	42000	42000	\N	\N	43000	43000	14500	\N	\N	1000	\N	\N	t	t	t	85	VALIDATED	2025-10-01 02:24:24.440567	2025-10-01 02:24:24.440567
20	182795	2024-25	manual	41000	41000	\N	\N	42000	42000	15000	\N	\N	1000	\N	\N	t	t	t	85	VALIDATED	2025-10-01 02:24:24.440567	2025-10-01 02:24:24.440567
21	182634	2024-25	manual	46000	46000	\N	\N	47000	47000	15500	\N	\N	1000	\N	\N	t	t	t	85	VALIDATED	2025-10-01 02:24:24.440567	2025-10-01 02:24:24.440567
22	183071	2024-25	manual	16000	32000	\N	\N	17000	33000	12000	\N	\N	1000	\N	\N	t	t	t	85	VALIDATED	2025-10-01 02:24:24.440567	2025-10-01 02:24:24.440567
23	182917	2024-25	manual	28000	28000	\N	\N	29000	29000	12000	\N	\N	1000	\N	\N	t	t	t	85	VALIDATED	2025-10-01 02:24:24.440567	2025-10-01 02:24:24.440567
24	183150	2024-25	manual	7500	15000	\N	\N	8500	16000	10000	\N	\N	1000	\N	\N	t	t	t	85	VALIDATED	2025-10-01 02:24:24.440567	2025-10-01 02:24:24.440567
\.


--
-- Data for Name: user_profiles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_profiles (id, user_id, high_school_name, graduation_year, gpa, gpa_scale, intended_major, state, sat_score, act_score, academic_interests, date_of_birth, phone_number, city, zip_code, sat_math, sat_verbal, act_math, act_english, act_science, act_reading, secondary_major, minor_interests, career_goals, ap_courses, honors_courses, dual_enrollment, class_rank, class_size, extracurricular_activities, volunteer_experience, volunteer_hours, work_experience, leadership_positions, awards_honors, competitions, sports_activities, arts_activities, musical_instruments, ethnicity, gender, first_generation_college, household_income_range, family_size, military_connection, disability_status, lgbtq_identification, rural_background, preferred_college_size, preferred_states, college_application_status, max_tuition_budget, financial_aid_needed, work_study_interest, campus_setting, religious_affiliation, greek_life_interest, research_opportunities_important, study_abroad_interest, has_personal_statement, has_leadership_essay, has_challenges_essay, has_diversity_essay, has_community_service_essay, has_academic_interest_essay, scholarship_types_interested, application_deadline_preference, min_scholarship_amount, renewable_scholarships_only, local_scholarships_priority, languages_spoken, special_talents, certifications, additional_notes, parent_education_level, parent_occupation, parent_employer, profile_tier, profile_completed, completion_percentage, last_matching_update, created_at, updated_at, completed_at) FROM stdin;
1	1	\N	\N	\N	4.0	\N	MA	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	{MA}	\N	\N	\N	f	\N	\N	\N	f	f	f	f	f	f	f	f	\N	\N	\N	f	t	\N	\N	\N	\N	\N	\N	\N	basic	f	0	\N	2025-10-02 00:38:46.55523-07	2025-10-02 06:38:01.815375-07	\N
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, email, username, hashed_password, first_name, last_name, is_active, is_superuser, is_verified, created_at, updated_at, last_login_at) FROM stdin;
1	daneahern@yahoo.com	dahern	$2b$12$COUBLG5PZOXBofyzJ0NioeWa5uuXKq7DTi5U4XhstTNK6rJe5loMa	Dane 	Ahern	t	f	f	2025-10-01 00:50:15.912611-07	2025-10-02 06:27:03.761028-07	2025-10-02 13:27:03.97595-07
\.


--
-- Name: essay_ai_interactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.essay_ai_interactions_id_seq', 1, false);


--
-- Name: essay_templates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.essay_templates_id_seq', 1, false);


--
-- Name: essays_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.essays_id_seq', 1, false);


--
-- Name: institution_matches_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.institution_matches_id_seq', 1, false);


--
-- Name: institutions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.institutions_id_seq', 24, true);


--
-- Name: oauth_accounts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.oauth_accounts_id_seq', 1, false);


--
-- Name: oauth_states_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.oauth_states_id_seq', 1, true);


--
-- Name: scholarship_matches_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.scholarship_matches_id_seq', 1, false);


--
-- Name: scholarships_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.scholarships_id_seq', 12, true);


--
-- Name: tuition_data_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tuition_data_id_seq', 24, true);


--
-- Name: user_profiles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_profiles_id_seq', 1, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 1, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: essay_ai_interactions essay_ai_interactions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.essay_ai_interactions
    ADD CONSTRAINT essay_ai_interactions_pkey PRIMARY KEY (id);


--
-- Name: essay_templates essay_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.essay_templates
    ADD CONSTRAINT essay_templates_pkey PRIMARY KEY (id);


--
-- Name: essays essays_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.essays
    ADD CONSTRAINT essays_pkey PRIMARY KEY (id);


--
-- Name: institution_matches institution_matches_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.institution_matches
    ADD CONSTRAINT institution_matches_pkey PRIMARY KEY (id);


--
-- Name: institutions institutions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.institutions
    ADD CONSTRAINT institutions_pkey PRIMARY KEY (id);


--
-- Name: oauth_accounts oauth_accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.oauth_accounts
    ADD CONSTRAINT oauth_accounts_pkey PRIMARY KEY (id);


--
-- Name: oauth_states oauth_states_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.oauth_states
    ADD CONSTRAINT oauth_states_pkey PRIMARY KEY (id);


--
-- Name: scholarship_matches scholarship_matches_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scholarship_matches
    ADD CONSTRAINT scholarship_matches_pkey PRIMARY KEY (id);


--
-- Name: scholarships scholarships_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scholarships
    ADD CONSTRAINT scholarships_pkey PRIMARY KEY (id);


--
-- Name: tuition_data tuition_data_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tuition_data
    ADD CONSTRAINT tuition_data_pkey PRIMARY KEY (id);


--
-- Name: tuition_data uq_tuition_institution_year_source; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tuition_data
    ADD CONSTRAINT uq_tuition_institution_year_source UNIQUE (ipeds_id, academic_year, data_source);


--
-- Name: user_profiles user_profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_profiles
    ADD CONSTRAINT user_profiles_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: idx_institution_control_size; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_institution_control_size ON public.institutions USING btree (control_type, size_category);


--
-- Name: idx_institution_customer_rank; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_institution_customer_rank ON public.institutions USING btree (customer_rank);


--
-- Name: idx_institution_image_quality; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_institution_image_quality ON public.institutions USING btree (primary_image_quality_score);


--
-- Name: idx_institution_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_institution_name ON public.institutions USING btree (name);


--
-- Name: idx_institution_state_city; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_institution_state_city ON public.institutions USING btree (state, city);


--
-- Name: ix_essay_ai_interactions_essay_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_essay_ai_interactions_essay_id ON public.essay_ai_interactions USING btree (essay_id);


--
-- Name: ix_essay_ai_interactions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_essay_ai_interactions_id ON public.essay_ai_interactions USING btree (id);


--
-- Name: ix_essay_ai_interactions_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_essay_ai_interactions_user_id ON public.essay_ai_interactions USING btree (user_id);


--
-- Name: ix_essay_templates_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_essay_templates_id ON public.essay_templates USING btree (id);


--
-- Name: ix_essays_essay_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_essays_essay_type ON public.essays USING btree (essay_type);


--
-- Name: ix_essays_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_essays_id ON public.essays USING btree (id);


--
-- Name: ix_essays_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_essays_user_id ON public.essays USING btree (user_id);


--
-- Name: ix_institution_matches_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_institution_matches_id ON public.institution_matches USING btree (id);


--
-- Name: ix_institution_matches_institution_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_institution_matches_institution_id ON public.institution_matches USING btree (institution_id);


--
-- Name: ix_institution_matches_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_institution_matches_user_id ON public.institution_matches USING btree (user_id);


--
-- Name: ix_institutions_city; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_institutions_city ON public.institutions USING btree (city);


--
-- Name: ix_institutions_control_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_institutions_control_type ON public.institutions USING btree (control_type);


--
-- Name: ix_institutions_customer_rank; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_institutions_customer_rank ON public.institutions USING btree (customer_rank);


--
-- Name: ix_institutions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_institutions_id ON public.institutions USING btree (id);


--
-- Name: ix_institutions_image_extraction_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_institutions_image_extraction_status ON public.institutions USING btree (image_extraction_status);


--
-- Name: ix_institutions_ipeds_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_institutions_ipeds_id ON public.institutions USING btree (ipeds_id);


--
-- Name: ix_institutions_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_institutions_name ON public.institutions USING btree (name);


--
-- Name: ix_institutions_primary_image_quality_score; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_institutions_primary_image_quality_score ON public.institutions USING btree (primary_image_quality_score);


--
-- Name: ix_institutions_region; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_institutions_region ON public.institutions USING btree (region);


--
-- Name: ix_institutions_size_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_institutions_size_category ON public.institutions USING btree (size_category);


--
-- Name: ix_institutions_state; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_institutions_state ON public.institutions USING btree (state);


--
-- Name: ix_oauth_accounts_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_oauth_accounts_id ON public.oauth_accounts USING btree (id);


--
-- Name: ix_oauth_states_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_oauth_states_id ON public.oauth_states USING btree (id);


--
-- Name: ix_oauth_states_state; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_oauth_states_state ON public.oauth_states USING btree (state);


--
-- Name: ix_scholarship_matches_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_scholarship_matches_id ON public.scholarship_matches USING btree (id);


--
-- Name: ix_scholarship_matches_scholarship_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_scholarship_matches_scholarship_id ON public.scholarship_matches USING btree (scholarship_id);


--
-- Name: ix_scholarship_matches_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_scholarship_matches_user_id ON public.scholarship_matches USING btree (user_id);


--
-- Name: ix_scholarships_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_scholarships_id ON public.scholarships USING btree (id);


--
-- Name: ix_scholarships_image_extraction_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_scholarships_image_extraction_status ON public.scholarships USING btree (image_extraction_status);


--
-- Name: ix_scholarships_organization; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_scholarships_organization ON public.scholarships USING btree (organization);


--
-- Name: ix_scholarships_primary_image_quality_score; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_scholarships_primary_image_quality_score ON public.scholarships USING btree (primary_image_quality_score);


--
-- Name: ix_scholarships_scholarship_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_scholarships_scholarship_type ON public.scholarships USING btree (scholarship_type);


--
-- Name: ix_scholarships_title; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_scholarships_title ON public.scholarships USING btree (title);


--
-- Name: ix_tuition_data_academic_year; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tuition_data_academic_year ON public.tuition_data USING btree (academic_year);


--
-- Name: ix_tuition_data_data_completeness_score; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tuition_data_data_completeness_score ON public.tuition_data USING btree (data_completeness_score);


--
-- Name: ix_tuition_data_data_source; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tuition_data_data_source ON public.tuition_data USING btree (data_source);


--
-- Name: ix_tuition_data_has_fees_data; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tuition_data_has_fees_data ON public.tuition_data USING btree (has_fees_data);


--
-- Name: ix_tuition_data_has_living_data; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tuition_data_has_living_data ON public.tuition_data USING btree (has_living_data);


--
-- Name: ix_tuition_data_has_tuition_data; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tuition_data_has_tuition_data ON public.tuition_data USING btree (has_tuition_data);


--
-- Name: ix_tuition_data_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tuition_data_id ON public.tuition_data USING btree (id);


--
-- Name: ix_tuition_data_ipeds_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tuition_data_ipeds_id ON public.tuition_data USING btree (ipeds_id);


--
-- Name: ix_tuition_data_tuition_fees_in_state; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tuition_data_tuition_fees_in_state ON public.tuition_data USING btree (tuition_fees_in_state);


--
-- Name: ix_tuition_data_tuition_fees_out_state; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tuition_data_tuition_fees_out_state ON public.tuition_data USING btree (tuition_fees_out_state);


--
-- Name: ix_tuition_data_tuition_in_state; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tuition_data_tuition_in_state ON public.tuition_data USING btree (tuition_in_state);


--
-- Name: ix_tuition_data_tuition_out_state; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tuition_data_tuition_out_state ON public.tuition_data USING btree (tuition_out_state);


--
-- Name: ix_tuition_data_validation_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tuition_data_validation_status ON public.tuition_data USING btree (validation_status);


--
-- Name: ix_user_profiles_act_score; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_profiles_act_score ON public.user_profiles USING btree (act_score);


--
-- Name: ix_user_profiles_city; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_profiles_city ON public.user_profiles USING btree (city);


--
-- Name: ix_user_profiles_first_generation_college; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_profiles_first_generation_college ON public.user_profiles USING btree (first_generation_college);


--
-- Name: ix_user_profiles_gpa; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_profiles_gpa ON public.user_profiles USING btree (gpa);


--
-- Name: ix_user_profiles_graduation_year; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_profiles_graduation_year ON public.user_profiles USING btree (graduation_year);


--
-- Name: ix_user_profiles_high_school_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_profiles_high_school_name ON public.user_profiles USING btree (high_school_name);


--
-- Name: ix_user_profiles_household_income_range; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_profiles_household_income_range ON public.user_profiles USING btree (household_income_range);


--
-- Name: ix_user_profiles_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_profiles_id ON public.user_profiles USING btree (id);


--
-- Name: ix_user_profiles_intended_major; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_profiles_intended_major ON public.user_profiles USING btree (intended_major);


--
-- Name: ix_user_profiles_sat_score; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_profiles_sat_score ON public.user_profiles USING btree (sat_score);


--
-- Name: ix_user_profiles_state; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_profiles_state ON public.user_profiles USING btree (state);


--
-- Name: ix_user_profiles_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_user_profiles_user_id ON public.user_profiles USING btree (user_id);


--
-- Name: ix_user_profiles_zip_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_profiles_zip_code ON public.user_profiles USING btree (zip_code);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- Name: essay_ai_interactions essay_ai_interactions_essay_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.essay_ai_interactions
    ADD CONSTRAINT essay_ai_interactions_essay_id_fkey FOREIGN KEY (essay_id) REFERENCES public.essays(id);


--
-- Name: essay_ai_interactions essay_ai_interactions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.essay_ai_interactions
    ADD CONSTRAINT essay_ai_interactions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: essays essays_parent_essay_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.essays
    ADD CONSTRAINT essays_parent_essay_id_fkey FOREIGN KEY (parent_essay_id) REFERENCES public.essays(id);


--
-- Name: essays essays_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.essays
    ADD CONSTRAINT essays_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: institution_matches institution_matches_institution_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.institution_matches
    ADD CONSTRAINT institution_matches_institution_id_fkey FOREIGN KEY (institution_id) REFERENCES public.institutions(id);


--
-- Name: institution_matches institution_matches_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.institution_matches
    ADD CONSTRAINT institution_matches_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: oauth_accounts oauth_accounts_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.oauth_accounts
    ADD CONSTRAINT oauth_accounts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: scholarship_matches scholarship_matches_scholarship_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scholarship_matches
    ADD CONSTRAINT scholarship_matches_scholarship_id_fkey FOREIGN KEY (scholarship_id) REFERENCES public.scholarships(id);


--
-- Name: scholarship_matches scholarship_matches_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scholarship_matches
    ADD CONSTRAINT scholarship_matches_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: scholarships scholarships_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scholarships
    ADD CONSTRAINT scholarships_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: tuition_data tuition_data_ipeds_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tuition_data
    ADD CONSTRAINT tuition_data_ipeds_id_fkey FOREIGN KEY (ipeds_id) REFERENCES public.institutions(ipeds_id) ON DELETE CASCADE;


--
-- Name: user_profiles user_profiles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_profiles
    ADD CONSTRAINT user_profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

