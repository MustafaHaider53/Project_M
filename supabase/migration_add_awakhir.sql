-- SQL Migration: Add granular Talqeen and Tanbeeh counters for secondary mistakes
-- Run this in your Supabase SQL Editor (Dashboard -> SQL Editor -> New Query)

-- 1. Add awakhir_ul_ayat and the specific talqeen/tanbeeh columns to mistake_counts table
ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS awakhir_ul_ayat int NOT NULL DEFAULT 0;

ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS irab_talqeen int NOT NULL DEFAULT 0;
ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS irab_tanbeeh int NOT NULL DEFAULT 0;

ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS repeat_mistake_talqeen int NOT NULL DEFAULT 0;
ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS repeat_mistake_tanbeeh int NOT NULL DEFAULT 0;

ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS mutashabehat_talqeen int NOT NULL DEFAULT 0;
ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS mutashabehat_tanbeeh int NOT NULL DEFAULT 0;

ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS awakhir_ul_ayat_talqeen int NOT NULL DEFAULT 0;
ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS awakhir_ul_ayat_tanbeeh int NOT NULL DEFAULT 0;

-- 2. Populate historical data (map existing totals to Talqeen columns)
UPDATE public.mistake_counts 
SET 
  irab_talqeen = COALESCE(irab, 0),
  repeat_mistake_talqeen = COALESCE(repeat_mistake, 0),
  mutashabehat_talqeen = COALESCE(mutashabehat, 0);

-- 3. Update the check constraint on mistake_events table to support new kinds
ALTER TABLE public.mistake_events DROP CONSTRAINT IF EXISTS mistake_events_kind_check;
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
    'awakhir_ul_ayat_tanbeeh'
  )
);
