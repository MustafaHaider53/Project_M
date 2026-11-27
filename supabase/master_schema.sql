-- ========================================================================
-- MASTER SCHEMA FOR NEW SUPABASE INSTANCE (PROJECT M)
-- Run this entire script in Supabase Dashboard -> SQL Editor -> New Query
-- ========================================================================

create extension if not exists "uuid-ossp";

-- ------------------------------------------------------------------------
-- 1. SURAHS MASTER TABLE & SEED (114 Surahs)
-- ------------------------------------------------------------------------
create table if not exists public.surahs (
  id bigint generated always as identity primary key,
  number int not null unique,
  name_en text not null,
  name_ar text not null
);

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
 (42,'Ash-Shura','الشورى'),
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
 (93,'Ad-Duha','الضحى'),
 (94,'Ash-Sharh','الشرح'),
 (95,'At-Tin','التين'),
 (96,'Al-Alaq','العلق'),
 (97,'Al-Qadr','القدر'),
 (98,'Al-Bayyinah','البينة'),
 (99,'Az-Zalzalah','الزلزلة'),
 (100,'Al-Adiyat','العاديات'),
 (101,'Al-Qari’ah','القارعة'),
 (102,'At-Takathur','التكاثر'),
 (103,'Al-Asr','العصر'),
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

-- ------------------------------------------------------------------------
-- 2. STUDENTS TABLE
-- ------------------------------------------------------------------------
create table if not exists public.students (
  id uuid primary key default uuid_generate_v4(),
  full_name text not null,
  email text,
  its text,
  created_at timestamptz not null default now(),
  unique (full_name)
);

-- ------------------------------------------------------------------------
-- 3. TEACHERS (MUSAIDEEN) TABLE
-- ------------------------------------------------------------------------
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

-- ------------------------------------------------------------------------
-- 4. TEACHER ATTENDANCE LOGS
-- ------------------------------------------------------------------------
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

-- ------------------------------------------------------------------------
-- 5. LISTENING SESSIONS (Murajat & Juz'ul Hali)
-- ------------------------------------------------------------------------
create table if not exists public.listening_sessions (
  id uuid primary key default uuid_generate_v4(),
  student_id uuid not null references public.students(id) on delete cascade,
  activity_date date not null default current_date,
  mode text not null check (mode in ('murajat', 'juzulhali')),
  surah_id bigint references public.surahs(id),
  page_number int,
  created_at timestamptz not null default now(),
  teacher_id uuid,
  teacher_name text,
  duration_seconds int default null,
  start_time text default null,
  end_time text default null,
  is_weak boolean not null default false
);

-- ------------------------------------------------------------------------
-- 6. MISTAKE COUNTS (All Detailed Analysis Columns)
-- ------------------------------------------------------------------------
create table if not exists public.mistake_counts (
  session_id uuid primary key references public.listening_sessions(id) on delete cascade,
  talqeen int not null default 0,
  tanbeeh int not null default 0,
  repeat_mistake int not null default 0,
  mutashabehat int not null default 0,
  irab int not null default 0,
  awakhir_ul_ayat int not null default 0,
  irab_talqeen int not null default 0,
  irab_tanbeeh int not null default 0,
  repeat_mistake_talqeen int not null default 0,
  repeat_mistake_tanbeeh int not null default 0,
  mutashabehat_talqeen int not null default 0,
  mutashabehat_tanbeeh int not null default 0,
  awakhir_ul_ayat_talqeen int not null default 0,
  awakhir_ul_ayat_tanbeeh int not null default 0,
  ikhfa int not null default 0,
  izhaar int not null default 0,
  qalqalah int not null default 0,
  ism_jalalah int not null default 0,
  tahreek_sakin int not null default 0,
  gunnah int not null default 0,
  idgham int not null default 0,
  madd_lazim int not null default 0,
  madd_muttasil int not null default 0,
  mad_tabaiee int not null default 0,
  ikhfa_shafawi int not null default 0,
  iqlab int not null default 0,
  -- Makharij Columns
  makhraj_alif int not null default 0,
  makhraj_baa int not null default 0,
  makhraj_taa int not null default 0,
  makhraj_thaa int not null default 0,
  makhraj_jeem int not null default 0,
  makhraj_haa int not null default 0,
  makhraj_khaa int not null default 0,
  makhraj_daal int not null default 0,
  makhraj_thaal int not null default 0,
  makhraj_raa int not null default 0,
  makhraj_zaa int not null default 0,
  makhraj_seen int not null default 0,
  makhraj_sheen int not null default 0,
  makhraj_saad int not null default 0,
  makhraj_daad int not null default 0,
  makhraj_taa_thick int not null default 0,
  makhraj_zaa_thick int not null default 0,
  makhraj_ain int not null default 0,
  makhraj_ghain int not null default 0,
  makhraj_faa int not null default 0,
  makhraj_qaaf int not null default 0,
  makhraj_kaaf int not null default 0,
  makhraj_laam int not null default 0,
  makhraj_meem int not null default 0,
  makhraj_noon int not null default 0,
  makhraj_haa_weak int not null default 0,
  makhraj_waw int not null default 0,
  makhraj_yaa int not null default 0,
  -- Musaid Analysis Columns
  musaid_end_part int not null default 0,
  musaid_beg_part int not null default 0,
  musaid_ayat_after_ayat int not null default 0,
  musaid_page_after_page int not null default 0,
  musaid_no_image int not null default 0,
  musaid_lehen int not null default 0,
  -- Flags & Manual Marks
  is_zero_marks boolean not null default false,
  manual_marks numeric default null,
  updated_at timestamptz not null default now()
);

-- ------------------------------------------------------------------------
-- 7. MISTAKE EVENTS (Audit Log)
-- ------------------------------------------------------------------------
create table if not exists public.mistake_events (
  id uuid primary key default uuid_generate_v4(),
  session_id uuid not null references public.listening_sessions(id) on delete cascade,
  kind text not null,
  activity_date date not null default current_date,
  created_at timestamptz not null default now()
);

-- ------------------------------------------------------------------------
-- 8. JADEED ENTRIES
-- ------------------------------------------------------------------------
create table if not exists public.jadeed_entries (
  id uuid primary key default uuid_generate_v4(),
  student_id uuid not null references public.students(id) on delete cascade,
  activity_date date not null default current_date,
  surah_id bigint not null references public.surahs(id),
  page_number int not null,
  ayah_number int not null,
  volume text not null,
  created_at timestamptz not null default now(),
  teacher_id uuid,
  teacher_name text,
  start_time text,
  end_time text,
  duration_seconds int,
  is_weak boolean not null default false,
  has_tanbeeh boolean not null default false,
  has_talqeen boolean not null default false,
  weak_hifz boolean not null default false,
  airab_mistakes boolean not null default false,
  time_exceeded boolean not null default false,
  weak_murajat boolean not null default false,
  weak_juzulhali boolean not null default false,
  weak_jadeed boolean not null default false
);

-- ------------------------------------------------------------------------
-- 9. JADEED DAILY (Status)
-- ------------------------------------------------------------------------
create table if not exists public.jadeed_daily (
  student_id uuid not null references public.students(id) on delete cascade,
  activity_date date not null,
  no_jadeed boolean not null default false,
  weak_hifz boolean not null default false,
  airab_mistakes boolean not null default false,
  time_exceeded boolean not null default false,
  weak_murajat boolean not null default false,
  weak_juzulhali boolean not null default false,
  weak_jadeed boolean not null default false,
  updated_at timestamptz not null default now(),
  primary key (student_id, activity_date)
);

-- ------------------------------------------------------------------------
-- 10. TAKHTEET DAILY (Homework)
-- ------------------------------------------------------------------------
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
  teacher_id uuid,
  teacher_name text,
  primary key (student_id, activity_date)
);

