-- Migration: Add Teachers (Musaideen) Table, Attendance Logs, and Teacher Columns across Tasmee Tables

-- 1. Create Teachers Table
create table if not exists public.teachers (
  id uuid primary key default gen_random_uuid(),
  username text not null unique,
  full_name text not null,
  password text not null,
  role text not null default 'teacher',
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.teachers enable row level security;

do $$
begin
  if not exists (select 1 from pg_policies where schemaname='public' and tablename='teachers') then
    create policy "crud teachers" on public.teachers for all using (true) with check (true);
  end if;
end $$;

-- 2. Insert Default 'burooj' Admin and Teachers if not exists
insert into public.teachers (username, full_name, password, role)
values 
  ('burooj', 'Burooj', 'Burooj@53', 'admin'),
  ('zahra', 'Zahra Mulla Mufaddal Ratlamwala', 'Zahra@53', 'teacher'),
  ('zahabiyah', 'Zahabiyah Saifuddin Anjarwala', 'Zahabiyah@53', 'teacher'),
  ('aliasgar', 'Aliasgar Mohammed Darussalamwala', 'Aliasgar@53', 'teacher'),
  ('mustafa', 'Mustafa Haiderali Saboowala', 'Mustafa@53', 'teacher'),
  ('ammar', 'Ammar Aamir Mandasorwala', 'Ammar@53', 'teacher'),
  ('quraish', 'Quraish bhai Hussain bhai Mithaiwala', 'Quraish@53', 'teacher'),
  ('mustansir', 'Mustansir Mithai', 'Mustansir@53', 'teacher'),
  ('husaina', 'Husaina Shaikh Shamoil Ujjainwala', 'Husaina@53', 'teacher')
on conflict (username) do update
set full_name = excluded.full_name, password = excluded.password, role = excluded.role;

-- 3. Add Teacher Columns to listening_sessions (Murajat & Juz'ul Hali)
alter table public.listening_sessions add column if not exists teacher_id uuid;
alter table public.listening_sessions add column if not exists teacher_name text;

-- 4. Add Teacher Columns to jadeed_entries (Jadeed)
alter table public.jadeed_entries add column if not exists teacher_id uuid;
alter table public.jadeed_entries add column if not exists teacher_name text;

-- 5. Add Teacher Columns to takhteet_daily (Homework)
alter table public.takhteet_daily add column if not exists teacher_id uuid;
alter table public.takhteet_daily add column if not exists teacher_name text;

-- 6. Create Teacher Attendance Logs Table
create table if not exists public.teacher_attendance_logs (
  id uuid primary key default gen_random_uuid(),
  teacher_id uuid not null,
  teacher_name text not null,
  activity_date date not null default current_date,
  first_tasmee_at timestamptz not null default now(),
  sessions_count int not null default 1,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint teacher_attendance_unique_day unique (teacher_id, activity_date)
);

alter table public.teacher_attendance_logs enable row level security;

do $$
begin
  if not exists (select 1 from pg_policies where schemaname='public' and tablename='teacher_attendance_logs') then
    create policy "crud teacher attendance logs" on public.teacher_attendance_logs for all using (true) with check (true);
  end if;
end $$;
