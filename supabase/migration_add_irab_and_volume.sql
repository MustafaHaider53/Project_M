-- Migration: Add I'rab column to mistake_counts, check constraint for mistake_events kind, and new columns to listening_sessions.
-- Also update jadeed_entries volume check constraint.

-- 1. Add irab column to mistake_counts
alter table public.mistake_counts add column if not exists irab int not null default 0;

-- 2. Update check constraint on mistake_events kind
alter table public.mistake_events drop constraint if exists mistake_events_kind_check;
alter table public.mistake_events add constraint mistake_events_kind_check check (kind in ('talqeen','tanbeeh','repeat_mistake','mutashabehat','irab'));

-- 3. Update check constraint on jadeed_entries volume
alter table public.jadeed_entries drop constraint if exists jadeed_entries_volume_check;
alter table public.jadeed_entries drop constraint if exists jadeed_entries_how_much_check;
alter table public.jadeed_entries add constraint jadeed_entries_volume_check check (volume in ('Half', 'Full', 'Ruba', 'Nisf', 'Sulus', 'Kamil'));
