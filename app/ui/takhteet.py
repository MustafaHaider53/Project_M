from __future__ import annotations

import streamlit as st

from app.db import get_takhteet_today, upsert_takhteet_today
from app.ui.shared import back_home_button
from app.ui.student import current_student_badge


def render_takhteet() -> None:
    back_home_button()
    st.subheader("Homework")
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

    col1, col2 = st.columns([1.3, 1])
    with col1:
        if st.button("💾 Save Homework", type="primary", width="stretch"):
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
            st.success("Homework saved for today.")

    with col2:
        if st.button("✉️ Send Email", width="stretch"):
            with st.spinner("Saving & preparing email..."):
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

                import threading
                from app.db import get_student_daily_summary, send_single_student_daily_email

                summary = get_student_daily_summary(student_id=student_id, date_str=today)
                recipient = summary.get("student_email") if summary else None

                if not recipient:
                    st.warning("⚠️ Student has no registered email.")
                else:
                    threading.Thread(
                        target=send_single_student_daily_email,
                        kwargs={"student_id": student_id, "date_str": today},
                        daemon=True,
                    ).start()
                    st.success(f"✉️ Email dispatch started for {recipient}!")

    # Generous bottom clearance spacer so nothing is hidden behind thumb dock
    st.markdown("<div style='height: 160px;'></div>", unsafe_allow_html=True)

