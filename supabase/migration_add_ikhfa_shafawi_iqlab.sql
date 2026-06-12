-- SQL Migration: Add ikhfa_shafawi and iqlab mistake columns and update constraints
-- Run this in your Supabase SQL Editor (Dashboard -> SQL Editor -> New Query)

-- 1. Add columns to mistake_counts
ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS ikhfa_shafawi int NOT NULL DEFAULT 0;
ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS iqlab int NOT NULL DEFAULT 0;

-- 2. Drop all previous check constraints on mistake_events to avoid conflicts
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

-- 3. Add the complete new check constraint
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
    'mad_tabaiee',
    'ikhfa_shafawi',
    'iqlab',
    -- Makharij letters
    'makhraj_alif',
    'makhraj_baa',
    'makhraj_taa',
    'makhraj_thaa',
    'makhraj_jeem',
    'makhraj_haa',
    'makhraj_khaa',
    'makhraj_daal',
    'makhraj_thaal',
    'makhraj_raa',
    'makhraj_zaa',
    'makhraj_seen',
    'makhraj_sheen',
    'makhraj_saad',
    'makhraj_daad',
    'makhraj_taa_thick',
    'makhraj_zaa_thick',
    'makhraj_ain',
    'makhraj_ghain',
    'makhraj_faa',
    'makhraj_qaaf',
    'makhraj_kaaf',
    'makhraj_laam',
    'makhraj_meem',
    'makhraj_noon',
    'makhraj_haa_weak',
    'makhraj_waw',
    'makhraj_yaa'
  )
);
