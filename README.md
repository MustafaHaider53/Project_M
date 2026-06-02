# Project M (Streamlit + Supabase)

Streamlit frontend for Quran listening workflows:

- **Murajat**: choose Surah → record mistake counts (Talqeen, Tanbeeh, Repeat Mistake, Mutashabehat)
- **Juzulhali**: choose page \(1–20\) → record mistake counts (same rules)
- **Jadeed**: data-entry table with Surah, Page Number, Ayah, How Much (Half/Full)

## 1) Supabase setup

Create a Supabase project and run the SQL in `supabase/schema.sql` in the Supabase SQL editor.

## 2) Configure secrets

Create `.streamlit/secrets.toml`:

```toml
SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
SUPABASE_KEY = "YOUR_SERVICE_ROLE_KEY_OR_ANON_KEY"
```

Notes:
- For **quick start**, you can use the **anon key** if your RLS policies allow it.
- For simplest server-side writes, use the **service role key** (keep it private; don’t commit).

## 3) Run locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## 4) Deploy free

- **Streamlit Community Cloud** (free tier): connect GitHub repo and set the same secrets in Streamlit “Secrets”.
- Supabase free tier works well for this use case.

