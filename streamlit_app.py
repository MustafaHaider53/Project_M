import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import streamlit as st

from app.ui.style import apply_islamic_theme


def main() -> None:
    st.set_page_config(page_title="Al Madrasa-tus-Saifiyah-tul-Burhaniyah", layout="wide")
    apply_islamic_theme()

    from app.ui.shared import verify_session_signature, generate_session_signature

    # Restore login and user role from query parameters if present and signature is valid
    if not st.session_state.get("logged_in"):
        if st.query_params.get("logged_in") == "true":
            user_role = st.query_params.get("user_role") or "admin"
            student_id = st.query_params.get("student_id") or ""
            teacher_id = st.query_params.get("teacher_id") or ""
            teacher_name = st.query_params.get("teacher_name") or ""
            teacher_username = st.query_params.get("teacher_username") or ""
            sig = st.query_params.get("sig") or ""
            
            if verify_session_signature(user_role, student_id, sig, teacher_id=teacher_id):
                st.session_state.logged_in = True
                st.session_state.user_role = user_role
                if teacher_id:
                    st.session_state.teacher_id = teacher_id
                    st.session_state.teacher_name = teacher_name
                    st.session_state.teacher_username = teacher_username
            else:
                # Invalid signature! Wipe all parameters immediately to prevent bypass
                st.query_params.clear()
                st.session_state.logged_in = False
                st.session_state.user_role = None
                st.session_state.student_id = None
                st.session_state.student_name = None
                st.session_state.teacher_id = None
                st.session_state.teacher_name = None
                st.session_state.teacher_username = None

    # Extra security validation: if logged in but query params have a signature, make sure it matches
    if st.session_state.get("logged_in"):
        user_role = st.session_state.get("user_role") or "admin"
        student_id = st.session_state.get("student_id") or ""
        teacher_id = st.session_state.get("teacher_id") or ""
        sig = st.query_params.get("sig") or ""
        if sig and not verify_session_signature(user_role, student_id, sig, teacher_id=teacher_id):
            # Signature mismatch! Force logout
            st.query_params.clear()
            st.session_state.logged_in = False
            st.session_state.user_role = None
            st.session_state.student_id = None
            st.session_state.student_name = None
            st.session_state.teacher_id = None
            st.session_state.teacher_name = None
            st.session_state.teacher_username = None
            st.rerun()

    # Restore student and page from query parameters if logged in and not already set in session state
    if st.session_state.get("logged_in"):
        if not st.session_state.get("student_id") and st.query_params.get("student_id"):
            st.session_state.student_id = st.query_params.get("student_id")
            st.session_state.student_name = st.query_params.get("student_name")
            if st.query_params.get("page"):
                st.session_state.page = st.query_params.get("page")
        if not st.session_state.get("user_role") and st.query_params.get("user_role"):
            st.session_state.user_role = st.query_params.get("user_role")
        if not st.session_state.get("teacher_id") and st.query_params.get("teacher_id"):
            st.session_state.teacher_id = st.query_params.get("teacher_id")
            st.session_state.teacher_name = st.query_params.get("teacher_name")
            st.session_state.teacher_username = st.query_params.get("teacher_username")

    is_logged_in = "true" if st.session_state.get("logged_in") else "false"
    is_manual_logout = "true" if st.session_state.pop("manual_logout", False) else "false"
    user_role_val = st.session_state.get("user_role") or "admin"
    student_id_val = st.session_state.get("student_id") or ""
    student_name_val = st.session_state.get("student_name") or ""
    teacher_id_val = st.session_state.get("teacher_id") or ""
    teacher_name_val = st.session_state.get("teacher_name") or ""
    teacher_username_val = st.session_state.get("teacher_username") or ""
    sig_val = st.query_params.get("sig") or ""
    if st.session_state.get("logged_in") and not sig_val:
        sig_val = generate_session_signature(user_role_val, student_id_val, teacher_id=teacher_id_val)

    iframe_js = """
        <script>
            (function() {
                let parentDoc = null;
                let parentWin = null;
                try {
                    parentDoc = window.parent.document;
                    parentWin = window.parent;
                } catch (e) {
                    // Blocked cross-origin or strict WebKit iframe access
                    return;
                }
                if (!parentDoc || !parentWin) return;

                // Safe localStorage wrapper to prevent SecurityError / QuotaExceededError on iOS WebKit & Private Browsing
                const safeStorage = {
                    getItem: function(key) {
                        try {
                            return (parentWin.localStorage && typeof parentWin.localStorage.getItem === 'function') 
                                ? parentWin.localStorage.getItem(key) : null;
                        } catch (e) {
                            return null;
                        }
                    },
                    setItem: function(key, val) {
                        try {
                            if (parentWin.localStorage && typeof parentWin.localStorage.setItem === 'function') {
                                parentWin.localStorage.setItem(key, val);
                            }
                        } catch (e) {}
                    },
                    removeItem: function(key) {
                        try {
                            if (parentWin.localStorage && typeof parentWin.localStorage.removeItem === 'function') {
                                parentWin.localStorage.removeItem(key);
                            }
                        } catch (e) {}
                    }
                };
                
                // Session Persistence Logic
                try {
                    const isLoggedIn = {is_logged_in};
                    const isManualLogout = {is_manual_logout};
                    const userRole = "{user_role}";
                    const studentId = "{student_id}";
                    const studentName = "{student_name}";
                    const teacherId = "{teacher_id}";
                    const teacherName = "{teacher_name}";
                    const teacherUsername = "{teacher_username}";
                    const sig = "{sig}";
                    
                    if (isManualLogout) {
                        safeStorage.removeItem('mukhayyam_logged_in');
                        safeStorage.removeItem('mukhayyam_user_role');
                        safeStorage.removeItem('mukhayyam_student_id');
                        safeStorage.removeItem('mukhayyam_student_name');
                        safeStorage.removeItem('mukhayyam_teacher_id');
                        safeStorage.removeItem('mukhayyam_teacher_name');
                        safeStorage.removeItem('mukhayyam_teacher_username');
                        safeStorage.removeItem('mukhayyam_sig');
                        
                        try {
                            const url = new URL(parentWin.location.href);
                            url.searchParams.delete('logged_in');
                            url.searchParams.delete('user_role');
                            url.searchParams.delete('student_id');
                            url.searchParams.delete('student_name');
                            url.searchParams.delete('teacher_id');
                            url.searchParams.delete('teacher_name');
                            url.searchParams.delete('teacher_username');
                            url.searchParams.delete('page');
                            url.searchParams.delete('sig');
                            parentWin.history.replaceState({}, '', url.toString());
                        } catch (err) {}
                    } else if (isLoggedIn) {
                        safeStorage.setItem('mukhayyam_logged_in', 'true');
                        safeStorage.setItem('mukhayyam_user_role', userRole);
                        safeStorage.setItem('mukhayyam_sig', sig);
                        if (studentId) {
                            safeStorage.setItem('mukhayyam_student_id', studentId);
                            safeStorage.setItem('mukhayyam_student_name', studentName);
                        } else {
                            safeStorage.removeItem('mukhayyam_student_id');
                            safeStorage.removeItem('mukhayyam_student_name');
                        }
                        if (teacherId) {
                            safeStorage.setItem('mukhayyam_teacher_id', teacherId);
                            safeStorage.setItem('mukhayyam_teacher_name', teacherName);
                            safeStorage.setItem('mukhayyam_teacher_username', teacherUsername);
                        } else {
                            safeStorage.removeItem('mukhayyam_teacher_id');
                            safeStorage.removeItem('mukhayyam_teacher_name');
                            safeStorage.removeItem('mukhayyam_teacher_username');
                        }
                        
                        try {
                            const url = new URL(parentWin.location.href);
                            let urlChanged = false;
                            
                            if (url.searchParams.get('logged_in') !== 'true') {
                                url.searchParams.set('logged_in', 'true');
                                urlChanged = true;
                            }
                            if (url.searchParams.get('user_role') !== userRole) {
                                url.searchParams.set('user_role', userRole);
                                urlChanged = true;
                            }
                            if (url.searchParams.get('sig') !== sig) {
                                url.searchParams.set('sig', sig);
                                urlChanged = true;
                            }
                            if (studentId && url.searchParams.get('student_id') !== studentId) {
                                url.searchParams.set('student_id', studentId);
                                url.searchParams.set('student_name', studentName);
                                urlChanged = true;
                            }
                            if (teacherId && url.searchParams.get('teacher_id') !== teacherId) {
                                url.searchParams.set('teacher_id', teacherId);
                                url.searchParams.set('teacher_name', teacherName);
                                url.searchParams.set('teacher_username', teacherUsername);
                                urlChanged = true;
                            }
                            
                            if (urlChanged) {
                                parentWin.history.replaceState({}, '', url.toString());
                            }
                        } catch (err) {}
                    } else {
                        if (safeStorage.getItem('mukhayyam_logged_in') === 'true') {
                            try {
                                const url = new URL(parentWin.location.href);
                                const storedRole = safeStorage.getItem('mukhayyam_user_role') || 'admin';
                                const storedStudentId = safeStorage.getItem('mukhayyam_student_id') || '';
                                const storedStudentName = safeStorage.getItem('mukhayyam_student_name') || '';
                                const storedTeacherId = safeStorage.getItem('mukhayyam_teacher_id') || '';
                                const storedTeacherName = safeStorage.getItem('mukhayyam_teacher_name') || '';
                                const storedTeacherUsername = safeStorage.getItem('mukhayyam_teacher_username') || '';
                                const storedSig = safeStorage.getItem('mukhayyam_sig') || '';
                                
                                let urlChanged = false;
                                if (url.searchParams.get('logged_in') !== 'true') {
                                    url.searchParams.set('logged_in', 'true');
                                    urlChanged = true;
                                }
                                if (url.searchParams.get('user_role') !== storedRole) {
                                    url.searchParams.set('user_role', storedRole);
                                    urlChanged = true;
                                }
                                if (url.searchParams.get('sig') !== storedSig) {
                                    url.searchParams.set('sig', storedSig);
                                    urlChanged = true;
                                }
                                if (storedStudentId && url.searchParams.get('student_id') !== storedStudentId) {
                                    url.searchParams.set('student_id', storedStudentId);
                                    url.searchParams.set('student_name', storedStudentName);
                                    urlChanged = true;
                                }
                                if (storedTeacherId && url.searchParams.get('teacher_id') !== storedTeacherId) {
                                    url.searchParams.set('teacher_id', storedTeacherId);
                                    url.searchParams.set('teacher_name', storedTeacherName);
                                    url.searchParams.set('teacher_username', storedTeacherUsername);
                                    urlChanged = true;
                                }
                                
                                if (urlChanged) {
                                    parentWin.location.href = url.toString();
                                }
                            } catch (err) {}
                        }
                    }
                } catch (persistErr) {
                    console.warn('Session persistence error caught safely:', persistErr);
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
                try {
                    parentDoc.addEventListener('focusin', function(e) {
                        try {
                            const target = e.target;
                            if (target && (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA')) {
                                setTimeout(() => {
                                    try {
                                        target.scrollIntoView({ block: 'center', behavior: 'smooth' });
                                    } catch (err) {}
                                }, 250);
                            }
                        } catch (err) {}
                    });
                } catch (err) {}
                
                // Wake Lock API
                let wakeLock = null;
                async function requestWakeLock() {
                    try {
                        if (parentWin.navigator && 'wakeLock' in parentWin.navigator) {
                            wakeLock = await parentWin.navigator.wakeLock.request('screen');
                            console.log('Screen Wake Lock acquired');
                        }
                    } catch (err) {
                        console.warn('Wake Lock request failed:', err);
                    }
                }
                try {
                    parentDoc.addEventListener('visibilitychange', () => {
                        try {
                            if (parentDoc.visibilityState === 'visible') requestWakeLock();
                        } catch (err) {}
                    });
                    ['click', 'touchstart', 'scroll'].forEach(e => {
                        try {
                            parentDoc.addEventListener(e, requestWakeLock, { once: true });
                        } catch (err) {}
                    });
                    requestWakeLock();
                } catch (err) {}

                // Fullscreen Toggle
                try {
                    parentDoc.addEventListener('click', function(e) {
                        try {
                            const btn = e.target.closest('#fullscreen-toggle-btn');
                            if (btn) {
                                const docEl = parentDoc.documentElement;
                                const isFull = parentDoc.fullscreenElement ? true : (parentDoc.webkitFullscreenElement ? true : false);
                                if (!isFull) {
                                    if (docEl.requestFullscreen) {
                                        docEl.requestFullscreen().then(() => {
                                            btn.textContent = '📱 Exit Full';
                                            if (parentWin.screen && parentWin.screen.orientation && parentWin.screen.orientation.lock) {
                                                parentWin.screen.orientation.lock('landscape').catch(err => {
                                                    console.warn('Orientation lock failed:', err);
                                                });
                                            }
                                        }).catch(err => {
                                            console.warn('Fullscreen request failed:', err);
                                        });
                                    } else if (docEl.webkitRequestFullscreen) {
                                        docEl.webkitRequestFullscreen();
                                        btn.textContent = '📱 Exit Full';
                                        if (parentWin.screen && parentWin.screen.orientation && parentWin.screen.orientation.lock) {
                                            parentWin.screen.orientation.lock('landscape').catch(err => {
                                                console.warn('Orientation lock failed:', err);
                                            });
                                        }
                                    }
                                } else {
                                    if (parentDoc.exitFullscreen) {
                                        parentDoc.exitFullscreen().then(() => {
                                            btn.textContent = '📱 Fullscreen';
                                            if (parentWin.screen && parentWin.screen.orientation && parentWin.screen.orientation.unlock) {
                                                parentWin.screen.orientation.unlock();
                                            }
                                        });
                                    } else if (parentDoc.webkitExitFullscreen) {
                                        parentDoc.webkitExitFullscreen();
                                        btn.textContent = '📱 Fullscreen';
                                        if (parentWin.screen && parentWin.screen.orientation && parentWin.screen.orientation.unlock) {
                                            parentWin.screen.orientation.unlock();
                                        }
                                    }
                                }
                            }
                        } catch (err) {}
                    });

                    function updateFullscreenButton() {
                        try {
                            const btn = parentDoc.getElementById('fullscreen-toggle-btn');
                            if (btn) {
                                const isFull = parentDoc.fullscreenElement ? true : (parentDoc.webkitFullscreenElement ? true : false);
                                if (isFull) {
                                    btn.textContent = '📱 Exit Full';
                                } else {
                                    btn.textContent = '📱 Fullscreen';
                                    if (parentWin.screen && parentWin.screen.orientation && parentWin.screen.orientation.unlock) {
                                        parentWin.screen.orientation.unlock();
                                    }
                                }
                            }
                        } catch (err) {}
                    }

                    parentDoc.addEventListener('fullscreenchange', updateFullscreenButton);
                    parentDoc.addEventListener('webkitfullscreenchange', updateFullscreenButton);
                } catch (err) {}
            })();
        </script>
    """
    st.iframe(
        iframe_js.replace("{is_logged_in}", is_logged_in)
        .replace("{is_manual_logout}", is_manual_logout)
        .replace("{user_role}", user_role_val)
        .replace("{student_id}", student_id_val)
        .replace("{student_name}", student_name_val)
        .replace("{teacher_id}", teacher_id_val)
        .replace("{teacher_name}", teacher_name_val)
        .replace("{teacher_username}", teacher_username_val)
        .replace("{sig}", sig_val),
        height=1
    )

    # 0. Check if user is logged in
    if not st.session_state.get("logged_in"):
        header_cols = st.columns([7.8, 2.2])
        with header_cols[0]:
            st.markdown("<div class='login-header-anchor' style='display: none;'></div>", unsafe_allow_html=True)
            st.markdown("<div style='font-size: 0.95rem; line-height: 1.2; color: var(--emerald); font-weight: bold; font-family: sans-serif; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding: 2px 0;'>Al Madrasa-tus-Saifiyah-tul-Burhaniyah</div>", unsafe_allow_html=True)
        with header_cols[1]:
            st.markdown('<button id="fullscreen-toggle-btn" style="width: 100%; background: linear-gradient(180deg, var(--emerald), #0a4d3a); color: white; border: none; border-radius: 6px; padding: 1px 2px; font-weight: bold; cursor: pointer; font-size: 9px; height: 24px; min-height: 24px; line-height: 1.2; display: flex; align-items: center; justify-content: center; gap: 2px; font-family: sans-serif; box-shadow: 0 1px 3px rgba(0,0,0,0.12);">📱 Full</button>', unsafe_allow_html=True)
            
        from app.ui.login import render_login
        render_login()
        return

    # Render header when logged in
    user_role = st.session_state.get("user_role", "admin")
    teacher_display_name = st.session_state.get("teacher_name") or ""
    
    if user_role == "parent":
        header_cols = st.columns([7, 1.5, 1.5])
        with header_cols[0]:
            st.markdown("<h2 style='font-size: 1.15rem; margin: 0; padding: 2px 0; color: var(--emerald); font-weight: bold; font-family: sans-serif;'>Al Madrasa-tus-Saifiyah-tul-Burhaniyah</h2>", unsafe_allow_html=True)
        with header_cols[1]:
            st.markdown('<button id="fullscreen-toggle-btn" style="width: 100%; background: linear-gradient(180deg, var(--emerald), #0a4d3a); color: white; border: none; border-radius: 8px; padding: 2px 4px; font-weight: bold; cursor: pointer; font-size: 10px; height: 26px; min-height: 26px; line-height: 1.2; display: flex; align-items: center; justify-content: center; gap: 4px; font-family: sans-serif; box-shadow: 0 2px 4px rgba(0,0,0,0.12);">📱 Fullscreen</button>', unsafe_allow_html=True)
        with header_cols[2]:
            if st.button("🔒 Logout", width="stretch", key="header_logout_btn"):
                st.session_state.logged_in = False
                st.session_state.student_id = None
                st.session_state.student_name = None
                st.session_state.teacher_id = None
                st.session_state.teacher_name = None
                st.session_state.teacher_username = None
                st.session_state.page = "home"
                st.session_state.user_role = "admin"
                st.query_params.clear()
                st.session_state.manual_logout = True
                st.rerun()

        # Render parent report content directly and return
        from app.ui.parent_report import render_parent_report
        render_parent_report()
        return

    # Render admin / teacher header when logged in (Compact 1-row header)
    header_cols = st.columns([6.8, 1.6, 1.6])
    with header_cols[0]:
        st.markdown("<div class='header-row-anchor' style='display: none;'></div>", unsafe_allow_html=True)
        teacher_badge = f"<span style='background: rgba(14, 107, 80, 0.12); color: var(--emerald); font-size: 0.72rem; padding: 1px 6px; border-radius: 4px; margin-left: 6px; font-weight: 600; vertical-align: middle;'>👨‍🏫 {teacher_display_name}</span>" if teacher_display_name else ""
        st.markdown(f"<div style='display: flex; align-items: center; overflow: hidden; white-space: nowrap;'><span style='font-size: 0.88rem; margin: 0; color: var(--emerald); font-weight: bold; font-family: sans-serif; overflow: hidden; text-overflow: ellipsis;'>AMSB</span>{teacher_badge}</div>", unsafe_allow_html=True)
    with header_cols[1]:
        st.markdown('<button id="fullscreen-toggle-btn" style="width: 100%; background: linear-gradient(180deg, var(--emerald), #0a4d3a); color: white; border: none; border-radius: 6px; padding: 1px 2px; font-weight: bold; cursor: pointer; font-size: 9px; height: 24px; min-height: 24px; line-height: 1.2; display: flex; align-items: center; justify-content: center; gap: 2px; font-family: sans-serif; box-shadow: 0 1px 3px rgba(0,0,0,0.12);">📱 Full</button>', unsafe_allow_html=True)
    with header_cols[2]:
        if st.button("🔒 Exit", width="stretch", key="header_logout_btn"):
            st.session_state.logged_in = False
            st.session_state.student_id = None
            st.session_state.student_name = None
            st.session_state.teacher_id = None
            st.session_state.teacher_name = None
            st.session_state.teacher_username = None
            st.session_state.page = "home"
            st.query_params.clear()
            st.session_state.manual_logout = True
            st.rerun()

    # 1. Check if student is selected
    student_id = st.session_state.get("student_id")
    
    from app.ui.student import require_student
    
    if not student_id:
        require_student()
        return

    # 2. Top Student Bar (Tap to change student)
    current_page = st.session_state.get("page", "home")
    if current_page == "home":
        current_page = "murajat"
        st.session_state.page = "murajat"

    # 2. Top Student Bar (Elegant Luxury Pill + Switch Button)
    student_name = st.session_state.get("student_name", "Student")
    stu_cols = st.columns([3.8, 1.2])
    with stu_cols[0]:
        st.markdown(f"""
        <div class="student-luxury-pill" onclick="const b=document.querySelector('.student-change-btn-wrapper button');if(b)b.click();" title="Click to change student">
          <span class="student-avatar-badge">👤</span>
          <span class="student-title-text">{student_name}</span>
        </div>
        """, unsafe_allow_html=True)
    with stu_cols[1]:
        st.markdown("<div class='student-change-btn-wrapper'>", unsafe_allow_html=True)
        if st.button("⇄ Switch", width="stretch", key="nav_student_change_btn", help="Click to select another student"):
            st.session_state.student_id = None
            st.session_state.student_name = None
            st.session_state.page = "home"
            st.query_params.pop("student_id", None)
            st.query_params.pop("student_name", None)
            st.query_params.pop("page", None)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # 3. Bottom Thumb-Zone Navigation Dock
    with st.container(border=True):
        st.markdown("<div class='mobile-bottom-dock-anchor' style='display: none;'></div>", unsafe_allow_html=True)
        
        # Sub-tray for utility pages (Planner, Email, Report) when 'More' is open or active
        is_utility_page = current_page in ["planner", "email", "report"]
        if st.session_state.get("show_more_tray") or is_utility_page:
            st.markdown("<div class='dock-tray-anchor' style='display: none;'></div>", unsafe_allow_html=True)
            tray_cols = st.columns(3)
            with tray_cols[0]:
                if st.button("📅 Planner", type="primary" if current_page == "planner" else "secondary", width="stretch", key="dock_btn_planner"):
                    st.session_state.page = "planner"
                    st.query_params["page"] = "planner"
                    st.session_state.show_more_tray = False
                    st.rerun()
            with tray_cols[1]:
                if st.button("✉️ Email", type="primary" if current_page == "email" else "secondary", width="stretch", key="dock_btn_email"):
                    st.session_state.page = "email"
                    st.query_params["page"] = "email"
                    st.session_state.show_more_tray = False
                    st.rerun()
            with tray_cols[2]:
                if st.button("📊 Report", type="primary" if current_page == "report" else "secondary", width="stretch", key="dock_btn_report"):
                    st.session_state.page = "report"
                    st.query_params["page"] = "report"
                    st.session_state.show_more_tray = False
                    st.rerun()

        st.markdown("<div class='dock-main-anchor' style='display: none;'></div>", unsafe_allow_html=True)
        dock_cols = st.columns(5)
        with dock_cols[0]:
            if st.button("📖 Murajat", type="primary" if current_page == "murajat" else "secondary", width="stretch", key="dock_btn_murajat"):
                st.session_state.page = "murajat"
                st.query_params["page"] = "murajat"
                st.session_state.show_more_tray = False
                st.rerun()
        with dock_cols[1]:
            if st.button("📑 Juz'Hali", type="primary" if current_page == "juzulhali" else "secondary", width="stretch", key="dock_btn_juzulhali"):
                st.session_state.page = "juzulhali"
                st.query_params["page"] = "juzulhali"
                st.session_state.show_more_tray = False
                st.rerun()
        with dock_cols[2]:
            if st.button("✨ Jadeed", type="primary" if current_page == "jadeed" else "secondary", width="stretch", key="dock_btn_jadeed"):
                st.session_state.page = "jadeed"
                st.query_params["page"] = "jadeed"
                st.session_state.show_more_tray = False
                st.rerun()
        with dock_cols[3]:
            if st.button("📋 Takhteet", type="primary" if current_page == "takhteet" else "secondary", width="stretch", key="dock_btn_takhteet"):
                st.session_state.page = "takhteet"
                st.query_params["page"] = "takhteet"
                st.session_state.show_more_tray = False
                st.rerun()
        with dock_cols[4]:
            more_label = "⋯ More"
            if is_utility_page:
                more_label = f"⋯ {current_page.capitalize()[:4]}"
            if st.button(more_label, type="primary" if is_utility_page else "secondary", width="stretch", key="dock_btn_more"):
                st.session_state.show_more_tray = not st.session_state.get("show_more_tray", False)
                st.rerun()

    # --- ORIGINAL 8 DESKTOP BUTTONS (Preserved in code for reference) ---
    # cols = st.columns(8)
    # with cols[0]:
    #     if st.button("👥 Change", width="stretch"):
    #         st.session_state.student_id = None
    #         st.session_state.student_name = None
    #         st.session_state.page = "home"
    #         st.query_params.pop("student_id", None)
    #         st.query_params.pop("student_name", None)
    #         st.query_params.pop("page", None)
    #         st.rerun()
    # with cols[1]:
    #     if st.button("Murajat", type="primary" if current_page == "murajat" else "secondary", width="stretch"):
    #         st.session_state.page = "murajat"
    #         st.query_params["page"] = "murajat"
    #         st.rerun()
    # with cols[2]:
    #     if st.button("Juzulhali", type="primary" if current_page == "juzulhali" else "secondary", width="stretch"):
    #         st.session_state.page = "juzulhali"
    #         st.query_params["page"] = "juzulhali"
    #         st.rerun()
    # with cols[3]:
    #     if st.button("Jadeed", type="primary" if current_page == "jadeed" else "secondary", width="stretch"):
    #         st.session_state.page = "jadeed"
    #         st.query_params["page"] = "jadeed"
    #         st.rerun()
    # with cols[4]:
    #     if st.button("Takhteet", type="primary" if current_page == "takhteet" else "secondary", width="stretch"):
    #         st.session_state.page = "takhteet"
    #         st.query_params["page"] = "takhteet"
    #         st.rerun()
    # with cols[5]:
    #     if st.button("Planner", type="primary" if current_page == "planner" else "secondary", width="stretch"):
    #         st.session_state.page = "planner"
    #         st.query_params["page"] = "planner"
    #         st.rerun()
    # with cols[6]:
    #     if st.button("Email", type="primary" if current_page == "email" else "secondary", width="stretch"):
    #         st.session_state.page = "email"
    #         st.query_params["page"] = "email"
    #         st.rerun()
    # with cols[7]:
    #     if st.button("Report", type="primary" if current_page == "report" else "secondary", width="stretch"):
    #         st.session_state.page = "report"
    #         st.query_params["page"] = "report"
    #         st.rerun()
    # --- END ORIGINAL 8 DESKTOP BUTTONS ---
            


    # 4. Render content based on current page
    if current_page == "home":
        st.session_state.page = "murajat"
        st.rerun()
    elif current_page == "murajat":
        from app.ui.murajat import render_murajat
        render_murajat()
    elif current_page == "juzulhali":
        from app.ui.juzulhali import render_juzulhali
        render_juzulhali()
    elif current_page == "jadeed":
        from app.ui.jadeed import render_jadeed
        render_jadeed()
    elif current_page == "takhteet":
        from app.ui.takhteet import render_takhteet
        render_takhteet()
    elif current_page == "planner":
        from app.ui.planner import render_planner
        render_planner()
    elif current_page == "email":
        from app.ui.email_page import render_email_page
        render_email_page()
    elif current_page == "report":
        from app.ui.report import render_report
        render_report()
    else:
        st.session_state.page = "home"
        st.rerun()


if __name__ == "__main__":
    main()