-- ------------------------------------------------------------------------
-- 11. EMAIL LOGS
-- ------------------------------------------------------------------------
create table if not exists public.email_logs (
  student_id uuid not null references public.students(id) on delete cascade,
  activity_date date not null,
  sent boolean not null default false,
  primary key (student_id, activity_date)
);

-- ------------------------------------------------------------------------
-- 12. PARENT REPORT VIEWS
-- ------------------------------------------------------------------------
create table if not exists public.parent_report_views (
  student_id uuid not null references public.students(id) on delete cascade,
  activity_date date not null,
  viewed_at timestamptz not null default now(),
  primary key (student_id, activity_date)
);

-- ------------------------------------------------------------------------
-- 13. ENABLE ROW LEVEL SECURITY & OPEN PERMISSIVE POLICIES
-- ------------------------------------------------------------------------
alter table public.surahs enable row level security;
alter table public.students enable row level security;
alter table public.teachers enable row level security;
alter table public.teacher_attendance_logs enable row level security;
alter table public.listening_sessions enable row level security;
alter table public.mistake_counts enable row level security;
alter table public.mistake_events enable row level security;
alter table public.jadeed_entries enable row level security;
alter table public.jadeed_daily enable row level security;
alter table public.takhteet_daily enable row level security;
alter table public.email_logs enable row level security;
alter table public.parent_report_views enable row level security;

do $$
declare
  t text;
begin
  for t in select unnest(array[
    'surahs', 'students', 'teachers', 'teacher_attendance_logs',
    'listening_sessions', 'mistake_counts', 'mistake_events',
    'jadeed_entries', 'jadeed_daily', 'takhteet_daily',
    'email_logs', 'parent_report_views'
  ]) loop
    if not exists (select 1 from pg_policies where schemaname='public' and tablename=t and policyname='allow_all_' || t) then
      execute format('create policy %I on public.%I for all using (true) with check (true);', 'allow_all_' || t, t);
    end if;
  end loop;
end $$;
