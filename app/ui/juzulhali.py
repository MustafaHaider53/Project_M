from __future__ import annotations

import streamlit as st

from app.db import create_listening_session, get_session_counts, increment_mistake
from app.ui.shared import back_home_button, mistake_buttons
from app.ui.student import current_student_badge


def render_juzulhali() -> None:
    back_home_button()
    st.subheader("Juzulhali")
    current_student_badge()

    student_id = st.session_state.get("student_id")
    if not student_id:
        st.warning("Please select a student on Home first.")
        return

    page_number = st.number_input("Page number (1–20)", min_value=1, max_value=20, value=1, step=1)

    # Reset session ID if student or page changes
    if (
        st.session_state.get("juzulhali_page_number") != page_number
        or st.session_state.get("juzulhali_student_id") != student_id
    ):
        st.session_state.pop("juzulhali_session_id", None)
        st.session_state.pop("juzulhali_counts", None)
        st.session_state.pop("juzulhali_counts_session_id", None)
        st.session_state.juzulhali_page_number = page_number
        st.session_state.juzulhali_student_id = student_id

    session_id = st.session_state.get("juzulhali_session_id")
    if session_id:
        if "juzulhali_counts" not in st.session_state or st.session_state.get("juzulhali_counts_session_id") != session_id:
            st.session_state.juzulhali_counts = get_session_counts(session_id)
            st.session_state.juzulhali_counts_session_id = session_id
        counts = st.session_state.juzulhali_counts
    else:
        counts = {"talqeen": 0, "tanbeeh": 0, "repeat_mistake": 0, "mutashabehat": 0}

    def _on_click(kind: str) -> None:
        sid = st.session_state.get("juzulhali_session_id")
        if not sid:
            session = create_listening_session(student_id=student_id, mode="juzulhali", surah_id=None, page_number=int(page_number))
            sid = session["id"]
            st.session_state.juzulhali_session_id = sid
            st.session_state.juzulhali_counts = {"talqeen": 0, "tanbeeh": 0, "repeat_mistake": 0, "mutashabehat": 0}
            st.session_state.juzulhali_counts_session_id = sid
            
        local_counts = st.session_state.juzulhali_counts
        if kind == "talqeen":
            local_counts["talqeen"] += 1
        elif kind == "tanbeeh":
            local_counts["tanbeeh"] += 1
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
    if not session_id:
        # Show record button for 0 mistakes
        if st.button("Record Recitation (0 Mistakes)", type="primary", width="stretch"):
            session = create_listening_session(student_id=student_id, mode="juzulhali", surah_id=None, page_number=int(page_number))
            st.session_state.juzulhali_session_id = session["id"]
            st.session_state.pop("juzulhali_counts", None)
            st.session_state.pop("juzulhali_counts_session_id", None)
            st.toast("Recitation recorded with 0 mistakes.")
            st.rerun()
    else:
        # Show session controls when active
        if st.button("New session (same page)", width="stretch"):
            session = create_listening_session(student_id=student_id, mode="juzulhali", surah_id=None, page_number=int(page_number))
            st.session_state.juzulhali_session_id = session["id"]
            st.session_state.pop("juzulhali_counts", None)
            st.session_state.pop("juzulhali_counts_session_id", None)
            st.rerun()

