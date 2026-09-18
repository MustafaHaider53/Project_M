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
        list_jadeed_mistake_history.clear()
        get_takhteet_today.clear()
        get_previous_takhteet.clear()
        fetch_monthly_report.clear()
        get_student_daily_summary.clear()
        get_today_jadeed_state.clear()
        get_student_current_jadeed.clear()
        get_all_students_current_jadeed.clear()
        get_student_sessions_with_counts.clear()
        get_session_counts.clear()
        get_student_page_listening_history.clear()
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
    return rest.select("students", select="id,full_name,created_at,email", params={"order": "full_name.asc"})


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

MUSAID_COLS = [
    "musaid_end_part", "musaid_beg_part", "musaid_ayat_after_ayat",
    "musaid_page_after_page", "musaid_no_image", "musaid_lehen"
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
        for col in MUSAID_COLS:
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
    for col in MUSAID_COLS:
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


def update_session_duration(session_id: str, duration_seconds: int, time_exceeded: bool = False) -> None:
    rest = get_rest()
    if rest is None or not session_id:
        return
    def _bg_update():
        try:
            rest.update("listening_sessions", match={"id": session_id}, patch={
                "duration_seconds": int(duration_seconds),
                "time_exceeded": bool(time_exceeded),
            })
            clear_all_read_caches()
        except Exception:
            pass
    t = threading.Thread(target=_bg_update)
    t.daemon = True
    t.start()


def increment_mistake_bg(session_id: str, kind: str, counts: Dict[str, int], duration_seconds: int = 0, time_exceeded: bool = False) -> None:
    rest = get_rest()
    if rest is None:
        return
    clear_all_read_caches()
    t = threading.Thread(target=_bg_update_mistake, args=(rest, session_id, kind, counts.copy(), duration_seconds, time_exceeded))
    t.daemon = True
    t.start()


def _bg_update_mistake(rest: SupabaseRest, session_id: str, kind: str, counts: Dict[str, int], duration_seconds: int = 0, time_exceeded: bool = False) -> None:
    global _db_supported_columns
    try:
        if duration_seconds and int(duration_seconds) > 0:
            try:
                rest.update("listening_sessions", match={"id": session_id}, patch={
                    "duration_seconds": int(duration_seconds),
                    "time_exceeded": bool(time_exceeded),
                })
            except Exception:
                pass

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
        ] + MAKHARIJ_COLS + MUSAID_COLS
        
        if not _db_supported_columns:
            all_possible_cols = {
                "session_id", "talqeen", "tanbeeh", "repeat_mistake", "mutashabehat", "irab", "updated_at",
                "awakhir_ul_ayat", "irab_talqeen", "irab_tanbeeh", "repeat_mistake_talqeen", "repeat_mistake_tanbeeh",
                "mutashabehat_talqeen", "mutashabehat_tanbeeh", "awakhir_ul_ayat_talqeen", "awakhir_ul_ayat_tanbeeh",
                "ikhfa", "izhaar", "qalqalah", "ism_jalalah", "tahreek_sakin", "gunnah", "idgham", "madd_lazim",
                "madd_muttasil", "mad_tabaiee", "ikhfa_shafawi", "iqlab", "is_zero_marks"
            } | set(MAKHARIJ_COLS) | set(MUSAID_COLS)
            _db_supported_columns = all_possible_cols

        for col in new_cols:
            if _db_supported_columns and col in _db_supported_columns:
                patch[col] = counts.get(col, 0)

        # Use upsert to handle new sessions where the mistake_counts row does not exist yet
        payload = {"session_id": session_id, **patch}
        rest.upsert(
            "mistake_counts",
            [payload],
            on_conflict="session_id",
            returning="minimal"
        )
        if kind in {"talqeen", "tanbeeh", "repeat_mistake", "mutashabehat", "irab"}:
            rest.insert(
                "mistake_events",
                [{"session_id": session_id, "kind": kind}],
                returning="minimal",
            )
        clear_all_read_caches()
    except Exception as e:
        import logging
        logging.error(f"Background database update error: {e}")


