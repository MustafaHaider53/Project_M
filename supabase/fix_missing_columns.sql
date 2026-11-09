-- ========================================================================
-- FIX MISSING COLUMNS IN NEW SUPABASE INSTANCE
-- Run this in your new Supabase Dashboard -> SQL Editor -> New Query
-- ========================================================================

-- 1. Add missing columns to jadeed_entries
ALTER TABLE public.jadeed_entries ADD COLUMN IF NOT EXISTS weak_hifz boolean NOT NULL DEFAULT false;
ALTER TABLE public.jadeed_entries ADD COLUMN IF NOT EXISTS airab_mistakes boolean NOT NULL DEFAULT false;
ALTER TABLE public.jadeed_entries ADD COLUMN IF NOT EXISTS time_exceeded boolean NOT NULL DEFAULT false;
ALTER TABLE public.jadeed_entries ADD COLUMN IF NOT EXISTS duration_seconds int DEFAULT null;
ALTER TABLE public.jadeed_entries ADD COLUMN IF NOT EXISTS start_time text DEFAULT null;
ALTER TABLE public.jadeed_entries ADD COLUMN IF NOT EXISTS end_time text DEFAULT null;
ALTER TABLE public.jadeed_entries ADD COLUMN IF NOT EXISTS weak_murajat boolean NOT NULL DEFAULT false;
ALTER TABLE public.jadeed_entries ADD COLUMN IF NOT EXISTS weak_juzulhali boolean NOT NULL DEFAULT false;
ALTER TABLE public.jadeed_entries ADD COLUMN IF NOT EXISTS weak_jadeed boolean NOT NULL DEFAULT false;
ALTER TABLE public.jadeed_entries ADD COLUMN IF NOT EXISTS is_weak boolean NOT NULL DEFAULT false;
ALTER TABLE public.jadeed_entries ADD COLUMN IF NOT EXISTS has_tanbeeh boolean NOT NULL DEFAULT false;
ALTER TABLE public.jadeed_entries ADD COLUMN IF NOT EXISTS has_talqeen boolean NOT NULL DEFAULT false;
ALTER TABLE public.jadeed_entries ADD COLUMN IF NOT EXISTS teacher_id uuid;
ALTER TABLE public.jadeed_entries ADD COLUMN IF NOT EXISTS teacher_name text;

-- 2. Add missing columns to jadeed_daily
ALTER TABLE public.jadeed_daily ADD COLUMN IF NOT EXISTS weak_hifz boolean NOT NULL DEFAULT false;
ALTER TABLE public.jadeed_daily ADD COLUMN IF NOT EXISTS airab_mistakes boolean NOT NULL DEFAULT false;
ALTER TABLE public.jadeed_daily ADD COLUMN IF NOT EXISTS time_exceeded boolean NOT NULL DEFAULT false;
ALTER TABLE public.jadeed_daily ADD COLUMN IF NOT EXISTS weak_murajat boolean NOT NULL DEFAULT false;
ALTER TABLE public.jadeed_daily ADD COLUMN IF NOT EXISTS weak_juzulhali boolean NOT NULL DEFAULT false;
ALTER TABLE public.jadeed_daily ADD COLUMN IF NOT EXISTS weak_jadeed boolean NOT NULL DEFAULT false;

-- 3. Add manual_marks and extra analysis columns to mistake_counts
ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS manual_marks numeric DEFAULT null;
ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS awakhir_ul_ayat int NOT NULL DEFAULT 0;
ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS irab_talqeen int NOT NULL DEFAULT 0;
ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS irab_tanbeeh int NOT NULL DEFAULT 0;
ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS repeat_mistake_talqeen int NOT NULL DEFAULT 0;
ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS repeat_mistake_tanbeeh int NOT NULL DEFAULT 0;
ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS mutashabehat_talqeen int NOT NULL DEFAULT 0;
ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS mutashabehat_tanbeeh int NOT NULL DEFAULT 0;
ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS awakhir_ul_ayat_talqeen int NOT NULL DEFAULT 0;
ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS awakhir_ul_ayat_tanbeeh int NOT NULL DEFAULT 0;
ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS ikhfa int NOT NULL DEFAULT 0;
ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS izhaar int NOT NULL DEFAULT 0;
ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS qalqalah int NOT NULL DEFAULT 0;
ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS ism_jalalah int NOT NULL DEFAULT 0;
ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS tahreek_sakin int NOT NULL DEFAULT 0;
ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS gunnah int NOT NULL DEFAULT 0;
ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS idgham int NOT NULL DEFAULT 0;
ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS madd_lazim int NOT NULL DEFAULT 0;
ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS madd_muttasil int NOT NULL DEFAULT 0;
ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS mad_tabaiee int NOT NULL DEFAULT 0;
ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS ikhfa_shafawi int NOT NULL DEFAULT 0;
ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS iqlab int NOT NULL DEFAULT 0;

-- 4. Add missing columns to listening_sessions
ALTER TABLE public.listening_sessions ADD COLUMN IF NOT EXISTS teacher_id uuid;
ALTER TABLE public.listening_sessions ADD COLUMN IF NOT EXISTS teacher_name text;
ALTER TABLE public.listening_sessions ADD COLUMN IF NOT EXISTS duration_seconds int DEFAULT null;
ALTER TABLE public.listening_sessions ADD COLUMN IF NOT EXISTS start_time text DEFAULT null;
ALTER TABLE public.listening_sessions ADD COLUMN IF NOT EXISTS end_time text DEFAULT null;
ALTER TABLE public.listening_sessions ADD COLUMN IF NOT EXISTS is_weak boolean NOT NULL DEFAULT false;

-- 5. Add missing columns to students
ALTER TABLE public.students ADD COLUMN IF NOT EXISTS email text;
ALTER TABLE public.students ADD COLUMN IF NOT EXISTS its text;

-- 6. Add missing columns to takhteet_daily
ALTER TABLE public.takhteet_daily ADD COLUMN IF NOT EXISTS teacher_id uuid;
ALTER TABLE public.takhteet_daily ADD COLUMN IF NOT EXISTS teacher_name text;
