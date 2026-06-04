import streamlit as st

from app.ui.home import render_home
from app.ui.jadeed import render_jadeed
from app.ui.juzulhali import render_juzulhali
from app.ui.murajat import render_murajat
from app.ui.report import render_report
from app.ui.style import apply_islamic_theme
from app.ui.takhteet import render_takhteet


def main() -> None:
    st.set_page_config(page_title="Al Madrasa-tus-Saifiyah-tul-Burhaniyah", layout="wide")
    apply_islamic_theme()

    st.title("Al Madrasa-tus-Saifiyah-tul-Burhaniyah")

    # 1. Check if student is selected
    student_id = st.session_state.get("student_id")
    
    from app.ui.student import require_student, current_student_badge
    
    if not student_id:
        require_student()
        return

    # 2. Show prominent student banner
    current_student_badge(force=True)

    # 3. Render Header Navigation buttons
    current_page = st.session_state.get("page", "home")
    
    cols = st.columns(6)
    with cols[0]:
        if st.button("👥 Change Student", width="stretch"):
            st.session_state.student_id = None
            st.session_state.student_name = None
            st.session_state.page = "home"
            st.rerun()
            
    with cols[1]:
        if st.button("Murajat", type="primary" if current_page == "murajat" else "secondary", width="stretch"):
            st.session_state.page = "murajat"
            st.rerun()
            
    with cols[2]:
        if st.button("Juzulhali", type="primary" if current_page == "juzulhali" else "secondary", width="stretch"):
            st.session_state.page = "juzulhali"
            st.rerun()
            
    with cols[3]:
        if st.button("Jadeed", type="primary" if current_page == "jadeed" else "secondary", width="stretch"):
            st.session_state.page = "jadeed"
            st.rerun()
            
    with cols[4]:
        if st.button("Takhteet", type="primary" if current_page == "takhteet" else "secondary", width="stretch"):
            st.session_state.page = "takhteet"
            st.rerun()
            
    with cols[5]:
        if st.button("Report", type="primary" if current_page == "report" else "secondary", width="stretch"):
            st.session_state.page = "report"
            st.rerun()
            
    st.markdown("---")

    # 4. Render content based on current page
    if current_page == "home":
        st.session_state.page = "murajat"
        st.rerun()
    elif current_page == "murajat":
        render_murajat()
    elif current_page == "juzulhali":
        render_juzulhali()
    elif current_page == "jadeed":
        render_jadeed()
    elif current_page == "takhteet":
        render_takhteet()
    elif current_page == "report":
        render_report()
    else:
        st.session_state.page = "home"
        st.rerun()


if __name__ == "__main__":
    main()

