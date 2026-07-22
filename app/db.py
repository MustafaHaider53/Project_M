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


def clear_all_read_caches() -> None:
    try:
        get_today_listening_sessions.clear()
        list_jadeed_entries.clear()
        get_takhteet_today.clear()
        get_previous_takhteet.clear()
        fetch_monthly_report.clear()
        get_student_daily_summary.clear()
        get_today_jadeed_state.clear()
        get_student_current_jadeed.clear()
        get_all_students_current_jadeed.clear()
        get_student_sessions_with_counts.clear()
        get_session_counts.clear()
        calculate_student_average_pace.clear()
        get_student_position_before_month.clear()
        get_student_monthly_actuals.clear()
        get_student_email.clear()
    except Exception:
        pass


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
        clear_all_read_caches()
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
    force_new: bool = False,
) -> Dict[str, Any]:
    rest = get_rest()
    if rest is None:
        raise RuntimeError("Supabase is not configured. Set SUPABASE_URL and SUPABASE_KEY in Streamlit secrets.")

    if not force_new:
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
        
        existing = rest.select("listening_sessions", select="id,mode,surah_id,page_number,created_at", params=params)
        if existing:
            return existing[0]

    payload: Dict[str, Any] = {
        "student_id": student_id,
        "activity_date": today_iso(),
        "mode": mode,
        "surah_id": surah_id,
        "page_number": page_number,
        "created_at": now_utc_iso(),
    }
    res = rest.insert("listening_sessions", [payload])
    clear_all_read_caches()
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


@st.cache_data(show_spinner=False)
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

@st.cache_data(show_spinner=False)
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
            "is_zero_marks": False,
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
            "is_zero_marks": False,
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
        "is_zero_marks": bool(row.get("is_zero_marks", False)),
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

    if kind == "is_zero_marks":
        counts["is_zero_marks"] = not counts.get("is_zero_marks", False)
    elif kind == "talqeen":
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
        "is_zero_marks",
    ] + MAKHARIJ_COLS
    for col in new_cols:
        if _db_supported_columns and col in _db_supported_columns:
            patch[col] = counts.get(col, 0)

    rest.update(
        "mistake_counts",
        match={"session_id": session_id},
        patch=patch,
    )

    if kind != "is_zero_marks":
        rest.insert(
            "mistake_events",
            [{"session_id": session_id, "kind": kind}],
            returning="minimal",
        )

    clear_all_read_caches()
    return counts


def increment_mistake_bg(session_id: str, kind: str, counts: Dict[str, int]) -> None:
    rest = get_rest()
    if rest is None:
        return
    clear_all_read_caches()
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
            "is_zero_marks",
        ] + MAKHARIJ_COLS
        for col in new_cols:
            if _db_supported_columns and col in _db_supported_columns:
                patch[col] = counts.get(col, 0)

        rest.update(
            "mistake_counts",
            match={"session_id": session_id},
            patch=patch,
        )
        if kind != "is_zero_marks":
            rest.insert(
                "mistake_events",
                [{"session_id": session_id, "kind": kind}],
                returning="minimal",
            )
        clear_all_read_caches()
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
    clear_all_read_caches()


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
    clear_all_read_caches()


@st.cache_data(show_spinner=False)
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
            "order": "activity_date.desc,created_at.desc",
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
    clear_all_read_caches()


@st.cache_data(show_spinner=False)
def get_takhteet_today(*, student_id: str) -> Optional[Dict[str, Any]]:
    rest = get_rest()
    if rest is None:
        raise RuntimeError("Supabase is not configured.")
    return rest.select_single(
        "takhteet_daily",
        select="student_id,activity_date,murajat_text_raw,juzulhali_text_raw,jadeed_text_raw,murajat_text_clean,juzulhali_text_clean,jadeed_text_clean,updated_at",
        params={"student_id": f"eq.{student_id}", "activity_date": f"eq.{today_iso()}"},
    )


@st.cache_data(show_spinner=False)
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


