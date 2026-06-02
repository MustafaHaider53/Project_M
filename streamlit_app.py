import streamlit as st

from app.ui.home import render_home
from app.ui.jadeed import render_jadeed
from app.ui.juzulhali import render_juzulhali
from app.ui.murajat import render_murajat
from app.ui.style import apply_islamic_theme


def main() -> None:
    st.set_page_config(page_title="Al Madrasa-tus-Saifiyah-tul-Burhaniyah", layout="wide")
    apply_islamic_theme()

    st.title("Al Madrasa-tus-Saifiyah-tul-Burhaniyah")
    # st.caption("Murajat • Juzulhali • Jadeed")

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

