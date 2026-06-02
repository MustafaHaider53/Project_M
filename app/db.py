from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import streamlit as st
import requests

from app.config import get_settings


@st.cache_resource(show_spinner=False)
def get_rest() -> Optional["SupabaseRest"]:
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_key:
        return None
    return SupabaseRest(url=settings.supabase_url, key=settings.supabase_key)


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


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
        return list(r.json() or [])

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
        return list(r.json() or [])

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


def list_surahs() -> List[Dict[str, Any]]:
    rest = get_rest()
    if rest is None:
        return []
    return rest.select("surahs", select="id,name_ar,name_en,number", params={"order": "number.asc"})


def create_listening_session(
    *,
    mode: str,
    surah_id: Optional[int],
    page_number: Optional[int],
) -> Dict[str, Any]:
    rest = get_rest()
    if rest is None:
        raise RuntimeError("Supabase is not configured. Set SUPABASE_URL and SUPABASE_KEY in Streamlit secrets.")

    payload: Dict[str, Any] = {
        "mode": mode,
        "surah_id": surah_id,
        "page_number": page_number,
        "created_at": now_utc_iso(),
    }
    res = rest.insert("listening_sessions", [payload])
    return res[0]


def get_session_counts(session_id: str) -> Dict[str, int]:
    rest = get_rest()
    if rest is None:
        raise RuntimeError("Supabase is not configured.")
    row = rest.select_single(
        "mistake_counts",
        select="talqeen,tanbeeh,repeat_mistake,mutashabehat",
        params={"session_id": f"eq.{session_id}"},
    )
    if not row:
        # initialize counts row
        init = {
            "session_id": session_id,
            "talqeen": 0,
            "tanbeeh": 0,
            "repeat_mistake": 0,
            "mutashabehat": 0,
            "updated_at": now_utc_iso(),
        }
        rest.insert("mistake_counts", [init], returning="minimal")
        return {"talqeen": 0, "tanbeeh": 0, "repeat_mistake": 0, "mutashabehat": 0}

    return {
        "talqeen": int(row.get("talqeen", 0) or 0),
        "tanbeeh": int(row.get("tanbeeh", 0) or 0),
        "repeat_mistake": int(row.get("repeat_mistake", 0) or 0),
        "mutashabehat": int(row.get("mutashabehat", 0) or 0),
    }


def increment_mistake(session_id: str, kind: str) -> Dict[str, int]:
    """
    Business rules:
    - talqeen increments talqeen
    - tanbeeh increments tanbeeh
    - repeat_mistake increments repeat_mistake AND talqeen
    - mutashabehat increments mutashabehat AND talqeen
    """
    counts = get_session_counts(session_id)

    if kind == "talqeen":
        counts["talqeen"] += 1
    elif kind == "tanbeeh":
        counts["tanbeeh"] += 1
    elif kind == "repeat_mistake":
        counts["repeat_mistake"] += 1
        counts["talqeen"] += 1
    elif kind == "mutashabehat":
        counts["mutashabehat"] += 1
        counts["talqeen"] += 1
    else:
        raise ValueError(f"Unknown kind: {kind}")

    rest = get_rest()
    if rest is None:
        raise RuntimeError("Supabase is not configured.")

    rest.update(
        "mistake_counts",
        match={"session_id": session_id},
        patch={
            "talqeen": counts["talqeen"],
            "tanbeeh": counts["tanbeeh"],
            "repeat_mistake": counts["repeat_mistake"],
            "mutashabehat": counts["mutashabehat"],
            "updated_at": now_utc_iso(),
        },
    )

    rest.insert(
        "mistake_events",
        [{"session_id": session_id, "kind": kind, "created_at": now_utc_iso()}],
        returning="minimal",
    )

    return counts


def insert_jadeed_rows(rows: List[Dict[str, Any]]) -> None:
    rest = get_rest()
    if rest is None:
        raise RuntimeError("Supabase is not configured.")
    if not rows:
        return
    for r in rows:
        r["created_at"] = now_utc_iso()
    rest.insert("jadeed_entries", rows, returning="minimal")

