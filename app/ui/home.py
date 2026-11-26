import streamlit as st

from app.db import get_rest
from app.ui.student import current_student_badge, require_student


def render_home() -> None:
    rest = get_rest()
    if rest is None:
        st.warning("Supabase is not configured yet. Add SUPABASE_URL and SUPABASE_KEY in Streamlit secrets.")
        return

    student_id = require_student()
    if not student_id:
        return

    current_student_badge()
    
    from app.ui.shared import show_previous_takhteet
    show_previous_takhteet(student_id)

    st.subheader("Choose a module")

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        if st.button("Murajat", width="stretch"):
            st.session_state.page = "murajat"
            st.rerun()
    with c2:
        if st.button("Juzulhali", width="stretch"):
            st.session_state.page = "juzulhali"
            st.rerun()
    with c3:
        if st.button("Jadeed", width="stretch"):
            st.session_state.page = "jadeed"
            st.rerun()
    with c4:
        if st.button("Homework", width="stretch"):
            st.session_state.page = "takhteet"
            st.rerun()
    with c5:
        if st.button("Report", width="stretch"):
            st.session_state.page = "report"
            st.rerun()

