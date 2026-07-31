-- SQL: Create parent report views table
CREATE TABLE IF NOT EXISTS public.parent_report_views (
  student_id uuid NOT NULL REFERENCES public.students(id) ON DELETE CASCADE,
  activity_date date NOT NULL,
  viewed_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (student_id, activity_date)
);

ALTER TABLE public.parent_report_views ENABLE ROW LEVEL SECURITY;

-- Policy to allow all CRUD actions (since PostgREST requests will read/write it)
CREATE POLICY "crud parent views" ON public.parent_report_views FOR ALL USING (true) WITH CHECK (true);
