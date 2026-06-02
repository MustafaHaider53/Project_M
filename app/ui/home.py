import streamlit as st

from app.db import get_rest


def render_home() -> None:
    rest = get_rest()
    if rest is None:
        st.warning("Supabase is not configured yet. Add SUPABASE_URL and SUPABASE_KEY in Streamlit secrets.")

    st.subheader("Choose a module")

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Murajat", use_container_width=True):
            st.session_state.page = "murajat"
            st.rerun()
    with c2:
        if st.button("Juzulhali", use_container_width=True):
            st.session_state.page = "juzulhali"
            st.rerun()
    with c3:
        if st.button("Jadeed", use_container_width=True):
            st.session_state.page = "jadeed"
            st.rerun()