@st.cache_data(show_spinner=False)
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
        counts = s.get("mistake_counts")
        if isinstance(counts, list):
            counts = counts[0] if counts else None
        if not counts:
            continue
        talqeen = int(counts.get("talqeen", 0) or 0)
        tanbeeh = int(counts.get("tanbeeh", 0) or 0)
        repeat_mistake = int(counts.get("repeat_mistake", 0) or 0)
        mutashabehat = int(counts.get("mutashabehat", 0) or 0)
        irab = int(counts.get("irab", 0) or 0)
        is_zero = bool(counts.get("is_zero_marks", False))
        if is_zero:
            marks = 0.0
        else:
            marks = 10.0 - (0.5 * talqeen) - (0.25 * tanbeeh)
            if marks < 0:
                marks = 0.0
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


@st.cache_data(show_spinner=False)
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

    valid_sessions = []
    for s in sessions:
        counts = s.get("mistake_counts")
        if isinstance(counts, list):
            counts = counts[0] if counts else None
        if counts:
            valid_sessions.append(s)

    murajat_sessions = [s for s in valid_sessions if s.get("mode") == "murajat"]
    juzulhali_sessions = [s for s in valid_sessions if s.get("mode") == "juzulhali"]

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


@st.cache_data(show_spinner=False)
def get_today_jadeed_state(*, student_id: str, date_str: str) -> Dict[str, Any]:
    rest = get_rest()
    if rest is None:
        return {"jadeed": [], "no_jadeed": False}

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

    return {
        "jadeed": jadeed_rows,
        "no_jadeed": bool(jadeed_daily_row.get("no_jadeed")) if jadeed_daily_row else False,
    }


# --- SURAH AYAH COUNTS FOR TASK PLANNER ---
SURAH_AYAH_COUNTS = {
    1: 7, 2: 286, 3: 200, 4: 176, 5: 120, 6: 165, 7: 206, 8: 75, 9: 129, 10: 109,
    11: 123, 12: 111, 13: 43, 14: 52, 15: 99, 16: 128, 17: 111, 18: 110, 19: 98, 20: 135,
    21: 112, 22: 78, 23: 118, 24: 64, 25: 77, 26: 227, 27: 93, 28: 88, 29: 69, 30: 60,
    31: 34, 32: 30, 33: 73, 34: 54, 35: 45, 36: 83, 37: 182, 38: 88, 39: 75, 40: 85,
    41: 54, 42: 53, 43: 89, 44: 59, 45: 37, 46: 35, 47: 38, 48: 29, 49: 18, 50: 45,
    51: 60, 52: 49, 53: 62, 54: 55, 55: 78, 56: 96, 57: 29, 58: 22, 59: 24, 60: 13,
    61: 14, 62: 11, 63: 11, 64: 18, 65: 12, 66: 12, 67: 30, 68: 52, 69: 52, 70: 44,
    71: 28, 72: 28, 73: 20, 74: 56, 75: 40, 76: 31, 77: 50, 78: 40, 79: 46, 80: 42,
    81: 29, 82: 19, 83: 36, 84: 25, 85: 22, 86: 17, 87: 19, 88: 26, 89: 30, 90: 20,
    91: 15, 92: 21, 93: 11, 94: 8, 95: 8, 96: 19, 97: 5, 98: 8, 99: 8, 100: 11,
    101: 11, 102: 8, 103: 3, 104: 9, 105: 5, 106: 4, 107: 7, 108: 3, 109: 6, 110: 3,
    111: 5, 112: 4, 113: 5, 114: 6
}


