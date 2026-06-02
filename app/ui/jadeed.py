from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st

from app.db import insert_jadeed_rows, list_jadeed_entries, list_surahs, mark_no_jadeed_today, today_iso
from app.ui.shared import back_home_button
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
        how = str(r.get("How Much") or "").strip()
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
                "How Much": str(t.get("how_much") or "Full"),
            }
            for t in todays
        ]
        st.session_state.jadeed_rows = loaded_rows
        st.session_state.jadeed_existing_keys = {_row_key(r) for r in loaded_rows}
        st.session_state.jadeed_init_key = init_key

    edited = st.data_editor(
        st.session_state.jadeed_rows,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Surat": st.column_config.SelectboxColumn("Surat", options=surah_labels, required=True),
            "Page Number": st.column_config.NumberColumn("Page Number", min_value=1, step=1, required=True),
            "Ayah": st.column_config.NumberColumn("Ayah", min_value=1, step=1, required=True),
            "How Much": st.column_config.SelectboxColumn("How Much", options=["Half", "Full"], required=True),
        },
        key="jadeed_editor",
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Save to Supabase", type="primary", use_container_width=True):
            payload: List[Dict[str, Any]] = []
            existing_keys = set(st.session_state.get("jadeed_existing_keys") or set())
            for r in edited:
                # Don't re-save rows already saved today
                if _row_key(r) in existing_keys:
                    continue
                label = (r.get("Surat") or "").strip()
                surah_id = surah_options.get(label)
                if not surah_id:
                    continue
                payload.append(
                    {
                        "surah_id": int(surah_id),
                        "page_number": int(r.get("Page Number") or 1),
                        "ayah_number": int(r.get("Ayah") or 1),
                        "how_much": str(r.get("How Much") or "Full"),
                    }
                )

            insert_jadeed_rows(student_id=student_id, rows=payload)
            st.session_state.jadeed_flash = f"Saved {len(payload)} row(s) for today."
            st.session_state.pop("jadeed_init_key", None)  # force refresh from DB
            st.session_state.pop("jadeed_existing_keys", None)
            st.rerun()
    with c2:
        if st.button("Reset table", use_container_width=True):
            st.session_state.jadeed_rows = []
            # keep init key so reset means "start adding new" without reloading
            st.rerun()
    with c3:
        if st.button("No Jadeed today", use_container_width=True):
            mark_no_jadeed_today(student_id=student_id)
            st.session_state.jadeed_flash = "Marked: No Jadeed for today."
            st.rerun()

