import streamlit as st

from app.ui.home import render_home
from app.ui.jadeed import render_jadeed
from app.ui.juzulhali import render_juzulhali
from app.ui.murajat import render_murajat


def main() -> None:
    st.set_page_config(page_title="Project M", layout="wide")

    st.title("Project M")
    st.caption("Murajat • Juzulhali • Jadeed")

    page = st.session_state.get("page", "home")
    if page == "home":
        render_home()
    elif page == "murajat":
        render_murajat()
    elif page == "juzulhali":
        render_juzulhali()
    elif page == "jadeed":
        render_jadeed()
    else:
        st.session_state.page = "home"
        st.rerun()


if __name__ == "__main__":
    main()