@st.cache_data(show_spinner=False)
def get_student_current_jadeed(*, student_id: str) -> Optional[Dict[str, Any]]:
    rest = get_rest()
    if rest is None:
        return None
    
    select = "id,student_id,activity_date,surah_id,page_number,ayah_number,volume,created_at,surahs(name_en,name_ar,number)"
    rows = rest.select(
        "jadeed_entries",
        select=select,
        params={
            "student_id": f"eq.{student_id}",
            "order": "activity_date.desc,created_at.desc",
            "limit": "1",
        },
    )
    latest_entry = rows[0] if rows else None

    latest_daily_no = None
    try:
        daily_rows = rest.select(
            "jadeed_daily",
            select="activity_date,no_jadeed",
            params={
                "student_id": f"eq.{student_id}",
                "no_jadeed": "eq.true",
                "order": "activity_date.desc",
                "limit": "1"
            }
        )
        if daily_rows:
            latest_daily_no = daily_rows[0]
    except Exception:
        pass

    entry_date = latest_entry["activity_date"] if latest_entry else None
    daily_date = latest_daily_no["activity_date"] if latest_daily_no else None

    if entry_date and (not daily_date or entry_date >= daily_date):
        return latest_entry
    elif latest_daily_no:
        return {
            "no_jadeed": True,
            "activity_date": daily_date
        }
    return None


@st.cache_data(show_spinner=False)
def get_all_students_current_jadeed() -> List[Dict[str, Any]]:
    rest = get_rest()
    if rest is None:
        return []
    
    students = rest.select("students", select="id,full_name", params={"order": "full_name.asc"})
    if not students:
        return []

    entries = rest.select(
        "jadeed_entries",
        select="student_id,activity_date,surah_id,page_number,ayah_number,volume,created_at,surahs(name_en,name_ar,number)",
        params={"order": "activity_date.desc,created_at.desc"}
    )
    
    daily = rest.select(
        "jadeed_daily",
        select="student_id,activity_date,no_jadeed",
        params={"no_jadeed": "eq.true", "order": "activity_date.desc"}
    )
    
    entries_by_student = defaultdict(list)
    for e in entries:
        entries_by_student[e["student_id"]].append(e)
        
    daily_by_student = defaultdict(list)
    for d in daily:
        daily_by_student[d["student_id"]].append(d)
        
    result = []
    for s in students:
        s_id = s["id"]
        s_name = s["full_name"]
        
        s_entries = entries_by_student.get(s_id, [])
        s_daily = daily_by_student.get(s_id, [])
        
        latest_entry = s_entries[0] if s_entries else None
        latest_daily_no = s_daily[0] if s_daily else None
        
        current_status = "None recorded"
        last_date = "N/A"
        surah_display = "-"
        page_num = "-"
        ayah_num = "-"
        volume_val = "-"
        is_no_jadeed = False
        
        entry_date = latest_entry["activity_date"] if latest_entry else None
        daily_date = latest_daily_no["activity_date"] if latest_daily_no else None
        
        if entry_date and (not daily_date or entry_date >= daily_date):
            surah = latest_entry.get("surahs") or {}
            if isinstance(surah, list):
                surah = surah[0] if surah else {}
            surah_name = surah.get("name_en", "?")
            surah_ar = surah.get("name_ar", "")
            surah_num = surah.get("number", "?")
            surah_display = f"{surah_num} - {surah_name} ({surah_ar})"
            page_num = str(latest_entry.get("page_number", "-"))
            ayah_num = str(latest_entry.get("ayah_number", "-"))
            volume_val = latest_entry.get("volume", "-")
            last_date = entry_date
            current_status = "Active"
        elif daily_date:
            last_date = daily_date
            current_status = "Marked 'No Jadeed'"
            is_no_jadeed = True
            
        result.append({
            "student_id": s_id,
            "student_name": s_name,
            "last_date": last_date,
            "surah": surah_display,
            "page": page_num,
            "ayah": ayah_num,
            "volume": volume_val,
            "status": current_status,
            "is_no_jadeed": is_no_jadeed
        })
        
    return result


