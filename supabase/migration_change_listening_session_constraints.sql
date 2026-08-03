-- Drop old check constraints that restricted page_number to be null in murajat and surah_id to be null in juzulhali
ALTER TABLE public.listening_sessions DROP CONSTRAINT IF EXISTS murajat_needs_surah;
ALTER TABLE public.listening_sessions DROP CONSTRAINT IF EXISTS juzulhali_needs_page;

-- Add updated check constraints that allow both fields to be non-null (for both new and historical records)
ALTER TABLE public.listening_sessions ADD CONSTRAINT murajat_needs_surah CHECK (
  (mode <> 'murajat') or (surah_id is not null)
);

ALTER TABLE public.listening_sessions ADD CONSTRAINT juzulhali_needs_page CHECK (
  (mode <> 'juzulhali') or (page_number is not null)
);