def insert_jadeed_rows(*, student_id: str, rows: List[Dict[str, Any]], no_jadeed_reasons: Optional[Dict[str, bool]] = None) -> None:
    rest = get_rest()
    if rest is None:
        raise RuntimeError("Supabase is not configured.")

    date_today = today_iso()

    # Step 1: Delete existing entries for this student on this day
    rest.delete("jadeed_entries", match={"student_id": student_id, "activity_date": date_today})
    
    # Step 2: Concurrently insert new rows and upsert jadeed_daily
    if rows:
        insert_rows = []
        for r in rows:
            insert_rows.append({
                "created_at": now_utc_iso(),
                "student_id": student_id,
                "activity_date": date_today,
                "surah_id": r.get("surah_id"),
                "page_number": int(r.get("page_number") or 1),
                "ayah_number": int(r.get("ayah_number") or 1),
                "volume": r.get("volume") or "Kamil",
                "weak_hifz": bool(r.get("weak_hifz", False)),
                "airab_mistakes": bool(r.get("airab_mistakes", False)),
                "time_exceeded": bool(r.get("time_exceeded", False)),
                "duration_seconds": int(r.get("duration_seconds", 0) or 0),
                "weak_murajat": bool(r.get("weak_murajat", False)),
                "weak_juzulhali": bool(r.get("weak_juzulhali", False)),
            })

        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            try:
                f1 = executor.submit(rest.insert, "jadeed_entries", insert_rows, returning="minimal")
                f2 = executor.submit(
                    rest.upsert,
                    "jadeed_daily",
                    [{
                        "student_id": student_id,
                        "activity_date": date_today,
                        "no_jadeed": False,
                        "weak_hifz": False,
                        "airab_mistakes": False,
                        "time_exceeded": False,
                        "weak_murajat": False,
                        "weak_juzulhali": False,
                        "updated_at": now_utc_iso()
                    }],
                    on_conflict="student_id,activity_date",
                    returning="minimal",
                )
                f1.result()
                f2.result()
            except Exception:
                # Fallback if weak_murajat / weak_juzulhali columns are not created in DB yet
                insert_rows_fb = []
                for r in insert_rows:
                    rfb = dict(r)
                    rfb.pop("weak_murajat", None)
                    rfb.pop("weak_juzulhali", None)
                    insert_rows_fb.append(rfb)
                f1 = executor.submit(rest.insert, "jadeed_entries", insert_rows_fb, returning="minimal")
                f2 = executor.submit(
                    rest.upsert,
                    "jadeed_daily",
                    [{"student_id": student_id, "activity_date": date_today, "no_jadeed": False, "updated_at": now_utc_iso()}],
                    on_conflict="student_id,activity_date",
                    returning="minimal",
                )
                f1.result()
                f2.result()
    else:
        reasons = no_jadeed_reasons or {}
        try:
            rest.upsert(
                "jadeed_daily",
                [{
                    "student_id": student_id,
                    "activity_date": date_today,
                    "no_jadeed": True,
                    "weak_hifz": bool(reasons.get("weak_hifz", False)),
                    "airab_mistakes": bool(reasons.get("airab_mistakes", False)),
                    "time_exceeded": bool(reasons.get("time_exceeded", False)),
                    "weak_murajat": bool(reasons.get("weak_murajat", False)),
                    "weak_juzulhali": bool(reasons.get("weak_juzulhali", False)),
                    "updated_at": now_utc_iso()
                }],
                on_conflict="student_id,activity_date",
                returning="minimal",
            )
        except Exception:
            rest.upsert(
                "jadeed_daily",
                [{"student_id": student_id, "activity_date": date_today, "no_jadeed": True, "updated_at": now_utc_iso()}],
                on_conflict="student_id,activity_date",
                returning="minimal",
            )
    clear_all_read_caches()


def mark_no_jadeed_today(*, student_id: str, reasons: Optional[Dict[str, bool]] = None) -> None:
    rest = get_rest()
    if rest is None:
        raise RuntimeError("Supabase is not configured.")
    date_today = today_iso()
    rest.delete("jadeed_entries", match={"student_id": student_id, "activity_date": date_today})
    r = reasons or {}
    try:
        rest.upsert(
            "jadeed_daily",
            [{
                "student_id": student_id,
                "activity_date": date_today,
                "no_jadeed": True,
                "weak_hifz": bool(r.get("weak_hifz", False)),
                "airab_mistakes": bool(r.get("airab_mistakes", False)),
                "time_exceeded": bool(r.get("time_exceeded", False)),
                "weak_murajat": bool(r.get("weak_murajat", False)),
                "weak_juzulhali": bool(r.get("weak_juzulhali", False)),
                "updated_at": now_utc_iso()
            }],
            on_conflict="student_id,activity_date",
            returning="minimal",
        )
    except Exception:
        rest.upsert(
            "jadeed_daily",
            [{"student_id": student_id, "activity_date": date_today, "no_jadeed": True, "updated_at": now_utc_iso()}],
            on_conflict="student_id,activity_date",
            returning="minimal",
        )
    clear_all_read_caches()


@st.cache_data(show_spinner=False)
def list_jadeed_entries(*, student_id: str, limit: int = 200) -> List[Dict[str, Any]]:
    rest = get_rest()
    if rest is None:
        raise RuntimeError("Supabase is not configured.")
    
    select = "id,student_id,activity_date,surah_id,page_number,ayah_number,volume,weak_hifz,airab_mistakes,time_exceeded,duration_seconds,weak_murajat,weak_juzulhali,created_at,surahs(name_en,name_ar,number)"
    try:
        return rest.select(
            "jadeed_entries",
            select=select,
            params={
                "student_id": f"eq.{student_id}",
                "order": "activity_date.desc,created_at.desc",
                "limit": str(int(limit)),
            },
        )
    except Exception:
        select_fb = "id,student_id,activity_date,surah_id,page_number,ayah_number,volume,weak_hifz,airab_mistakes,time_exceeded,duration_seconds,created_at,surahs(name_en,name_ar,number)"
        try:
            return rest.select(
                "jadeed_entries",
                select=select_fb,
                params={
                    "student_id": f"eq.{student_id}",
                    "order": "activity_date.desc,created_at.desc",
                    "limit": str(int(limit)),
                },
            )
        except Exception:
            select_fb2 = "id,student_id,activity_date,surah_id,page_number,ayah_number,volume,weak_hifz,airab_mistakes,created_at,surahs(name_en,name_ar,number)"
            return rest.select(
                "jadeed_entries",
                select=select_fb2,
                params={
                    "student_id": f"eq.{student_id}",
                    "order": "activity_date.desc,created_at.desc",
                    "limit": str(int(limit)),
                },
            )


