import streamlit as st


def render_login() -> None:
    # Try to get credentials from st.secrets first, fallback to hardcoded values
    CORRECT_USERNAME = "mukhayyam"
    CORRECT_PASSWORD = "mukhayyam12"

    if "credentials" in st.secrets:
        CORRECT_USERNAME = st.secrets.credentials.get("username", CORRECT_USERNAME)
        CORRECT_PASSWORD = st.secrets.credentials.get("password", CORRECT_PASSWORD)
    elif "login_username" in st.secrets:
        CORRECT_USERNAME = st.secrets.get("login_username", CORRECT_USERNAME)
        CORRECT_PASSWORD = st.secrets.get("login_password", CORRECT_PASSWORD)

    st.markdown("<div style='height: 8vh;'></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container(border=True):
            st.markdown(
                """
                <div style="text-align: center; margin-bottom: 1.5rem;">
                    <h2 style="color: var(--emerald); font-family: 'Amiri', 'Noto Naskh Arabic', serif; font-size: 2rem; margin-bottom: 0.2rem; margin-top: 0.5rem;">Mukhayyam Login</h2>
                    <p style="color: var(--ink); opacity: 0.7; font-size: 0.9rem; margin-top: 0;">Sign in to access student recitation portal</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.form("login_form", border=False):
                username = st.text_input(
                    "Username",
                    placeholder="Enter username",
                    key="login_username_input",
                    autocomplete="username",
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter password",
                    key="login_password_input",
                    autocomplete="current-password",
                )

                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

                submitted = st.form_submit_button(
                    "Sign In", type="primary", use_container_width=True
                )

                if submitted:
                    if username.strip() == CORRECT_USERNAME and password == CORRECT_PASSWORD:
                        st.session_state.logged_in = True
                        st.session_state.login_error = None
                        st.rerun()
                    else:
                        st.session_state.login_error = "Invalid username or password."
                        st.rerun()

            if st.session_state.get("login_error"):
                st.error(st.session_state.login_error)
