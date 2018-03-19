-- table users --
CREATE SEQUENCE public.users_id_seq;
ALTER TABLE public.users_id_seq
  OWNER TO postgres;

CREATE TABLE public.users
(
  id bigint NOT NULL DEFAULT nextval('users_id_seq'::regclass),
  password character varying(100),
  email character varying(120),
  name character varying(100),
  password_algo character varying(100),
  password_salt character varying,
  CONSTRAINT users_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.users
  OWNER TO postgres;


-- table tags --

CREATE SEQUENCE public.tags_id_seq;
ALTER TABLE public.tags_id_seq
  OWNER TO postgres;

CREATE TABLE public.tags
(
  id bigint NOT NULL DEFAULT nextval('tags_id_seq'::regclass),
  name character varying(100),
  CONSTRAINT tags_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.tags
  OWNER TO postgres;

-- table contents --

CREATE SEQUENCE public.contents_id_seq;
ALTER TABLE public.contents_id_seq
  OWNER TO postgres;

CREATE TABLE public.contents
(
  id bigint NOT NULL DEFAULT nextval('contents_id_seq'::regclass),
  id_user bigint NOT NULL,
  title character varying(100),
  description text,
  created_at TIMESTAMP DEFAULT NOW(),
  CONSTRAINT contents_fuserkey FOREIGN KEY (id_user) REFERENCES public.users(id),
  CONSTRAINT contents_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.contents
  OWNER TO postgres;


-- table contents x tags --

CREATE TABLE public.contents_tags
(
    id_content bigint not null ,
    id_tag bigint not null ,
    constraint fkey_contents_tags_content foreign key (id_content) references public.contents(id),
    constraint fkey_contents_tags_tag foreign key (id_tag) references public.tags(id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.contents
  OWNER TO postgres;