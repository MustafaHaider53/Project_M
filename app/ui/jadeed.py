from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st

from app.db import insert_jadeed_rows, list_surahs, mark_no_jadeed_today
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
    surah_labels = list(surah_options.keys())

    st.markdown("### Entries")

    if "jadeed_rows" not in st.session_state:
        st.session_state.jadeed_rows = [
            {"Surat": surah_labels[0], "Page Number": 1, "Ayah": 1, "How Much": "Full"}
        ]

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
                        "how_much": str(r.get("How Much") or "Full"),
                    }
                )

            insert_jadeed_rows(student_id=student_id, rows=payload)
            st.session_state.jadeed_flash = f"Saved {len(payload)} row(s) for today."
            st.session_state.jadeed_rows = [
                {"Surat": surah_labels[0], "Page Number": 1, "Ayah": 1, "How Much": "Full"}
            ]
            st.rerun()
    with c2:
        if st.button("Reset table", use_container_width=True):
            st.session_state.jadeed_rows = [
                {"Surat": surah_labels[0], "Page Number": 1, "Ayah": 1, "How Much": "Full"}
            ]
            st.rerun()
    with c3:
        if st.button("No Jadeed today", use_container_width=True):
            mark_no_jadeed_today(student_id=student_id)
            st.session_state.jadeed_flash = "Marked: No Jadeed for today."
            st.rerun()