@st.cache_data(show_spinner=False)
def calculate_student_average_pace(*, student_id: str) -> float:
    rest = get_rest()
    if rest is None:
        return 5.0
    
    rows = rest.select(
        "jadeed_entries",
        select="activity_date,surah_id,ayah_number,created_at,surahs(number)",
        params={
            "student_id": f"eq.{student_id}",
            "order": "activity_date.asc,created_at.asc"
        }
    )
    if len(rows) < 2:
        return 5.0
    
    differences = []
    for i in range(1, len(rows)):
        prev = rows[i-1]
        curr = rows[i]
        
        p_surah_info = prev.get("surahs") or {}
        if isinstance(p_surah_info, list): p_surah_info = p_surah_info[0] if p_surah_info else {}
        p_surah = int(p_surah_info.get("number") or prev.get("surah_id") or 1)
        
        c_surah_info = curr.get("surahs") or {}
        if isinstance(c_surah_info, list): c_surah_info = c_surah_info[0] if c_surah_info else {}
        c_surah = int(c_surah_info.get("number") or curr.get("surah_id") or 1)
        
        p_ayah = int(prev.get("ayah_number") or 1)
        c_ayah = int(curr.get("ayah_number") or 1)
        
        if c_surah == p_surah:
            diff = c_ayah - p_ayah
            if diff > 0:
                differences.append(diff)
        elif c_surah < p_surah: # progress to lower Surah number (backward hifz direction)
            diff = SURAH_AYAH_COUNTS.get(p_surah, 7) - p_ayah
            for s in range(c_surah + 1, p_surah):
                diff += SURAH_AYAH_COUNTS.get(s, 0)
            diff += c_ayah
            if diff > 0:
                differences.append(diff)
        else:
            # went to higher Surah number, could be revision or restarting
            if c_ayah > 0:
                differences.append(c_ayah)
                
    if not differences:
        return 5.0
    return sum(differences) / len(differences)


@st.cache_data(show_spinner=False)
def get_student_position_before_month(*, student_id: str, year: int, month: int) -> Optional[Dict[str, Any]]:
    rest = get_rest()
    if rest is None:
        return None
    
    first_of_month = f"{year:04d}-{month:02d}-01"
    rows = rest.select(
        "jadeed_entries",
        select="id,surah_id,page_number,ayah_number,volume,activity_date,surahs(number,name_en,name_ar)",
        params={
            "student_id": f"eq.{student_id}",
            "activity_date": f"lt.{first_of_month}",
            "order": "activity_date.desc,created_at.desc",
            "limit": "1"
        }
    )
    return rows[0] if rows else None


@st.cache_data(show_spinner=False)
def get_student_monthly_actuals(*, student_id: str, year: int, month: int) -> List[Dict[str, Any]]:
    rest = get_rest()
    if rest is None:
        return []
    
    import calendar
    _, last_day = calendar.monthrange(year, month)
    start_date = f"{year:04d}-{month:02d}-01"
    end_date = f"{year:04d}-{month:02d}-{last_day:02d}"
    
    # Range query in PostgREST using "and" logic
    rows = rest.select(
        "jadeed_entries",
        select="activity_date,surah_id,page_number,ayah_number,volume,surahs(number,name_en,name_ar)",
        params={
            "student_id": f"eq.{student_id}",
            "and": f"(activity_date.gte.{start_date},activity_date.lte.{end_date})",
            "order": "activity_date.asc,created_at.asc"
        }
    )
    return rows


@st.cache_data(show_spinner=False)
def get_student_email(*, student_id: str) -> Optional[str]:
    rest = get_rest()
    if rest is None:
        return None
    try:
        student = rest.select_single("students", select="email", params={"id": f"eq.{student_id}"})
        return student.get("email") if student else None
    except Exception:
        return None


@st.cache_data(show_spinner=False)
def get_student_sessions_with_counts(*, student_id: str) -> List[Dict[str, Any]]:
    rest = get_rest()
    if rest is None:
        return []
    sessions = rest.select(
        "listening_sessions",
        select="id,activity_date,mode,surah_id,page_number,created_at,surahs(number,name_en,name_ar),mistake_counts(*)",
        params={
            "student_id": f"eq.{student_id}",
            "order": "activity_date.desc,created_at.desc",
        },
    )
    valid_sessions = []
    for s in sessions:
        counts = s.get("mistake_counts")
        if isinstance(counts, list):
            counts = counts[0] if counts else None
        if counts:
            valid_sessions.append(s)
    return valid_sessions


