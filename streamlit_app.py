import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import streamlit as st

from app.ui.home import render_home
from app.ui.jadeed import render_jadeed
from app.ui.juzulhali import render_juzulhali
from app.ui.murajat import render_murajat
from app.ui.report import render_report
from app.ui.style import apply_islamic_theme
from app.ui.takhteet import render_takhteet
from app.ui.planner import render_planner


def main() -> None:
    st.set_page_config(page_title="Al Madrasa-tus-Saifiyah-tul-Burhaniyah", layout="wide")
    apply_islamic_theme()

    # Restore login from query parameter if present
    if not st.session_state.get("logged_in"):
        if st.query_params.get("logged_in") == "true":
            st.session_state.logged_in = True

    # Restore student and page from query parameters if logged in and not already set in session state
    if st.session_state.get("logged_in"):
        if not st.session_state.get("student_id") and st.query_params.get("student_id"):
            st.session_state.student_id = st.query_params.get("student_id")
            st.session_state.student_name = st.query_params.get("student_name")
            if st.query_params.get("page"):
                st.session_state.page = st.query_params.get("page")

    is_logged_in = "true" if st.session_state.get("logged_in") else "false"
    is_manual_logout = "true" if st.session_state.pop("manual_logout", False) else "false"

    iframe_js = """
        <script>
            (function() {
                const parentDoc = window.parent.document;
                const parentWin = window.parent;
                
                // Session Persistence Logic
                const isLoggedIn = {is_logged_in};
                const isManualLogout = {is_manual_logout};
                
                if (isManualLogout) {
                    parentWin.localStorage.removeItem('mukhayyam_logged_in');
                    const url = new URL(parentWin.location.href);
                    if (url.searchParams.has('logged_in')) {
                        url.searchParams.delete('logged_in');
                        parentWin.history.replaceState({}, '', url.toString());
                    }
                } else if (isLoggedIn) {
                    parentWin.localStorage.setItem('mukhayyam_logged_in', 'true');
                    const url = new URL(parentWin.location.href);
                    if (url.searchParams.get('logged_in') !== 'true') {
                        url.searchParams.set('logged_in', 'true');
                        parentWin.history.replaceState({}, '', url.toString());
                    }
                } else {
                    if (parentWin.localStorage.getItem('mukhayyam_logged_in') === 'true') {
                        const url = new URL(parentWin.location.href);
                        if (url.searchParams.get('logged_in') !== 'true') {
                            url.searchParams.set('logged_in', 'true');
                            parentWin.location.href = url.toString();
                        }
                    }
                }

                // Auto-blur all inputs on rerun to close mobile keyboard (immediate + delayed to handle React async renders)
                function forceBlur() {
                    try {
                        parentDoc.querySelectorAll('input, textarea, select').forEach(el => el.blur());
                        if (parentDoc.activeElement) {
                            parentDoc.activeElement.blur();
                        }
                    } catch (e) {}
                }
                forceBlur();
                setTimeout(forceBlur, 100);
                setTimeout(forceBlur, 300);
                setTimeout(forceBlur, 500);
                
                // Auto-scroll focused inputs into view for mobile landscape readability
                parentDoc.addEventListener('focusin', function(e) {
                    const target = e.target;
                    if (target && (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA')) {
                        setTimeout(() => {
                            try {
                                target.scrollIntoView({ block: 'center', behavior: 'smooth' });
                            } catch (err) {}
                        }, 250);
                    }
                });
                
                // Wake Lock API
                let wakeLock = null;
                async function requestWakeLock() {
                    try {
                        if ('wakeLock' in window.parent.navigator) {
                            wakeLock = await window.parent.navigator.wakeLock.request('screen');
                            console.log('Screen Wake Lock acquired');
                        }
                    } catch (err) {
                        console.warn('Wake Lock request failed:', err);
                    }
                }
                parentDoc.addEventListener('visibilitychange', () => {
                    if (parentDoc.visibilityState === 'visible') requestWakeLock();
                });
                ['click', 'touchstart', 'scroll'].forEach(e => {
                    parentDoc.addEventListener(e, requestWakeLock, { once: true });
                });
                requestWakeLock();

                // Fullscreen Toggle
                parentDoc.addEventListener('click', function(e) {
                    const btn = e.target.closest('#fullscreen-toggle-btn');
                    if (btn) {
                        const docEl = parentDoc.documentElement;
                        const isFull = parentDoc.fullscreenElement ? true : (parentDoc.webkitFullscreenElement ? true : false);
                        if (!isFull) {
                            if (docEl.requestFullscreen) {
                                docEl.requestFullscreen().then(() => {
                                    btn.textContent = '📱 Exit Full';
                                    if (window.parent.screen && window.parent.screen.orientation && window.parent.screen.orientation.lock) {
                                        window.parent.screen.orientation.lock('landscape').catch(err => {
                                            console.warn('Orientation lock failed:', err);
                                        });
                                    }
                                }).catch(err => {
                                    console.warn('Fullscreen request failed:', err);
                                });
                            } else if (docEl.webkitRequestFullscreen) {
                                docEl.webkitRequestFullscreen();
                                btn.textContent = '📱 Exit Full';
                                if (window.parent.screen && window.parent.screen.orientation && window.parent.screen.orientation.lock) {
                                    window.parent.screen.orientation.lock('landscape').catch(err => {
                                        console.warn('Orientation lock failed:', err);
                                    });
                                }
                            }
                        } else {
                            if (parentDoc.exitFullscreen) {
                                parentDoc.exitFullscreen().then(() => {
                                    btn.textContent = '📱 Fullscreen';
                                    if (window.parent.screen && window.parent.screen.orientation && window.parent.screen.orientation.unlock) {
                                        window.parent.screen.orientation.unlock();
                                    }
                                });
                            } else if (parentDoc.webkitExitFullscreen) {
                                parentDoc.webkitExitFullscreen();
                                btn.textContent = '📱 Fullscreen';
                                if (window.parent.screen && window.parent.screen.orientation && window.parent.screen.orientation.unlock) {
                                    window.parent.screen.orientation.unlock();
                                }
                            }
                        }
                    }
                });

                function updateFullscreenButton() {
                    const btn = parentDoc.getElementById('fullscreen-toggle-btn');
                    if (btn) {
                        const isFull = parentDoc.fullscreenElement ? true : (parentDoc.webkitFullscreenElement ? true : false);
                        if (isFull) {
                            btn.textContent = '📱 Exit Full';
                        } else {
                            btn.textContent = '📱 Fullscreen';
                            if (window.parent.screen && window.parent.screen.orientation && window.parent.screen.orientation.unlock) {
                                window.parent.screen.orientation.unlock();
                            }
                        }
                    }
                }

                parentDoc.addEventListener('fullscreenchange', updateFullscreenButton);
                parentDoc.addEventListener('webkitfullscreenchange', updateFullscreenButton);
            })();
        </script>
    """
    st.iframe(iframe_js.replace("{is_logged_in}", is_logged_in).replace("{is_manual_logout}", is_manual_logout), height=1)

    # 0. Check if user is logged in
    if not st.session_state.get("logged_in"):
        header_cols = st.columns([8.5, 1.5])
        with header_cols[0]:
            st.markdown("<h2 style='font-size: 1.15rem; margin: 0; padding: 2px 0; color: var(--emerald); font-weight: bold; font-family: sans-serif;'>Al Madrasa-tus-Saifiyah-tul-Burhaniyah</h2>", unsafe_allow_html=True)
        with header_cols[1]:
            st.markdown('<button id="fullscreen-toggle-btn" style="width: 100%; background: linear-gradient(180deg, var(--emerald), #0a4d3a); color: white; border: none; border-radius: 8px; padding: 2px 4px; font-weight: bold; cursor: pointer; font-size: 10px; height: 26px; min-height: 26px; line-height: 1.2; display: flex; align-items: center; justify-content: center; gap: 4px; font-family: sans-serif; box-shadow: 0 2px 4px rgba(0,0,0,0.12);">📱 Fullscreen</button>', unsafe_allow_html=True)
            
        from app.ui.login import render_login
        render_login()
        return

    # Render header when logged in
    user_role = st.session_state.get("user_role", "admin")
    if user_role == "parent":
        header_cols = st.columns([7, 1.5, 1.5])
        with header_cols[0]:
            st.markdown("<h2 style='font-size: 1.15rem; margin: 0; padding: 2px 0; color: var(--emerald); font-weight: bold; font-family: sans-serif;'>Al Madrasa-tus-Saifiyah-tul-Burhaniyah</h2>", unsafe_allow_html=True)
        with header_cols[1]:
            st.markdown('<button id="fullscreen-toggle-btn" style="width: 100%; background: linear-gradient(180deg, var(--emerald), #0a4d3a); color: white; border: none; border-radius: 8px; padding: 2px 4px; font-weight: bold; cursor: pointer; font-size: 10px; height: 26px; min-height: 26px; line-height: 1.2; display: flex; align-items: center; justify-content: center; gap: 4px; font-family: sans-serif; box-shadow: 0 2px 4px rgba(0,0,0,0.12);">📱 Fullscreen</button>', unsafe_allow_html=True)
        with header_cols[2]:
            if st.button("🔒 Logout", use_container_width=True, key="header_logout_btn"):
                st.session_state.logged_in = False
                st.session_state.student_id = None
                st.session_state.student_name = None
                st.session_state.page = "home"
                st.session_state.user_role = "admin"
                st.query_params.clear()
                st.session_state.manual_logout = True
                st.rerun()

        # Render parent report content directly and return
        from app.ui.parent_report import render_parent_report
        render_parent_report()
        return

    # Render admin header when logged in
    header_cols = st.columns([7, 1.5, 1.5])
    with header_cols[0]:
        st.markdown("<h2 style='font-size: 1.15rem; margin: 0; padding: 2px 0; color: var(--emerald); font-weight: bold; font-family: sans-serif;'>Al Madrasa-tus-Saifiyah-tul-Burhaniyah</h2>", unsafe_allow_html=True)
    with header_cols[1]:
        st.markdown('<button id="fullscreen-toggle-btn" style="width: 100%; background: linear-gradient(180deg, var(--emerald), #0a4d3a); color: white; border: none; border-radius: 8px; padding: 2px 4px; font-weight: bold; cursor: pointer; font-size: 10px; height: 26px; min-height: 26px; line-height: 1.2; display: flex; align-items: center; justify-content: center; gap: 4px; font-family: sans-serif; box-shadow: 0 2px 4px rgba(0,0,0,0.12);">📱 Fullscreen</button>', unsafe_allow_html=True)
    with header_cols[2]:
        if st.button("🔒 Logout", use_container_width=True, key="header_logout_btn"):
            st.session_state.logged_in = False
            st.session_state.student_id = None
            st.session_state.student_name = None
            st.session_state.page = "home"
            st.query_params.clear()
            st.session_state.manual_logout = True
            st.rerun()

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
    
    cols = st.columns(8)
    with cols[0]:
        if st.button("👥 Change", use_container_width=True):
            st.session_state.student_id = None
            st.session_state.student_name = None
            st.session_state.page = "home"
            st.query_params.pop("student_id", None)
            st.query_params.pop("student_name", None)
            st.query_params.pop("page", None)
            st.rerun()
            
    with cols[1]:
        if st.button("Murajat", type="primary" if current_page == "murajat" else "secondary", use_container_width=True):
            st.session_state.page = "murajat"
            st.query_params["page"] = "murajat"
            st.rerun()
            
    with cols[2]:
        if st.button("Juzulhali", type="primary" if current_page == "juzulhali" else "secondary", use_container_width=True):
            st.session_state.page = "juzulhali"
            st.query_params["page"] = "juzulhali"
            st.rerun()
            
    with cols[3]:
        if st.button("Jadeed", type="primary" if current_page == "jadeed" else "secondary", use_container_width=True):
            st.session_state.page = "jadeed"
            st.query_params["page"] = "jadeed"
            st.rerun()
            
    with cols[4]:
        if st.button("Takhteet", type="primary" if current_page == "takhteet" else "secondary", use_container_width=True):
            st.session_state.page = "takhteet"
            st.query_params["page"] = "takhteet"
            st.rerun()

    with cols[5]:
        if st.button("Planner", type="primary" if current_page == "planner" else "secondary", use_container_width=True):
            st.session_state.page = "planner"
            st.query_params["page"] = "planner"
            st.rerun()
            
    with cols[6]:
        if st.button("Email", type="primary" if current_page == "email" else "secondary", use_container_width=True):
            st.session_state.page = "email"
            st.query_params["page"] = "email"
            st.rerun()
            
    with cols[7]:
        if st.button("Report", type="primary" if current_page == "report" else "secondary", use_container_width=True):
            st.session_state.page = "report"
            st.query_params["page"] = "report"
            st.rerun()
            


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
    elif current_page == "planner":
        render_planner()
    elif current_page == "email":
        from app.ui.email_page import render_email_page
        render_email_page()
    elif current_page == "report":
        render_report()
    else:
        st.session_state.page = "home"
        st.rerun()


if __name__ == "__main__":
    main()

