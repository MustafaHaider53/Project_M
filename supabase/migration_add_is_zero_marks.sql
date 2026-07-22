-- Migration: Add is_zero_marks column to mistake_counts
ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS is_zero_marks boolean NOT NULL DEFAULT false;
