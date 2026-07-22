-- Project M schema (Supabase / Postgres)

create extension if not exists "uuid-ossp";

-- Surah master (seeded below)
create table if not exists public.surahs (
  id bigint generated always as identity primary key,
  number int not null unique,
  name_en text not null,
  name_ar text not null
);

-- Students master
create table if not exists public.students (
  id uuid primary key default uuid_generate_v4(),
  full_name text not null,
  created_at timestamptz not null default now(),
  unique (full_name)
);

-- Listening sessions: Murajat or Juzulhali
create table if not exists public.listening_sessions (
  id uuid primary key default uuid_generate_v4(),
  student_id uuid not null references public.students(id) on delete cascade,
  activity_date date not null default current_date,
  mode text not null check (mode in ('murajat', 'juzulhali')),
  surah_id bigint references public.surahs(id),
  page_number int,
  created_at timestamptz not null default now(),
  constraint murajat_needs_surah check (
    (mode <> 'murajat') or (surah_id is not null and page_number is null)
  ),
  constraint juzulhali_needs_page check (
    (mode <> 'juzulhali') or (page_number is not null and surah_id is null)
  )
);

-- One row per session, kept in sync by the app
create table if not exists public.mistake_counts (
  session_id uuid primary key references public.listening_sessions(id) on delete cascade,
  talqeen int not null default 0,
  tanbeeh int not null default 0,
  repeat_mistake int not null default 0,
  mutashabehat int not null default 0,
  irab int not null default 0,
  is_zero_marks boolean not null default false,
  updated_at timestamptz not null default now()
);

-- Event log (optional but useful for audits)
create table if not exists public.mistake_events (
  id uuid primary key default uuid_generate_v4(),
  session_id uuid not null references public.listening_sessions(id) on delete cascade,
  kind text not null check (kind in ('talqeen','tanbeeh','repeat_mistake','mutashabehat','irab')),
  activity_date date not null default current_date,
  created_at timestamptz not null default now()
);

-- Jadeed entries (data table)
create table if not exists public.jadeed_entries (
  id uuid primary key default uuid_generate_v4(),
  student_id uuid not null references public.students(id) on delete cascade,
  activity_date date not null default current_date,
  surah_id bigint not null references public.surahs(id),
  page_number int not null,
  ayah_number int not null,
  volume text not null check (volume in ('Half', 'Full', 'Ruba', 'Nisf', 'Sulus', 'Kamil')),
  created_at timestamptz not null default now()
);

-- Daily Jadeed status (no user-chosen date; always current_date from app)
create table if not exists public.jadeed_daily (
  student_id uuid not null references public.students(id) on delete cascade,
  activity_date date not null,
  no_jadeed boolean not null default false,
  updated_at timestamptz not null default now(),
  primary key (student_id, activity_date)
);

-- Daily Takhteet (homework text)
create table if not exists public.takhteet_daily (
  student_id uuid not null references public.students(id) on delete cascade,
  activity_date date not null,
  murajat_text_raw text not null default '',
  juzulhali_text_raw text not null default '',
  jadeed_text_raw text not null default '',
  murajat_text_clean text not null default '',
  juzulhali_text_clean text not null default '',
  jadeed_text_clean text not null default '',
  updated_at timestamptz not null default now(),
  primary key (student_id, activity_date)
);

