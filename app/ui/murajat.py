from __future__ import annotations

import streamlit as st

from app.db import create_listening_session, get_session_counts, increment_mistake, list_surahs
from app.ui.shared import back_home_button, mistake_buttons, surah_selector, show_previous_takhteet
from app.ui.student import current_student_badge


def render_murajat() -> None:
    back_home_button()
    st.subheader("Murajat")
    current_student_badge()

    student_id = st.session_state.get("student_id")
    if not student_id:
        st.warning("Please select a student on Home first.")
        return

    show_previous_takhteet(student_id)

    surahs = list_surahs()
    surah_id, surah = surah_selector(surahs=surahs, key="murajat_surah")

    if surah_id is None:
        st.info("Please select a Surah to start Murajat recitation.")
        return

    # Reset session ID if student or surah changes
    if (
        st.session_state.get("murajat_surah_id") != surah_id
        or st.session_state.get("murajat_student_id") != student_id
        or not st.session_state.get("murajat_session_id")
    ):
        st.session_state.murajat_surah_id = surah_id
        st.session_state.murajat_student_id = student_id
        # Automatically create session
        session = create_listening_session(student_id=student_id, mode="murajat", surah_id=surah_id, page_number=None)
        st.session_state.murajat_session_id = session["id"]
        st.session_state.pop("murajat_counts", None)
        st.session_state.pop("murajat_counts_session_id", None)

    st.markdown(f"**Selected**: {surah['name_en']} ({surah['name_ar']})" if surah else "**Selected**: Surah")
    session_id = st.session_state.get("murajat_session_id")

    if session_id:
        if "murajat_counts" not in st.session_state or st.session_state.get("murajat_counts_session_id") != session_id:
            st.session_state.murajat_counts = get_session_counts(session_id)
            st.session_state.murajat_counts_session_id = session_id
        counts = st.session_state.murajat_counts
    else:
        counts = {"talqeen": 0, "tanbeeh": 0, "repeat_mistake": 0, "mutashabehat": 0, "irab": 0}

    def _on_click(kind: str) -> None:
        sid = st.session_state.get("murajat_session_id")
        if not sid:
            session = create_listening_session(student_id=student_id, mode="murajat", surah_id=surah_id, page_number=None)
            sid = session["id"]
            st.session_state.murajat_session_id = sid
            st.session_state.murajat_counts = {"talqeen": 0, "tanbeeh": 0, "repeat_mistake": 0, "mutashabehat": 0, "irab": 0}
            st.session_state.murajat_counts_session_id = sid
            
        if "murajat_counts" not in st.session_state or st.session_state.get("murajat_counts_session_id") != sid:
            st.session_state.murajat_counts = get_session_counts(sid)
            st.session_state.murajat_counts_session_id = sid
            
        local_counts = st.session_state.murajat_counts
        if kind == "talqeen":
            local_counts["talqeen"] += 1
        elif kind == "tanbeeh":
            local_counts["tanbeeh"] += 1
        elif kind == "irab":
            local_counts["irab"] += 1
            local_counts["talqeen"] += 1
        elif kind == "repeat_mistake":
            local_counts["repeat_mistake"] += 1
            local_counts["talqeen"] += 1
        elif kind == "mutashabehat":
            local_counts["mutashabehat"] += 1
            local_counts["talqeen"] += 1
            
        from app.db import increment_mistake_bg
        increment_mistake_bg(sid, kind, local_counts)

    mistake_buttons(session_id=session_id or "", counts=counts, on_click=_on_click)

    st.divider()
    # Show session controls when active
    c1, _, c2 = st.columns([2, 5, 2])
    with c1:
        if st.button("New session (Same Surah)", width="stretch"):
            session = create_listening_session(student_id=student_id, mode="murajat", surah_id=surah_id, page_number=None)
            st.session_state.murajat_session_id = session["id"]
            st.session_state.pop("murajat_counts", None)
            st.session_state.pop("murajat_counts_session_id", None)
            st.rerun()
    with c2:
        if st.button("Change Surah", width="stretch"):
            st.session_state.pop("murajat_session_id", None)
            st.session_state.pop("murajat_surah_id", None)
            st.session_state.pop("murajat_counts", None)
            st.session_state.pop("murajat_counts_session_id", None)
            st.rerun()

