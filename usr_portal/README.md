# MSB Collective USR — Multi-School Admin Portal (Vercel)

Standalone, zero-sleep, mobile-first Unified Summary Report (USR) portal connected to **all** Supabase projects (`Main`, `Inter-School`, `After-School`, and any future projects).

## Features
- **Plug-and-Play Multi-Supabase**: Add or remove Supabase projects in one Vercel environment variable (`SUPABASE_SOURCES_JSON`) — zero code changes.
- **Instant Search (< 5ms)**: Searches across all schools by Name or 8-digit ITS in memory (no full-list wall).
- **Recent Students Chips**: Last 8 viewed students saved on the admin's phone (`localStorage`) for 1-tap access.
- **0ms Month Switching (`Nov` / `Oct` / `Sep`)**: Prefetches the last 3 months in one parallel 4-table query when a student is tapped; `Older ▾` loads any past month on demand.
- **Mobile Fit-to-Screen 3-in-1 USR + Full 10-Col Toggle + Print PDF**: Compact 4-column grouped layout fits standard phone screens with zero/minimal horizontal scroll, with a 1-tap toggle to the full 10-column USR table.

## Deploy on Vercel (2 Minutes)
1. Go to [vercel.com/new](https://vercel.com/new) → Import **`MustafaHaider53/Project_M`**.
2. Set **Root Directory** to **`usr_portal`**, Framework Preset: **`Other`** (no build command needed).
3. Under **Environment Variables**, add **`SUPABASE_SOURCES_JSON`**:
   ```json
   [
     {
       "id": "main",
       "label": "Main / Mukhayyam",
       "color": "#0E6B50",
       "url": "https://zpumlchzlyqdlxbgugcn.supabase.co",
       "key": "<MAIN_SUPABASE_ANON_KEY>"
     },
     {
       "id": "inter_school",
       "label": "Inter-School",
       "color": "#1d4ed8",
       "url": "https://<INTER_SCHOOL_PROJECT>.supabase.co",
       "key": "<INTER_SCHOOL_ANON_KEY>"
     },
     {
       "id": "after_school",
       "label": "After-School",
       "color": "#7e22ce",
       "url": "https://plvqjblfupapsasopjej.supabase.co",
       "key": "<AFTER_SCHOOL_ANON_KEY>"
     }
   ]
   ```
4. Click **Deploy**! To add a 4th or 5th school later, simply edit `SUPABASE_SOURCES_JSON` in Vercel Settings and redeploy.
