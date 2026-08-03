-- Migration: Add Musaid Analysis columns to mistake_counts
ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS musaid_end_part int NOT NULL DEFAULT 0;
ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS musaid_beg_part int NOT NULL DEFAULT 0;
ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS musaid_ayat_after_ayat int NOT NULL DEFAULT 0;
ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS musaid_page_after_page int NOT NULL DEFAULT 0;
ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS musaid_no_image int NOT NULL DEFAULT 0;
ALTER TABLE public.mistake_counts ADD COLUMN IF NOT EXISTS musaid_lehen int NOT NULL DEFAULT 0;
