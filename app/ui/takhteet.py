from __future__ import annotations

import streamlit as st

from app.db import get_takhteet_today, upsert_takhteet_today
from app.ui.shared import back_home_button
from app.ui.student import current_student_badge


def render_takhteet() -> None:
    back_home_button()
    st.subheader("Takhteet (Homework)")
    st.caption("Daily homework notes for Murajat, Juzulhali, and Jadeed.")
    current_student_badge()

    student_id = st.session_state.get("student_id")
    if not student_id:
        st.warning("Please select a student on Home first.")
        return

    from app.db import today_iso
    today = today_iso()
    init_key = f"takhteet_init::{student_id}::{today}"
    if st.session_state.get("takhteet_init_key") != init_key:
        with st.spinner("Loading today's homework..."):
            st.session_state.takhteet_today = get_takhteet_today(student_id=student_id) or {}
        st.session_state.takhteet_init_key = init_key

    existing = st.session_state.takhteet_today
    default_m = existing.get("murajat_text_raw", "")
    default_jh = existing.get("juzulhali_text_raw", "")
    default_j = existing.get("jadeed_text_raw", "")

    murajat_text = st.text_area("Murajat", value=default_m, height=120, key="takhteet_murajat")
    juzulhali_text = st.text_area("Juzulhali", value=default_jh, height=120, key="takhteet_juzulhali")
    jadeed_text = st.text_area("Jadeed", value=default_j, height=120, key="takhteet_jadeed")

    if st.button("Save Takhteet", type="primary", width="stretch"):
        with st.spinner("Saving homework..."):
            upsert_takhteet_today(
                student_id=student_id,
                murajat_text_raw=murajat_text,
                juzulhali_text_raw=juzulhali_text,
                jadeed_text_raw=jadeed_text,
            )
        st.session_state.takhteet_today = {
            "murajat_text_raw": murajat_text,
            "juzulhali_text_raw": juzulhali_text,
            "jadeed_text_raw": jadeed_text,
        }
        cache_key = f"prev_takhteet_{student_id}"
        if cache_key in st.session_state:
            del st.session_state[cache_key]
        st.success("Takhteet saved for today.")

