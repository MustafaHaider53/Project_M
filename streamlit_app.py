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

    st.iframe("""
        <script>
            (function() {
                const parentDoc = window.parent.document;
                
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
                                    parentDoc.body.classList.add('force-landscape');
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
                                parentDoc.body.classList.add('force-landscape');
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
                                    parentDoc.body.classList.remove('force-landscape');
                                    if (window.parent.screen && window.parent.screen.orientation && window.parent.screen.orientation.unlock) {
                                        window.parent.screen.orientation.unlock();
                                    }
                                });
                            } else if (parentDoc.webkitExitFullscreen) {
                                parentDoc.webkitExitFullscreen();
                                btn.textContent = '📱 Fullscreen';
                                parentDoc.body.classList.remove('force-landscape');
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
                            parentDoc.body.classList.add('force-landscape');
                        } else {
                            btn.textContent = '📱 Fullscreen';
                            parentDoc.body.classList.remove('force-landscape');
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
    """, height=1)

    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 8px;">
            <h2 style='font-size: 1.15rem; margin: 0; padding: 2px 0; color: var(--emerald); font-weight: bold; font-family: sans-serif;'>Al Madrasa-tus-Saifiyah-tul-Burhaniyah</h2>
            <button id="fullscreen-toggle-btn" style="background: linear-gradient(180deg, var(--emerald), #0a4d3a); color: white; border: none; border-radius: 8px; padding: 6px 12px; font-weight: bold; cursor: pointer; font-size: 0.75rem; box-shadow: 0 2px 4px rgba(0,0,0,0.12); display: flex; align-items: center; gap: 4px; font-family: sans-serif;">📱 Fullscreen</button>
        </div>
    """, unsafe_allow_html=True)

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
    
    cols = st.columns(7)
    with cols[0]:
        if st.button("👥 Change", use_container_width=True):
            st.session_state.student_id = None
            st.session_state.student_name = None
            st.session_state.page = "home"
            st.rerun()
            
    with cols[1]:
        if st.button("Murajat", type="primary" if current_page == "murajat" else "secondary", use_container_width=True):
            st.session_state.page = "murajat"
            st.rerun()
            
    with cols[2]:
        if st.button("Juzulhali", type="primary" if current_page == "juzulhali" else "secondary", use_container_width=True):
            st.session_state.page = "juzulhali"
            st.rerun()
            
    with cols[3]:
        if st.button("Jadeed", type="primary" if current_page == "jadeed" else "secondary", use_container_width=True):
            st.session_state.page = "jadeed"
            st.rerun()
            
    with cols[4]:
        if st.button("Takhteet", type="primary" if current_page == "takhteet" else "secondary", use_container_width=True):
            st.session_state.page = "takhteet"
            st.rerun()
            
    with cols[5]:
        if st.button("Email", type="primary" if current_page == "email" else "secondary", use_container_width=True):
            st.session_state.page = "email"
            st.rerun()
            
    with cols[6]:
        if st.button("Report", type="primary" if current_page == "report" else "secondary", use_container_width=True):
            st.session_state.page = "report"
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