@st.cache_data(show_spinner=False)
def list_jadeed_mistake_history(*, student_id: str, limit: int = 300) -> List[Dict[str, Any]]:
    """
    Returns combined Jadeed history for mistake and quality analytics, including:
    - Recited Jadeed entries from jadeed_entries
    - 'No Jadeed' records from jadeed_daily with reason flags
    """
    rest = get_rest()
    if rest is None:
        raise RuntimeError("Supabase is not configured.")

    entries = list_jadeed_entries(student_id=student_id, limit=limit)
    
    daily_rows = []
    try:
        daily_rows = rest.select(
            "jadeed_daily",
            select="student_id,activity_date,no_jadeed,weak_hifz,airab_mistakes,time_exceeded,weak_murajat,weak_juzulhali,updated_at",
            params={
                "student_id": f"eq.{student_id}",
                "no_jadeed": "eq.true",
                "order": "activity_date.desc",
                "limit": str(int(limit)),
            }
        )
    except Exception:
        try:
            daily_rows = rest.select(
                "jadeed_daily",
                select="student_id,activity_date,no_jadeed,updated_at",
                params={
                    "student_id": f"eq.{student_id}",
                    "no_jadeed": "eq.true",
                    "order": "activity_date.desc",
                    "limit": str(int(limit)),
                }
            )
        except Exception:
            daily_rows = []

    # Dates already covered by jadeed_entries
    covered_dates = {str(e.get("activity_date")) for e in entries if e.get("activity_date")}
    
    combined = list(entries)
    for jd in daily_rows:
        d = str(jd.get("activity_date"))
        if d and d not in covered_dates and bool(jd.get("no_jadeed")):
            combined.append({
                "id": f"no_jad_{d}",
                "is_no_jadeed": True,
                "student_id": student_id,
                "activity_date": d,
                "surah_id": None,
                "page_number": "-",
                "ayah_number": "-",
                "volume": "No Jadeed",
                "weak_hifz": bool(jd.get("weak_hifz", False)),
                "airab_mistakes": bool(jd.get("airab_mistakes", False)),
                "time_exceeded": bool(jd.get("time_exceeded", False)),
                "weak_murajat": bool(jd.get("weak_murajat", False)),
                "weak_juzulhali": bool(jd.get("weak_juzulhali", False)),
                "duration_seconds": 0,
                "created_at": jd.get("updated_at") or "",
                "surahs": {"name_en": "No Jadeed", "name_ar": "لا جديد", "number": "-"},
            })

    # Sort combined history by activity_date desc
    combined.sort(key=lambda x: str(x.get("activity_date", "")), reverse=True)
    return combined[:limit]


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

    # Fetch data concurrently using a thread pool
    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_sessions = executor.submit(
            rest.select,
            "listening_sessions",
            select="id,activity_date,mode,surah_id,page_number,duration_seconds,time_exceeded,created_at,surahs(number,name_en,name_ar),mistake_counts(*)",
            params={
                "student_id": f"eq.{student_id}",
                "and": f"(activity_date.gte.{from_date},activity_date.lte.{to_date})",
                "order": "activity_date.asc,created_at.asc",
            }
        )
        
        future_jadeed = executor.submit(
            rest.select,
            "jadeed_entries",
            select="id,activity_date,surah_id,page_number,ayah_number,volume,weak_hifz,airab_mistakes,time_exceeded,duration_seconds,weak_murajat,weak_juzulhali,created_at,surahs(number,name_en,name_ar)",
            params={
                "student_id": f"eq.{student_id}",
                "and": f"(activity_date.gte.{from_date},activity_date.lte.{to_date})",
                "order": "activity_date.asc,created_at.asc",
            }
        )
        
        future_daily = executor.submit(
            rest.select,
            "jadeed_daily",
            select="student_id,activity_date,no_jadeed,updated_at",
            params={
                "student_id": f"eq.{student_id}",
                "and": f"(activity_date.gte.{from_date},activity_date.lte.{to_date})",
                "order": "activity_date.asc",
            }
        )
        
        future_takhteet = executor.submit(
            rest.select,
            "takhteet_daily",
            select="student_id,activity_date,murajat_text_clean,juzulhali_text_clean,jadeed_text_clean,murajat_text_raw,juzulhali_text_raw,jadeed_text_raw,updated_at",
            params={
                "student_id": f"eq.{student_id}",
                "and": f"(activity_date.gte.{from_date},activity_date.lte.{to_date})",
                "order": "activity_date.asc",
            }
        )
        
        try:
            session_rows = future_sessions.result()
        except Exception:
            session_rows = rest.select(
                "listening_sessions",
                select="id,activity_date,mode,surah_id,page_number,created_at,surahs(number,name_en,name_ar),mistake_counts(*)",
                params={
                    "student_id": f"eq.{student_id}",
                    "and": f"(activity_date.gte.{from_date},activity_date.lte.{to_date})",
                    "order": "activity_date.asc,created_at.asc",
                }
            )
        jadeed_rows = future_jadeed.result()
        jadeed_daily_rows = future_daily.result()
        takhteet_rows = future_takhteet.result()

    by_date: Dict[str, Dict[str, Any]] = {}
    for day in range(1, last_day + 1):
        d = f"{year:04d}-{month:02d}-{day:02d}"
        by_date[d] = {
            "activity_date": d,
            "murajat": [],
            "juzulhali": [],
            "jadeed": [],
            "no_jadeed": False,
            "takhteet": {
                "murajat": "",
                "juzulhali": "",
                "jadeed": "",
                "murajat_text": "",
                "juzulhali_text": "",
                "jadeed_text": "",
                "murajat_text_clean": "",
                "juzulhali_text_clean": "",
                "jadeed_text_clean": "",
                "murajat_text_raw": "",
                "juzulhali_text_raw": "",
                "jadeed_text_raw": "",
            },
        }

    for s in session_rows:
        d = str(s.get("activity_date"))
        if d not in by_date:
            continue
        counts = s.get("mistake_counts") or {}
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
            "id": s.get("id"),
            "talqeen": talqeen,
            "tanbeeh": tanbeeh,
            "repeat_mistake": repeat_mistake,
            "mutashabehat": mutashabehat,
            "irab": irab,
            "marks": marks,
            "duration_seconds": int(s.get("duration_seconds", 0) or 0),
            "time_exceeded": bool(s.get("time_exceeded", False)),
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
        mode = s.get("mode")
        if mode == "murajat":
            surah = s.get("surahs") or {}
            if isinstance(surah, list):
                surah = surah[0] if surah else {}
            if surah.get("number"):
                row["surat"] = f"{surah.get('number', '')} - {surah.get('name_en', '')}".strip(" -")
                row["surah_name_ar"] = surah.get("name_ar", "")
                row["surah_number"] = surah.get("number", "")
            else:
                row["surat"] = ""
                row["surah_name_ar"] = ""
                row["surah_number"] = ""
            row["page_number"] = int(s.get("page_number") or 0)
            by_date[d]["murajat"].append(row)
        elif mode == "juzulhali":
            surah = s.get("surahs") or {}
            if isinstance(surah, list):
                surah = surah[0] if surah else {}
            if surah.get("number"):
                row["surat"] = f"{surah.get('number', '')} - {surah.get('name_en', '')}".strip(" -")
                row["surah_name_ar"] = surah.get("name_ar", "")
                row["surah_number"] = surah.get("number", "")
            else:
                row["surat"] = ""
                row["surah_name_ar"] = ""
                row["surah_number"] = ""
            row["page_number"] = int(s.get("page_number") or 0)
            by_date[d]["juzulhali"].append(row)

    for j in jadeed_rows:
        d = str(j.get("activity_date"))
        if d not in by_date:
            continue
        surah = j.get("surahs") or {}
        if isinstance(surah, list):
            surah = surah[0] if surah else {}
        entry_item = {
            "surah_id": j.get("surah_id") or (surah.get("number") if surah else 0),
            "surat": f"{surah.get('number', '')} - {surah.get('name_en', '')}".strip(" -"),
            "surah_name_ar": surah.get("name_ar", ""),
            "surah_number": surah.get("number", ""),
            "page_number": int(j.get("page_number") or 0),
            "ayah_number": int(j.get("ayah_number") or 0),
            "volume": j.get("volume") or "",
            "weak_hifz": bool(j.get("weak_hifz", False)),
            "airab_mistakes": bool(j.get("airab_mistakes", False)),
            "time_exceeded": bool(j.get("time_exceeded", False)),
            "duration_seconds": int(j.get("duration_seconds", 0) or 0),
            "weak_murajat": bool(j.get("weak_murajat", False)),
            "weak_juzulhali": bool(j.get("weak_juzulhali", False)),
        }
        by_date[d]["jadeed"].append(entry_item)

    for jd in jadeed_daily_rows:
        d = str(jd.get("activity_date"))
        if d in by_date:
            by_date[d]["no_jadeed"] = bool(jd.get("no_jadeed"))

    for t in takhteet_rows:
        d = str(t.get("activity_date"))
        if d in by_date:
            m_raw = (t.get("murajat_text_raw") or "").strip()
            j_raw = (t.get("juzulhali_text_raw") or "").strip()
            jd_raw = (t.get("jadeed_text_raw") or "").strip()
            m_clean = (t.get("murajat_text_clean") or "").strip()
            j_clean = (t.get("juzulhali_text_clean") or "").strip()
            jd_clean = (t.get("jadeed_text_clean") or "").strip()

            m_val = m_raw or m_clean
            j_val = j_raw or j_clean
            jd_val = jd_raw or jd_clean

            by_date[d]["takhteet"] = {
                "murajat": m_val,
                "juzulhali": j_val,
                "jadeed": jd_val,
                "murajat_text": m_val,
                "juzulhali_text": j_val,
                "jadeed_text": jd_val,
                "murajat_text_clean": m_clean,
                "juzulhali_text_clean": j_clean,
                "jadeed_text_clean": jd_clean,
                "murajat_text_raw": m_raw,
                "juzulhali_text_raw": j_raw,
                "jadeed_text_raw": jd_raw,
            }

    # Format result list
    result = []
    for d, data in by_date.items():
        result.append(
            {
                "activity_date": d,
                "murajat": data["murajat"],
                "juzulhali": data["juzulhali"],
                "jadeed": data["jadeed"],
                "no_jadeed": data["no_jadeed"],
                "takhteet": data["takhteet"],
            }
        )
    return result


