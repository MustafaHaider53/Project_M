-- Migration to add email logs table (lightweight boolean only)
create table if not exists public.email_logs (
  student_id uuid not null references public.students(id) on delete cascade,
  activity_date date not null,
  sent boolean not null default false,
  primary key (student_id, activity_date)
);

-- Enable RLS and create permissive CRUD policy
alter table public.email_logs enable row level security;

do $$
begin
  if not exists (select 1 from pg_policies where schemaname='public' and tablename='email_logs') then
    create policy "crud email logs" on public.email_logs for all using (true) with check (true);
  end if;
end $$;
