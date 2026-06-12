from __future__ import annotations

from datetime import datetime, timezone
from datetime import date
from typing import Any, Dict, List, Optional
from collections import defaultdict

import streamlit as st
import requests
import threading
from requests.exceptions import JSONDecodeError as RequestsJSONDecodeError

from app.config import get_settings


@st.cache_resource(show_spinner=False)
def get_rest() -> Optional["SupabaseRest"]:
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_key:
        return None
    return SupabaseRest(url=settings.supabase_url, key=settings.supabase_key)


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def today_iso() -> str:
    # Date-wise storage; user does not select date.
    return date.today().isoformat()


def normalize_text(value: str) -> str:
    """
    Basic normalization for user-entered homework text:
    - trim each line
    - collapse repeated spaces
    - keep user content, only improve readability consistency
    """
    lines = str(value or "").replace("\r\n", "\n").replace("\r", "\n").split("\n")
    cleaned: List[str] = []
    for ln in lines:
        parts = ln.strip().split()
        cleaned.append(" ".join(parts))
    # keep non-empty lines, but preserve line breaks between meaningful entries
    cleaned = [ln for ln in cleaned if ln]
    return "\n".join(cleaned)

class SupabaseRest:
    def __init__(self, *, url: str, key: str):
        self.url = url.rstrip("/")
        self.key = key.strip()

    def _headers(self, *, prefer: Optional[str] = None) -> Dict[str, str]:
        h = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
        }
        if prefer:
            h["Prefer"] = prefer
        return h

    def select(self, table: str, *, select: str, params: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        r = requests.get(
            f"{self.url}/rest/v1/{table}",
            headers=self._headers(),
            params={"select": select, **(params or {})},
            timeout=20,
        )
        r.raise_for_status()
        if not r.content or not r.content.strip():
            return []
        try:
            return list(r.json() or [])
        except Exception:
            raise RuntimeError(
                f"Supabase returned non-JSON for select {table}. "
                f"status={r.status_code} content_type={r.headers.get('content-type')} body={r.text[:300]!r}"
            ) from None

    def select_single(
        self, table: str, *, select: str, params: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        data = self.select(table, select=select, params=params)
        if not data:
            return None
        return data[0]

    def insert(self, table: str, rows: List[Dict[str, Any]], *, returning: str = "representation") -> List[Dict[str, Any]]:
        r = requests.post(
            f"{self.url}/rest/v1/{table}",
            headers=self._headers(prefer=f"return={returning}"),
            json=rows,
            timeout=20,
        )
        r.raise_for_status()
        # With Prefer: return=minimal, PostgREST returns an empty body.
        # Even when "representation" is requested, some setups can still return an empty body.
        if returning == "minimal" or not r.content or not r.content.strip():
            return []
        # Some proxies/middlewares can return non-JSON HTML/text even on 2xx.
        # Guard so we never raise JSONDecodeError here.
        try:
            payload = r.json()
        except Exception:
            return []
        return list(payload or [])

    def upsert(
        self,
        table: str,
        rows: List[Dict[str, Any]],
        *,
        on_conflict: str,
        returning: str = "minimal",
    ) -> None:
        r = requests.post(
            f"{self.url}/rest/v1/{table}",
            headers=self._headers(prefer=f"resolution=merge-duplicates,return={returning}"),
            params={"on_conflict": on_conflict},
            json=rows,
            timeout=20,
        )
        r.raise_for_status()

    def update(self, table: str, *, match: Dict[str, Any], patch: Dict[str, Any]) -> None:
        params = {k: f"eq.{v}" for k, v in match.items()}
        r = requests.patch(
            f"{self.url}/rest/v1/{table}",
            headers=self._headers(),
            params=params,
            json=patch,
            timeout=20,
        )
        r.raise_for_status()

    def delete(self, table: str, *, match: Dict[str, Any]) -> None:
        params = {k: f"eq.{v}" for k, v in match.items()}
        r = requests.delete(
            f"{self.url}/rest/v1/{table}",
            headers=self._headers(),
            params=params,
            timeout=20,
        )
        r.raise_for_status()


@st.cache_data(show_spinner=False)
def list_surahs() -> List[Dict[str, Any]]:
    rest = get_rest()
    if rest is None:
        return []
    return rest.select("surahs", select="id,name_ar,name_en,number", params={"order": "number.asc"})


@st.cache_data(show_spinner=False)
def list_students() -> List[Dict[str, Any]]:
    rest = get_rest()
    if rest is None:
        return []
    return rest.select("students", select="id,full_name,created_at", params={"order": "full_name.asc"})


def create_student(*, full_name: str) -> Dict[str, Any]:
    rest = get_rest()
    if rest is None:
        raise RuntimeError("Supabase is not configured.")
    full_name = full_name.strip()
    if not full_name:
        raise ValueError("Student name is required.")
    # Try insert; if unique constraint blocks, fetch existing.
    try:
        res = rest.insert("students", [{"full_name": full_name}])
        list_students.clear()
        if res:
            return res[0]
    except requests.HTTPError:
        pass
    existing = rest.select_single("students", select="id,full_name,created_at", params={"full_name": f"eq.{full_name}"})
    if not existing:
        raise RuntimeError("Could not create or fetch student.")
    return existing

def create_listening_session(
    *,
    student_id: str,
    mode: str,
    surah_id: Optional[int],
    page_number: Optional[int],
) -> Dict[str, Any]:
    rest = get_rest()
    if rest is None:
        raise RuntimeError("Supabase is not configured. Set SUPABASE_URL and SUPABASE_KEY in Streamlit secrets.")

    payload: Dict[str, Any] = {
        "student_id": student_id,
        "activity_date": today_iso(),
        "mode": mode,
        "surah_id": surah_id,
        "page_number": page_number,
        "created_at": now_utc_iso(),
    }
    res = rest.insert("listening_sessions", [payload])
    return res[0]


def get_recent_listening_session(
    *,
    student_id: str,
    mode: str,
    surah_id: Optional[int],
    page_number: Optional[int],
) -> Optional[Dict[str, Any]]:
    rest = get_rest()
    if rest is None:
        return None

    params = {
        "student_id": f"eq.{student_id}",
        "mode": f"eq.{mode}",
        "activity_date": f"eq.{today_iso()}",
    }
    if surah_id is not None:
        params["surah_id"] = f"eq.{surah_id}"
    else:
        params["surah_id"] = "is.null"

    if page_number is not None:
        params["page_number"] = f"eq.{page_number}"
    else:
        params["page_number"] = "is.null"

    params["order"] = "created_at.desc"
    params["limit"] = "1"

    rows = rest.select("listening_sessions", select="id,created_at", params=params)
    if rows:
        return rows[0]
    return None


def get_today_listening_sessions(*, student_id: str) -> List[Dict[str, Any]]:
    rest = get_rest()
    if rest is None:
        return []
    params = {
        "student_id": f"eq.{student_id}",
        "activity_date": f"eq.{today_iso()}",
        "order": "created_at.desc"
    }
    return rest.select("listening_sessions", select="id,mode,surah_id,page_number", params=params)


# Global variable to cache which columns are supported by the database
_db_supported_columns: set[str] | None = None

MAKHARIJ_COLS = [
    "makhraj_alif", "makhraj_baa", "makhraj_taa", "makhraj_thaa", "makhraj_jeem",
    "makhraj_haa", "makhraj_khaa", "makhraj_daal", "makhraj_thaal", "makhraj_raa",
    "makhraj_zaa", "makhraj_seen", "makhraj_sheen", "makhraj_saad", "makhraj_daad",
    "makhraj_taa_thick", "makhraj_zaa_thick", "makhraj_ain", "makhraj_ghain",
    "makhraj_faa", "makhraj_qaaf", "makhraj_kaaf", "makhraj_laam", "makhraj_meem",
    "makhraj_noon", "makhraj_haa_weak", "makhraj_waw", "makhraj_yaa"
]

def get_session_counts(session_id: str) -> Dict[str, int]:
    global _db_supported_columns
    rest = get_rest()
    if rest is None:
        raise RuntimeError("Supabase is not configured.")
    row = rest.select_single(
        "mistake_counts",
        select="*",
        params={"session_id": f"eq.{session_id}"},
    )
    
    if row:
        _db_supported_columns = set(row.keys())

    if not row:
        # initialize counts row
        init = {
            "session_id": session_id,
            "talqeen": 0,
            "tanbeeh": 0,
            "repeat_mistake": 0,
            "mutashabehat": 0,
            "irab": 0,
            "updated_at": now_utc_iso(),
        }
        rest.insert("mistake_counts", [init], returning="minimal")
        res = {
            "talqeen": 0,
            "tanbeeh": 0,
            "repeat_mistake": 0,
            "mutashabehat": 0,
            "irab": 0,
            "awakhir_ul_ayat": 0,
            "irab_talqeen": 0,
            "irab_tanbeeh": 0,
            "repeat_mistake_talqeen": 0,
            "repeat_mistake_tanbeeh": 0,
            "mutashabehat_talqeen": 0,
            "mutashabehat_tanbeeh": 0,
            "awakhir_ul_ayat_talqeen": 0,
            "awakhir_ul_ayat_tanbeeh": 0,
            "ikhfa": 0,
            "izhaar": 0,
            "qalqalah": 0,
            "ism_jalalah": 0,
            "tahreek_sakin": 0,
            "gunnah": 0,
            "idgham": 0,
            "madd_lazim": 0,
            "madd_muttasil": 0,
            "mad_tabaiee": 0,
            "ikhfa_shafawi": 0,
            "iqlab": 0,
        }
        for col in MAKHARIJ_COLS:
            res[col] = 0
        return res

    res = {
        "talqeen": int(row.get("talqeen", 0) or 0),
        "tanbeeh": int(row.get("tanbeeh", 0) or 0),
        "repeat_mistake": int(row.get("repeat_mistake", 0) or 0),
        "mutashabehat": int(row.get("mutashabehat", 0) or 0),
        "irab": int(row.get("irab", 0) or 0),
        "awakhir_ul_ayat": int(row.get("awakhir_ul_ayat", 0) or 0),
        "irab_talqeen": int(row.get("irab_talqeen", 0) or 0),
        "irab_tanbeeh": int(row.get("irab_tanbeeh", 0) or 0),
        "repeat_mistake_talqeen": int(row.get("repeat_mistake_talqeen", 0) or 0),
        "repeat_mistake_tanbeeh": int(row.get("repeat_mistake_tanbeeh", 0) or 0),
        "mutashabehat_talqeen": int(row.get("mutashabehat_talqeen", 0) or 0),
        "mutashabehat_tanbeeh": int(row.get("mutashabehat_tanbeeh", 0) or 0),
        "awakhir_ul_ayat_talqeen": int(row.get("awakhir_ul_ayat_talqeen", 0) or 0),
        "awakhir_ul_ayat_tanbeeh": int(row.get("awakhir_ul_ayat_tanbeeh", 0) or 0),
        "ikhfa": int(row.get("ikhfa", 0) or 0),
        "izhaar": int(row.get("izhaar", 0) or 0),
        "qalqalah": int(row.get("qalqalah", 0) or 0),
        "ism_jalalah": int(row.get("ism_jalalah", 0) or 0),
        "tahreek_sakin": int(row.get("tahreek_sakin", 0) or 0),
        "gunnah": int(row.get("gunnah", 0) or 0),
        "idgham": int(row.get("idgham", 0) or 0),
        "madd_lazim": int(row.get("madd_lazim", 0) or 0),
        "madd_muttasil": int(row.get("madd_muttasil", 0) or 0),
        "mad_tabaiee": int(row.get("mad_tabaiee", 0) or 0),
        "ikhfa_shafawi": int(row.get("ikhfa_shafawi", 0) or 0),
        "iqlab": int(row.get("iqlab", 0) or 0),
    }
    for col in MAKHARIJ_COLS:
        res[col] = int(row.get(col, 0) or 0)
    return res


def increment_mistake(session_id: str, kind: str) -> Dict[str, int]:
    """
    Business rules:
    - talqeen/tanbeeh increments talqeen/tanbeeh respectively
    - secondary mistakes (repeat, mutashabehat, irab, awakhir_ul_ayat) are partitioned into Talqeen or Tanbeeh clicks:
      - talqeen variant increments the specific Talqeen category counter, the aggregate category counter, and global Talqeen
      - tanbeeh variant increments the specific Tanbeeh category counter, the aggregate category counter, and global Tanbeeh
    - Ahkam mistakes (ikhfa, izhaar, etc.) only increment themselves.
    """
    counts = get_session_counts(session_id)

    if kind == "talqeen":
        counts["talqeen"] += 1
    elif kind == "tanbeeh":
        counts["tanbeeh"] += 1
        
    elif kind in ("irab", "irab_talqeen"):
        counts["irab_talqeen"] = counts.get("irab_talqeen", 0) + 1
        counts["irab"] = counts.get("irab", 0) + 1
        counts["talqeen"] += 1
    elif kind == "irab_tanbeeh":
        counts["irab_tanbeeh"] = counts.get("irab_tanbeeh", 0) + 1
        counts["irab"] = counts.get("irab", 0) + 1
        counts["tanbeeh"] += 1
        
    elif kind in ("repeat_mistake", "repeat_mistake_talqeen"):
        counts["repeat_mistake_talqeen"] = counts.get("repeat_mistake_talqeen", 0) + 1
        counts["repeat_mistake"] = counts.get("repeat_mistake", 0) + 1
        counts["talqeen"] += 1
    elif kind == "repeat_mistake_tanbeeh":
        counts["repeat_mistake_tanbeeh"] = counts.get("repeat_mistake_tanbeeh", 0) + 1
        counts["repeat_mistake"] = counts.get("repeat_mistake", 0) + 1
        counts["tanbeeh"] += 1
        
    elif kind in ("mutashabehat", "mutashabehat_talqeen"):
        counts["mutashabehat_talqeen"] = counts.get("mutashabehat_talqeen", 0) + 1
        counts["mutashabehat"] = counts.get("mutashabehat", 0) + 1
        counts["talqeen"] += 1
    elif kind == "mutashabehat_tanbeeh":
        counts["mutashabehat_tanbeeh"] = counts.get("mutashabehat_tanbeeh", 0) + 1
        counts["mutashabehat"] = counts.get("mutashabehat", 0) + 1
        counts["tanbeeh"] += 1
        
    elif kind in ("awakhir_ul_ayat", "awakhir_ul_ayat_talqeen"):
        counts["awakhir_ul_ayat_talqeen"] = counts.get("awakhir_ul_ayat_talqeen", 0) + 1
        counts["awakhir_ul_ayat"] = counts.get("awakhir_ul_ayat", 0) + 1
        counts["talqeen"] += 1
    elif kind == "awakhir_ul_ayat_tanbeeh":
        counts["awakhir_ul_ayat_tanbeeh"] = counts.get("awakhir_ul_ayat_tanbeeh", 0) + 1
        counts["awakhir_ul_ayat"] = counts.get("awakhir_ul_ayat", 0) + 1
        counts["tanbeeh"] += 1
        
    elif kind in ("ikhfa", "izhaar", "qalqalah", "ism_jalalah", "tahreek_sakin", "gunnah", "idgham", "madd_lazim", "madd_muttasil", "mad_tabaiee", "ikhfa_shafawi", "iqlab"):
        counts[kind] = counts.get(kind, 0) + 1
    elif kind in MAKHARIJ_COLS:
        counts[kind] = 1 if counts.get(kind, 0) == 0 else 0
    else:
        raise ValueError(f"Unknown kind: {kind}")

    rest = get_rest()
    if rest is None:
        raise RuntimeError("Supabase is not configured.")

    patch = {
        "talqeen": counts["talqeen"],
        "tanbeeh": counts["tanbeeh"],
        "repeat_mistake": counts["repeat_mistake"],
        "mutashabehat": counts["mutashabehat"],
        "irab": counts["irab"],
        "updated_at": now_utc_iso(),
    }
    
    new_cols = [
        "awakhir_ul_ayat",
        "irab_talqeen",
        "irab_tanbeeh",
        "repeat_mistake_talqeen",
        "repeat_mistake_tanbeeh",
        "mutashabehat_talqeen",
        "mutashabehat_tanbeeh",
        "awakhir_ul_ayat_talqeen",
        "awakhir_ul_ayat_tanbeeh",
        "ikhfa",
        "izhaar",
        "qalqalah",
        "ism_jalalah",
        "tahreek_sakin",
        "gunnah",
        "idgham",
        "madd_lazim",
        "madd_muttasil",
        "mad_tabaiee",
        "ikhfa_shafawi",
        "iqlab",
    ] + MAKHARIJ_COLS
    for col in new_cols:
        if _db_supported_columns and col in _db_supported_columns:
            patch[col] = counts.get(col, 0)

    rest.update(
        "mistake_counts",
        match={"session_id": session_id},
        patch=patch,
    )

    rest.insert(
        "mistake_events",
        [{"session_id": session_id, "kind": kind}],
        returning="minimal",
    )

    return counts


def increment_mistake_bg(session_id: str, kind: str, counts: Dict[str, int]) -> None:
    rest = get_rest()
    if rest is None:
        return
    t = threading.Thread(target=_bg_update_mistake, args=(rest, session_id, kind, counts.copy()))
    t.daemon = True
    t.start()


def _bg_update_mistake(rest: SupabaseRest, session_id: str, kind: str, counts: Dict[str, int]) -> None:
    try:
        patch = {
            "talqeen": counts["talqeen"],
            "tanbeeh": counts["tanbeeh"],
            "repeat_mistake": counts["repeat_mistake"],
            "mutashabehat": counts["mutashabehat"],
            "irab": counts["irab"],
            "updated_at": now_utc_iso(),
        }
        
        new_cols = [
            "awakhir_ul_ayat",
            "irab_talqeen",
            "irab_tanbeeh",
            "repeat_mistake_talqeen",
            "repeat_mistake_tanbeeh",
            "mutashabehat_talqeen",
            "mutashabehat_tanbeeh",
            "awakhir_ul_ayat_talqeen",
            "awakhir_ul_ayat_tanbeeh",
            "ikhfa",
            "izhaar",
            "qalqalah",
            "ism_jalalah",
            "tahreek_sakin",
            "gunnah",
            "idgham",
            "madd_lazim",
            "madd_muttasil",
            "mad_tabaiee",
            "ikhfa_shafawi",
            "iqlab",
        ] + MAKHARIJ_COLS
        for col in new_cols:
            if _db_supported_columns and col in _db_supported_columns:
                patch[col] = counts.get(col, 0)

        rest.update(
            "mistake_counts",
            match={"session_id": session_id},
            patch=patch,
        )
        rest.insert(
            "mistake_events",
            [{"session_id": session_id, "kind": kind}],
            returning="minimal",
        )
    except Exception as e:
        import logging
        logging.error(f"Background database update error: {e}")


def insert_jadeed_rows(*, student_id: str, rows: List[Dict[str, Any]]) -> None:
    rest = get_rest()
    if rest is None:
        raise RuntimeError("Supabase is not configured.")
    # Delete existing entries for this student on this day first
    rest.delete("jadeed_entries", match={"student_id": student_id, "activity_date": today_iso()})
    
    if rows:
        for r in rows:
            r["created_at"] = now_utc_iso()
            r["student_id"] = student_id
            r["activity_date"] = today_iso()
        rest.insert("jadeed_entries", rows, returning="minimal")

    # Mark whether this student did jadeed today
    rest.upsert(
        "jadeed_daily",
        [{"student_id": student_id, "activity_date": today_iso(), "no_jadeed": not bool(rows), "updated_at": now_utc_iso()}],
        on_conflict="student_id,activity_date",
        returning="minimal",
    )


def mark_no_jadeed_today(*, student_id: str) -> None:
    rest = get_rest()
    if rest is None:
        raise RuntimeError("Supabase is not configured.")
    rest.upsert(
        "jadeed_daily",
        [{"student_id": student_id, "activity_date": today_iso(), "no_jadeed": True, "updated_at": now_utc_iso()}],
        on_conflict="student_id,activity_date",
        returning="minimal",
    )


def list_jadeed_entries(*, student_id: str, limit: int = 200) -> List[Dict[str, Any]]:
    rest = get_rest()
    if rest is None:
        raise RuntimeError("Supabase is not configured.")
    # Include joined surah fields for display.
    select = "id,student_id,activity_date,surah_id,page_number,ayah_number,volume,created_at,surahs(name_en,name_ar,number)"
    return rest.select(
        "jadeed_entries",
        select=select,
        params={
            "student_id": f"eq.{student_id}",
            "order": "created_at.desc",
            "limit": str(int(limit)),
        },
    )


def upsert_takhteet_today(*, student_id: str, murajat_text_raw: str, juzulhali_text_raw: str, jadeed_text_raw: str) -> None:
    rest = get_rest()
    if rest is None:
        raise RuntimeError("Supabase is not configured.")

    row = {
        "student_id": student_id,
        "activity_date": today_iso(),
        "murajat_text_raw": murajat_text_raw or "",
        "juzulhali_text_raw": juzulhali_text_raw or "",
        "jadeed_text_raw": jadeed_text_raw or "",
        "murajat_text_clean": normalize_text(murajat_text_raw),
        "juzulhali_text_clean": normalize_text(juzulhali_text_raw),
        "jadeed_text_clean": normalize_text(jadeed_text_raw),
        "updated_at": now_utc_iso(),
    }
    rest.upsert("takhteet_daily", [row], on_conflict="student_id,activity_date", returning="minimal")


def get_takhteet_today(*, student_id: str) -> Optional[Dict[str, Any]]:
    rest = get_rest()
    if rest is None:
        raise RuntimeError("Supabase is not configured.")
    return rest.select_single(
        "takhteet_daily",
        select="student_id,activity_date,murajat_text_raw,juzulhali_text_raw,jadeed_text_raw,murajat_text_clean,juzulhali_text_clean,jadeed_text_clean,updated_at",
        params={"student_id": f"eq.{student_id}", "activity_date": f"eq.{today_iso()}"},
    )


def get_previous_takhteet(*, student_id: str) -> Optional[Dict[str, Any]]:
    rest = get_rest()
    if rest is None:
        raise RuntimeError("Supabase is not configured.")
    rows = rest.select(
        "takhteet_daily",
        select="student_id,activity_date,murajat_text_raw,juzulhali_text_raw,jadeed_text_raw,murajat_text_clean,juzulhali_text_clean,jadeed_text_clean",
        params={
            "student_id": f"eq.{student_id}",
            "activity_date": f"lt.{today_iso()}",
            "order": "activity_date.desc",
            "limit": "1",
        }
    )
    if rows:
        return rows[0]
    return None


def _extract_count(value: Any) -> int:
    if isinstance(value, list):
        if not value:
            return 0
        value = value[0]
    if isinstance(value, dict):
        return int(value.get("count", 0) or 0)
    return int(value or 0)


def fetch_monthly_report(*, student_id: str, year: int, month: int) -> List[Dict[str, Any]]:
    """
    Returns date-wise structured report data for web + PDF for a specific month/year:
    [
      {
        "activity_date": "YYYY-MM-DD",
        "murajat": [...],
        "juzulhali": [...],
        "jadeed": [...],
        "no_jadeed": bool,
        "takhteet": {...}
      }
    ]
    """
    rest = get_rest()
    if rest is None:
        raise RuntimeError("Supabase is not configured.")

    import calendar
    _, last_day = calendar.monthrange(year, month)
    from_date = f"{year:04d}-{month:02d}-01"
    to_date = f"{year:04d}-{month:02d}-{last_day:02d}"

    # Sessions + counts + surah
    sessions = rest.select(
        "listening_sessions",
        select="id,activity_date,mode,surah_id,page_number,created_at,surahs(number,name_en,name_ar),mistake_counts(*)",
        params={
            "student_id": f"eq.{student_id}",
            "and": f"(activity_date.gte.{from_date},activity_date.lte.{to_date})",
            "order": "activity_date.asc,created_at.asc",
        },
    )

    jadeed_rows = rest.select(
        "jadeed_entries",
        select="id,activity_date,surah_id,page_number,ayah_number,volume,created_at,surahs(number,name_en,name_ar)",
        params={
            "student_id": f"eq.{student_id}",
            "and": f"(activity_date.gte.{from_date},activity_date.lte.{to_date})",
            "order": "activity_date.asc,created_at.asc",
        },
    )

    jadeed_daily_rows = rest.select(
        "jadeed_daily",
        select="student_id,activity_date,no_jadeed,updated_at",
        params={
            "student_id": f"eq.{student_id}",
            "and": f"(activity_date.gte.{from_date},activity_date.lte.{to_date})",
            "order": "activity_date.asc",
        },
    )

    takhteet_rows = rest.select(
        "takhteet_daily",
        select="student_id,activity_date,murajat_text_clean,juzulhali_text_clean,jadeed_text_clean,updated_at",
        params={
            "student_id": f"eq.{student_id}",
            "and": f"(activity_date.gte.{from_date},activity_date.lte.{to_date})",
            "order": "activity_date.asc",
        },
    )

    by_date: Dict[str, Dict[str, Any]] = {}
    for day in range(1, last_day + 1):
        d = f"{year:04d}-{month:02d}-{day:02d}"
        by_date[d] = {
            "activity_date": d,
            "murajat": [],
            "juzulhali": [],
            "jadeed": [],
            "no_jadeed": False,
            "takhteet": {"murajat": "", "juzulhali": "", "jadeed": ""},
        }

    for s in sessions:
        d = str(s.get("activity_date"))
        if d not in by_date:
            continue
        counts = s.get("mistake_counts") or {}
        if isinstance(counts, list):
            counts = counts[0] if counts else {}
        talqeen = int(counts.get("talqeen", 0) or 0)
        tanbeeh = int(counts.get("tanbeeh", 0) or 0)
        repeat_mistake = int(counts.get("repeat_mistake", 0) or 0)
        mutashabehat = int(counts.get("mutashabehat", 0) or 0)
        irab = int(counts.get("irab", 0) or 0)
        marks = 10.0 - (0.5 * talqeen) - (0.25 * tanbeeh)
        row = {
            "talqeen": talqeen,
            "tanbeeh": tanbeeh,
            "repeat_mistake": repeat_mistake,
            "mutashabehat": mutashabehat,
            "irab": irab,
            "marks": marks,
            # Ahkam
            "ikhfa": int(counts.get("ikhfa", 0) or 0),
            "izhaar": int(counts.get("izhaar", 0) or 0),
            "qalqalah": int(counts.get("qalqalah", 0) or 0),
            "ism_jalalah": int(counts.get("ism_jalalah", 0) or 0),
            "tahreek_sakin": int(counts.get("tahreek_sakin", 0) or 0),
            "gunnah": int(counts.get("gunnah", 0) or 0),
            "idgham": int(counts.get("idgham", 0) or 0),
            "madd_lazim": int(counts.get("madd_lazim", 0) or 0),
            "madd_muttasil": int(counts.get("madd_muttasil", 0) or 0),
            "mad_tabaiee": int(counts.get("mad_tabaiee", 0) or 0),
            "ikhfa_shafawi": int(counts.get("ikhfa_shafawi", 0) or 0),
            "iqlab": int(counts.get("iqlab", 0) or 0),
        }
        for col in MAKHARIJ_COLS:
            row[col] = int(counts.get(col, 0) or 0)
        if s.get("mode") == "murajat":
            surah = s.get("surahs") or {}
            if isinstance(surah, list):
                surah = surah[0] if surah else {}
            row["surat"] = f"{surah.get('number', '')} - {surah.get('name_en', '')}".strip(" -")
            row["surah_name_ar"] = surah.get("name_ar", "")
            row["surah_number"] = surah.get("number", "")
            by_date[d]["murajat"].append(row)
        elif s.get("mode") == "juzulhali":
            row["page_number"] = int(s.get("page_number") or 0)
            by_date[d]["juzulhali"].append(row)

    for j in jadeed_rows:
        d = str(j.get("activity_date"))
        if d not in by_date:
            continue
        surah = j.get("surahs") or {}
        if isinstance(surah, list):
            surah = surah[0] if surah else {}
        by_date[d]["jadeed"].append(
            {
                "surat": f"{surah.get('number', '')} - {surah.get('name_en', '')}".strip(" -"),
                "surah_name_ar": surah.get("name_ar", ""),
                "surah_number": surah.get("number", ""),
                "page_number": int(j.get("page_number") or 0),
                "ayah_number": int(j.get("ayah_number") or 0),
                "volume": j.get("volume") or "",
            }
        )

    for jd in jadeed_daily_rows:
        d = str(jd.get("activity_date"))
        if d in by_date:
            by_date[d]["no_jadeed"] = bool(jd.get("no_jadeed"))

    for t in takhteet_rows:
        d = str(t.get("activity_date"))
        if d in by_date:
            by_date[d]["takhteet"] = {
                "murajat": t.get("murajat_text_clean") or "",
                "juzulhali": t.get("juzulhali_text_clean") or "",
                "jadeed": t.get("jadeed_text_clean") or "",
            }

    return [by_date[k] for k in sorted(by_date.keys())]


def get_student_email(*, student_id: str) -> Optional[str]:
    rest = get_rest()
    if rest is None:
        return None
    try:
        res = rest.select_single("students", select="email", params={"id": f"eq.{student_id}"})
        if res:
            return res.get("email")
    except Exception:
        pass
    return None


def get_student_daily_summary(*, student_id: str, date_str: str) -> Dict[str, Any]:
    rest = get_rest()
    if rest is None:
        raise RuntimeError("Supabase is not configured.")

    try:
        student = rest.select_single("students", select="full_name,email", params={"id": f"eq.{student_id}"})
    except Exception:
        student = rest.select_single("students", select="full_name", params={"id": f"eq.{student_id}"})

    if not student:
        raise ValueError("Student not found.")

    sessions = rest.select(
        "listening_sessions",
        select="id,mode,surah_id,page_number,created_at,surahs(number,name_en,name_ar),mistake_counts(*)",
        params={
            "student_id": f"eq.{student_id}",
            "activity_date": f"eq.{date_str}",
            "order": "created_at.asc",
        },
    )

    jadeed_rows = rest.select(
        "jadeed_entries",
        select="id,surah_id,page_number,ayah_number,volume,created_at,surahs(number,name_en,name_ar)",
        params={
            "student_id": f"eq.{student_id}",
            "activity_date": f"eq.{date_str}",
            "order": "created_at.asc",
        },
    )

    jadeed_daily_row = None
    try:
        jadeed_daily_row = rest.select_single(
            "jadeed_daily",
            select="no_jadeed",
            params={
                "student_id": f"eq.{student_id}",
                "activity_date": f"eq.{date_str}",
            },
        )
    except Exception:
        pass

    takhteet_row = None
    try:
        takhteet_row = rest.select_single(
            "takhteet_daily",
            select="murajat_text_raw,juzulhali_text_raw,jadeed_text_raw,murajat_text_clean,juzulhali_text_clean,jadeed_text_clean",
            params={
                "student_id": f"eq.{student_id}",
                "activity_date": f"eq.{date_str}",
            },
        )
    except Exception:
        pass

    murajat_sessions = [s for s in sessions if s.get("mode") == "murajat"]
    juzulhali_sessions = [s for s in sessions if s.get("mode") == "juzulhali"]

    return {
        "student_name": student.get("full_name"),
        "student_email": student.get("email"),
        "activity_date": date_str,
        "murajat": murajat_sessions,
        "juzulhali": juzulhali_sessions,
        "jadeed": jadeed_rows,
        "no_jadeed": bool(jadeed_daily_row.get("no_jadeed")) if jadeed_daily_row else False,
        "takhteet": takhteet_row or {},
    }