def get_student_email(*, student_id: str) -> Optional[str]:
    rest = get_rest()
    if rest is None:
        return None
    try:
        row = rest.select_single("students", select="email", params={"id": f"eq.{student_id}"})
        if row and row.get("email"):
            return str(row["email"]).strip()
    except Exception:
        pass
    return None


@st.cache_data(show_spinner=False)
def get_student_daily_summary(*, student_id: str, date_str: str) -> Dict[str, Any]:
    rest = get_rest()
    if rest is None:
        return {}

    try:
        student = rest.select_single("students", select="full_name,email", params={"id": f"eq.{student_id}"})
    except Exception:
        student = rest.select_single("students", select="full_name", params={"id": f"eq.{student_id}"})

    if not student:
        return {}

    try:
        sessions = rest.select(
            "listening_sessions",
            select="id,mode,surah_id,page_number,duration_seconds,time_exceeded,created_at,surahs(number,name_en,name_ar),mistake_counts(*)",
            params={
                "student_id": f"eq.{student_id}",
                "activity_date": f"eq.{date_str}",
                "order": "created_at.asc",
            },
        )
    except Exception:
        sessions = rest.select(
            "listening_sessions",
            select="id,mode,surah_id,page_number,created_at,surahs(number,name_en,name_ar),mistake_counts(*)",
            params={
                "student_id": f"eq.{student_id}",
                "activity_date": f"eq.{date_str}",
                "order": "created_at.asc",
            },
        )

    jadeed_select = "id,surah_id,page_number,ayah_number,volume,weak_hifz,airab_mistakes,time_exceeded,duration_seconds,weak_murajat,weak_juzulhali,created_at,surahs(number,name_en,name_ar)"
    try:
        jadeed_rows = rest.select(
            "jadeed_entries",
            select=jadeed_select,
            params={
                "student_id": f"eq.{student_id}",
                "activity_date": f"eq.{date_str}",
                "order": "created_at.asc",
            },
        )
    except Exception:
        jadeed_rows = rest.select(
            "jadeed_entries",
            select="id,surah_id,page_number,ayah_number,volume,weak_hifz,airab_mistakes,time_exceeded,duration_seconds,created_at,surahs(number,name_en,name_ar)",
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

    jadeed_select = "id,surah_id,page_number,ayah_number,volume,weak_hifz,airab_mistakes,time_exceeded,duration_seconds,weak_murajat,weak_juzulhali,created_at,surahs(number,name_en,name_ar)"
    try:
        jadeed_rows = rest.select(
            "jadeed_entries",
            select=jadeed_select,
            params={
                "student_id": f"eq.{student_id}",
                "activity_date": f"eq.{date_str}",
                "order": "created_at.asc",
            },
        )
    except Exception:
        jadeed_rows = rest.select(
            "jadeed_entries",
            select="id,surah_id,page_number,ayah_number,volume,weak_hifz,airab_mistakes,time_exceeded,duration_seconds,created_at,surahs(number,name_en,name_ar)",
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
            select="no_jadeed,weak_hifz,airab_mistakes,time_exceeded,weak_murajat,weak_juzulhali",
            params={
                "student_id": f"eq.{student_id}",
                "activity_date": f"eq.{date_str}",
            },
        )
    except Exception:
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
        "no_jadeed_details": jadeed_daily_row if (jadeed_daily_row and jadeed_daily_row.get("no_jadeed")) else None,
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
    students = [s for s in students if "test" not in s["full_name"].lower()]
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
            pg_val = latest_entry.get("page_number")
            page_num = str(pg_val) if pg_val is not None else "-"
            ay_val = latest_entry.get("ayah_number")
            ayah_num = str(ay_val) if ay_val is not None else "-"
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
    students = [s for s in students if "test" not in s["full_name"].lower()]
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
            takhteet = day_data["takhteet"]
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
        rows = rest.select("students", select="id,full_name", params={"order": "full_name.asc"})
        return [r for r in rows if "test" not in r["full_name"].lower()]

    def fetch_jadeed():
        return rest.select(
            "jadeed_entries",
            select="student_id,activity_date,page_number,ayah_number,volume,created_at,surahs(number,name_en,name_ar)",
            params={
                "activity_date": f"lte.{to_date}",
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


def log_parent_view(*, student_id: str, date_str: str) -> None:
    rest = get_rest()
    if rest is None:
        return
    payload = {
        "student_id": student_id,
        "activity_date": date_str,
        "viewed_at": now_utc_iso()
    }
    try:
        rest.upsert("parent_report_views", [payload], on_conflict="student_id,activity_date", returning="minimal")
    except Exception as e:
        print(f"[log_parent_view error] {e}")


def fetch_parent_views(*, date_str: str) -> List[Dict[str, Any]]:
    rest = get_rest()
    if rest is None:
        return []
    try:
        return rest.select("parent_report_views", select="student_id,activity_date,viewed_at", params={"activity_date": f"eq.{date_str}"})
    except Exception as e:
        print(f"[fetch_parent_views error] {e}")
        return []


def fetch_ummul_banin_report_data() -> List[Dict[str, Any]]:
    import concurrent.futures
    rest = get_rest()
    if rest is None:
        return []
        
    students = list_students()
    students = [s for s in students if "test" not in s["full_name"].lower()]
    if not students:
        return []
        
    today = today_iso()
    
    # Fetch today's jadeed entries
    today_entries = rest.select(
        "jadeed_entries",
        select="student_id,activity_date,surah_id,page_number,ayah_number,volume,created_at,surahs(name_en,name_ar,number)",
        params={
            "activity_date": f"eq.{today}"
        }
    )
    
    # Fetch today's no_jadeed daily flags
    today_no_jadeed = rest.select(
        "jadeed_daily",
        select="student_id,no_jadeed",
        params={
            "activity_date": f"eq.{today}"
        }
    )
    no_jadeed_map = {row["student_id"]: bool(row["no_jadeed"]) for row in today_no_jadeed}
    
    # Fetch today's takhteet (murajat, juzulhali, jadeed)
    today_takhteet = rest.select(
        "takhteet_daily",
        select="student_id,murajat_text_clean,juzulhali_text_clean,jadeed_text_clean,murajat_text_raw,juzulhali_text_raw,jadeed_text_raw",
        params={
            "activity_date": f"eq.{today}"
        }
    )
    takhteet_map = {
        row["student_id"]: {
            "jadeed": (row.get("jadeed_text_clean") or row.get("jadeed_text_raw") or "").strip(),
            "juzulhali": (row.get("juzulhali_text_clean") or row.get("juzulhali_text_raw") or "").strip(),
            "murajat": (row.get("murajat_text_clean") or row.get("murajat_text_raw") or "").strip(),
        }
        for row in today_takhteet
    }
    
    # For each today's entry, map student_id -> entry (sort by created_at desc to get latest if multiple today)
    today_entries_map = {}
    for entry in sorted(today_entries, key=lambda x: x.get("created_at") or "", reverse=True):
        sid = entry["student_id"]
        if sid not in today_entries_map:
            today_entries_map[sid] = entry
            
    # We will build a list of student records
    # If a student has no entry today OR has no_jadeed map as True, we need their last historical entry
    historical_needed_ids = []
    for s in students:
        sid = s["id"]
        has_today = (sid in today_entries_map)
        is_no_jadeed = no_jadeed_map.get(sid, False)
        if not has_today or is_no_jadeed:
            historical_needed_ids.append(sid)
            
    # Fetch last historical entry for each of these students in parallel
    historical_entries_map = {}
    if historical_needed_ids:
        def fetch_last_entry(sid: str):
            try:
                res = rest.select(
                    "jadeed_entries",
                    select="student_id,activity_date,surah_id,page_number,ayah_number,volume,created_at,surahs(name_en,name_ar,number)",
                    params={
                        "student_id": f"eq.{sid}",
                        "activity_date": f"lt.{today}",
                        "order": "activity_date.desc,created_at.desc",
                        "limit": "1"
                    }
                )
                return sid, res[0] if res else None
            except Exception:
                return sid, None
                
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(fetch_last_entry, historical_needed_ids)
            for sid, entry in results:
                if entry:
                    historical_entries_map[sid] = entry
                    
    report_data = []
    for s in students:
        sid = s["id"]
        has_today = (sid in today_entries_map)
        is_no_jadeed = no_jadeed_map.get(sid, False)
        
        entry = None
        is_historical = False
        
        if has_today and not is_no_jadeed:
            entry = today_entries_map[sid]
        else:
            entry = historical_entries_map.get(sid)
            is_historical = True
            
        t_info = takhteet_map.get(sid, {})
        report_data.append({
            "student_id": sid,
            "student_name": s["full_name"],
            "entry": entry,
            "is_historical": is_historical,
            "is_no_jadeed_today": is_no_jadeed,
            "takhteet_jadeed": t_info.get("jadeed", ""),
            "takhteet_juzulhali": t_info.get("juzulhali", ""),
            "takhteet_murajat": t_info.get("murajat", ""),
        })
        
    return report_data


def log_email_status(student_id: str, activity_date: str, sent: bool) -> None:
    client = get_rest()
    if not client:
        return
    try:
        client.upsert(
            "email_logs",
            [
                {
                    "student_id": student_id,
                    "activity_date": activity_date,
                    "sent": sent,
                }
            ],
            on_conflict="student_id,activity_date",
        )
    except Exception as e:
        print(f"Failed to log email status: {e}")


def get_daily_email_status(date_str: str) -> List[Dict[str, Any]]:
    client = get_rest()
    if not client:
        return []
    try:
        # Get all students
        students = client.select("students", select="id,full_name,email")
        # Get email logs for the specific date
        logs = client.select("email_logs", select="student_id,sent", params={"activity_date": f"eq.{date_str}"})
        
        log_map = {l["student_id"]: l["sent"] for l in logs}
        
        result = []
        for s in students:
            # Exclude test students
            if "test" in s["full_name"].lower():
                continue
            is_sent = log_map.get(s["id"], False)
            result.append({
                "student_id": s["id"],
                "student_name": s["full_name"],
                "student_email": s["email"] or "No Email Registered",
                "sent": is_sent,
            })
        # Sort by student name
        result.sort(key=lambda x: x["student_name"])
        return result
    except Exception as e:
        print(f"Failed to get daily email status: {e}")
        return []


def volume_to_page_weight(vol: Optional[str]) -> float:
    """Converts a Jadeed volume string to fractional Quran pages."""
    if not vol:
        return 1.0
    v = str(vol).strip().lower()
    if "kamil" in v or "full" in v:
        return 1.0
    if "nisf" in v or "half" in v or "0.5" in v:
        return 0.5
    if "ruba" in v or "quarter" in v or "0.25" in v:
        return 0.25
    if "sulus" in v or "0.75" in v:
        return 0.75
    return 1.0


@st.cache_data(show_spinner=False)
def fetch_jadeed_pages_summary_report(*, from_date: str, to_date: str) -> Dict[str, Any]:
    """
    Fetches collective Jadeed total pages for all students within an arbitrary date range,
    broken down by month and sorted in descending order by total pages recited.
    """
    import concurrent.futures
    from datetime import datetime
    rest = get_rest()
    if rest is None:
        raise RuntimeError("Supabase is not configured.")

    def fetch_students():
        rows = rest.select("students", select="id,full_name,email", params={"order": "full_name.asc"})
        return [r for r in rows if "test" not in r["full_name"].lower()]

    def fetch_jadeed():
        try:
            return rest.select(
                "jadeed_entries",
                select="id,student_id,activity_date,page_number,ayah_number,volume,weak_hifz,airab_mistakes,created_at,surahs(number,name_en,name_ar)",
                params={
                    "and": f"(activity_date.gte.{from_date},activity_date.lte.{to_date})",
                    "order": "activity_date.asc,created_at.asc"
                }
            )
        except Exception:
            return rest.select(
                "jadeed_entries",
                select="id,student_id,activity_date,page_number,ayah_number,volume,created_at,surahs(number,name_en,name_ar)",
                params={
                    "and": f"(activity_date.gte.{from_date},activity_date.lte.{to_date})",
                    "order": "activity_date.asc,created_at.asc"
                }
            )

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_students = executor.submit(fetch_students)
        future_jadeed = executor.submit(fetch_jadeed)

        students = future_students.result()
        jadeed_rows = future_jadeed.result()

    # Determine unique months between from_date and to_date
    start_dt = datetime.strptime(from_date, "%Y-%m-%d")
    end_dt = datetime.strptime(to_date, "%Y-%m-%d")

    months = []
    curr_y, curr_m = start_dt.year, start_dt.month
    end_y, end_m = end_dt.year, end_dt.month

    while (curr_y, curr_m) <= (end_y, end_m):
        m_key = f"{curr_y:04d}-{curr_m:02d}"
        dt_month = datetime(curr_y, curr_m, 1)
        months.append({
            "key": m_key,
            "label": dt_month.strftime("%B %Y"),
            "short_label": dt_month.strftime("%b %Y"),
            "year": curr_y,
            "month": curr_m
        })
        if curr_m == 12:
            curr_y += 1
            curr_m = 1
        else:
            curr_m += 1

    # Map Jadeed entries by student_id
    from collections import defaultdict
    student_jadeed_map = defaultdict(list)
    for j in jadeed_rows:
        s_id = j.get("student_id")
        if s_id:
            student_jadeed_map[s_id].append(j)

    student_records = []
    total_class_pages = 0.0
    active_student_count = 0

    for s in students:
        s_id = s["id"]
        s_name = s["full_name"]
        s_entries = student_jadeed_map.get(s_id, [])

        # Group student entries by month
        month_entries = defaultdict(list)
        distinct_days = set()
        for e in s_entries:
            act_date = str(e.get("activity_date") or "")
            if act_date:
                m_key = act_date[:7]
                distinct_days.add(act_date)
                month_entries[m_key].append(e)

        # Physical Quran pages computation per month
        months_pages = {m["key"]: 0 for m in months}
        for m in months:
            k = m["key"]
            m_list = month_entries.get(k, [])
            if not m_list:
                months_pages[k] = 0
                continue

            # Group by Surah in this month to calculate physical page span
            surah_pages = defaultdict(set)
            for e in m_list:
                s_info = e.get("surahs") or {}
                if isinstance(s_info, list):
                    s_info = s_info[0] if s_info else {}
                s_num = s_info.get("number")
                p_num = e.get("page_number")
                if s_num and p_num:
                    try:
                        surah_pages[int(s_num)].add(int(p_num))
                    except (ValueError, TypeError):
                        pass

            m_tot = 0
            for s_num, p_set in surah_pages.items():
                if p_set:
                    span = max(p_set) - min(p_set) + 1
                    m_tot += span
            months_pages[k] = m_tot

        total_pages = sum(months_pages.values())
        has_jadeed = len(s_entries) > 0 and total_pages > 0

        if has_jadeed:
            active_student_count += 1
            total_class_pages += total_pages

        latest_entry = s_entries[-1] if s_entries else None
        latest_surah = None
        if latest_entry:
            s_info = latest_entry.get("surahs") or {}
            if isinstance(s_info, list):
                s_info = s_info[0] if s_info else {}
            latest_surah = {
                "surah_number": s_info.get("number"),
                "surah_name": s_info.get("name_en"),
                "surah_name_ar": s_info.get("name_ar"),
                "page_number": latest_entry.get("page_number"),
                "ayah_number": latest_entry.get("ayah_number"),
                "volume": latest_entry.get("volume"),
                "date": latest_entry.get("activity_date"),
            }

        student_records.append({
            "student_id": s_id,
            "student_name": s_name,
            "student_email": s.get("email") or "",
            "months_pages": months_pages,
            "total_pages": int(total_pages),
            "total_entries": len(s_entries),
            "active_days": len(distinct_days),
            "has_jadeed": has_jadeed,
            "latest_entry": latest_surah,
        })

    # Sort descending by total_pages, then alphabetically by name
    student_records.sort(key=lambda x: (-x["total_pages"], x["student_name"].lower()))

    # Assign ranks
    current_rank = 1
    for idx, rec in enumerate(student_records):
        if rec["has_jadeed"] and rec["total_pages"] > 0:
            rec["rank"] = current_rank
            current_rank += 1
        else:
            rec["rank"] = "-"

    top_student_str = "None"
    if student_records and student_records[0]["has_jadeed"]:
        top = student_records[0]
        pages_fmt = int(top["total_pages"]) if top["total_pages"].is_integer() else top["total_pages"]
        top_student_str = f"{top['student_name']} ({pages_fmt} pgs)"

    avg_pages = (total_class_pages / len(students)) if students else 0.0

    return {
        "from_date": from_date,
        "to_date": to_date,
        "months": months,
        "students": student_records,
        "stats": {
            "total_students": len(students),
            "students_with_jadeed": active_student_count,
            "students_without_jadeed": len(students) - active_student_count,
            "total_class_pages": round(total_class_pages, 2),
            "avg_pages_per_student": round(avg_pages, 1),
            "top_student": top_student_str,
        }
    }


@st.cache_data(show_spinner=False)
def get_student_page_listening_history(
    *, 
    student_id: str, 
    page_number: int, 
    mode: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Fetches all historical listening sessions for a specific student and page number,
    chronologically ordered, with calculated scores, mistake categories, and deltas.
    """
    rest = get_rest()
    if rest is None:
        return []

    params: Dict[str, str] = {
        "student_id": f"eq.{student_id}",
        "page_number": f"eq.{page_number}",
        "order": "activity_date.asc,created_at.asc"
    }
    if mode:
        params["mode"] = f"eq.{mode}"

    try:
        rows = rest.select(
            "listening_sessions",
            select="id,student_id,activity_date,mode,page_number,surah_id,created_at,surahs(number,name_en,name_ar),mistake_counts(*)",
            params=params
        )
    except Exception as e:
        print(f"[get_student_page_listening_history error] {e}")
        return []

    history = []
    prev_score = None

    for idx, r in enumerate(rows):
        counts = r.get("mistake_counts")
        if isinstance(counts, list):
            counts = counts[0] if counts else {}
        elif not isinstance(counts, dict):
            counts = {}

        talqeen = int(counts.get("talqeen", 0) or 0)
        tanbeeh = int(counts.get("tanbeeh", 0) or 0)
        is_zero = bool(counts.get("is_zero_marks", False))

        if is_zero:
            score = 0.0
        else:
            score = max(0.0, 10.0 - (0.5 * talqeen) - (0.25 * tanbeeh))

        score_delta = None
        if prev_score is not None:
            score_delta = score - prev_score
        prev_score = score

        s_info = r.get("surahs") or {}
        if isinstance(s_info, list):
            s_info = s_info[0] if s_info else {}

        # Ahkam breakdown
        ahkam_items = []
        for col_name, label in [
            ("ikhfa", "Ikhfa"), ("izhaar", "Izhaar"), ("qalqalah", "Qalqalah"),
            ("ism_jalalah", "Ism Jalal"), ("tahreek_sakin", "Tahreek"), ("gunnah", "Gunnah"),
            ("idgham", "Idgham"), ("madd_lazim", "M. Lazim"), ("madd_muttasil", "M. Mutta."),
            ("mad_tabaiee", "M. Tabai."), ("ikhfa_shafawi", "Ikh. Shaf."), ("iqlab", "Iqlab")
        ]:
            val = int(counts.get(col_name, 0) or 0)
            if val > 0:
                ahkam_items.append(f"{label} ({val})" if val > 1 else label)

        # Makharij breakdown
        makhraj_chars = {
            "makhraj_alif": "أ", "makhraj_baa": "ب", "makhraj_taa": "ت", "makhraj_thaa": "ث",
            "makhraj_jeem": "ج", "makhraj_haa": "ح", "makhraj_khaa": "خ", "makhraj_daal": "د",
            "makhraj_thaal": "ذ", "makhraj_raa": "ر", "makhraj_zaa": "ز", "makhraj_seen": "س",
            "makhraj_sheen": "ش", "makhraj_saad": "ص", "makhraj_daad": "ض", "makhraj_taa_thick": "ط",
            "makhraj_zaa_thick": "ظ", "makhraj_ain": "ع", "makhraj_ghain": "غ", "makhraj_faa": "ف",
            "makhraj_qaaf": "ق", "makhraj_kaaf": "ك", "makhraj_laam": "ل", "makhraj_meem": "م",
            "makhraj_noon": "ن", "makhraj_waw": "و", "makhraj_haa_weak": "هـ", "makhraj_yaa": "ي"
        }
        makharij_items = []
        for col_name, letter in makhraj_chars.items():
            val = int(counts.get(col_name, 0) or 0)
            if val > 0:
                makharij_items.append(f"{letter} ({val})" if val > 1 else letter)

        history.append({
            "session_id": r.get("id"),
            "attempt_number": idx + 1,
            "activity_date": r.get("activity_date"),
            "mode": r.get("mode"),
            "page_number": r.get("page_number"),
            "surah_number": s_info.get("number"),
            "surah_name": s_info.get("name_en") or s_info.get("name_ar") or "Unknown",
            "surah_name_ar": s_info.get("name_ar") or "",
            "score": round(score, 2),
            "score_delta": round(score_delta, 2) if score_delta is not None else None,
            "talqeen": talqeen,
            "tanbeeh": tanbeeh,
            "irab": int(counts.get("irab", 0) or 0),
            "awakhir": int(counts.get("awakhir_ul_ayat", 0) or 0),
            "repeat": int(counts.get("repeat_mistake", 0) or 0),
            "mutashabehat": int(counts.get("mutashabehat", 0) or 0),
            "total_mistakes": talqeen + tanbeeh + int(counts.get("irab", 0) or 0) + int(counts.get("awakhir_ul_ayat", 0) or 0) + int(counts.get("repeat_mistake", 0) or 0) + int(counts.get("mutashabehat", 0) or 0),
            "ahkam_list": ahkam_items,
            "makharij_list": makharij_items,
            "raw_counts": counts,
        })

    return history









