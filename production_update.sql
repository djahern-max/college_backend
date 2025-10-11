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
    'STEM',
    'ARTS',
    'DIVERSITY',
    'ATHLETIC',
    'LEADERSHIP',
    'MILITARY',
    'CAREER_SPECIFIC',
    'OTHER'
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
-- Name: institutions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.institutions (
    id integer NOT NULL,
    ipeds_id integer NOT NULL,
    name character varying(255) NOT NULL,
    city character varying(100) NOT NULL,
    state character varying(2) NOT NULL,
    control_type public.controltype NOT NULL,
    primary_image_url character varying(500),
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.institutions OWNER TO postgres;

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
-- Name: scholarships; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.scholarships (
    id integer NOT NULL,
    title character varying(255) NOT NULL,
    organization character varying(255) NOT NULL,
    scholarship_type public.scholarshiptype NOT NULL,
    status public.scholarshipstatus DEFAULT 'ACTIVE'::public.scholarshipstatus NOT NULL,
    difficulty_level public.difficultylevel DEFAULT 'MODERATE'::public.difficultylevel NOT NULL,
    amount_min integer NOT NULL,
    amount_max integer NOT NULL,
    is_renewable boolean DEFAULT false NOT NULL,
    number_of_awards integer,
    deadline date,
    application_opens date,
    for_academic_year character varying(20),
    description character varying(500),
    website_url character varying(500),
    min_gpa numeric(3,2),
    primary_image_url character varying(500),
    verified boolean DEFAULT false NOT NULL,
    featured boolean DEFAULT false NOT NULL,
    views_count integer DEFAULT 0 NOT NULL,
    applications_count integer DEFAULT 0 NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.scholarships OWNER TO postgres;

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
    state character varying(2),
    sat_score integer,
    act_score integer,
    city character varying(100),
    zip_code character varying(10),
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone
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
2388ad6d2bcb
\.


--
-- Data for Name: institutions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.institutions (id, ipeds_id, name, city, state, control_type, primary_image_url, created_at, updated_at) FROM stdin;
1	164465	Amherst College	Amherst	MA	PRIVATE_NONPROFIT	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ma/ma_curated_164465_amherst_college_optimized.jpg	2025-10-01 01:45:18.542629	2025-10-01 01:45:18.542629
2	164924	Boston College	Boston	MA	PRIVATE_NONPROFIT	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ma/ma_curated_164924_Boston_College_optimized.jpg	2025-10-01 01:45:18.542629	2025-10-01 01:45:18.542629
3	164988	Boston University	Boston	MA	PRIVATE_NONPROFIT	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ma/ma_curated_164988_Boston_University_optimized.jpg	2025-10-01 01:45:18.542629	2025-10-01 01:45:18.542629
4	165015	Brandeis University	Waltham	MA	PRIVATE_NONPROFIT	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ma/ma_curated_165015_BrandeisUniversity_optimized.jpg	2025-10-01 01:45:18.542629	2025-10-01 01:45:18.542629
5	166027	Harvard University	Cambridge	MA	PRIVATE_NONPROFIT	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ma/ma_curated_166027_Harvard_optimized.jpg	2025-10-01 01:45:18.542629	2025-10-01 01:45:18.542629
6	166629	University of Massachusetts Amherst	Amherst	MA	PUBLIC	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ma/ma_curated_166629_UMASS_amherst_optimized.jpg	2025-10-01 01:45:18.542629	2025-10-01 01:45:18.542629
7	166683	MIT	Cambridge	MA	PRIVATE_NONPROFIT	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ma/ma_curated_166683_MIT_optimized.jpg	2025-10-01 01:45:18.542629	2025-10-01 01:45:18.542629
8	167358	Northeastern University	Boston	MA	PRIVATE_NONPROFIT	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ma/ma_curated_167358_Northeastern_optimized.jpg	2025-10-01 01:45:18.542629	2025-10-01 01:45:18.542629
9	167835	Smith College	Northampton	MA	PRIVATE_NONPROFIT	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ma/ma_curated_167835_SmithCollege_optimized.jpg	2025-10-01 01:45:18.542629	2025-10-01 01:45:18.542629
10	168148	Tufts University	Medford	MA	PRIVATE_NONPROFIT	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ma/ma_curated_168148_Tufts_University_optimized.jpg	2025-10-01 01:45:18.542629	2025-10-01 01:45:18.542629
11	168218	Wellesley College	Wellesley	MA	PRIVATE_NONPROFIT	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ma/ma_curated_168218_Wellesley_College_optimized.jpg	2025-10-01 01:45:18.542629	2025-10-01 01:45:18.542629
12	168342	Williams College	Williamstown	MA	PRIVATE_NONPROFIT	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ma/ma_curated_168342_Williams_optimized.jpg	2025-10-01 01:45:18.542629	2025-10-01 01:45:18.542629
14	182670	Dartmouth College	Hanover	NH	PRIVATE_NONPROFIT	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/nh/nh_institution_1887_manual_images/institution_1887_dartmouth_optimized.jpg	2025-10-01 02:17:57.181804	2025-10-01 02:17:57.181804
23	182917	Magdalen College	Warner	NH	PRIVATE_NONPROFIT	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/nh/nh_institution_1893_manual_images/institution_1893_magdalen_optimized.jpg	2025-10-01 02:17:57.181804	2025-10-01 02:17:57.181804
18	183239	Saint Anselm College	Manchester	NH	PRIVATE_NONPROFIT	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/nh/nh_institution_1911_manual_images/institution_1911_saint_anselm_optimized.jpg	2025-10-01 02:17:57.181804	2025-10-01 02:17:57.181804
16	183080	Plymouth State University	Plymouth	NH	PUBLIC	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/nh/nh_institution_1901_manual_images/institution_1901_plymouth_state_optimized.jpg	2025-10-01 02:17:57.181804	2025-10-01 02:17:57.181804
20	182795	Franklin Pierce University	Rindge	NH	PRIVATE_NONPROFIT	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/nh/nh_institution_1890_manual_images/institution_1890_franklin_pierce_optimized.jpg	2025-10-01 02:17:57.181804	2025-10-01 02:17:57.181804
21	182634	Colby-Sawyer College	New London	NH	PRIVATE_NONPROFIT	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/nh/nh_institution_1886_manual_images/institution_1886_colby_sawyer_optimized.jpg	2025-10-01 02:17:57.181804	2025-10-01 02:17:57.181804
27	442523	Alaska Christian College	Soldotna	AK	PRIVATE_NONPROFIT	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ak/Alaska_Christian_College_optimized	2025-10-07 08:06:18.46186	2025-10-11 04:46:55.86246
32	102553	University of Alaska Anchorage	Anchorage	AK	PUBLIC	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ak/University_of_Alaska_Anchorage_optimized.jpg	2025-10-07 08:06:18.46186	2025-10-08 01:07:27.674752
29	102711	Alaska Vocational Technical Center	Seward	AK	PUBLIC	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ak/Alaska_Vocational_Technical_Center_optimized.jpg	2025-10-07 08:06:18.46186	2025-10-08 01:07:35.967262
26	103501	Alaska Career College	Anchorage	AK	PRIVATE_FOR_PROFIT	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ak/Alaska_Career_College_optimized.jpg	2025-10-07 08:06:18.46186	2025-10-08 01:07:36.542629
24	183150	Great Bay Community College	Portsmouth	NH	PUBLIC	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/nh/nh_institution_1908_manual_images/institution_1908_great_bay_optimized.jpg	2025-10-01 02:17:57.181804	2025-10-01 02:17:57.181804
31	434584	Ilisagvik College	Barrow	AK	PUBLIC	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ak/Ilisagvik_College_optimized.jpg	2025-10-07 08:06:18.46186	2025-10-08 01:07:37.095466
22	183071	University of New Hampshire at Manchester	Manchester	NH	PUBLIC	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/nh/nh_institution_1905_manual_images/institution_1905_lakes_region_optimized.jpg	2025-10-01 02:17:57.181804	2025-10-01 02:17:57.181804
17	183062	Keene State College	Keene	NH	PUBLIC	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/nh/nh_institution_1899_manual_images/institution_1899_keene_state_optimized.jpg	2025-10-01 02:17:57.181804	2025-10-01 02:17:57.181804
13	183044	University of New Hampshire-Main Campus	Durham	NH	PUBLIC	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/nh/nh_institution_1898_manual_images/institution_1898_unh_main_optimized.jpg	2025-10-01 02:17:57.181804	2025-10-01 02:17:57.181804
15	183026	Southern New Hampshire University	Manchester	NH	PRIVATE_NONPROFIT	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/nh/nh_institution_1896_manual_images/institution_1896_snhu_optimized.jpg	2025-10-01 02:17:57.181804	2025-10-01 02:17:57.181804
19	182980	New England College	Henniker	NH	PRIVATE_NONPROFIT	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/nh/nh_institution_1894_manual_images/institution_1894_new_england_optimized.jpg	2025-10-01 02:17:57.181804	2025-10-01 02:17:57.181804
28	102669	Alaska Pacific University	Anchorage	AK	PRIVATE_NONPROFIT	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ak/Alaska_Pacific_University_optimized.jpg	2025-10-07 08:06:18.46186	2025-10-08 01:07:33.743221
30	102845	Charter College	Anchorage	AK	PRIVATE_FOR_PROFIT	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ak/Charter_College_optimized.jpg	2025-10-07 08:06:18.46186	2025-10-08 01:07:35.251316
25	102580	Alaska Bible College	Palmer	AK	PRIVATE_NONPROFIT	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ak/Alaska_Bible_College_optimized.jpg	2025-10-07 08:06:18.46186	2025-10-08 01:07:29.004119
60	105899	Arizona Christian University	Glendale	AZ	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
61	495457	Arizona College of Nursing-Phoenix	Phoenix	AZ	PRIVATE_FOR_PROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
62	421708	Arizona College of Nursing-Tempe	Tempe	AZ	PRIVATE_FOR_PROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
63	104151	Arizona State University Campus Immersion	Tempe	AZ	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
64	483124	Arizona State University Digital Immersion	Scottsdale	AZ	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
65	104586	Embry-Riddle Aeronautical University-Prescott	Prescott	AZ	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
66	104717	Grand Canyon University	Phoenix	AZ	PRIVATE_FOR_PROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
67	105330	Northern Arizona University	Flagstaff	AZ	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
68	464226	Ottawa University-Surprise	Surprise	AZ	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
69	105589	Prescott College	Prescott	AZ	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
70	363934	University of Advancing Technology	Tempe	AZ	PRIVATE_FOR_PROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
71	104179	University of Arizona	Tucson	AZ	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
72	110565	California State University-Fullerton	Fullerton	CA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
73	110583	California State University-Long Beach	Long Beach	CA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
74	110608	California State University-Northridge	Northridge	CA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
75	110617	California State University-Sacramento	Sacramento	CA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
76	122409	San Diego State University	San Diego	CA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
77	122755	San Jose State University	San Jose	CA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
78	110635	University of California-Berkeley	Berkeley	CA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
79	110644	University of California-Davis	Davis	CA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
80	110653	University of California-Irvine	Irvine	CA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
81	110662	University of California-Los Angeles	Los Angeles	CA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
82	110680	University of California-San Diego	La Jolla	CA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
83	123961	University of Southern California	Los Angeles	CA	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
84	127556	Colorado Mesa University	Grand Junction	CO	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
85	126775	Colorado School of Mines	Golden	CO	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
86	476975	Colorado State University Global	Aurora	CO	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
87	128106	Colorado State University Pueblo	Pueblo	CO	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
88	126818	Colorado State University-Fort Collins	Fort Collins	CO	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
89	127565	Metropolitan State University of Denver	Denver	CO	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
90	127918	Regis University	Denver	CO	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
91	126614	University of Colorado Boulder	Boulder	CO	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
92	126580	University of Colorado Colorado Springs	Colorado Springs	CO	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
93	126562	University of Colorado Denver/Anschutz Medical Campus	Denver	CO	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
94	127060	University of Denver	Denver	CO	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
95	127741	University of Northern Colorado	Greeley	CO	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
96	128771	Central Connecticut State University	New Britain	CT	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
97	129215	Eastern Connecticut State University	Willimantic	CT	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
98	129242	Fairfield University	Fairfield	CT	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
99	130226	Quinnipiac University	Hamden	CT	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
100	130253	Sacred Heart University	Fairfield	CT	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
101	130493	Southern Connecticut State University	New Haven	CT	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
102	128744	University of Bridgeport	Bridgeport	CT	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
41	100751	The University of Alabama	Tuscaloosa	AL	PUBLIC	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/al/The_University_of_Alabama_optimized.jpg	2025-10-07 08:06:18.46186	2025-10-09 00:24:43.5323
40	102049	Samford University	Birmingham	AL	PRIVATE_NONPROFIT	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/al/Samford_University_optimized.jpg	2025-10-07 08:06:18.46186	2025-10-09 00:24:43.856979
42	102368	Troy University	Troy	AL	PUBLIC	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/al/Troy_University_optimized.jpg	2025-10-07 08:06:18.46186	2025-10-09 00:24:44.036451
44	100706	University of Alabama in Huntsville	Huntsville	AL	PUBLIC	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/al/University_of_Alabama_in_Huntsville_optimized.jpg	2025-10-07 08:06:18.46186	2025-10-09 00:24:44.879971
45	101879	University of North Alabama	Florence	AL	PUBLIC	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/al/University_of_North_Alabama_optimized.jpg	2025-10-07 08:06:18.46186	2025-10-09 00:24:45.152716
43	100663	University of Alabama at Birmingham	Birmingham	AL	PUBLIC	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/al/University_of_Alabama_at_Birmingham_optimized.jpg	2025-10-07 08:06:18.46186	2025-10-09 00:24:45.403089
39	101480	Jacksonville State University	Jacksonville	AL	PUBLIC	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/al/Jacksonville_State_University_optimized.jpg	2025-10-07 08:06:18.46186	2025-10-09 00:24:45.651897
49	106467	Arkansas Tech University	Russellville	AR	PUBLIC	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ar/Arkansas_Tech_University_optimized.jpg	2025-10-07 08:06:18.46186	2025-10-11 04:03:46.142164
52	107141	John Brown University	Siloam Springs	AR	PRIVATE_NONPROFIT	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ar/John_Brown_University_optimized.jpg	2025-10-07 08:06:18.46186	2025-10-11 04:03:46.602698
59	106704	University of Central Arkansas	Conway	AR	PUBLIC	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ar/University_of_Central_Arkansas_optimized.jpg	2025-10-07 08:06:18.46186	2025-10-11 04:03:46.901822
55	107585	University of Arkansas Community College-Morrilton	Morrilton	AR	PUBLIC	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ar/University_of_Arkansas_Community_College_Morrilton_optimized.jpg	2025-10-07 08:06:18.46186	2025-10-11 04:03:47.134475
56	106245	University of Arkansas at Little Rock	Little Rock	AR	PUBLIC	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ar/University_of_Arkansas_at_Little_Rock_optimized.jpg	2025-10-07 08:06:18.46186	2025-10-11 04:03:47.314003
103	129020	University of Connecticut	Storrs	CT	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
104	129525	University of Hartford	West Hartford	CT	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
105	129941	University of New Haven	West Haven	CT	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
106	130776	Western Connecticut State University	Danbury	CT	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
107	130794	Yale University	New Haven	CT	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
108	131159	American University	Washington	DC	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
109	131450	Gallaudet University	Washington	DC	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
110	131469	George Washington University	Washington	DC	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
111	131496	Georgetown University	Washington	DC	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
112	131520	Howard University	Washington	DC	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
113	131830	National Conservatory of Dramatic Arts	Washington	DC	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
114	496803	NewU University	Washington	DC	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
115	486424	Saint Michael College of Allied Health	Washington	DC	PRIVATE_FOR_PROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
116	459994	Strayer University-Global Region	Washington	DC	PRIVATE_FOR_PROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
117	131283	The Catholic University of America	Washington	DC	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
118	131876	Trinity Washington University	Washington	DC	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
119	131399	University of the District of Columbia	Washington	DC	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
120	130873	Dawn Career Institute LLC	Newark	DE	PRIVATE_FOR_PROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
121	432524	Delaware College of Art and Design	Wilmington	DE	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
122	130934	Delaware State University	Dover	DE	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
123	130907	Delaware Technical Community College-Terry	Dover	DE	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
124	130989	Goldey-Beacom College	Wilmington	DE	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
125	130837	Margaret H Rollins School of Nursing at Beebe Medical Center	Lewes	DE	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
126	459301	Paul Mitchell the School-Delaware	Newark	DE	PRIVATE_FOR_PROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
127	491473	Polytech Adult Education	Woodside	DE	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
128	131061	Schilling-Douglas School of Hair Design	Newark	DE	PRIVATE_FOR_PROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
129	450298	Strayer University-Delaware	Wilmington	DE	PRIVATE_FOR_PROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
130	130943	University of Delaware	Newark	DE	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
131	131113	Wilmington University	New Castle	DE	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
132	133669	Florida Atlantic University	Boca Raton	FL	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
133	433660	Florida Gulf Coast University	Fort Myers	FL	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
134	133951	Florida International University	Miami	FL	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
135	134097	Florida State University	Tallahassee	FL	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
136	135081	Keiser University-Ft Lauderdale	Fort Lauderdale	FL	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
137	136215	Nova Southeastern University	Fort Lauderdale	FL	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
138	132903	University of Central Florida	Orlando	FL	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
139	134130	University of Florida	Gainesville	FL	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
140	135726	University of Miami	Coral Gables	FL	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
141	136172	University of North Florida	Jacksonville	FL	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
142	137351	University of South Florida	Tampa	FL	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
143	138354	University of West Florida	Pensacola	FL	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
144	139658	Emory University	Atlanta	GA	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
145	447689	Georgia Gwinnett College	Lawrenceville	GA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
146	139755	Georgia Institute of Technology-Main Campus	Atlanta	GA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
147	139931	Georgia Southern University	Statesboro	GA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
148	139940	Georgia State University	Atlanta	GA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
149	244437	Georgia State University-Perimeter College	Atlanta	GA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
150	486840	Kennesaw State University	Kennesaw	GA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
151	140951	Savannah College of Art and Design	Savannah	GA	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
152	139959	University of Georgia	Athens	GA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
153	482680	University of North Georgia	Dahlonega	GA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
154	141334	University of West Georgia	Carrollton	GA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
155	141264	Valdosta State University	Valdosta	GA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
156	230047	Brigham Young University-Hawaii	Laie	HI	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
157	141486	Chaminade University of Honolulu	Honolulu	HI	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
158	383190	Hawaii Community College	Hilo	HI	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
159	141644	Hawaii Pacific University	Honolulu	HI	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
160	141680	Honolulu Community College	Honolulu	HI	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
161	141796	Kapiolani Community College	Honolulu	HI	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
162	141811	Leeward Community College	Pearl City	HI	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
163	141839	University of Hawaii Maui College	Kahului	HI	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
164	141565	University of Hawaii at Hilo	Hilo	HI	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
165	141574	University of Hawaii at Manoa	Honolulu	HI	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
166	141981	University of Hawaii-West Oahu	Kapolei	HI	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
167	141990	Windward Community College	Kaneohe	HI	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
168	153001	Buena Vista University	Storm Lake	IA	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
169	153250	Dordt University	Sioux Center	IA	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
170	153269	Drake University	Des Moines	IA	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
171	153375	Grand View University	Des Moines	IA	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
172	153603	Iowa State University	Ames	IA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
173	153861	Maharishi International University	Fairfield	IA	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
174	154004	Morningside University	Sioux City	IA	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
175	154235	Saint Ambrose University	Davenport	IA	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
176	153278	University of Dubuque	Dubuque	IA	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
177	153658	University of Iowa	Iowa City	IA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
178	154095	University of Northern Iowa	Cedar Falls	IA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
179	154493	Upper Iowa University	Fayette	IA	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
180	142090	Boise Bible College	Boise	ID	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
181	142115	Boise State University	Boise	ID	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
182	142522	Brigham Young University-Idaho	Rexburg	ID	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
183	142559	College of Southern Idaho	Twin Falls	ID	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
184	455114	College of Western Idaho	Nampa	ID	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
185	142276	Idaho State University	Pocatello	ID	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
186	142328	Lewis-Clark State College	Lewiston	ID	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
187	440396	New Saint Andrews College	Moscow	ID	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
188	142443	North Idaho College	Coeur d'Alene	ID	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
189	142461	Northwest Nazarene University	Nampa	ID	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
190	142294	The College of Idaho	Caldwell	ID	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
191	142285	University of Idaho	Moscow	ID	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
192	454227	Chamberlain University-Illinois	Addison	IL	PRIVATE_FOR_PROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
193	144740	DePaul University	Chicago	IL	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
194	482477	DeVry University-Illinois	Lisle	IL	PRIVATE_FOR_PROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
195	145813	Illinois State University	Normal	IL	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
196	146719	Loyola University Chicago	Chicago	IL	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
197	147703	Northern Illinois University	Dekalb	IL	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
198	147767	Northwestern University	Evanston	IL	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
199	149222	Southern Illinois University-Carbondale	Carbondale	IL	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
200	149231	Southern Illinois University-Edwardsville	Edwardsville	IL	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
201	144050	University of Chicago	Chicago	IL	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
202	145600	University of Illinois Chicago	Chicago	IL	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
203	145637	University of Illinois Urbana-Champaign	Champaign	IL	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
204	150136	Ball State University	Muncie	IN	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
205	150163	Butler University	Indianapolis	IN	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
206	151324	Indiana State University	Terre Haute	IN	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
207	151351	Indiana University-Bloomington	Bloomington	IN	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
208	151111	Indiana University-Indianapolis	Indianapolis	IN	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
209	151102	Purdue University Fort Wayne	Fort Wayne	IN	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
210	490805	Purdue University Northwest	Hammond	IN	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
211	243780	Purdue University-Main Campus	West Lafayette	IN	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
212	414878	Trine University-Regional/Non-Traditional Campuses	Angola	IN	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
213	151263	University of Indianapolis	Indianapolis	IN	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
214	152080	University of Notre Dame	Notre Dame	IN	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
215	151306	University of Southern Indiana	Evansville	IN	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
216	154688	Baker University	Baldwin City	KS	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
217	154712	Benedictine College	Atchison	KS	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
218	155025	Emporia State University	Emporia	KS	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
219	155061	Fort Hays State University	Hays	KS	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
220	155089	Friends University	Wichita	KS	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
221	155399	Kansas State University	Manhattan	KS	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
222	155520	MidAmerica Nazarene University	Olathe	KS	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
223	155335	Newman University	Wichita	KS	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
224	155681	Pittsburg State University	Pittsburg	KS	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
225	155317	University of Kansas	Lawrence	KS	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
226	155812	University of Saint Mary	Leavenworth	KS	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
227	156125	Wichita State University	Wichita	KS	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
228	156286	Bellarmine University	Louisville	KY	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
229	156365	Campbellsville University	Campbellsville	KY	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
230	156620	Eastern Kentucky University	Richmond	KY	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
231	157386	Morehead State University	Morehead	KY	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
232	157401	Murray State University	Murray	KY	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
233	157447	Northern Kentucky University	Highland Heights	KY	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
234	157748	The Southern Baptist Theological Seminary	Louisville	KY	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
235	157809	Thomas More University	Crestview Hills	KY	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
236	157085	University of Kentucky	Lexington	KY	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
237	157289	University of Louisville	Louisville	KY	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
238	156541	University of the Cumberlands	Williamsburg	KY	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
239	157951	Western Kentucky University	Bowling Green	KY	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
240	159391	Louisiana State University and Agricultural & Mechanical College	Baton Rouge	LA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
241	159416	Louisiana State University-Shreveport	Shreveport	LA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
242	159647	Louisiana Tech University	Ruston	LA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
243	159717	McNeese State University	Lake Charles	LA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
244	159966	Nicholls State University	Thibodaux	LA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
245	160038	Northwestern State University of Louisiana	Natchitoches	LA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
246	160612	Southeastern Louisiana University	Hammond	LA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
247	160621	Southern University and A & M College	Baton Rouge	LA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
248	160755	Tulane University of Louisiana	New Orleans	LA	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
249	160658	University of Louisiana at Lafayette	Lafayette	LA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
250	159993	University of Louisiana at Monroe	Monroe	LA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
251	159939	University of New Orleans	New Orleans	LA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
252	162007	Bowie State University	Bowie	MD	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
253	162584	Frostburg State University	Frostburg	MD	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
254	162928	Johns Hopkins University	Baltimore	MD	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
255	163046	Loyola University Maryland	Baltimore	MD	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
256	163453	Morgan State University	Baltimore	MD	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
257	163851	Salisbury University	Salisbury	MD	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
258	164173	Stevenson University	Owings Mills	MD	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
259	164076	Towson University	Towson	MD	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
260	164155	United States Naval Academy	Annapolis	MD	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
261	161873	University of Baltimore	Baltimore	MD	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
262	163268	University of Maryland-Baltimore County	Baltimore	MD	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
263	163286	University of Maryland-College Park	College Park	MD	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
264	160977	Bates College	Lewiston	ME	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
265	161004	Bowdoin College	Brunswick	ME	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
266	161086	Colby College	Waterville	ME	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
267	487524	Husson University	Bangor	ME	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
268	161518	Saint Joseph's College of Maine	Standish	ME	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
269	161563	Thomas College	Waterville	ME	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
270	161572	Unity Environmental University	New Gloucester	ME	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
271	161253	University of Maine	Orono	ME	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
272	161226	University of Maine at Farmington	Farmington	ME	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
273	161341	University of Maine at Presque Isle	Presque Isle	ME	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
274	161457	University of New England	Biddeford	ME	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
275	161554	University of Southern Maine	Portland	ME	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
276	169248	Central Michigan University	Mount Pleasant	MI	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
277	169798	Eastern Michigan University	Ypsilanti	MI	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
278	169910	Ferris State University	Big Rapids	MI	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
279	170082	Grand Valley State University	Allendale	MI	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
280	171100	Michigan State University	East Lansing	MI	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
281	171128	Michigan Technological University	Houghton	MI	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
282	171456	Northern Michigan University	Marquette	MI	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
283	171571	Oakland University	Rochester Hills	MI	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
284	170976	University of Michigan-Ann Arbor	Ann Arbor	MI	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
285	171137	University of Michigan-Dearborn	Dearborn	MI	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
286	172644	Wayne State University	Detroit	MI	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
287	172699	Western Michigan University	Kalamazoo	MI	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
288	173124	Bemidji State University	Bemidji	MN	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
289	173328	Concordia University-Saint Paul	Saint Paul	MN	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
290	174020	Metropolitan State University	Saint Paul	MN	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
291	174358	Minnesota State University Moorhead	Moorhead	MN	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
292	173920	Minnesota State University-Mankato	Mankato	MN	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
293	174783	Saint Cloud State University	Saint Cloud	MN	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
294	174817	Saint Mary's University of Minnesota	Winona	MN	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
295	175078	Southwest Minnesota State University	Marshall	MN	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
296	174233	University of Minnesota-Duluth	Duluth	MN	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
297	174066	University of Minnesota-Twin Cities	Minneapolis	MN	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
298	174914	University of St Thomas	Saint Paul	MN	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
299	175272	Winona State University	Winona	MN	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
300	177968	Lindenwood University	Saint Charles	MO	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
301	178059	Maryville University of Saint Louis	Saint Louis	MO	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
302	179566	Missouri State University-Springfield	Springfield	MO	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
303	178624	Northwest Missouri State University	Maryville	MO	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
304	179159	Saint Louis University	Saint Louis	MO	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
305	179557	Southeast Missouri State University	Cape Girardeau	MO	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
306	176965	University of Central Missouri	Warrensburg	MO	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
307	178396	University of Missouri-Columbia	Columbia	MO	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
308	178402	University of Missouri-Kansas City	Kansas City	MO	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
309	178420	University of Missouri-St Louis	Saint Louis	MO	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
310	179867	Washington University in St Louis	Saint Louis	MO	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
311	179894	Webster University	Saint Louis	MO	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
312	175342	Alcorn State University	Alcorn State	MS	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
313	175421	Belhaven University	Jackson	MS	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
314	175430	Blue Mountain Christian University	Blue Mountain	MS	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
315	175616	Delta State University	Cleveland	MS	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
316	175856	Jackson State University	Jackson	MS	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
317	176053	Mississippi College	Clinton	MS	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
318	176080	Mississippi State University	Mississippi State	MS	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
319	176035	Mississippi University for Women	Columbus	MS	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
320	176044	Mississippi Valley State University	Itta Bena	MS	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
321	176017	University of Mississippi	University	MS	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
322	176372	University of Southern Mississippi	Hattiesburg	MS	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
323	176479	William Carey University	Hattiesburg	MS	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
324	180106	Carroll College	Helena	MT	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
325	180197	Flathead Valley Community College	Kalispell	MT	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
326	180249	Great Falls College Montana State University	Great Falls	MT	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
327	180276	Helena College University of Montana	Helena	MT	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
328	262165	Montana Bible College	Billings	MT	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
329	180461	Montana State University	Bozeman	MT	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
330	180179	Montana State University Billings	Billings	MT	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
331	180416	Montana Technological University	Butte	MT	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
332	180595	Rocky Mountain College	Billings	MT	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
333	180489	The University of Montana	Missoula	MT	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
334	180692	The University of Montana-Western	Dillon	MT	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
335	180258	University of Providence	Great Falls	MT	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
336	197869	Appalachian State University	Boone	NC	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
337	198419	Duke University	Durham	NC	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
338	198464	East Carolina University	Greenville	NC	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
339	199102	North Carolina A & T State University	Greensboro	NC	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
340	199157	North Carolina Central University	Durham	NC	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
341	199193	North Carolina State University at Raleigh	Raleigh	NC	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
342	199218	University of North Carolina Wilmington	Wilmington	NC	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
343	199120	University of North Carolina at Chapel Hill	Chapel Hill	NC	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
344	199139	University of North Carolina at Charlotte	Charlotte	NC	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
345	199148	University of North Carolina at Greensboro	Greensboro	NC	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
346	199847	Wake Forest University	Winston-Salem	NC	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
347	200004	Western Carolina University	Cullowhee	NC	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
348	200022	Bismarck State College	Bismarck	ND	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
349	200314	Dakota College at Bottineau	Bottineau	ND	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
350	200059	Dickinson State University	Dickinson	ND	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
351	200192	Lake Region State College	Devils Lake	ND	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
352	200253	Minot State University	Minot	ND	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
353	200305	North Dakota State College of Science	Wahpeton	ND	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
354	200332	North Dakota State University-Main Campus	Fargo	ND	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
355	200484	Trinity Bible College and Graduate School	Ellendale	ND	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
356	200156	University of Jamestown	Jamestown	ND	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
357	200217	University of Mary	Bismarck	ND	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
358	200280	University of North Dakota	Grand Forks	ND	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
359	200572	Valley City State University	Valley City	ND	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
360	180878	Bryan College of Health Sciences	Lincoln	NE	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
361	180832	Clarkson College	Omaha	NE	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
362	180984	Concordia University-Nebraska	Seward	NE	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
363	181002	Creighton University	Omaha	NE	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
364	181020	Doane University	Crete	NE	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
365	181127	Hastings College	Hastings	NE	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
366	181330	Midland University	Fremont	NE	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
367	181297	Nebraska Methodist College of Nursing & Allied Health	Omaha	NE	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
368	181446	Nebraska Wesleyan University	Lincoln	NE	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
369	181215	University of Nebraska at Kearney	Kearney	NE	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
370	181394	University of Nebraska at Omaha	Omaha	NE	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
371	181464	University of Nebraska-Lincoln	Lincoln	NE	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
372	185262	Kean University	Union	NJ	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
373	185590	Montclair State University	Montclair	NJ	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
374	185828	New Jersey Institute of Technology	Newark	NJ	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
375	186131	Princeton University	Princeton	NJ	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
376	184782	Rowan University	Glassboro	NJ	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
377	186380	Rutgers University-New Brunswick	New Brunswick	NJ	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
378	186399	Rutgers University-Newark	Newark	NJ	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
379	186584	Seton Hall University	South Orange	NJ	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
380	186867	Stevens Institute of Technology	Hoboken	NJ	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
381	186876	Stockton University	Galloway	NJ	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
382	187134	The College of New Jersey	Ewing	NJ	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
383	187444	William Paterson University of New Jersey	Wayne	NJ	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
384	187532	Central New Mexico Community College	Albuquerque	NM	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
385	187648	Eastern New Mexico University-Main Campus	Portales	NM	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
386	187745	Institute of American Indian and Alaska Native Culture and Arts Development	Santa Fe	NM	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
387	187967	New Mexico Institute of Mining and Technology	Socorro	NM	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
388	187912	New Mexico Military Institute	Roswell	NM	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
389	187620	New Mexico State University-Dona Ana	Las Cruces	NM	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
390	188030	New Mexico State University-Main Campus	Las Cruces	NM	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
391	188100	San Juan College	Farmington	NM	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
392	188137	Santa Fe Community College	Santa Fe	NM	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
393	245652	St. John's College	Santa Fe	NM	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
394	187985	University of New Mexico-Main Campus	Albuquerque	NM	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
395	188304	Western New Mexico University	Silver City	NM	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
396	487375	Arizona College of Nursing-Las Vegas	Las Vegas	NV	PRIVATE_FOR_PROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
397	486938	Chamberlain University-Nevada	Las Vegas	NV	PRIVATE_FOR_PROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
398	182005	College of Southern Nevada	Las Vegas	NV	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
399	482547	DeVry University-Nevada	Henderson	NV	PRIVATE_FOR_PROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
400	182306	Great Basin College	Elko	NV	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
401	441900	Nevada State University	Henderson	NV	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
402	445735	Roseman University of Health Sciences	Henderson	NV	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
403	459824	Touro University Nevada	Henderson	NV	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
404	182500	Truckee Meadows Community College	Reno	NV	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
405	182281	University of Nevada-Las Vegas	Las Vegas	NV	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
406	182290	University of Nevada-Reno	Reno	NV	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
407	182564	Western Nevada College	Carson City	NV	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
408	196079	Binghamton University	Vestal	NY	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
409	190512	CUNY Bernard M Baruch College	New York	NY	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
410	190594	CUNY Hunter College	New York	NY	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
411	190150	Columbia University in the City of New York	New York	NY	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
412	190415	Cornell University	Ithaca	NY	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
413	193900	New York University	New York	NY	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
414	195003	Rochester Institute of Technology	Rochester	NY	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
415	195809	St. John's University-New York	Queens	NY	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
416	196097	Stony Brook University	Stony Brook	NY	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
417	196413	Syracuse University	Syracuse	NY	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
418	196060	University at Albany	Albany	NY	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
419	196088	University at Buffalo	Buffalo	NY	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
420	201441	Bowling Green State University-Main Campus	Bowling Green	OH	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
421	201645	Case Western Reserve University	Cleveland	OH	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
422	202134	Cleveland State University	Cleveland	OH	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
423	203517	Kent State University at Kent	Kent	OH	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
424	204024	Miami University-Oxford	Oxford	OH	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
425	204796	Ohio State University-Main Campus	Columbus	OH	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
426	204857	Ohio University-Main Campus	Athens	OH	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
427	200800	University of Akron Main Campus	Akron	OH	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
428	201885	University of Cincinnati-Main Campus	Cincinnati	OH	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
429	202480	University of Dayton	Dayton	OH	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
430	206084	University of Toledo	Toledo	OH	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
431	206695	Youngstown State University	Youngstown	OH	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
432	207041	East Central University	Ada	OK	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
433	207263	Northeastern State University	Tahlequah	OK	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
434	207306	Northwestern Oklahoma State University	Alva	OK	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
435	207324	Oklahoma Christian University	Edmond	OK	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
436	207458	Oklahoma City University	Oklahoma City	OK	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
437	207388	Oklahoma State University-Main Campus	Stillwater	OK	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
438	207582	Oral Roberts University	Tulsa	OK	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
439	207847	Southeastern Oklahoma State University	Durant	OK	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
440	207865	Southwestern Oklahoma State University	Weatherford	OK	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
441	206941	University of Central Oklahoma	Edmond	OK	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
442	207500	University of Oklahoma-Norman Campus	Norman	OK	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
443	207971	University of Tulsa	Tulsa	OK	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
444	208646	Eastern Oregon University	La Grande	OR	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
445	208822	George Fox University	Newberg	OR	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
446	209056	Lewis & Clark College	Portland	OR	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
447	209506	Oregon Institute of Technology	Klamath Falls	OR	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
448	209542	Oregon State University	Corvallis	OR	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
449	209612	Pacific University	Forest Grove	OR	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
450	209807	Portland State University	Portland	OR	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
451	210146	Southern Oregon University	Ashland	OR	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
452	209551	University of Oregon	Eugene	OR	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
453	209825	University of Portland	Portland	OR	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
454	210429	Western Oregon University	Monmouth	OR	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
455	210401	Willamette University	Salem	OR	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
456	211440	Carnegie Mellon University	Pittsburgh	PA	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
457	498562	Commonwealth University of Pennsylvania	Bloomsburg	PA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
458	212054	Drexel University	Philadelphia	PA	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
459	213020	Indiana University of Pennsylvania-Main Campus	Indiana	PA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
460	214777	Pennsylvania State University-Main Campus	University Park	PA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
461	479956	Pennsylvania State University-World Campus	University Park	PA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
462	498571	Pennsylvania Western University	California	PA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
463	216339	Temple University	Philadelphia	PA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
464	215062	University of Pennsylvania	Philadelphia	PA	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
465	215293	University of Pittsburgh-Pittsburgh Campus	Pittsburgh	PA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
466	216597	Villanova University	Villanova	PA	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
467	216764	West Chester University of Pennsylvania	West Chester	PA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
468	217156	Brown University	Providence	RI	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
469	217165	Bryant University	Smithfield	RI	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
470	437237	IYRS School of Technology & Trades	Newport	RI	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
471	460349	Johnson & Wales University-Online	Providence	RI	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
472	217235	Johnson & Wales University-Providence	Providence	RI	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
473	217305	New England Institute of Technology	East Greenwich	RI	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
474	217402	Providence College	Providence	RI	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
475	217420	Rhode Island College	Providence	RI	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
476	217493	Rhode Island School of Design	Providence	RI	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
477	217518	Roger Williams University	Bristol	RI	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
478	217536	Salve Regina University	Newport	RI	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
479	217484	University of Rhode Island	Kingston	RI	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
480	217633	Anderson University	Anderson	SC	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
481	217688	Charleston Southern University	Charleston	SC	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
482	217864	Citadel Military College of South Carolina	Charleston	SC	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
483	217882	Clemson University	Clemson	SC	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
484	218724	Coastal Carolina University	Conway	SC	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
485	217819	College of Charleston	Charleston	SC	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
486	218061	Francis Marion University	Florence	SC	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
487	218229	Lander University	Greenwood	SC	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
488	218645	University of South Carolina Aiken	Aiken	SC	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
489	218663	University of South Carolina-Columbia	Columbia	SC	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
490	218742	University of South Carolina-Upstate	Spartanburg	SC	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
491	218964	Winthrop University	Rock Hill	SC	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
492	219000	Augustana University	Sioux Falls	SD	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
493	219046	Black Hills State University	Spearfish	SD	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
494	219082	Dakota State University	Madison	SD	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
495	219091	Dakota Wesleyan University	Mitchell	SD	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
496	219240	Kairos University	Sioux Falls	SD	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
497	219198	Mount Marty University	Yankton	SD	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
498	219259	Northern State University	Aberdeen	SD	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
499	219347	South Dakota School of Mines and Technology	Rapid City	SD	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
500	219356	South Dakota State University	Brookings	SD	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
501	219426	Southeast Technical College	Sioux Falls	SD	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
502	219383	University of Sioux Falls	Sioux Falls	SD	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
503	219471	University of South Dakota	Vermillion	SD	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
504	219602	Austin Peay State University	Clarksville	TN	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
505	219709	Belmont University	Nashville	TN	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
506	220075	East Tennessee State University	Johnson City	TN	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
507	220631	Lincoln Memorial University	Harrogate	TN	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
508	220978	Middle Tennessee State University	Murfreesboro	TN	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
509	221838	Tennessee State University	Nashville	TN	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
510	221847	Tennessee Technological University	Cookeville	TN	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
511	221740	The University of Tennessee-Chattanooga	Chattanooga	TN	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
512	221759	The University of Tennessee-Knoxville	Knoxville	TN	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
513	221768	The University of Tennessee-Martin	Martin	TN	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
514	220862	University of Memphis	Memphis	TN	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
515	221999	Vanderbilt University	Nashville	TN	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
516	227881	Sam Houston State University	Huntsville	TX	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
517	228723	Texas A & M University-College Station	College Station	TX	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
518	228459	Texas State University	San Marcos	TX	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
519	229115	Texas Tech University	Lubbock	TX	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
520	227368	The University of Texas Rio Grande Valley	Edinburg	TX	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
521	228769	The University of Texas at Arlington	Arlington	TX	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
522	228778	The University of Texas at Austin	Austin	TX	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
523	228787	The University of Texas at Dallas	Richardson	TX	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
524	228796	The University of Texas at El Paso	El Paso	TX	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
525	229027	The University of Texas at San Antonio	San Antonio	TX	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
526	225511	University of Houston	Houston	TX	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
527	227216	University of North Texas	Denton	TX	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
528	497268	Arizona College of Nursing-Salt Lake City	Murray	UT	PRIVATE_FOR_PROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
529	481456	Bonnie Joseph Academy of Cosmetology & Barbering	Heber City	UT	PRIVATE_FOR_PROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
530	230038	Brigham Young University	Provo	UT	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
531	447263	Joyce University of Nursing and Health Sciences	Draper	UT	PRIVATE_FOR_PROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
532	480985	Midwives College of Utah	Salt Lake City	UT	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
533	445692	Neumont College of Computer Science	Salt Lake City	UT	PRIVATE_FOR_PROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
534	230603	Southern Utah University	Cedar City	UT	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
535	230764	University of Utah	Salt Lake City	UT	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
536	230728	Utah State University	Logan	UT	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
537	230737	Utah Valley University	Orem	UT	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
538	433387	Western Governors University	Salt Lake City	UT	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
539	230807	Westminster University	Salt Lake City	UT	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
540	232186	George Mason University	Fairfax	VA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
541	232423	James Madison University	Harrisonburg	VA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
542	232557	Liberty University	Lynchburg	VA	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
543	232937	Norfolk State University	Norfolk	VA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
544	232982	Old Dominion University	Norfolk	VA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
545	233277	Radford University	Radford	VA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
546	231651	Regent University	Virginia Beach	VA	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
547	234076	University of Virginia-Main Campus	Charlottesville	VA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
548	234030	Virginia Commonwealth University	Richmond	VA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
549	233921	Virginia Polytechnic Institute and State University	Blacksburg	VA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
550	234155	Virginia State University	Petersburg	VA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
551	231624	William & Mary	Williamsburg	VA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
552	230816	Bennington College	Bennington	VT	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
553	230852	Champlain College	Burlington	VT	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
554	230861	Community College of Vermont	Montpelier	VT	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
555	230889	Goddard College	Plainfield	VT	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
556	247649	Landmark College	Putney	VT	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
557	230959	Middlebury College	Middlebury	VT	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
558	230995	Norwich University	Northfield	VT	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
559	231059	Saint Michael's College	Colchester	VT	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
560	231095	Sterling College	Craftsbury Common	VT	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
561	231174	University of Vermont	Burlington	VT	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
562	231147	Vermont Law and Graduate School	South Royalton	VT	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
563	231165	Vermont State University	Randolph	VT	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
564	234827	Central Washington University	Ellensburg	WA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
565	235097	Eastern Washington University	Cheney	WA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
566	235316	Gonzaga University	Spokane	WA	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
567	236230	Pacific Lutheran University	Tacoma	WA	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
568	236577	Seattle Pacific University	Seattle	WA	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
569	236595	Seattle University	Seattle	WA	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
570	377555	University of Washington-Bothell Campus	Bothell	WA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
571	236948	University of Washington-Seattle Campus	Seattle	WA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
572	377564	University of Washington-Tacoma Campus	Tacoma	WA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
573	236939	Washington State University	Pullman	WA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
574	237011	Western Washington University	Bellingham	WA	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
575	237066	Whitworth University	Spokane	WA	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
576	239105	Marquette University	Milwaukee	WI	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
577	240268	University of Wisconsin-Eau Claire	Eau Claire	WI	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
578	240277	University of Wisconsin-Green Bay	Green Bay	WI	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
579	240329	University of Wisconsin-La Crosse	La Crosse	WI	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
580	240444	University of Wisconsin-Madison	Madison	WI	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
581	240453	University of Wisconsin-Milwaukee	Milwaukee	WI	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
582	240365	University of Wisconsin-Oshkosh	Oshkosh	WI	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
583	240462	University of Wisconsin-Platteville	Platteville	WI	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
584	240471	University of Wisconsin-River Falls	River Falls	WI	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
585	240480	University of Wisconsin-Stevens Point	Stevens Point	WI	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
586	240417	University of Wisconsin-Stout	Menomonie	WI	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
587	240189	University of Wisconsin-Whitewater	Whitewater	WI	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
588	237215	Bluefield State University	Bluefield	WV	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
589	237330	Concord University	Athens	WV	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
590	237367	Fairmont State University	Fairmont	WV	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
591	237525	Marshall University	Huntington	WV	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
592	237792	Shepherd University	Shepherdstown	WV	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
593	237312	University of Charleston	Charleston	WV	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
594	237932	West Liberty University	West Liberty	WV	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
595	237899	West Virginia State University	Institute	WV	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
596	238032	West Virginia University	Morgantown	WV	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
597	237950	West Virginia University Institute of Technology	Beckley	WV	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
598	237969	West Virginia Wesleyan College	Buckhannon	WV	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
599	238078	Wheeling University	Wheeling	WV	PRIVATE_NONPROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
600	240505	Casper College	Casper	WY	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
601	240514	Central Wyoming College	Riverton	WY	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
602	240709	Cheeks Beauty Academy	Cheyenne	WY	PRIVATE_FOR_PROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
603	240596	Eastern Wyoming College	Torrington	WY	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
604	240620	Laramie County Community College	Cheyenne	WY	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
605	240666	Northern Wyoming Community College District	Sheridan	WY	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
606	240657	Northwest College	Powell	WY	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
607	240727	University of Wyoming	Laramie	WY	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
608	240693	Western Wyoming Community College	Rock Springs	WY	PUBLIC		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
609	240718	WyoTech	Laramie	WY	PRIVATE_FOR_PROFIT		2025-10-07 08:06:18.46186	2025-10-07 08:06:18.46186
34	102632	University of Alaska Southeast	Juneau	AK	PUBLIC	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ak/University_of_Alaska_Southeast_optimized.jpg	2025-10-07 08:06:18.46186	2025-10-08 01:07:30.23237
35	103529	University of Alaska System of Higher Education	Fairbanks	AK	PUBLIC	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ak/University_of_Alaska_System_of_Higher_Education_optimized.jpg	2025-10-07 08:06:18.46186	2025-10-08 01:07:32.793164
33	102614	University of Alaska Fairbanks	Fairbanks	AK	PUBLIC	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ak/University_of_Alaska_Fairbanks_optimized.jpg	2025-10-07 08:06:18.46186	2025-10-08 01:07:34.533961
37	100858	Auburn University	Auburn	AL	PUBLIC	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/al/Auburn_University_optimized.jpg	2025-10-07 08:06:18.46186	2025-10-09 00:24:44.172519
38	100830	Auburn University at Montgomery	Montgomery	AL	PUBLIC	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/al/Auburn_University_at_Montgomery_optimized.jpg	2025-10-07 08:06:18.46186	2025-10-09 00:24:44.374878
47	101587	University of West Alabama	Livingston	AL	PUBLIC	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/al/University_of_West_Alabama_optimized.jpg	2025-10-07 08:06:18.46186	2025-10-09 00:24:45.026355
36	100654	Alabama A & M University	Normal	AL	PUBLIC	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/al/Alabama_A_M_University_optimized.jpg	2025-10-07 08:06:18.46186	2025-10-09 00:24:45.267089
46	102094	University of South Alabama	Mobile	AL	PUBLIC	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/al/University_of_South_Alabama_optimized.jpg	2025-10-07 08:06:18.46186	2025-10-09 00:24:45.545613
48	106458	Arkansas State University	Jonesboro	AR	PUBLIC	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ar/Arkansas_State_University_optimized.jpg	2025-10-07 08:06:18.46186	2025-10-11 04:03:46.024936
50	107044	Harding University	Searcy	AR	PRIVATE_NONPROFIT	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ar/Harding_University_optimized.jpg	2025-10-07 08:06:18.46186	2025-10-11 04:03:46.276636
51	107071	Henderson State University	Arkadelphia	AR	PUBLIC	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ar/Henderson_State_University_optimized.jpg	2025-10-07 08:06:18.46186	2025-10-11 04:03:46.493599
53	107983	Southern Arkansas University Main Campus	Magnolia	AR	PUBLIC	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ar/Southern_Arkansas_University_Main_Campus_optimized.jpg	2025-10-07 08:06:18.46186	2025-10-11 04:03:46.707587
58	108092	University of Arkansas-Fort Smith	Fort Smith	AR	PUBLIC	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ar/University_of_Arkansas_Fort_Smith_optimized.jpg	2025-10-07 08:06:18.46186	2025-10-11 04:03:47.006186
54	106397	University of Arkansas	Fayetteville	AR	PUBLIC	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ar/University_of_Arkansas_optimized.jpg	2025-10-07 08:06:18.46186	2025-10-11 04:03:47.20208
57	106412	University of Arkansas at Pine Bluff	Pine Bluff	AR	PUBLIC	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/institutions/ar/University_of_Arkansas_at_Pine_Bluff_optimized.jpg	2025-10-07 08:06:18.46186	2025-10-11 04:03:47.493303
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
-- Data for Name: scholarships; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.scholarships (id, title, organization, scholarship_type, status, difficulty_level, amount_min, amount_max, is_renewable, number_of_awards, deadline, application_opens, for_academic_year, description, website_url, min_gpa, primary_image_url, verified, featured, views_count, applications_count, created_at, updated_at) FROM stdin;
4	UNCF General Scholarship	United Negro College Fund	DIVERSITY	ACTIVE	MODERATE	500	10000	f	\N	2026-03-31	2025-10-15	2026-2027	Supporting African American students attending UNCF member institutions or any accredited four-year institution. Award amounts vary based on financial need and merit.	https://uncf.org/scholarships	2.50	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/uncf_general_scholarship.jpg	t	f	0	0	2025-10-09 12:44:37.276296	2025-10-09 13:14:27.051725
6	Elks Most Valuable Student	Elks National Foundation	LEADERSHIP	ACTIVE	HARD	4000	50000	t	500	2025-11-15	2025-08-01	2026-2027	Renewable scholarship for high school seniors demonstrating leadership, scholarship, and financial need. Awards range from $4,000 to $50,000 over four years.	https://www.elks.org/scholars/	3.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/elks_national_foundation_most_valuable_student.jpg	t	f	2	0	2025-10-09 12:44:37.276296	2025-10-09 13:43:50.837742
5	National Merit Scholarship	National Merit Scholarship Corporation	ACADEMIC_MERIT	ACTIVE	VERY_HARD	2500	2500	f	2500	2025-10-15	\N	2026-2027	One-time award for high school seniors who score in the top 1% on the PSAT/NMSQT. Recipients are selected based on PSAT scores, academic record, and essay.	https://www.nationalmerit.org/	3.50	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/national_merit_scholarship.jpg	t	t	6	0	2025-10-09 12:44:37.276296	2025-10-09 13:43:57.326834
1	Coca-Cola Scholars Program	Coca-Cola Scholars Foundation	LEADERSHIP	ACTIVE	VERY_HARD	20000	20000	f	150	2025-10-31	2025-08-01	2026-2027	Merit-based scholarship for high school seniors who demonstrate leadership, academic excellence, and commitment to community service. Awarded to 150 students annually.	https://www.coca-colascholarsfoundation.org/	3.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/coca_cola_scholars_program_v1760118125.jpg	t	t	5	0	2025-10-09 12:44:37.276296	2025-10-10 11:06:27.834993
3	Google Lime Scholarship	Google	STEM	ACTIVE	HARD	10000	10000	f	\N	2025-12-15	2025-09-01	2026-2027	For computer science students with disabilities pursuing degrees in STEM. Recipients also receive mentorship and networking opportunities with Google engineers.	https://www.limeconnect.com/programs/page/google-lime-scholarship	3.70	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/google_lime_scholarship.jpg	t	f	2	0	2025-10-09 12:44:37.276296	2025-10-09 13:15:32.341177
7	Gates Scholarship	Bill & Melinda Gates Foundation	NEED_BASED	ACTIVE	VERY_HARD	40000	70000	t	300	2025-09-15	2025-08-01	2026-2027	Full scholarship for exceptional, Pell-eligible minority high school seniors. Covers full cost of attendance not covered by other financial aid. Includes mentoring and academic support.	https://www.thegatesscholarship.org/	3.30	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/gates_scholarship.jpg	t	t	0	0	2025-10-11 05:37:48.775251	\N
2	Pell Grant	U.S. Department of Education	NEED_BASED	ACTIVE	EASY	750	7395	t	\N	2026-06-30	2025-10-01	2026-2027	Federal grant for undergraduate students with exceptional financial need. Award amount varies based on financial need, cost of attendance, and enrollment status.	https://studentaid.gov/understand-aid/types/grants/pell	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/pell_grant.jpg	t	t	2	0	2025-10-09 12:44:37.276296	2025-10-09 13:26:51.139921
8	Dell Scholars Program	Michael & Susan Dell Foundation	NEED_BASED	ACTIVE	MODERATE	20000	20000	f	500	2025-12-01	2025-10-01	2026-2027	Scholarship for students with financial need who demonstrate determination to succeed. Includes ongoing support, mentorship, textbook credits, and a laptop.	https://www.dellscholars.org/	2.40	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/dell_scholars_program.jpg	t	f	0	0	2025-10-11 05:37:48.775251	\N
9	QuestBridge National College Match	QuestBridge	NEED_BASED	ACTIVE	VERY_HARD	50000	85000	t	1500	2025-09-26	2025-08-01	2026-2027	Full four-year scholarships to top colleges for high-achieving, low-income students. Covers tuition, room, board, books, and travel expenses at partner institutions.	https://www.questbridge.org/	3.50	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/questbridge_national_college_match.jpg	t	t	0	0	2025-10-11 05:37:48.775251	\N
10	Amazon Future Engineer Scholarship	Amazon	STEM	ACTIVE	MODERATE	40000	40000	t	100	2026-01-31	2025-10-01	2026-2027	For students pursuing computer science degrees. Includes $10,000 per year for four years plus a guaranteed paid internship at Amazon after freshman year.	https://www.amazonfutureengineer.com/	3.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/amazon_future_engineer_scholarship.jpg	t	t	0	0	2025-10-11 05:37:48.775251	\N
11	Hispanic Scholarship Fund	Hispanic Scholarship Fund	DIVERSITY	ACTIVE	EASY	500	5000	t	10000	2026-02-15	2025-11-01	2026-2027	Scholarships for Hispanic/Latino students of any major pursuing higher education. Awards based on merit and financial need. Renewable annually with continued eligibility.	https://www.hsf.net/	3.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/hispanic_scholarship_fund.jpg	t	f	0	0	2025-10-11 05:37:48.775251	\N
12	AXA Achievement Scholarship	AXA Foundation	LEADERSHIP	ACTIVE	MODERATE	2500	25000	f	60	2025-12-15	2025-10-01	2026-2027	For students who demonstrate ambition, drive, determination, and self-discipline to succeed. Recognizes students who have overcome significant obstacles.	https://www.axa-achievement.com/	3.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/axa_achievement_scholarship.jpg	t	f	0	0	2025-10-11 05:37:48.775251	\N
13	Burger King Scholars Program	Burger King Foundation	NEED_BASED	ACTIVE	EASY	1000	50000	f	3500	2025-12-15	2025-10-01	2026-2027	Scholarships for high school seniors with demonstrated financial need, work experience, and community service. Award amounts vary based on need and merit.	https://www.burgerkingfoundation.org/	2.50	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/burger_king_scholars_program.jpg	t	f	0	0	2025-10-11 05:37:48.775251	\N
14	Jack Kent Cooke Foundation College Scholarship	Jack Kent Cooke Foundation	ACADEMIC_MERIT	ACTIVE	VERY_HARD	40000	55000	t	40	2025-11-14	2025-08-01	2026-2027	For high-achieving high school seniors with financial need. Covers tuition, living expenses, books, and fees for up to four years. One of the largest scholarships available.	https://www.jkcf.org/	3.50	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/jack_kent_cooke_foundation_college_scholarship.jpg	t	t	0	0	2025-10-11 05:37:48.775251	\N
15	Ron Brown Scholar Program	Ron Brown Scholar Program	DIVERSITY	ACTIVE	VERY_HARD	40000	40000	t	10	2026-01-09	2025-09-01	2026-2027	For African American high school seniors who demonstrate academic excellence, leadership, and community service. Provides $10,000 per year for four years plus mentoring.	https://www.ronbrown.org/	3.50	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/ron_brown_scholar_program.jpg	t	f	0	0	2025-10-11 05:37:48.775251	\N
16	Horatio Alger National Scholarship	Horatio Alger Association	NEED_BASED	ACTIVE	MODERATE	25000	25000	f	106	2025-10-25	2025-08-01	2026-2027	For students who have faced and overcome great obstacles, demonstrate perseverance, and have financial need. Recognizes students who exhibit integrity and determination.	https://scholars.horatioalger.org/	2.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/horatio_alger_national_scholarship.jpg	t	f	0	0	2025-10-11 05:37:48.775251	\N
17	Davidson Fellows Scholarship	Davidson Institute	STEM	ACTIVE	VERY_HARD	10000	50000	f	20	2026-02-13	2025-10-01	2026-2027	For students 18 and under who have completed a significant piece of work in STEM, literature, music, or philosophy. Requires submission of an extraordinary project.	https://www.davidsongifted.org/fellows-scholarship	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/davidson_fellows_scholarship.jpg	t	f	0	0	2025-10-11 05:37:48.775251	\N
18	Foot Locker Scholar Athletes Program	Foot Locker Foundation	ATHLETIC	ACTIVE	MODERATE	5000	20000	f	20	2026-01-07	2025-10-01	2026-2027	For student-athletes who demonstrate leadership on and off the field. Must participate in high school sports and maintain strong academics while contributing to community.	https://www.footlockerscholarathletes.com/	3.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/foot_locker_scholar_athletes_program.jpg	t	f	4	0	2025-10-11 05:37:48.775251	2025-10-11 06:02:15.440355
19	Google Generation Scholarship	Google	STEM	ACTIVE	HARD	10000	10000	t	\N	2025-12-04	2025-09-01	2026-2027	For women in computer science and gaming. Includes mentorship opportunities and invitation to Google annual retreat. Open to undergraduate and graduate students.	https://buildyourfuture.withgoogle.com/scholarships/generation-google-scholarship	3.50	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/google_generation_scholarship.jpg	t	t	0	0	2025-10-11 05:48:42.198731	\N
20	Microsoft Tuition Scholarship	Microsoft	STEM	ACTIVE	HARD	12000	12000	t	50	2026-01-30	2025-10-01	2026-2027	For students pursuing degrees in computer science, computer engineering, or related STEM disciplines. Preference given to students who demonstrate financial need.	https://www.microsoft.com/en-us/diversity/programs/scholarships	3.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/microsoft_tuition_scholarship.jpg	t	t	0	0	2025-10-11 05:48:42.198731	\N
21	Society of Women Engineers Scholarship	Society of Women Engineers	STEM	ACTIVE	MODERATE	1000	15000	f	260	2026-02-15	2025-12-01	2026-2027	Multiple scholarships for women pursuing ABET-accredited engineering, technology, or computing programs. Awards range based on academic level and financial need.	https://swe.org/scholarships/	3.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/society_of_women_engineers_scholarship.jpg	t	f	0	0	2025-10-11 05:48:42.198731	\N
22	NSBE Scholars Program	National Society of Black Engineers	STEM	ACTIVE	MODERATE	500	10000	f	300	2026-01-31	2025-10-01	2026-2027	For Black/African American students pursuing degrees in engineering, computer science, or related fields. Must be NSBE member or willing to join.	https://www.nsbe.org/Programs-Services/Scholarships-and-Fellowships.aspx	3.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/nsbe_scholars_program.jpg	t	f	0	0	2025-10-11 05:48:42.198731	\N
23	Palantir Women in Technology Scholarship	Palantir Technologies	STEM	ACTIVE	VERY_HARD	7000	7000	f	15	2025-11-15	2025-09-01	2026-2027	For undergraduate women studying computer science or related technical fields. Winners receive scholarship plus trip to Palantir headquarters for mentorship and networking.	https://www.palantir.com/students/scholarship/wit-north-america/	3.30	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/palantir_women_in_technology_scholarship.jpg	t	f	0	0	2025-10-11 05:48:42.198731	\N
24	SHPE Scholarship Program	Society of Hispanic Professional Engineers	STEM	ACTIVE	MODERATE	1000	5000	f	200	2026-04-30	2026-01-01	2026-2027	For Hispanic students pursuing engineering, math, science, or technology degrees. Must be SHPE member. Multiple scholarship levels available.	https://www.shpe.org/students/scholarships	3.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/shpe_scholarship_program.jpg	t	f	0	0	2025-10-11 05:48:42.198731	\N
25	IEEE Presidents' Scholarship	Institute of Electrical and Electronics Engineers	STEM	ACTIVE	HARD	10000	10000	f	1	2026-05-31	2026-01-01	2026-2027	Single prestigious award for an undergraduate student in electrical engineering, electronics, or computer science with demonstrated leadership and involvement in IEEE activities.	https://www.ieee.org/membership/students/awards/presidents-scholarship.html	3.50	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/ieee_presidents_scholarship.jpg	t	f	0	0	2025-10-11 05:48:42.198731	\N
26	SMART Scholarship for Service Program	Department of Defense	STEM	ACTIVE	VERY_HARD	25000	50000	t	200	2025-12-01	2025-08-01	2026-2027	Full scholarship for STEM students. Covers full tuition, stipend, summer internships, and mentorship. Requires post-graduation employment with Department of Defense.	https://www.smartscholarship.org/	3.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/smart_scholarship_for_service_program.jpg	t	t	0	0	2025-10-11 05:48:42.198731	\N
27	NASA Space Grant Scholarships	NASA	STEM	ACTIVE	HARD	2000	8000	t	\N	2026-03-31	2025-12-01	2026-2027	For students pursuing aerospace, engineering, or STEM fields. Awards and deadlines vary by state consortium. Check your state Space Grant office for specific requirements.	https://www.nasa.gov/stem/spacegrant/about/index.html	3.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/nasa_space_grant_scholarships.jpg	t	f	0	0	2025-10-11 05:48:42.198731	\N
28	Barry Goldwater Scholarship	Barry Goldwater Scholarship Foundation	STEM	ACTIVE	VERY_HARD	7500	7500	t	400	2026-01-27	2025-09-01	2026-2027	Prestigious award for sophomores and juniors pursuing research careers in natural sciences, mathematics, or engineering. One of the most competitive undergraduate STEM scholarships.	https://goldwaterscholarship.gov/	3.70	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/barry_goldwater_scholarship.jpg	t	t	0	0	2025-10-11 05:48:42.198731	\N
29	AISES Scholarship	American Indian Science and Engineering Society	STEM	ACTIVE	MODERATE	1000	5000	f	200	2026-05-31	2026-02-01	2026-2027	For Native American students pursuing degrees in STEM fields. Must be AISES member and demonstrate commitment to Native American community.	https://www.aises.org/scholarships	3.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/aises_scholarship.jpg	t	f	0	0	2025-10-11 05:48:42.198731	\N
30	Astronaut Scholarship	Astronaut Scholarship Foundation	STEM	ACTIVE	VERY_HARD	15000	15000	f	60	2025-12-31	2025-09-01	2026-2027	For exceptional undergraduate juniors and seniors in STEM fields who intend to pursue research careers. Students must be nominated by faculty at participating institutions.	https://www.astronautscholarship.org/	3.50	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/astronaut_scholarship.jpg	t	f	0	0	2025-10-11 05:48:42.198731	\N
31	NCAA Division I Athletic Scholarships	National Collegiate Athletic Association	ATHLETIC	ACTIVE	VERY_HARD	1000	70000	t	\N	2026-05-01	2025-07-01	2026-2027	Full and partial athletic scholarships for exceptional student-athletes competing at Division I level. Covers tuition, fees, room, board, and books. Must meet NCAA eligibility requirements.	https://www.ncaa.org/sports/2015/6/26/scholarships.aspx	2.30	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/ncaa_division_i_athletic_scholarships.jpg	t	t	0	0	2025-10-11 05:52:36.801973	\N
32	NAIA Athletic Scholarships	National Association of Intercollegiate Athletics	ATHLETIC	ACTIVE	HARD	1000	50000	t	\N	2026-05-01	2025-07-01	2026-2027	Athletic scholarships for student-athletes at NAIA institutions. More flexible eligibility requirements than NCAA. Scholarships can be combined with academic awards.	https://www.naia.org/	2.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/naia_athletic_scholarships.jpg	t	f	0	0	2025-10-11 05:52:36.801973	\N
33	NCAA Postgraduate Scholarship	National Collegiate Athletic Association	ATHLETIC	ACTIVE	VERY_HARD	10000	10000	f	174	2026-01-15	2025-10-01	2026-2027	For student-athletes in final year of eligibility with strong academic records planning to attend graduate school. Recognizes academic achievement and athletic excellence.	https://www.ncaa.org/sports/2013/11/14/postgraduate-scholarship-program.aspx	3.20	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/ncaa_postgraduate_scholarship.jpg	t	t	0	0	2025-10-11 05:52:36.801973	\N
34	NFHS Spirit of Sport Award	National Federation of State High School Associations	ATHLETIC	ACTIVE	MODERATE	1000	1000	f	8	2026-03-01	2025-12-01	2026-2027	For high school student-athletes who demonstrate exemplary sportsmanship, ethics, integrity, and character. One winner selected per NFHS section across the country.	https://www.nfhs.org/articles/spirit-of-sport-award/	3.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/nfhs_spirit_of_sport_award.jpg	t	f	0	0	2025-10-11 05:52:36.801973	\N
35	Women's Sports Foundation Travel & Training Fund	Women's Sports Foundation	ATHLETIC	ACTIVE	MODERATE	1000	5000	f	150	2026-04-01	2025-10-01	2026-2027	Grants for female athletes to help cover training, travel, and competition expenses. For athletes with financial need pursuing competitive sports at national or international level.	https://www.womenssportsfoundation.org/programs/travel-training-grants/	2.50	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/womens_sports_foundation_travel_training_fund.jpg	t	f	0	0	2025-10-11 05:52:36.801973	\N
36	Jackie Robinson Foundation Scholarship	Jackie Robinson Foundation	ATHLETIC	ACTIVE	VERY_HARD	30000	30000	t	60	2026-01-31	2025-10-01	2026-2027	Four-year scholarship for minority high school seniors demonstrating leadership, financial need, and commitment to community service. Named after baseball legend who broke color barrier.	https://www.jackierobinson.org/	3.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/jackie_robinson_foundation_scholarship.jpg	t	t	0	0	2025-10-11 05:52:36.801973	\N
37	All-American Scholar Award	USAG Gymnastics	ATHLETIC	ACTIVE	HARD	1000	5000	f	12	2026-02-15	2025-11-01	2026-2027	For high school senior gymnasts competing at Level 9 or 10 who demonstrate athletic excellence and strong academics. Must be USA Gymnastics member planning to attend four-year institution.	https://usagym.org/pages/education/scholarships/	3.50	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/all_american_scholar_award.jpg	t	f	0	0	2025-10-11 05:52:36.801973	\N
38	NSCA Scholarship	National Strength and Conditioning Association	ATHLETIC	ACTIVE	MODERATE	1500	2500	f	10	2026-03-15	2025-12-01	2026-2027	For undergraduate students majoring in strength and conditioning or related field. Must be NSCA member and demonstrate career commitment to strength and conditioning profession.	https://www.nsca.com/membership/scholarships/	3.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/nsca_scholarship.jpg	t	f	0	0	2025-10-11 05:52:36.801973	\N
39	Pop Warner Little Scholars Program	Pop Warner Little Scholars	ATHLETIC	ACTIVE	MODERATE	1000	2000	f	100	2026-02-28	2025-11-01	2026-2027	For graduating high school seniors who participated in Pop Warner youth football or cheerleading. Based on academics, community service, and financial need.	https://www.popwarner.com/Default.aspx?tabid=1476649	3.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/pop_warner_little_scholars_program.jpg	t	f	0	0	2025-10-11 05:52:36.801973	\N
40	AAU Scholarship	Amateur Athletic Union	ATHLETIC	ACTIVE	MODERATE	500	2500	f	50	2026-04-15	2026-01-01	2026-2027	For high school seniors who participated in AAU sports programs. Recognizes academic achievement, athletic participation, and community involvement. Must have been AAU member.	https://aausports.org/page.php?page_id=119854	2.80	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/aau_scholarship.jpg	t	f	0	0	2025-10-11 05:52:36.801973	\N
41	Abe and Annie Seibel Foundation Scholarship	Abe and Annie Seibel Foundation	ATHLETIC	ACTIVE	HARD	4000	4000	t	10	2026-03-01	2025-12-01	2026-2027	For student-athletes from Texas attending public universities in Texas. Must demonstrate strong academics and athletic participation. Renewable for up to four years with continued eligibility.	https://www.seibelfoundation.org/	3.25	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/abe_and_annie_seibel_foundation_scholarship.jpg	t	f	0	0	2025-10-11 05:52:36.801973	\N
42	NCSAA Scholarship Program	National Christian College Athletic Association	ATHLETIC	ACTIVE	MODERATE	1000	3000	f	25	2026-02-01	2025-11-01	2026-2027	For Christian student-athletes attending NCCAA member institutions. Based on athletic ability, academic achievement, Christian character, and financial need.	https://www.thenccaa.org/	2.75	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/ncsaa_scholarship_program.jpg	t	f	0	0	2025-10-11 05:52:36.801973	\N
43	FBLA Scholarship	Future Business Leaders of America	CAREER_SPECIFIC	ACTIVE	MODERATE	1000	5000	f	75	2026-03-01	2025-12-01	2026-2027	For FBLA members pursuing business-related degrees. Multiple awards available. Based on FBLA participation, leadership, academics, and essay demonstrating business knowledge.	https://www.fbla-pbl.org/fbla/programs/scholarships/	3.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/fbla_scholarship.jpg	t	f	0	0	2025-10-11 05:55:23.389439	\N
44	DECA Scholarship	DECA Inc.	CAREER_SPECIFIC	ACTIVE	MODERATE	1000	5000	f	50	2026-01-17	2025-10-01	2026-2027	For DECA members pursuing marketing, entrepreneurship, finance, hospitality, or management. Must demonstrate leadership through DECA activities and competitive events participation.	https://www.deca.org/high-school-programs/scholarships/	3.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/deca_scholarship.jpg	t	f	0	0	2025-10-11 05:55:23.389439	\N
45	Health Professions Scholarship Program	U.S. Department of Defense	CAREER_SPECIFIC	ACTIVE	VERY_HARD	45000	90000	t	200	2026-01-15	2025-06-01	2026-2027	Full scholarship for medical, dental, pharmacy, psychology, and optometry students. Covers tuition, fees, books, and monthly stipend. Requires military service commitment as healthcare officer.	https://www.usuhs.edu/hpsp	3.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/health_professions_scholarship_program.jpg	t	t	0	0	2025-10-11 05:55:23.389439	\N
46	Nurse Corps Scholarship Program	U.S. Department of Health and Human Services	CAREER_SPECIFIC	ACTIVE	HARD	10000	50000	t	1000	2026-04-30	2025-11-01	2026-2027	For nursing students committed to working in underserved communities. Covers tuition, fees, and monthly stipend. Requires service commitment in critical shortage facility after graduation.	https://bhw.hrsa.gov/funding/apply-scholarship	2.50	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/nurse_corps_scholarship_program.jpg	t	t	0	0	2025-10-11 05:55:23.389439	\N
47	AICPA Accounting Scholarship	American Institute of CPAs	CAREER_SPECIFIC	ACTIVE	MODERATE	2500	10000	f	200	2026-03-01	2025-12-01	2026-2027	For undergraduate and graduate students majoring in accounting. Multiple scholarship programs including awards for minority students. Must demonstrate commitment to accounting profession.	https://www.aicpa.org/membership/join/scholarships	3.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/aicpa_accounting_scholarship.jpg	t	f	0	0	2025-10-11 05:55:23.389439	\N
48	ABA Legal Opportunity Scholarship	American Bar Association	CAREER_SPECIFIC	ACTIVE	HARD	15000	15000	t	20	2026-03-02	2025-11-01	2026-2027	For racial and ethnic minority students entering first year of law school. Renewable for second and third years. Provides mentorship and networking opportunities in legal profession.	https://www.americanbar.org/groups/diversity/diversity_pipeline/projects_initiatives/legal_opportunity_scholarship/	3.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/aba_legal_opportunity_scholarship.jpg	t	f	0	0	2025-10-11 05:55:23.389439	\N
49	TEACH Grant	U.S. Department of Education	CAREER_SPECIFIC	ACTIVE	MODERATE	4000	4000	t	\N	2026-06-30	2025-10-01	2026-2027	For students pursuing teaching careers in high-need fields and low-income schools. Up to $4,000 per year. Requires teaching service commitment. Converts to loan if service not completed.	https://studentaid.gov/understand-aid/types/grants/teach	3.25	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/teach_grant.jpg	t	t	0	0	2025-10-11 05:55:23.389439	\N
50	Mike Rowe WORKS Foundation Scholarship	mikeroweWORKS Foundation	CAREER_SPECIFIC	ACTIVE	MODERATE	1000	5000	f	50	2026-05-31	2026-01-01	2026-2027	For students pursuing skilled trades including welding, HVAC, plumbing, electrical, construction. Must demonstrate strong work ethic and commitment to trade career. No service obligation.	https://www.mikeroweworks.org/scholarship/	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/mike_rowe_works_foundation_scholarship.jpg	t	f	0	0	2025-10-11 05:55:23.389439	\N
51	FFA Scholarship	National FFA Organization	CAREER_SPECIFIC	ACTIVE	MODERATE	1000	10000	f	1800	2026-02-01	2025-10-01	2026-2027	Over 1,800 scholarships for FFA members pursuing agriculture, food science, natural resources, or related fields. Largest scholarship program in agricultural education.	https://www.ffa.org/participate/scholarships/	2.50	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/ffa_scholarship.jpg	t	f	0	0	2025-10-11 05:55:23.389439	\N
52	HOSA Scholarship	HOSA-Future Health Professionals	CAREER_SPECIFIC	ACTIVE	MODERATE	1000	5000	f	50	2026-03-15	2025-12-01	2026-2027	For HOSA members pursuing health science careers including nursing, medicine, dentistry, pharmacy, and allied health. Based on HOSA involvement, academics, and career goals.	https://hosa.org/scholarships/	3.20	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/hosa_scholarship.jpg	t	f	0	0	2025-10-11 05:55:23.389439	\N
53	AHLEF Scholarship	American Hotel & Lodging Educational Foundation	CAREER_SPECIFIC	ACTIVE	MODERATE	1000	5000	f	500	2026-05-01	2026-01-01	2026-2027	For students pursuing hospitality management degrees. Must demonstrate passion for hospitality industry and career commitment. Multiple scholarship levels based on academic standing.	https://www.ahlef.org/scholarships/	2.75	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/ahlef_scholarship.jpg	t	f	0	0	2025-10-11 05:55:23.389439	\N
54	ASM Materials Education Foundation Scholarship	ASM Materials Education Foundation	CAREER_SPECIFIC	ACTIVE	HARD	1000	10000	f	40	2026-05-01	2026-01-01	2026-2027	For undergraduate and graduate students studying materials science and engineering, metallurgy, or related fields. Based on academics, essay, and demonstrated interest in materials science.	https://www.asminternational.org/web/asmmef/home	3.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/asm_materials_education_foundation_scholarship.jpg	t	f	0	0	2025-10-11 05:55:23.389439	\N
55	FBLA Scholarship	Future Business Leaders of America	CAREER_SPECIFIC	ACTIVE	MODERATE	1000	5000	f	75	2026-03-01	2025-12-01	2026-2027	For FBLA members pursuing business-related degrees. Multiple awards available. Based on FBLA participation, leadership, academics, and essay demonstrating business knowledge.	https://www.fbla-pbl.org/fbla/programs/scholarships/	3.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/fbla_scholarship.jpg	t	f	0	0	2025-10-11 05:56:01.192991	\N
56	DECA Scholarship	DECA Inc.	CAREER_SPECIFIC	ACTIVE	MODERATE	1000	5000	f	50	2026-01-17	2025-10-01	2026-2027	For DECA members pursuing marketing, entrepreneurship, finance, hospitality, or management. Must demonstrate leadership through DECA activities and competitive events participation.	https://www.deca.org/high-school-programs/scholarships/	3.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/deca_scholarship.jpg	t	f	0	0	2025-10-11 05:56:01.192991	\N
57	Health Professions Scholarship Program	U.S. Department of Defense	CAREER_SPECIFIC	ACTIVE	VERY_HARD	45000	90000	t	200	2026-01-15	2025-06-01	2026-2027	Full scholarship for medical, dental, pharmacy, psychology, and optometry students. Covers tuition, fees, books, and monthly stipend. Requires military service commitment as healthcare officer.	https://www.usuhs.edu/hpsp	3.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/health_professions_scholarship_program.jpg	t	t	0	0	2025-10-11 05:56:01.192991	\N
58	Nurse Corps Scholarship Program	U.S. Department of Health and Human Services	CAREER_SPECIFIC	ACTIVE	HARD	10000	50000	t	1000	2026-04-30	2025-11-01	2026-2027	For nursing students committed to working in underserved communities. Covers tuition, fees, and monthly stipend. Requires service commitment in critical shortage facility after graduation.	https://bhw.hrsa.gov/funding/apply-scholarship	2.50	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/nurse_corps_scholarship_program.jpg	t	t	0	0	2025-10-11 05:56:01.192991	\N
59	AICPA Accounting Scholarship	American Institute of CPAs	CAREER_SPECIFIC	ACTIVE	MODERATE	2500	10000	f	200	2026-03-01	2025-12-01	2026-2027	For undergraduate and graduate students majoring in accounting. Multiple scholarship programs including awards for minority students. Must demonstrate commitment to accounting profession.	https://www.aicpa.org/membership/join/scholarships	3.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/aicpa_accounting_scholarship.jpg	t	f	0	0	2025-10-11 05:56:01.192991	\N
60	ABA Legal Opportunity Scholarship	American Bar Association	CAREER_SPECIFIC	ACTIVE	HARD	15000	15000	t	20	2026-03-02	2025-11-01	2026-2027	For racial and ethnic minority students entering first year of law school. Renewable for second and third years. Provides mentorship and networking opportunities in legal profession.	https://www.americanbar.org/groups/diversity/diversity_pipeline/projects_initiatives/legal_opportunity_scholarship/	3.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/aba_legal_opportunity_scholarship.jpg	t	f	0	0	2025-10-11 05:56:01.192991	\N
61	TEACH Grant	U.S. Department of Education	CAREER_SPECIFIC	ACTIVE	MODERATE	4000	4000	t	\N	2026-06-30	2025-10-01	2026-2027	For students pursuing teaching careers in high-need fields and low-income schools. Up to $4,000 per year. Requires teaching service commitment. Converts to loan if service not completed.	https://studentaid.gov/understand-aid/types/grants/teach	3.25	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/teach_grant.jpg	t	t	0	0	2025-10-11 05:56:01.192991	\N
62	Mike Rowe WORKS Foundation Scholarship	mikeroweWORKS Foundation	CAREER_SPECIFIC	ACTIVE	MODERATE	1000	5000	f	50	2026-05-31	2026-01-01	2026-2027	For students pursuing skilled trades including welding, HVAC, plumbing, electrical, construction. Must demonstrate strong work ethic and commitment to trade career. No service obligation.	https://www.mikeroweworks.org/scholarship/	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/mike_rowe_works_foundation_scholarship.jpg	t	f	0	0	2025-10-11 05:56:01.192991	\N
63	FFA Scholarship	National FFA Organization	CAREER_SPECIFIC	ACTIVE	MODERATE	1000	10000	f	1800	2026-02-01	2025-10-01	2026-2027	Over 1,800 scholarships for FFA members pursuing agriculture, food science, natural resources, or related fields. Largest scholarship program in agricultural education.	https://www.ffa.org/participate/scholarships/	2.50	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/ffa_scholarship.jpg	t	f	0	0	2025-10-11 05:56:01.192991	\N
64	HOSA Scholarship	HOSA-Future Health Professionals	CAREER_SPECIFIC	ACTIVE	MODERATE	1000	5000	f	50	2026-03-15	2025-12-01	2026-2027	For HOSA members pursuing health science careers including nursing, medicine, dentistry, pharmacy, and allied health. Based on HOSA involvement, academics, and career goals.	https://hosa.org/scholarships/	3.20	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/hosa_scholarship.jpg	t	f	0	0	2025-10-11 05:56:01.192991	\N
65	AHLEF Scholarship	American Hotel & Lodging Educational Foundation	CAREER_SPECIFIC	ACTIVE	MODERATE	1000	5000	f	500	2026-05-01	2026-01-01	2026-2027	For students pursuing hospitality management degrees. Must demonstrate passion for hospitality industry and career commitment. Multiple scholarship levels based on academic standing.	https://www.ahlef.org/scholarships/	2.75	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/ahlef_scholarship.jpg	t	f	0	0	2025-10-11 05:56:01.192991	\N
66	ASM Materials Education Foundation Scholarship	ASM Materials Education Foundation	CAREER_SPECIFIC	ACTIVE	HARD	1000	10000	f	40	2026-05-01	2026-01-01	2026-2027	For undergraduate and graduate students studying materials science and engineering, metallurgy, or related fields. Based on academics, essay, and demonstrated interest in materials science.	https://www.asminternational.org/web/asmmef/home	3.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/asm_materials_education_foundation_scholarship.jpg	t	f	0	0	2025-10-11 05:56:01.192991	\N
67	Point Foundation Scholarship	Point Foundation	DIVERSITY	ACTIVE	HARD	4800	36000	t	30	2026-01-27	2025-10-01	2026-2027	For LGBTQ students with demonstrated leadership and community involvement. Largest scholarship program for LGBTQ students in nation. Includes mentorship and leadership development.	https://pointfoundation.org/point-apply/scholarship-faqs/	3.20	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/point_foundation_scholarship.jpg	t	t	0	0	2025-10-11 05:56:49.934039	\N
68	American Indian College Fund Scholarship	American Indian College Fund	DIVERSITY	ACTIVE	MODERATE	1000	10000	f	6000	2026-05-31	2026-01-01	2026-2027	For Native American and Alaska Native students. Over 200 different scholarships available for various majors and tribal affiliations. One application applies for all eligible awards.	https://collegefund.org/students/scholarships/	2.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/american_indian_college_fund_scholarship.jpg	t	t	0	0	2025-10-11 05:56:49.934039	\N
69	APIASF Scholarship	Asian & Pacific Islander American Scholarship Fund	DIVERSITY	ACTIVE	MODERATE	2500	20000	f	600	2026-01-16	2025-10-01	2026-2027	For students of Asian and Pacific Islander heritage. Based on financial need, academic achievement, and commitment to community service. Multiple scholarship programs available.	https://www.apiasf.org/scholarship.html	2.70	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/apiasf_scholarship.jpg	t	f	0	0	2025-10-11 05:56:49.934039	\N
70	LULAC National Scholarship Fund	League of United Latin American Citizens	DIVERSITY	ACTIVE	MODERATE	500	2000	f	1000	2026-03-31	2026-01-01	2026-2027	For Hispanic students of all majors. Awards based on academic achievement, community involvement, and financial need. Largest Hispanic scholarship program in the United States.	https://lnesc.org/	3.25	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/lulac_national_scholarship_fund.jpg	t	f	0	0	2025-10-11 05:56:49.934039	\N
71	NAACP Scholarships	National Association for the Advancement of Colored People	DIVERSITY	ACTIVE	MODERATE	1000	5000	f	50	2026-03-07	2025-12-01	2026-2027	For African American high school seniors and current undergraduates. Multiple scholarships available for various fields. Based on academics, financial need, and commitment to racial justice.	https://naacp.org/find-resources/scholarships	2.50	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/naacp_scholarships.jpg	t	f	0	0	2025-10-11 05:56:49.934039	\N
72	P.E.O. Program for Continuing Education	P.E.O. Sisterhood	DIVERSITY	ACTIVE	MODERATE	3000	3000	f	2500	2026-03-01	2025-11-01	2026-2027	For women returning to school to complete their education after interruption. One-time grant to help with tuition, books, and fees. Must be sponsored by local P.E.O. chapter.	https://www.peointernational.org/about-peo-sisterhood	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/peo_program_for_continuing_education.jpg	t	f	0	0	2025-10-11 05:56:49.934039	\N
73	Jeannette Rankin Women's Scholarship Fund	Jeannette Rankin Foundation	DIVERSITY	ACTIVE	MODERATE	2000	2000	f	50	2026-03-01	2025-11-01	2026-2027	For low-income women aged 35 and older pursuing undergraduate or technical education. Named after first woman elected to U.S. Congress. Focus on helping women achieve economic security.	https://rankinfoundation.org/students/application-information/	2.50	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/jeannette_rankin_womens_scholarship_fund.jpg	t	f	0	0	2025-10-11 05:56:49.934039	\N
74	Que Llueva Café Scholarship	Café Bustelo	DIVERSITY	ACTIVE	MODERATE	5000	5000	f	10	2026-04-28	2026-02-01	2026-2027	For Latino students demonstrating academic excellence, leadership, and commitment to making positive impact in their communities. Essay required about cultural heritage and aspirations.	https://www.cafebustelo.com/en/scholarship	3.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/que_llueva_cafe_scholarship.jpg	t	f	0	0	2025-10-11 05:56:49.934039	\N
75	First Generation Matching Grant Program	Taco Bell Foundation	DIVERSITY	ACTIVE	MODERATE	5000	25000	f	500	2026-01-31	2025-10-01	2026-2027	For first-generation college students ages 16-24 pursuing two or four-year degree. Based on passion, drive, and commitment to education. No minimum GPA requirement.	https://www.tacobellfoundation.org/live-mas-scholarship/	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/first_generation_matching_grant_program.jpg	t	t	0	0	2025-10-11 05:56:49.934039	\N
76	Dream.US National Scholarship	TheDream.US	DIVERSITY	ACTIVE	HARD	14000	33000	t	1000	2026-02-28	2025-11-01	2026-2027	For DREAMers (DACA and undocumented students) with significant unmet financial need. Largest college access program for immigrant youth. Covers tuition, fees, and books at partner colleges.	https://www.thedream.us/	2.50	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/dream_us_national_scholarship.jpg	t	t	0	0	2025-10-11 05:56:49.934039	\N
77	LAGRANT Foundation Scholarship	LAGRANT Foundation	DIVERSITY	ACTIVE	MODERATE	2500	10000	f	40	2026-02-28	2025-12-01	2026-2027	For ethnic minority students pursuing careers in advertising, marketing, or public relations. Includes mentorship and internship opportunities. Based on academics, financial need, and career goals.	https://www.lagrantfoundation.org/Scholarship%20Program	3.20	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/lagrant_foundation_scholarship.jpg	t	f	0	0	2025-10-11 05:56:49.934039	\N
78	Thurgood Marshall College Fund Scholarship	Thurgood Marshall College Fund	DIVERSITY	ACTIVE	MODERATE	3100	6200	f	500	2026-04-15	2026-01-01	2026-2027	For students attending TMCF member schools (historically Black public colleges and universities). Multiple scholarships available. Based on academics, leadership, and community service.	https://www.tmcf.org/students-alumni/scholarship/	3.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/thurgood_marshall_college_fund_scholarship.jpg	t	f	0	0	2025-10-11 05:56:49.934039	\N
79	National Honor Society Scholarship	National Honor Society	ACADEMIC_MERIT	ACTIVE	HARD	1000	25000	f	600	2026-01-27	2025-10-01	2026-2027	For NHS members demonstrating scholarship, service, leadership, and character. Multiple scholarship levels. Must be active NHS member at time of application.	https://www.nhs.us/students/the-nhs-scholarship/	3.50	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/national_honor_society_scholarship.jpg	t	t	0	0	2025-10-11 05:58:31.046873	\N
80	Phi Theta Kappa Scholarship	Phi Theta Kappa Honor Society	ACADEMIC_MERIT	ACTIVE	MODERATE	500	5000	f	200	2026-04-01	2026-01-01	2026-2027	For community college students who are PTK members transferring to four-year institutions. Based on academics, leadership, and PTK involvement. Over 600 partner colleges offer additional scholarships.	https://www.ptk.org/scholarships/	3.50	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/phi_theta_kappa_scholarship.jpg	t	f	0	0	2025-10-11 05:58:31.046873	\N
81	Phi Beta Kappa Academic Scholarship	Phi Beta Kappa Society	ACADEMIC_MERIT	ACTIVE	VERY_HARD	15000	15000	f	3	2026-01-31	2025-10-01	2026-2027	Mary Isabel Sibley Fellowship for women scholars in Greek or French studies. One of oldest and most prestigious academic honor societies. Highly competitive.	https://www.pbk.org/Scholarships	3.80	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/phi_beta_kappa_academic_scholarship.jpg	t	t	0	0	2025-10-11 05:58:31.046873	\N
82	Intel Science Talent Search	Society for Science	ACADEMIC_MERIT	ACTIVE	VERY_HARD	25000	250000	f	40	2025-11-13	2025-08-01	2026-2027	Oldest and most prestigious pre-college science competition. For high school seniors completing original research project. Top winner receives $250,000. Formerly known as Westinghouse and Intel STS.	https://www.societyforscience.org/regeneron-sts/	3.50	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/intel_science_talent_search.jpg	t	t	0	0	2025-10-11 05:58:31.046873	\N
83	Siemens Competition	Siemens Foundation	ACADEMIC_MERIT	ACTIVE	VERY_HARD	1000	100000	f	96	2025-10-01	2025-06-01	2026-2027	Premier competition for high school students conducting individual or team research projects in STEM. Regional and national finals. Grand prize of $100,000 for individuals.	https://www.siemensfoundation.org/programs/siemens-competition/	3.70	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/siemens_competition.jpg	t	t	0	0	2025-10-11 05:58:31.046873	\N
84	U.S. Presidential Scholars Program	U.S. Department of Education	ACADEMIC_MERIT	ACTIVE	VERY_HARD	0	0	f	161	2025-11-15	2025-09-01	2026-2027	One of nation's highest honors for graduating high school seniors. Recognition based on academic achievement, essays, leadership, and community service. Medallion ceremony at White House. No monetary award.	https://www2.ed.gov/programs/psp/index.html	3.80	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/us_presidential_scholars_program.jpg	t	t	0	0	2025-10-11 05:58:31.046873	\N
85	Coca-Cola National Scholar	Coca-Cola Scholars Foundation	ACADEMIC_MERIT	ACTIVE	VERY_HARD	20000	20000	f	150	2025-10-31	2025-08-01	2026-2027	Achievement-based scholarship for exceptional high school seniors. Based on capacity to lead and serve, academic achievement, and unusual circumstances overcome. One of most competitive scholarships.	https://www.coca-colascholarsfoundation.org/	3.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/coca_cola_national_scholar.jpg	t	t	0	0	2025-10-11 05:58:31.046873	\N
86	Golden Key Scholarship	Golden Key International Honour Society	ACADEMIC_MERIT	ACTIVE	MODERATE	1000	10000	f	150	2026-03-01	2025-12-01	2026-2027	For Golden Key members in top 15% of their class. Multiple scholarships for undergraduate and graduate study, study abroad, and professional development.	https://www.goldenkey.org/scholarships-awards/	3.50	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/golden_key_scholarship.jpg	t	f	0	0	2025-10-11 05:58:31.046873	\N
87	Tau Beta Pi Scholarship	Tau Beta Pi Engineering Honor Society	ACADEMIC_MERIT	ACTIVE	HARD	2000	2000	f	225	2026-04-01	2026-01-01	2026-2027	For engineering students who are Tau Beta Pi members. Oldest engineering honor society in United States. Based on academic excellence, leadership, and service to engineering profession.	https://www.tbp.org/memb/Scholars.cfm	3.70	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/tau_beta_pi_scholarship.jpg	t	f	0	0	2025-10-11 05:58:31.046873	\N
88	AKA Educational Advancement Foundation Scholarship	Alpha Kappa Alpha Sorority	ACADEMIC_MERIT	ACTIVE	MODERATE	1000	5000	f	100	2026-04-15	2026-01-01	2026-2027	For students demonstrating academic excellence and leadership. Preference given to members and descendants of AKA members. Multiple scholarships for various academic levels and majors.	https://akaeaf.org/scholarships	3.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/aka_educational_advancement_foundation_scholarship.jpg	t	f	0	0	2025-10-11 05:58:31.046873	\N
89	Boettcher Foundation Scholarship	Boettcher Foundation	ACADEMIC_MERIT	ACTIVE	VERY_HARD	13000	52000	t	42	2025-11-01	2025-08-01	2026-2027	Full-ride scholarship for Colorado high school seniors attending college in Colorado. Covers tuition, fees, books, and living stipend. One of most prestigious merit scholarships in Colorado.	https://boettcherfoundation.org/scholarships/	3.75	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/boettcher_foundation_scholarship.jpg	t	t	0	0	2025-10-11 05:58:31.046873	\N
90	Harry S. Truman Scholarship	Harry S. Truman Scholarship Foundation	ACADEMIC_MERIT	ACTIVE	VERY_HARD	30000	30000	f	60	2026-01-28	2025-09-01	2026-2027	For college juniors committed to careers in public service and government. Provides funding for graduate school. One of most prestigious national scholarships. Requires faculty nomination.	https://www.truman.gov/	3.50	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/harry_s_truman_scholarship.jpg	t	t	0	0	2025-10-11 05:58:31.046873	\N
91	Prudential Spirit of Community Awards	Prudential Financial	LEADERSHIP	ACTIVE	HARD	1000	5000	f	102	2025-11-05	2025-09-01	2026-2027	Nation's largest youth recognition program based entirely on volunteer community service. State honorees receive $1,000, national honorees receive $5,000. Trip to Washington D.C. for finalists.	https://spirit.prudential.com/	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/prudential_spirit_of_community_awards.jpg	t	t	0	0	2025-10-11 05:59:56.789664	\N
92	Kohl's Cares Scholarship	Kohl's Corporation	LEADERSHIP	ACTIVE	MODERATE	1000	10000	f	2100	2026-03-15	2026-01-01	2026-2027	For youth ages 6-18 who volunteer in their communities. Regional winners receive $1,000, national winners receive $10,000. Over 2,100 scholarships awarded annually.	https://www.kohlscorporation.com/scholarships	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/kohls_cares_scholarship.jpg	t	t	0	0	2025-10-11 05:59:56.789664	\N
94	Bonner Scholars Program	Corella & Bertram F. Bonner Foundation	LEADERSHIP	ACTIVE	HARD	2000	8000	t	2500	2026-02-01	2025-10-01	2026-2027	Four-year service scholarship at participating colleges. Students commit to 10 hours/week of community service. Combines financial support with leadership development and community engagement.	https://www.bonner.org/bonner-programs/bonner-scholar-program/	2.50	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/bonner_scholars_program_v1760189639.jpg	t	t	0	0	2025-10-11 05:59:56.789664	2025-10-11 06:33:59.839149
95	Violet Richardson Award	Soroptimist International	LEADERSHIP	ACTIVE	MODERATE	1000	5000	f	150	2025-11-15	2025-09-01	2026-2027	For young women ages 14-17 who demonstrate commitment to volunteering. Recognizes contributions to improving lives of women and girls. Local, regional, and international awards.	https://www.soroptimist.org/our-work/violet-richardson-award/index.html	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/violet_richardson_award_v1760189639.jpg	t	f	0	0	2025-10-11 05:59:56.789664	2025-10-11 06:33:59.957104
97	Gloria Barron Prize for Young Heroes	Barron Prize	LEADERSHIP	ACTIVE	HARD	10000	10000	f	25	2026-04-30	2026-01-01	2026-2027	For young people ages 8-18 who have made significant positive difference to people and planet. Recognizes service-oriented and environmental leadership. Top winners receive $10,000.	https://www.barronprize.org/	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/gloria_barron_prize_for_young_heroes_v1760189639.jpg	t	t	0	0	2025-10-11 05:59:56.789664	2025-10-11 06:34:00.088105
100	Samuel Huntington Public Service Award	Samuel Huntington Fund	LEADERSHIP	ACTIVE	VERY_HARD	15000	15000	f	3	2026-01-18	2025-10-01	2026-2027	For graduating college seniors to pursue one year of public service anywhere in the world. Stipend covers living expenses during service year. Highly selective and prestigious.	https://nationalgridus.com/huntington	3.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/samuel_huntington_public_service_award_v1760189640.jpg	t	t	0	0	2025-10-11 05:59:56.789664	2025-10-11 06:34:00.22669
98	Newman Civic Fellowship	Campus Compact	LEADERSHIP	ACTIVE	HARD	0	0	f	200	2026-03-06	2025-12-01	2026-2027	Year-long program recognizing student civic leaders. Fellows participate in virtual learning and networking. Focus on social change and community problem-solving. Recognition award, no monetary prize.	https://compact.org/initiatives/the-newman-civic-fellowship/	3.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/newman_civic_fellowship_v1760189640.jpg	t	f	0	0	2025-10-11 05:59:56.789664	2025-10-11 06:34:00.366049
93	Do Something Awards	DoSomething.org	LEADERSHIP	ACTIVE	MODERATE	500	10000	f	25	2026-04-30	2025-12-01	2026-2027	For young people making positive change in their communities through campaigns addressing social issues. Multiple monthly and annual awards. No minimum GPA required.	https://www.dosomething.org/us/about/easy-scholarships	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/do_something_awards_v1760189640.jpg	t	f	0	0	2025-10-11 05:59:56.789664	2025-10-11 06:34:00.484565
96	Horatio Alger State Scholarship	Horatio Alger Association	LEADERSHIP	ACTIVE	MODERATE	10000	10000	f	106	2025-10-25	2025-08-01	2026-2027	For students who have overcome adversity and demonstrated perseverance, integrity, and determination. State-level award. Must have financial need and be involved in community service.	https://scholars.horatioalger.org/scholarships/about-our-scholarship-programs/state-scholarships/	2.00	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/horatio_alger_state_scholarship_v1760189640.jpg	t	f	0	0	2025-10-11 05:59:56.789664	2025-10-11 06:34:00.61573
101	Carson Scholars Fund	Carson Scholars Fund	LEADERSHIP	ACTIVE	MODERATE	1000	1000	f	500	2026-01-12	2025-10-01	2026-2027	For students in grades 4-11 who demonstrate academic excellence and commitment to community. Founded by Dr. Ben Carson. Recognizes students who excel in both academics and humanitarian service.	https://carsonscholars.org/scholarships/	3.75	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/carson_scholars_fund.jpg	t	f	0	0	2025-10-11 05:59:56.789664	\N
99	Lowe's Educational Scholarship	Lowe's Corporation	LEADERSHIP	ACTIVE	MODERATE	2500	2500	f	140	2026-02-28	2025-12-01	2026-2027	For high school seniors who demonstrate leadership and community involvement. Must plan to attend accredited two or four-year college or technical school. No minimum GPA required.	https://www.lowes.com/l/about/lowes-scholarship	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/lowes_educational_scholarship_v1760189639.jpg	t	f	0	0	2025-10-11 05:59:56.789664	2025-10-11 06:33:59.548782
102	Target Community Scholarship	Target Corporation	LEADERSHIP	ACTIVE	MODERATE	2000	2000	f	500	2026-04-01	2026-01-01	2026-2027	For high school seniors demonstrating exceptional leadership in their communities. Based on community involvement, leadership activities, and commitment to making positive impact.	https://corporate.target.com/corporate-responsibility/philanthropy/team-member-giving	\N	https://magicscholar-images.nyc3.cdn.digitaloceanspaces.com/scholarships/target_community_scholarship_v1760189639.jpg	t	f	0	0	2025-10-11 05:59:56.789664	2025-10-11 06:33:59.736003
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
25	102580	2024-2025	MANUAL	9000	9000	730	730	9730	9730	7000	7000	\N	400	0	0	t	t	t	77	PENDING	2025-10-08 01:32:43.968084	2025-10-08 01:32:43.968084
26	103501	2024-2025	MANUAL	16245	16245	0	0	16245	16245	0	0	\N	0	0	0	t	t	t	22	PENDING	2025-10-08 01:32:43.980931	2025-10-08 01:32:43.980931
27	442523	2024-2025	MANUAL	8900	8900	0	0	8900	8900	0	0	\N	0	0	0	t	t	t	22	PENDING	2025-10-08 01:32:43.982566	2025-10-08 01:32:43.982566
28	102669	2024-2025	MANUAL	58348	58348	0	0	58348	58348	16272	16272	\N	1050	0	0	t	t	t	55	PENDING	2025-10-08 01:32:43.983794	2025-10-08 01:32:43.983794
29	102711	2024-2025	MANUAL	14674	14674	0	0	14674	14674	0	0	\N	0	0	0	t	t	t	22	PENDING	2025-10-08 01:32:43.985414	2025-10-08 01:32:43.985414
30	102845	2024-2025	MANUAL	46935	46935	0	0	46935	46935	0	0	\N	0	0	0	t	t	t	22	PENDING	2025-10-08 01:32:43.986627	2025-10-08 01:32:43.986627
31	434584	2021-2022	MANUAL	4920	4920	360	360	5280	5280	13000	13000	\N	800	0	0	t	t	t	77	PENDING	2025-10-08 01:32:43.987651	2025-10-08 01:32:43.987651
32	102553	2024-2025	MANUAL	6500	22000	1584	1584	8084	23584	13980	13980	\N	1400	0	0	t	t	t	77	PENDING	2025-10-08 01:32:43.988583	2025-10-08 01:32:43.988583
33	102614	2024-2025	MANUAL	11445	19945	1584	1584	13029	21529	13980	13980	\N	1400	0	0	t	t	t	77	PENDING	2025-10-08 01:32:43.989661	2025-10-08 01:32:43.989661
34	102632	2025-2026	MANUAL	6372	20844	1584	1584	7956	22428	13992	13992	\N	1400	0	0	t	t	t	77	PENDING	2025-10-08 01:32:43.990741	2025-10-08 01:32:43.990741
35	103529	2024-2025	MANUAL	6500	22000	1584	1584	8084	23584	13980	13980	\N	1400	0	0	t	t	t	77	PENDING	2025-10-08 01:32:43.991909	2025-10-08 01:32:43.991909
36	100654	2024-2025	institution_website	10566	19176	\N	\N	10566	19176	9465	\N	{"note": "Annual room and board for 2024-2025", "on_campus_total": 9465.0}	1400	3962	\N	t	f	t	100	VALIDATED	2025-10-09 01:20:24.873602	2025-10-09 01:20:24.873602
37	100858	2025-2026	institution_website	6659	18011	\N	\N	6659	18011	8605	7936	{"on_campus": 8605.0, "off_campus": 7936.0, "living_with_parent": 4304.0}	1400	3760	\N	t	f	t	100	VALIDATED	2025-10-09 01:20:24.881742	2025-10-09 01:20:24.881742
38	100830	2025-2026	institution_website	6659	18011	\N	\N	6659	18011	8605	7936	{"on_campus": 8605.0, "off_campus": 7936.0, "living_with_parent": 4304.0}	1400	3760	\N	t	f	t	100	VALIDATED	2025-10-09 01:20:24.882266	2025-10-09 01:20:24.882266
39	101480	2024-2025	institution_website	12426	\N	\N	\N	12426	\N	8894	\N	{"on_campus_total": 8894.0}	998	2506	\N	t	f	t	75	VALIDATED	2025-10-09 01:20:24.8829	2025-10-09 01:20:24.8829
40	102049	2025-2026	institution_website	40760	40760	1150	1150	41910	41910	14260	\N	{"total": 14260.0, "board_meal_plan": 6660.0, "room_vail_smith": 7600.0}	1400	\N	\N	t	t	t	100	VALIDATED	2025-10-09 01:20:24.883601	2025-10-09 01:20:24.883601
41	100751	2024-2025	institution_website	12180	34172	\N	\N	12180	34172	10134	\N	{"note": "Based on 2021 data, actual costs may vary", "total": 10134.0, "dining": 4234.0, "housing": 5900.0}	1400	\N	\N	t	f	t	100	VALIDATED	2025-10-09 01:20:24.884424	2025-10-09 01:20:24.884424
42	102368	2024-2025	institution_website	10176	\N	\N	\N	10176	\N	10068	5430	{"on_campus": 10068.0, "living_with_parent": 5430.0}	1000	\N	1000	t	f	t	75	VALIDATED	2025-10-09 01:20:24.885219	2025-10-09 01:20:24.885219
43	100663	2023-2024	institution_website	11640	28980	\N	\N	11640	28980	9955	\N	{"housing_max": 10050.0, "housing_min": 7180.0, "meal_plan_max": 5360.0, "meal_plan_min": 450.0, "typical_total": 9955.0}	1200	\N	\N	t	f	t	100	VALIDATED	2025-10-09 01:20:24.885799	2025-10-09 01:20:24.885799
44	100706	2025-2026	institution_website	11770	24662	\N	\N	11770	24662	\N	\N	\N	2796	\N	\N	t	f	t	75	VALIDATED	2025-10-09 01:20:24.886345	2025-10-09 01:20:24.886345
45	101879	2024-2025	institution_website	12240	\N	\N	\N	12240	\N	\N	\N	{"note": "Housing costs not provided", "dining_per_term": 350.0, "dining_annual_estimate": 700.0}	1400	\N	\N	t	f	t	50	VALIDATED	2025-10-09 01:20:24.886934	2025-10-09 01:20:24.886934
46	102094	2025-2026	institution_website	13460	27410	\N	\N	13460	27410	\N	\N	\N	1400	\N	\N	t	f	t	75	VALIDATED	2025-10-09 01:20:24.887477	2025-10-09 01:20:24.887477
47	101587	2025-2026	institution_website	\N	\N	\N	\N	23072	36322	\N	\N	{"note": "Total includes tuition, fees, room, and board but not broken down"}	1400	\N	\N	t	f	t	75	VALIDATED	2025-10-09 01:20:24.888	2025-10-09 01:20:24.888
48	106458	2024-2025	institution_website	10430	18740	\N	\N	10430	18740	6550	\N	\N	\N	\N	\N	t	t	t	85	VALIDATED	2025-10-11 04:34:05.043784	2025-10-11 04:34:05.043784
49	106467	2025-2026	institution_website	6174	12349	\N	\N	6174	12349	9852	\N	\N	1240	\N	\N	t	t	t	100	VALIDATED	2025-10-11 04:34:05.055467	2025-10-11 04:34:05.055467
50	107044	2024-2025	institution_website	26490	26490	\N	\N	27282	27282	10124	\N	\N	\N	\N	\N	t	t	t	90	VALIDATED	2025-10-11 04:34:05.056023	2025-10-11 04:34:05.056023
51	107071	2025-2026	institution_website	8250	11310	\N	\N	8250	11310	\N	\N	\N	\N	\N	\N	t	f	f	50	VALIDATED	2025-10-11 04:34:05.056398	2025-10-11 04:34:05.056398
52	107141	2024-2025	institution_website	32710	32710	\N	\N	32710	32710	10189	\N	\N	800	\N	\N	t	t	t	100	VALIDATED	2025-10-11 04:34:05.056692	2025-10-11 04:34:05.056692
53	107983	2023-2024	institution_website	10200	16080	\N	\N	10200	16080	\N	\N	\N	\N	\N	\N	t	t	f	60	VALIDATED	2025-10-11 04:34:05.056969	2025-10-11 04:34:05.056969
54	106397	2024-2025	institution_website	10496	31550	\N	\N	10496	31550	10758	\N	\N	\N	\N	\N	t	t	t	85	VALIDATED	2025-10-11 04:34:05.057247	2025-10-11 04:34:05.057247
55	107585	2024-2025	institution_website	3150	3150	1410	1410	4560	4560	\N	\N	\N	\N	\N	\N	t	t	f	70	VALIDATED	2025-10-11 04:34:05.057497	2025-10-11 04:34:05.057497
56	106245	2025-2026	institution_website	\N	22870	\N	\N	\N	22870	7606	\N	\N	1800	\N	\N	t	t	t	75	NEEDS_REVIEW	2025-10-11 04:34:05.057751	2025-10-11 04:34:05.057751
57	106412	2024-2025	institution_website	9019	17029	\N	\N	9019	17029	\N	\N	\N	\N	\N	\N	t	t	f	60	VALIDATED	2025-10-11 04:34:05.057993	2025-10-11 04:34:05.057993
58	108092	2024-2025	institution_website	9826	15226	\N	\N	9826	15226	\N	\N	\N	\N	\N	\N	t	t	f	60	VALIDATED	2025-10-11 04:34:05.058227	2025-10-11 04:34:05.058227
59	106704	2024-2025	institution_website	10523	18023	\N	\N	10523	18023	9552	\N	\N	1216	\N	\N	t	t	t	100	VALIDATED	2025-10-11 04:34:05.058457	2025-10-11 04:34:05.058457
\.


--
-- Data for Name: user_profiles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_profiles (id, user_id, high_school_name, graduation_year, gpa, gpa_scale, intended_major, state, sat_score, act_score, city, zip_code, created_at, updated_at) FROM stdin;
1	1	Exeter High School	2026	3.7	4.0	Computer Science	NH	1350	29	Exeter	03833	2025-10-02 00:38:46.55523	2025-10-10 12:10:52.109968
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, email, username, hashed_password, first_name, last_name, is_active, is_superuser, is_verified, created_at, updated_at, last_login_at) FROM stdin;
1	daneahern@yahoo.com	dahern	$2b$12$COUBLG5PZOXBofyzJ0NioeWa5uuXKq7DTi5U4XhstTNK6rJe5loMa	Dane 	Ahern	t	f	f	2025-10-01 00:50:15.912611-07	2025-10-03 01:43:11.818655-07	2025-10-03 08:43:12.015372-07
\.


--
-- Name: institutions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.institutions_id_seq', 609, true);


--
-- Name: oauth_accounts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.oauth_accounts_id_seq', 1, false);


--
-- Name: oauth_states_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.oauth_states_id_seq', 1, true);


--
-- Name: scholarships_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.scholarships_id_seq', 102, true);


--
-- Name: tuition_data_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tuition_data_id_seq', 59, true);


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
-- Name: idx_institution_state_city; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_institution_state_city ON public.institutions USING btree (state, city);


--
-- Name: ix_institutions_city; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_institutions_city ON public.institutions USING btree (city);


--
-- Name: ix_institutions_control_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_institutions_control_type ON public.institutions USING btree (control_type);


--
-- Name: ix_institutions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_institutions_id ON public.institutions USING btree (id);


--
-- Name: ix_institutions_ipeds_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_institutions_ipeds_id ON public.institutions USING btree (ipeds_id);


--
-- Name: ix_institutions_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_institutions_name ON public.institutions USING btree (name);


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
-- Name: ix_scholarships_deadline; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_scholarships_deadline ON public.scholarships USING btree (deadline);


--
-- Name: ix_scholarships_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_scholarships_id ON public.scholarships USING btree (id);


--
-- Name: ix_scholarships_organization; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_scholarships_organization ON public.scholarships USING btree (organization);


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
-- Name: ix_user_profiles_graduation_year; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_profiles_graduation_year ON public.user_profiles USING btree (graduation_year);


--
-- Name: ix_user_profiles_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_profiles_id ON public.user_profiles USING btree (id);


--
-- Name: ix_user_profiles_state; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_profiles_state ON public.user_profiles USING btree (state);


--
-- Name: ix_user_profiles_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_user_profiles_user_id ON public.user_profiles USING btree (user_id);


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
-- Name: oauth_accounts oauth_accounts_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.oauth_accounts
    ADD CONSTRAINT oauth_accounts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


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

