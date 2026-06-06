from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st

from app.db import insert_jadeed_rows, list_jadeed_entries, list_surahs, mark_no_jadeed_today, today_iso
from app.ui.shared import back_home_button, show_previous_takhteet
from app.ui.student import current_student_badge


def render_jadeed() -> None:
    back_home_button()
    st.subheader("Jadeed")
    st.caption("Enter new work (no mistake buttons).")
    current_student_badge()

    student_id = st.session_state.get("student_id")
    if not student_id:
        st.warning("Please select a student on Home first.")
        return

    show_previous_takhteet(student_id)

    # One-time success message (prevents accidental double-save)
    flash = st.session_state.pop("jadeed_flash", None)
    if flash:
        st.success(flash)

    surahs = list_surahs()
    if not surahs:
        st.info("No Surahs found yet. Run the SQL in `supabase/schema.sql` first.")
        return

    surah_options = {f'{s["number"]:03d} — {s["name_en"]} ({s["name_ar"]})': s["id"] for s in surahs}
    surah_by_id = {int(s["id"]): f'{s["number"]:03d} — {s["name_en"]} ({s["name_ar"]})' for s in surahs}
    surah_labels = list(surah_options.keys())

    st.markdown("### Entries")

    def _row_key(r: Dict[str, Any]) -> tuple:
        # Used to avoid re-inserting rows already saved today.
        label = str(r.get("Surat") or "").strip()
        page = int(r.get("Page Number") or 0)
        ayah = int(r.get("Ayah") or 0)
        how = str(r.get("Volume") or "").strip()
        return (label, page, ayah, how)

    # Load today's existing saved rows into the SAME data table.
    today = today_iso()
    init_key = f"jadeed_init::{student_id}::{today}"
    if st.session_state.get("jadeed_init_key") != init_key:
        existing = list_jadeed_entries(student_id=student_id, limit=200)
        todays = [r for r in existing if str(r.get("activity_date") or "") == today]
        loaded_rows = [
            {
                "Surat": surah_by_id.get(int((t.get("surahs") or {}).get("number") or 0), None)
                or surah_by_id.get(int(t.get("surah_id") or 0), surah_labels[0]),
                "Page Number": int(t.get("page_number") or 1),
                "Ayah": int(t.get("ayah_number") or 1),
                "Volume": str(t.get("volume") or "Kamil"),
            }
            for t in todays
        ]
        st.session_state.jadeed_rows = loaded_rows
        st.session_state.jadeed_existing_keys = {_row_key(r) for r in loaded_rows}
        st.session_state.jadeed_init_key = init_key

    import pandas as pd
    df = pd.DataFrame(st.session_state.jadeed_rows, columns=["Surat", "Page Number", "Ayah", "Volume"])
    
    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        width="stretch",
        column_config={
            "Surat": st.column_config.SelectboxColumn("Surat", options=surah_labels, required=True),
            "Page Number": st.column_config.NumberColumn("Page Number", min_value=1, step=1, required=True),
            "Ayah": st.column_config.NumberColumn("Ayah", min_value=1, step=1, required=True),
            "Volume": st.column_config.SelectboxColumn("Volume", options=["Ruba", "Nisf", "Sulus", "Kamil"], required=True),
        },
        key="jadeed_editor",
    )
    edited = edited_df.to_dict(orient="records")

    has_jadeed_today = len(edited) > 0

    if has_jadeed_today:
        if st.button("Save to Supabase", type="primary", width="stretch"):
            payload: List[Dict[str, Any]] = []
            for r in edited:
                label = (r.get("Surat") or "").strip()
                surah_id = surah_options.get(label)
                if not surah_id:
                    continue
                payload.append(
                    {
                        "surah_id": int(surah_id),
                        "page_number": int(r.get("Page Number") or 1),
                        "ayah_number": int(r.get("Ayah") or 1),
                        "volume": str(r.get("Volume") or "Kamil"),
                    }
                )

            insert_jadeed_rows(student_id=student_id, rows=payload)
            st.session_state.jadeed_flash = f"Saved {len(payload)} row(s) for today."
            st.session_state.pop("jadeed_init_key", None)  # force refresh from DB
            st.session_state.pop("jadeed_existing_keys", None)
            st.rerun()
    else:
        if st.button("No Jadeed today", type="primary", width="stretch"):
            insert_jadeed_rows(student_id=student_id, rows=[])
            st.session_state.jadeed_flash = "Marked: No Jadeed for today."
            st.rerun()