@st.cache_data(show_spinner=False)
def fetch_collective_attendance_report(*, year: int, month: int) -> Dict[str, Any]:
    """
    Fetches attendance and session summary for all students in a given month.
    """
    rest = get_rest()
    if rest is None:
        raise RuntimeError("Supabase is not configured.")

    students = list_students()
    if not students:
        return {"students": [], "days": [], "year": year, "month": month}

    import calendar
    _, last_day = calendar.monthrange(year, month)
    from_date = f"{year:04d}-{month:02d}-01"
    to_date = f"{year:04d}-{month:02d}-{last_day:02d}"

    # Query all records for the month in batch queries
    sessions = rest.select(
        "listening_sessions",
        select="student_id,activity_date,mode,surah_id,page_number,surahs(name_en,name_ar,number),mistake_counts(*)",
        params={
            "and": f"(activity_date.gte.{from_date},activity_date.lte.{to_date})",
        }
    )

    jadeed_rows = rest.select(
        "jadeed_entries",
        select="student_id,activity_date,surah_id,page_number,ayah_number,volume,surahs(name_en,name_ar,number)",
        params={
            "and": f"(activity_date.gte.{from_date},activity_date.lte.{to_date})",
        }
    )

    jadeed_daily_rows = rest.select(
        "jadeed_daily",
        select="student_id,activity_date,no_jadeed",
        params={
            "and": f"(activity_date.gte.{from_date},activity_date.lte.{to_date})",
        }
    )

    takhteet_rows = rest.select(
        "takhteet_daily",
        select="student_id,activity_date,murajat_text_clean,juzulhali_text_clean,jadeed_text_clean",
        params={
            "and": f"(activity_date.gte.{from_date},activity_date.lte.{to_date})",
        }
    )

    # Organize by student and date
    by_student_date = {}
    for s in students:
        s_id = s["id"]
        by_student_date[s_id] = {}
        for day in range(1, last_day + 1):
            d_str = f"{year:04d}-{month:02d}-{day:02d}"
            by_student_date[s_id][d_str] = {
                "activity_date": d_str,
                "murajat": [],
                "juzulhali": [],
                "jadeed": [],
                "no_jadeed": False,
                "takhteet": {"murajat": "", "juzulhali": "", "jadeed": ""},
            }

    for s in sessions:
        s_id = s.get("student_id")
        d = str(s.get("activity_date"))
        if s_id not in by_student_date or d not in by_student_date[s_id]:
            continue
        counts = s.get("mistake_counts")
        if isinstance(counts, list):
            counts = counts[0] if counts else None
        if not counts:
            continue
        talqeen = int(counts.get("talqeen", 0) or 0)
        tanbeeh = int(counts.get("tanbeeh", 0) or 0)
        is_zero = bool(counts.get("is_zero_marks", False))
        if is_zero:
            marks = 0.0
        else:
            marks = 10.0 - (0.5 * talqeen) - (0.25 * tanbeeh)
            if marks < 0:
                marks = 0.0
        
        row = {
            "mode": s.get("mode"),
            "marks": marks,
        }
        surah = s.get("surahs") or {}
        if isinstance(surah, list):
            surah = surah[0] if surah else {}
        surah_name = surah.get("name_en", "")
        
        if s.get("mode") == "murajat":
            row["surat"] = surah_name
            by_student_date[s_id][d]["murajat"].append(row)
        elif s.get("mode") == "juzulhali":
            row["page_number"] = int(s.get("page_number") or 0)
            by_student_date[s_id][d]["juzulhali"].append(row)

    for j in jadeed_rows:
        s_id = j.get("student_id")
        d = str(j.get("activity_date"))
        if s_id not in by_student_date or d not in by_student_date[s_id]:
            continue
        surah = j.get("surahs") or {}
        if isinstance(surah, list):
            surah = surah[0] if surah else {}
        by_student_date[s_id][d]["jadeed"].append({
            "surat": surah.get("name_en", ""),
            "page_number": int(j.get("page_number") or 0),
            "ayah_number": int(j.get("ayah_number") or 0),
            "volume": j.get("volume") or "",
        })

    for jd in jadeed_daily_rows:
        s_id = jd.get("student_id")
        d = str(jd.get("activity_date"))
        if s_id in by_student_date and d in by_student_date[s_id]:
            by_student_date[s_id][d]["no_jadeed"] = bool(jd.get("no_jadeed"))

    for t in takhteet_rows:
        s_id = t.get("student_id")
        d = str(t.get("activity_date"))
        if s_id in by_student_date and d in by_student_date[s_id]:
            by_student_date[s_id][d]["takhteet"] = {
                "murajat": t.get("murajat_text_clean") or "",
                "juzulhali": t.get("juzulhali_text_clean") or "",
                "jadeed": t.get("jadeed_text_clean") or "",
            }

    today_str = date.today().isoformat()
    students_list = []
    
    for s in students:
        s_id = s["id"]
        s_name = s["full_name"]
        
        attendance_map = {}
        weekday_present = 0
        weekday_absent = 0
        extra_weekend_present = 0
        
        for day in range(1, last_day + 1):
            d_str = f"{year:04d}-{month:02d}-{day:02d}"
            day_data = by_student_date[s_id][d_str]
            
            try:
                dt = datetime.strptime(d_str, "%Y-%m-%d")
                wd = dt.weekday()
            except Exception:
                wd = 0
            is_weekend = wd in (5, 6)
            
            murajat = day_data["murajat"]
            juzulhali = day_data["juzulhali"]
            jadeed = day_data["jadeed"]
            no_jadeed = day_data["no_jadeed"]
            is_present = bool(
                murajat
                or juzulhali
                or jadeed
                or no_jadeed
                or takhteet.get("murajat", "").strip()
                or takhteet.get("juzulhali", "").strip()
                or takhteet.get("jadeed", "").strip()
            )
            
            status = "Future"
            details = []
            
            if is_present:
                status = "Present"
                if is_weekend:
                    extra_weekend_present += 1
                else:
                    weekday_present += 1
                
                # Build details
                for m in murajat:
                    details.append(f"Murajat: {m['surat']} ({m['marks']:.1f}/10)")
                for jh in juzulhali:
                    details.append(f"Juzulhali: Page {jh['page_number']} ({jh['marks']:.1f}/10)")
                for jd in jadeed:
                    details.append(f"Jadeed: {jd['surat']} (Pg {jd['page_number']}, Ayah {jd['ayah_number']}, {jd['volume']})")
                if no_jadeed and not jadeed:
                    details.append("No Jadeed Lesson today")
                
                t_mur = takhteet.get("murajat", "").strip()
                t_juz = takhteet.get("juzulhali", "").strip()
                t_jad = takhteet.get("jadeed", "").strip()
                if t_mur or t_juz or t_jad:
                    details.append(f"Takhteet HW: M={t_mur or '-'}, J={t_juz or '-'}, JD={t_jad or '-'}")
            else:
                if d_str <= today_str:
                    if is_weekend:
                        status = "Weekend"
                        details.append("Weekend - No Session")
                    else:
                        status = "Absent"
                        weekday_absent += 1
                        details.append("Absent - No Activity")
                else:
                    status = "Future"
                    details.append("Future Date")
            
            attendance_map[d_str] = {
                "status": status,
                "details": " | ".join(details)
            }
            
        school_days = weekday_present + weekday_absent
        attendance_rate = (weekday_present / school_days * 100) if school_days > 0 else 100.0
        
        students_list.append({
            "id": s_id,
            "full_name": s_name,
            "attendance": attendance_map,
            "stats": {
                "school_days": school_days,
                "present_days": weekday_present,
                "absent_days": weekday_absent,
                "extra_weekend_days": extra_weekend_present,
                "attendance_rate": attendance_rate
            }
        })
        
    days_list = [f"{year:04d}-{month:02d}-{day:02d}" for day in range(1, last_day + 1)]
    return {
        "students": students_list,
        "days": days_list,
        "year": year,
        "month": month
    }


