from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import streamlit as st


def back_home_button() -> None:
    pass


def surah_selector(*, surahs: List[Dict[str, Any]], key: str) -> Tuple[Optional[int], Optional[Dict[str, Any]]]:
    if not surahs:
        st.info("No Surahs found yet. Run the SQL in `supabase/schema.sql` (it includes a seed list).")
        return None, None

    options = [(s["id"], f'{s["number"]:03d} — {s["name_en"]} ({s["name_ar"]})') for s in surahs]
    selected = st.selectbox(
        "Surah",
        options=options,
        index=None,
        placeholder="Select a Surah...",
        format_func=lambda x: x[1] if x else "",
        key=key
    )
    if not selected:
        return None, None
    surah_id = selected[0]
    surah = next((s for s in surahs if s["id"] == surah_id), None)
    return surah_id, surah


def mistake_buttons(*, session_id: str, counts: Dict[str, int], on_click) -> None:
    st.markdown("### Mistake buttons")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.button(
            f"Talqeen ({counts['talqeen']})",
            width="stretch",
            on_click=on_click,
            kwargs={"kind": "talqeen"},
        )
    with c2:
        st.button(
            f"Tanbeeh ({counts['tanbeeh']})",
            width="stretch",
            on_click=on_click,
            kwargs={"kind": "tanbeeh"},
        )
    with c3:
        st.button(
            f"I'rab ({counts.get('irab', 0)})",
            width="stretch",
            on_click=on_click,
            kwargs={"kind": "irab"},
        )
    with c4:
        st.button(
            f"Repeat mistake ({counts['repeat_mistake']})",
            width="stretch",
            on_click=on_click,
            kwargs={"kind": "repeat_mistake"},
        )
    with c5:
        st.button(
            f"Mutashabehat ({counts['mutashabehat']})",
            width="stretch",
            on_click=on_click,
            kwargs={"kind": "mutashabehat"},
        )


def show_previous_takhteet(student_id: str) -> None:
    from app.db import get_previous_takhteet
    prev = get_previous_takhteet(student_id=student_id)
    if prev:
        date_str = prev.get("activity_date", "Previous Day")
        try:
            from datetime import datetime
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            formatted_date = dt.strftime("%b %d, %Y (%a)")
        except Exception:
            formatted_date = date_str

        with st.expander(f"📋 **Previous Homework / Takhteet** (Recorded on {formatted_date})", expanded=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("**Murajat**")
                text = prev.get("murajat_text_raw", "").strip()
                st.write(text if text else "-")
            with c2:
                st.markdown("**Juzulhali**")
                text = prev.get("juzulhali_text_raw", "").strip()
                st.write(text if text else "-")
            with c3:
                st.markdown("**Jadeed**")
                text = prev.get("jadeed_text_raw", "").strip()
                st.write(text if text else "-")

