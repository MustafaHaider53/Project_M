-- Migration: Add time_exceeded and duration_seconds to jadeed_entries
-- Run this in your Supabase SQL Editor (Dashboard -> SQL Editor -> New Query)

ALTER TABLE public.jadeed_entries ADD COLUMN IF NOT EXISTS time_exceeded boolean NOT NULL DEFAULT false;
ALTER TABLE public.jadeed_entries ADD COLUMN IF NOT EXISTS duration_seconds int NOT NULL DEFAULT 0;
