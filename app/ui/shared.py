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
    selected = st.selectbox("Surah", options=options, format_func=lambda x: x[1], key=key)
    surah_id = selected[0]
    surah = next((s for s in surahs if s["id"] == surah_id), None)
    return surah_id, surah


def mistake_buttons(*, session_id: str, counts: Dict[str, int], on_click) -> None:
    st.markdown("### Mistake buttons")
    c1, c2, c3, c4 = st.columns(4)
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
            f"Repeat mistake ({counts['repeat_mistake']})",
            width="stretch",
            on_click=on_click,
            kwargs={"kind": "repeat_mistake"},
        )
    with c4:
        st.button(
            f"Mutashabehat ({counts['mutashabehat']})",
            width="stretch",
            on_click=on_click,
            kwargs={"kind": "mutashabehat"},
        )

