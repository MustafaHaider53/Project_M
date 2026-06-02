-- Migration for existing projects:
-- Adds students + links sessions/entries to a student.

create extension if not exists "uuid-ossp";

create table if not exists public.students (
  id uuid primary key default uuid_generate_v4(),
  full_name text not null,
  created_at timestamptz not null default now(),
  unique (full_name)
);

alter table public.students enable row level security;
do $$
begin
  if not exists (select 1 from pg_policies where schemaname='public' and tablename='students') then
    create policy "crud students" on public.students for all using (true) with check (true);
  end if;
end $$;

-- 1) Add columns as nullable first (to avoid breaking existing rows)
alter table public.listening_sessions add column if not exists student_id uuid;
alter table public.listening_sessions add column if not exists activity_date date;
alter table public.jadeed_entries add column if not exists student_id uuid;
alter table public.jadeed_entries add column if not exists activity_date date;

-- Daily Jadeed status
create table if not exists public.jadeed_daily (
  student_id uuid not null references public.students(id) on delete cascade,
  activity_date date not null,
  no_jadeed boolean not null default false,
  updated_at timestamptz not null default now(),
  primary key (student_id, activity_date)
);

alter table public.jadeed_daily enable row level security;
do $$
begin
  if not exists (select 1 from pg_policies where schemaname='public' and tablename='jadeed_daily') then
    create policy "crud jadeed daily" on public.jadeed_daily for all using (true) with check (true);
  end if;
end $$;

-- 2) Add FK (do NOT force NOT NULL; app will enforce selecting a student)
do $$
begin
  if not exists (
    select 1
    from information_schema.table_constraints
    where constraint_schema='public'
      and table_name='listening_sessions'
      and constraint_name='listening_sessions_student_id_fkey'
  ) then
    alter table public.listening_sessions
      add constraint listening_sessions_student_id_fkey
      foreign key (student_id) references public.students(id) on delete cascade;
  end if;
end $$;

do $$
begin
  if not exists (
    select 1
    from information_schema.table_constraints
    where constraint_schema='public'
      and table_name='jadeed_entries'
      and constraint_name='jadeed_entries_student_id_fkey'
  ) then
    alter table public.jadeed_entries
      add constraint jadeed_entries_student_id_fkey
      foreign key (student_id) references public.students(id) on delete cascade;
  end if;
end $$;

-- Ensure activity_date is always set for existing rows
update public.listening_sessions set activity_date = coalesce(activity_date, created_at::date) where activity_date is null;
update public.jadeed_entries set activity_date = coalesce(activity_date, created_at::date) where activity_date is null;