-- ---- Seed surahs (114)
insert into public.surahs (number, name_en, name_ar) values
 (1,'Al-Fatihah','الفاتحة'),
 (2,'Al-Baqarah','البقرة'),
 (3,'Aal-E-Imran','آل عمران'),
 (4,'An-Nisa','النساء'),
 (5,'Al-Ma’idah','المائدة'),
 (6,'Al-An’am','الأنعام'),
 (7,'Al-A’raf','الأعراف'),
 (8,'Al-Anfal','الأنفال'),
 (9,'At-Tawbah','التوبة'),
 (10,'Yunus','يونس'),
 (11,'Hud','هود'),
 (12,'Yusuf','يوسف'),
 (13,'Ar-Ra’d','الرعد'),
 (14,'Ibrahim','إبراهيم'),
 (15,'Al-Hijr','الحجر'),
 (16,'An-Nahl','النحل'),
 (17,'Al-Isra','الإسراء'),
 (18,'Al-Kahf','الكهف'),
 (19,'Maryam','مريم'),
 (20,'Ta-Ha','طه'),
 (21,'Al-Anbiya','الأنبياء'),
 (22,'Al-Hajj','الحج'),
 (23,'Al-Mu’minun','المؤمنون'),
 (24,'An-Nur','النور'),
 (25,'Al-Furqan','الفرقان'),
 (26,'Ash-Shu’ara','الشعراء'),
 (27,'An-Naml','النمل'),
 (28,'Al-Qasas','القصص'),
 (29,'Al-Ankabut','العنكبوت'),
 (30,'Ar-Rum','الروم'),
 (31,'Luqman','لقمان'),
 (32,'As-Sajdah','السجدة'),
 (33,'Al-Ahzab','الأحزاب'),
 (34,'Saba','سبأ'),
 (35,'Fatir','فاطر'),
 (36,'Ya-Sin','يس'),
 (37,'As-Saffat','الصافات'),
 (38,'Sad','ص'),
 (39,'Az-Zumar','الزمر'),
 (40,'Ghafir','غافر'),
 (41,'Fussilat','فصلت'),
 (42,'Ash-Shuraa','الشورى'),
 (43,'Az-Zukhruf','الزخرف'),
 (44,'Ad-Dukhan','الدخان'),
 (45,'Al-Jathiyah','الجاثية'),
 (46,'Al-Ahqaf','الأحقاف'),
 (47,'Muhammad','محمد'),
 (48,'Al-Fath','الفتح'),
 (49,'Al-Hujurat','الحجرات'),
 (50,'Qaf','ق'),
 (51,'Adh-Dhariyat','الذاريات'),
 (52,'At-Tur','الطور'),
 (53,'An-Najm','النجم'),
 (54,'Al-Qamar','القمر'),
 (55,'Ar-Rahman','الرحمن'),
 (56,'Al-Waqi’ah','الواقعة'),
 (57,'Al-Hadid','الحديد'),
 (58,'Al-Mujadila','المجادلة'),
 (59,'Al-Hashr','الحشر'),
 (60,'Al-Mumtahanah','الممتحنة'),
 (61,'As-Saff','الصف'),
 (62,'Al-Jumu’ah','الجمعة'),
 (63,'Al-Munafiqun','المنافقون'),
 (64,'At-Taghabun','التغابن'),
 (65,'At-Talaq','الطلاق'),
 (66,'At-Tahrim','التحريم'),
 (67,'Al-Mulk','الملك'),
 (68,'Al-Qalam','القلم'),
 (69,'Al-Haqqah','الحاقة'),
 (70,'Al-Ma’arij','المعارج'),
 (71,'Nuh','نوح'),
 (72,'Al-Jinn','الجن'),
 (73,'Al-Muzzammil','المزمل'),
 (74,'Al-Muddaththir','المدثر'),
 (75,'Al-Qiyamah','القيامة'),
 (76,'Al-Insan','الإنسان'),
 (77,'Al-Mursalat','المرسلات'),
 (78,'An-Naba','النبأ'),
 (79,'An-Nazi’at','النازعات'),
 (80,'Abasa','عبس'),
 (81,'At-Takwir','التكوير'),
 (82,'Al-Infitar','الانفطار'),
 (83,'Al-Mutaffifin','المطففين'),
 (84,'Al-Inshiqaq','الانشقاق'),
 (85,'Al-Buruj','البروج'),
 (86,'At-Tariq','الطارق'),
 (87,'Al-A’la','الأعلى'),
 (88,'Al-Ghashiyah','الغاشية'),
 (89,'Al-Fajr','الفجر'),
 (90,'Al-Balad','البلد'),
 (91,'Ash-Shams','الشمس'),
 (92,'Al-Layl','الليل'),
 (93,'Ad-Duhaa','الضحى'),
 (94,'Ash-Sharh','الشرح'),
 (95,'At-Tin','التين'),
 (96,'Al-’Alaq','العلق'),
 (97,'Al-Qadr','القدر'),
 (98,'Al-Bayyinah','البينة'),
 (99,'Az-Zalzalah','الزلزلة'),
 (100,'Al-’Adiyat','العاديات'),
 (101,'Al-Qari’ah','القارعة'),
 (102,'At-Takathur','التكاثر'),
 (103,'Al-’Asr','العصر'),
 (104,'Al-Humazah','الهمزة'),
 (105,'Al-Fil','الفيل'),
 (106,'Quraysh','قريش'),
 (107,'Al-Ma’un','الماعون'),
 (108,'Al-Kawthar','الكوثر'),
 (109,'Al-Kafirun','الكافرون'),
 (110,'An-Nasr','النصر'),
 (111,'Al-Masad','المسد'),
 (112,'Al-Ikhlas','الإخلاص'),
 (113,'Al-Falaq','الفلق'),
 (114,'An-Nas','الناس')
on conflict (number) do nothing;

-- RLS (optional): start permissive for quick prototyping
alter table public.surahs enable row level security;
alter table public.students enable row level security;
alter table public.listening_sessions enable row level security;
alter table public.mistake_counts enable row level security;
alter table public.mistake_events enable row level security;
alter table public.jadeed_entries enable row level security;
alter table public.jadeed_daily enable row level security;
alter table public.takhteet_daily enable row level security;

do $$
begin
  if not exists (select 1 from pg_policies where schemaname='public' and tablename='surahs') then
    create policy "read surahs" on public.surahs for select using (true);
  end if;

  if not exists (select 1 from pg_policies where schemaname='public' and tablename='students') then
    create policy "crud students" on public.students for all using (true) with check (true);
  end if;

  if not exists (select 1 from pg_policies where schemaname='public' and tablename='listening_sessions') then
    create policy "crud sessions" on public.listening_sessions for all using (true) with check (true);
  end if;

  if not exists (select 1 from pg_policies where schemaname='public' and tablename='mistake_counts') then
    create policy "crud counts" on public.mistake_counts for all using (true) with check (true);
  end if;

  if not exists (select 1 from pg_policies where schemaname='public' and tablename='mistake_events') then
    create policy "crud events" on public.mistake_events for all using (true) with check (true);
  end if;

  if not exists (select 1 from pg_policies where schemaname='public' and tablename='jadeed_entries') then
    create policy "crud jadeed" on public.jadeed_entries for all using (true) with check (true);
  end if;

  if not exists (select 1 from pg_policies where schemaname='public' and tablename='jadeed_daily') then
    create policy "crud jadeed daily" on public.jadeed_daily for all using (true) with check (true);
  end if;

  if not exists (select 1 from pg_policies where schemaname='public' and tablename='takhteet_daily') then
    create policy "crud takhteet daily" on public.takhteet_daily for all using (true) with check (true);
  end if;
end $$;

