-- SQL Migration: Add Ahkam mistake columns and update constraints
-- Run this in your Supabase SQL Editor (Dashboard -> SQL Editor -> New Query)

-- 1. Add Ahkam columns to mistake_counts
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

-- 2. Update mistake_events check constraint
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN
        SELECT constraint_name 
        FROM information_schema.table_constraints 
        WHERE table_schema = 'public' 
          AND table_name = 'mistake_events' 
          AND constraint_type = 'CHECK'
          AND constraint_name LIKE '%check%'
    LOOP
        EXECUTE 'ALTER TABLE public.mistake_events DROP CONSTRAINT ' || quote_ident(r.constraint_name);
    END LOOP;
END $$;

ALTER TABLE public.mistake_events ADD CONSTRAINT mistake_events_kind_check CHECK (
  kind IN (
    'talqeen',
    'tanbeeh',
    'repeat_mistake',
    'mutashabehat',
    'irab',
    'awakhir_ul_ayat',
    'irab_talqeen',
    'irab_tanbeeh',
    'repeat_mistake_talqeen',
    'repeat_mistake_tanbeeh',
    'mutashabehat_talqeen',
    'mutashabehat_tanbeeh',
    'awakhir_ul_ayat_talqeen',
    'awakhir_ul_ayat_tanbeeh',
    -- Ahkam categories
    'ikhfa',
    'izhaar',
    'qalqalah',
    'ism_jalalah',
    'tahreek_sakin',
    'gunnah',
    'idgham',
    'madd_lazim',
    'madd_muttasil',
    'mad_tabaiee'
  )
);

