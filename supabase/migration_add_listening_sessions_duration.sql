-- Migration: Add duration_seconds and time_exceeded to listening_sessions (for Murajat and Juz'ul Hali)
-- Run this in your Supabase SQL Editor (Dashboard -> SQL Editor -> New Query)

ALTER TABLE public.listening_sessions ADD COLUMN IF NOT EXISTS duration_seconds int NOT NULL DEFAULT 0;
ALTER TABLE public.listening_sessions ADD COLUMN IF NOT EXISTS time_exceeded boolean NOT NULL DEFAULT false;
