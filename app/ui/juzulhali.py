from __future__ import annotations

import streamlit as st

from app.db import create_listening_session, get_session_counts, increment_mistake
from app.ui.shared import back_home_button, mistake_buttons


def render_juzulhali() -> None:
    back_home_button()
    st.subheader("Juzulhali")

    page_number = st.number_input("Page number (1–20)", min_value=1, max_value=20, value=1, step=1)

    if "juzulhali_session_id" not in st.session_state or st.session_state.get("juzulhali_page_number") != page_number:
        st.session_state.juzulhali_page_number = page_number
        session = create_listening_session(mode="juzulhali", surah_id=None, page_number=int(page_number))
        st.session_state.juzulhali_session_id = session["id"]

    session_id = st.session_state.juzulhali_session_id
    counts = get_session_counts(session_id)

    def _on_click(kind: str) -> None:
        increment_mistake(session_id, kind)

    mistake_buttons(session_id=session_id, counts=counts, on_click=_on_click)

    st.divider()
    if st.button("New session (same page)"):
        session = create_listening_session(mode="juzulhali", surah_id=None, page_number=int(page_number))
        st.session_state.juzulhali_session_id = session["id"]
        st.rerun()