@st.cache_data(show_spinner=False)
def get_earliest_global_activity_date() -> str:
    """
    Returns the oldest activity_date from listening_sessions or jadeed_entries.
    Defaults to 2025-01-01 if none found.
    """
    rest = get_rest()
    if rest is None:
        return "2025-01-01"
    
    try:
        # Check listening sessions
        sessions = rest.select(
            "listening_sessions",
            select="activity_date",
            params={"order": "activity_date.asc", "limit": "1"}
        )
        if sessions:
            return str(sessions[0]["activity_date"])
    except Exception:
        pass
        
    try:
        # Check jadeed entries
        jadeed = rest.select(
            "jadeed_entries",
            select="activity_date",
            params={"order": "activity_date.asc", "limit": "1"}
        )
        if jadeed:
            return str(jadeed[0]["activity_date"])
    except Exception:
        pass
        
    return "2025-01-01"


@st.cache_data(show_spinner=False)
def fetch_ikhtebar_report(*, from_date: str, to_date: str) -> Dict[str, Any]:
    """
    Returns collective data for all students in a date range for the Ikhtebar/Assessment report.
    """
    import concurrent.futures
    rest = get_rest()
    if rest is None:
        raise RuntimeError("Supabase is not configured.")

    def fetch_students():
        return rest.select("students", select="id,full_name", params={"order": "full_name.asc"})

    def fetch_jadeed():
        return rest.select(
            "jadeed_entries",
            select="student_id,activity_date,page_number,ayah_number,volume,created_at,surahs(number,name_en,name_ar)",
            params={
                "and": f"(activity_date.gte.{from_date},activity_date.lte.{to_date})",
                "order": "activity_date.asc,created_at.asc"
            }
        )

    def fetch_sessions():
        session_rows = rest.select(
            "listening_sessions",
            select="student_id,activity_date,mode,page_number,surah_id,created_at,mistake_counts(talqeen,tanbeeh,is_zero_marks)",
            params={
                "and": f"(activity_date.gte.{from_date},activity_date.lte.{to_date})",
                "order": "activity_date.asc"
            }
        )
        valid_rows = []
        for s in session_rows:
            counts = s.get("mistake_counts")
            if isinstance(counts, list):
                counts = counts[0] if counts else None
            if not counts:
                continue
            talqeen = int(counts.get("talqeen", 0) or 0)
            tanbeeh = int(counts.get("tanbeeh", 0) or 0)
            is_zero = bool(counts.get("is_zero_marks", False))
            if is_zero:
                marks = 0.0
            else:
                marks = 10.0 - (0.5 * talqeen) - (0.25 * tanbeeh)
                if marks < 0:
                    marks = 0.0
            s["marks"] = marks
        return session_rows

    def fetch_jadeed_daily():
        return rest.select(
            "jadeed_daily",
            select="student_id,activity_date,no_jadeed",
            params={
                "and": f"(activity_date.gte.{from_date},activity_date.lte.{to_date})",
                "order": "activity_date.asc"
            }
        )

    def fetch_takhteet():
        return rest.select(
            "takhteet_daily",
            select="student_id,activity_date,murajat_text_clean,juzulhali_text_clean,jadeed_text_clean",
            params={
                "and": f"(activity_date.gte.{from_date},activity_date.lte.{to_date})",
                "order": "activity_date.asc"
            }
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_students = executor.submit(fetch_students)
        future_jadeed = executor.submit(fetch_jadeed)
        future_sessions = executor.submit(fetch_sessions)
        future_jadeed_daily = executor.submit(fetch_jadeed_daily)
        future_takhteet = executor.submit(fetch_takhteet)

        students = future_students.result()
        jadeed_rows = future_jadeed.result()
        session_rows = future_sessions.result()
        jadeed_daily_rows = future_jadeed_daily.result()
        takhteet_rows = future_takhteet.result()

    return {
        "students": students,
        "jadeed": jadeed_rows,
        "sessions": session_rows,
        "jadeed_daily": jadeed_daily_rows,
        "takhteet": takhteet_rows,
        "from_date": from_date,
        "to_date": to_date
    }








