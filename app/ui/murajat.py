from __future__ import annotations

import streamlit as st

from app.db import create_listening_session, get_session_counts, increment_mistake, list_surahs
from app.ui.shared import back_home_button, mistake_buttons, surah_selector
from app.ui.student import current_student_badge


def render_murajat() -> None:
    back_home_button()
    st.subheader("Murajat")
    current_student_badge()

    student_id = st.session_state.get("student_id")
    if not student_id:
        st.warning("Please select a student on Home first.")
        return

    surahs = list_surahs()
    surah_id, surah = surah_selector(surahs=surahs, key="murajat_surah")

    if surah_id is None:
        return

    if (
        "murajat_session_id" not in st.session_state
        or st.session_state.get("murajat_surah_id") != surah_id
        or st.session_state.get("murajat_student_id") != student_id
    ):
        st.session_state.murajat_surah_id = surah_id
        st.session_state.murajat_student_id = student_id
        session = create_listening_session(student_id=student_id, mode="murajat", surah_id=surah_id, page_number=None)
        st.session_state.murajat_session_id = session["id"]

    st.markdown(f"**Selected**: {surah['name_en']} ({surah['name_ar']})" if surah else "**Selected**: Surah")
    session_id = st.session_state.murajat_session_id

    counts = get_session_counts(session_id)

    def _on_click(kind: str) -> None:
        increment_mistake(session_id, kind)

    mistake_buttons(session_id=session_id, counts=counts, on_click=_on_click)

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("New session (same Surah)"):
            session = create_listening_session(student_id=student_id, mode="murajat", surah_id=surah_id, page_number=None)
            st.session_state.murajat_session_id = session["id"]
            st.rerun()
    with c2:
        if st.button("Change Surah"):
            st.session_state.pop("murajat_session_id", None)
            st.session_state.pop("murajat_surah_id", None)
            st.rerun()

