-- Migration: Add manual_marks column to mistake_counts
-- Allows teachers to manually assign 0-10 marks for Murajat and Juz'ul Hali recitations

ALTER TABLE public.mistake_counts 
ADD COLUMN IF NOT EXISTS manual_marks numeric(4,2) DEFAULT NULL;

COMMENT ON COLUMN public.mistake_counts.manual_marks IS 'Manual score between 0.0 and 10.0 entered by Musa''id';
