-- Migration: Add weak_murajat and weak_juzulhali flags to jadeed_entries & jadeed_daily
-- Run this in your Supabase SQL Editor (Dashboard -> SQL Editor -> New Query)

-- 1. Add flags to jadeed_entries
ALTER TABLE public.jadeed_entries ADD COLUMN IF NOT EXISTS weak_murajat boolean NOT NULL DEFAULT false;
ALTER TABLE public.jadeed_entries ADD COLUMN IF NOT EXISTS weak_juzulhali boolean NOT NULL DEFAULT false;

-- 2. Add flags to jadeed_daily (to store reasons when marked No Jadeed)
ALTER TABLE public.jadeed_daily ADD COLUMN IF NOT EXISTS weak_hifz boolean NOT NULL DEFAULT false;
ALTER TABLE public.jadeed_daily ADD COLUMN IF NOT EXISTS airab_mistakes boolean NOT NULL DEFAULT false;
ALTER TABLE public.jadeed_daily ADD COLUMN IF NOT EXISTS time_exceeded boolean NOT NULL DEFAULT false;
ALTER TABLE public.jadeed_daily ADD COLUMN IF NOT EXISTS weak_murajat boolean NOT NULL DEFAULT false;
ALTER TABLE public.jadeed_daily ADD COLUMN IF NOT EXISTS weak_juzulhali boolean NOT NULL DEFAULT false;
