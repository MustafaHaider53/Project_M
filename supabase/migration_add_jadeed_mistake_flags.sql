-- Migration: Add Weak Hifz and Airab Mistakes flags to jadeed_entries
-- Run this in your Supabase SQL Editor

ALTER TABLE public.jadeed_entries ADD COLUMN IF NOT EXISTS weak_hifz boolean NOT NULL DEFAULT false;
ALTER TABLE public.jadeed_entries ADD COLUMN IF NOT EXISTS airab_mistakes boolean NOT NULL DEFAULT false;
