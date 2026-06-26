from __future__ import annotations

import streamlit as st

from app.db import create_listening_session, get_session_counts, increment_mistake
from app.ui.shared import back_home_button, mistake_buttons, show_previous_takhteet, ensure_today_sessions, render_header_with_homework
from app.ui.student import current_student_badge


def render_juzulhali() -> None:
    student_id = st.session_state.get("student_id")
    if not student_id:
        back_home_button()
        st.subheader("Juzulhali")
        st.warning("Please select a student on Home first.")
        return

    # If the student changed, reset selected page and active session
    if st.session_state.get("juzulhali_student_id") != student_id:
        st.session_state.pop("juzulhali_selected_page_widget", None)
        st.session_state.pop("juzulhali_session_id", None)
        st.session_state.pop("juzulhali_page_number", None)
        st.session_state.juzulhali_student_id = student_id

    page_options = list(range(1, 21))

    # Define callbacks to modify widget session state before widget instantiation
    def click_prev():
        curr = st.session_state.get("juzulhali_selected_page_widget")
        if curr is not None and curr > 1:
            st.session_state.juzulhali_selected_page_widget = curr - 1

    def click_next():
        curr = st.session_state.get("juzulhali_selected_page_widget")
        if curr is not None and curr < 20:
            st.session_state.juzulhali_selected_page_widget = curr + 1

    # Render the sticky container wrapping header, student badge, navigation, and mistake cards
    with st.container():
        st.markdown('<div class="sticky-anchor"></div>', unsafe_allow_html=True)
        
        render_header_with_homework("Juzulhali", student_id)

        current_student_badge()
        
        col_sel, col_prev, col_next = st.columns([3, 1, 1])
        with col_sel:
            page_number = st.selectbox(
                "Page number",
                options=page_options,
                index=None,
                placeholder="Select Page...",
                label_visibility="collapsed",
                key="juzulhali_selected_page_widget"
            )
        with col_prev:
            st.button("◀ Prev", disabled=(page_number is None or page_number <= 1), use_container_width=True, on_click=click_prev)
        with col_next:
            st.button("Next ▶", disabled=(page_number is None or page_number >= 20), use_container_width=True, on_click=click_next)

    if page_number is not None:
        with st.spinner("Preparing recitation session..."):
            if (
                st.session_state.get("juzulhali_page_number") != page_number
                or st.session_state.get("juzulhali_student_id") != student_id
                or not st.session_state.get("juzulhali_session_id")
            ):
                st.session_state.juzulhali_page_number = page_number
                st.session_state.juzulhali_student_id = student_id
                # Check if there is an existing session for this student, mode, and page today using local cache
                ensure_today_sessions(student_id)
                key = ("juzulhali", None, int(page_number))
                existing_id = st.session_state.today_sessions.get(key)
                if existing_id:
                    st.session_state.juzulhali_session_id = existing_id
                else:
                    # Automatically create session
                    session = create_listening_session(student_id=student_id, mode="juzulhali", surah_id=None, page_number=int(page_number))
                    st.session_state.juzulhali_session_id = session["id"]
                    st.session_state.today_sessions[key] = session["id"]
                st.session_state.pop("juzulhali_counts", None)
                st.session_state.pop("juzulhali_counts_session_id", None)

            session_id = st.session_state.get("juzulhali_session_id")
            if session_id:
                if "juzulhali_counts" not in st.session_state or st.session_state.get("juzulhali_counts_session_id") != session_id:
                    st.session_state.juzulhali_counts = get_session_counts(session_id)
                    st.session_state.juzulhali_counts_session_id = session_id
                counts = st.session_state.juzulhali_counts
            else:
                counts = {
                    "talqeen": 0, "tanbeeh": 0, "repeat_mistake": 0, "mutashabehat": 0, "irab": 0, "awakhir_ul_ayat": 0,
                    "irab_talqeen": 0, "irab_tanbeeh": 0,
                    "repeat_mistake_talqeen": 0, "repeat_mistake_tanbeeh": 0,
                    "mutashabehat_talqeen": 0, "mutashabehat_tanbeeh": 0,
                    "awakhir_ul_ayat_talqeen": 0, "awakhir_ul_ayat_tanbeeh": 0,
                    "ikhfa": 0, "izhaar": 0, "qalqalah": 0, "ism_jalalah": 0, "tahreek_sakin": 0, "gunnah": 0,
                    "idgham": 0, "madd_lazim": 0, "madd_muttasil": 0, "mad_tabaiee": 0, "ikhfa_shafawi": 0, "iqlab": 0
                }
                from app.db import MAKHARIJ_COLS
                for col in MAKHARIJ_COLS:
                    counts[col] = 0

    def _on_click(kind: str) -> None:
        sid = st.session_state.get("juzulhali_session_id")
        if not sid:
            ensure_today_sessions(student_id)
            key = ("juzulhali", None, int(page_number))
            existing_id = st.session_state.today_sessions.get(key)
            if existing_id:
                sid = existing_id
            else:
                session = create_listening_session(student_id=student_id, mode="juzulhali", surah_id=None, page_number=int(page_number))
                sid = session["id"]
                st.session_state.today_sessions[key] = session["id"]
            st.session_state.juzulhali_session_id = sid
            st.session_state.juzulhali_counts = get_session_counts(sid)
            st.session_state.juzulhali_counts_session_id = sid
            
        if "juzulhali_counts" not in st.session_state or st.session_state.get("juzulhali_counts_session_id") != sid:
            st.session_state.juzulhali_counts = get_session_counts(sid)
            st.session_state.juzulhali_counts_session_id = sid
            
        local_counts = st.session_state.juzulhali_counts
        sub_mode = st.session_state.get("sub_mode_toggle", False)
        diff = -1 if sub_mode else 1
        
        if kind == "talqeen":
            local_counts["talqeen"] = max(0, local_counts.get("talqeen", 0) + diff)
        elif kind == "tanbeeh":
            local_counts["tanbeeh"] = max(0, local_counts.get("tanbeeh", 0) + diff)
        elif kind in ("irab", "irab_talqeen"):
            if sub_mode:
                if local_counts.get("irab_talqeen", 0) > 0:
                    local_counts["irab_talqeen"] -= 1
                    local_counts["irab"] = max(0, local_counts.get("irab", 0) - 1)
                    local_counts["talqeen"] = max(0, local_counts.get("talqeen", 0) - 1)
            else:
                local_counts["irab_talqeen"] = local_counts.get("irab_talqeen", 0) + 1
                local_counts["irab"] = local_counts.get("irab", 0) + 1
                local_counts["talqeen"] += 1
        elif kind == "irab_tanbeeh":
            if sub_mode:
                if local_counts.get("irab_tanbeeh", 0) > 0:
                    local_counts["irab_tanbeeh"] -= 1
                    local_counts["irab"] = max(0, local_counts.get("irab", 0) - 1)
                    local_counts["tanbeeh"] = max(0, local_counts.get("tanbeeh", 0) - 1)
            else:
                local_counts["irab_tanbeeh"] = local_counts.get("irab_tanbeeh", 0) + 1
                local_counts["irab"] = local_counts.get("irab", 0) + 1
                local_counts["tanbeeh"] += 1
        elif kind in ("repeat_mistake", "repeat_mistake_talqeen"):
            if sub_mode:
                if local_counts.get("repeat_mistake_talqeen", 0) > 0:
                    local_counts["repeat_mistake_talqeen"] -= 1
                    local_counts["repeat_mistake"] = max(0, local_counts.get("repeat_mistake", 0) - 1)
                    local_counts["talqeen"] = max(0, local_counts.get("talqeen", 0) - 1)
            else:
                local_counts["repeat_mistake_talqeen"] = local_counts.get("repeat_mistake_talqeen", 0) + 1
                local_counts["repeat_mistake"] = local_counts.get("repeat_mistake", 0) + 1
                local_counts["talqeen"] += 1
        elif kind == "repeat_mistake_tanbeeh":
            if sub_mode:
                if local_counts.get("repeat_mistake_tanbeeh", 0) > 0:
                    local_counts["repeat_mistake_tanbeeh"] -= 1
                    local_counts["repeat_mistake"] = max(0, local_counts.get("repeat_mistake", 0) - 1)
                    local_counts["tanbeeh"] = max(0, local_counts.get("tanbeeh", 0) - 1)
            else:
                local_counts["repeat_mistake_tanbeeh"] = local_counts.get("repeat_mistake_tanbeeh", 0) + 1
                local_counts["repeat_mistake"] = local_counts.get("repeat_mistake", 0) + 1
                local_counts["tanbeeh"] += 1
        elif kind in ("mutashabehat", "mutashabehat_talqeen"):
            if sub_mode:
                if local_counts.get("mutashabehat_talqeen", 0) > 0:
                    local_counts["mutashabehat_talqeen"] -= 1
                    local_counts["mutashabehat"] = max(0, local_counts.get("mutashabehat", 0) - 1)
                    local_counts["talqeen"] = max(0, local_counts.get("talqeen", 0) - 1)
            else:
                local_counts["mutashabehat_talqeen"] = local_counts.get("mutashabehat_talqeen", 0) + 1
                local_counts["mutashabehat"] = local_counts.get("mutashabehat", 0) + 1
                local_counts["talqeen"] += 1
        elif kind == "mutashabehat_tanbeeh":
            if sub_mode:
                if local_counts.get("mutashabehat_tanbeeh", 0) > 0:
                    local_counts["mutashabehat_tanbeeh"] -= 1
                    local_counts["mutashabehat"] = max(0, local_counts.get("mutashabehat", 0) - 1)
                    local_counts["tanbeeh"] = max(0, local_counts.get("tanbeeh", 0) - 1)
            else:
                local_counts["mutashabehat_tanbeeh"] = local_counts.get("mutashabehat_tanbeeh", 0) + 1
                local_counts["mutashabehat"] = local_counts.get("mutashabehat", 0) + 1
                local_counts["tanbeeh"] += 1
        elif kind in ("awakhir_ul_ayat", "awakhir_ul_ayat_talqeen"):
            if sub_mode:
                if local_counts.get("awakhir_ul_ayat_talqeen", 0) > 0:
                    local_counts["awakhir_ul_ayat_talqeen"] -= 1
                    local_counts["awakhir_ul_ayat"] = max(0, local_counts.get("awakhir_ul_ayat", 0) - 1)
                    local_counts["talqeen"] = max(0, local_counts.get("talqeen", 0) - 1)
            else:
                local_counts["awakhir_ul_ayat_talqeen"] = local_counts.get("awakhir_ul_ayat_talqeen", 0) + 1
                local_counts["awakhir_ul_ayat"] = local_counts.get("awakhir_ul_ayat", 0) + 1
                local_counts["talqeen"] += 1
        elif kind == "awakhir_ul_ayat_tanbeeh":
            if sub_mode:
                if local_counts.get("awakhir_ul_ayat_tanbeeh", 0) > 0:
                    local_counts["awakhir_ul_ayat_tanbeeh"] -= 1
                    local_counts["awakhir_ul_ayat"] = max(0, local_counts.get("awakhir_ul_ayat", 0) - 1)
                    local_counts["tanbeeh"] = max(0, local_counts.get("tanbeeh", 0) - 1)
            else:
                local_counts["awakhir_ul_ayat_tanbeeh"] = local_counts.get("awakhir_ul_ayat_tanbeeh", 0) + 1
                local_counts["awakhir_ul_ayat"] = local_counts.get("awakhir_ul_ayat", 0) + 1
                local_counts["tanbeeh"] += 1
        elif kind in ("ikhfa", "izhaar", "qalqalah", "ism_jalalah", "tahreek_sakin", "gunnah", "idgham", "madd_lazim", "madd_muttasil", "mad_tabaiee", "ikhfa_shafawi", "iqlab"):
            local_counts[kind] = max(0, local_counts.get(kind, 0) + diff)
        elif kind.startswith("makhraj_"):
            local_counts[kind] = 1 if local_counts.get(kind, 0) == 0 else 0
            
        from app.db import increment_mistake_bg
        increment_mistake_bg(sid, kind, local_counts)

    if page_number is None:
        st.info("Please select a Page to start Juzulhali recitation.")
        return

    mistake_buttons(session_id=session_id or "", counts=counts, on_click=_on_click)



    st.divider()
    # Show session controls when active
    if st.button("New session (same page)", use_container_width=True):
        session = create_listening_session(student_id=student_id, mode="juzulhali", surah_id=None, page_number=int(page_number))
        st.session_state.juzulhali_session_id = session["id"]
        ensure_today_sessions(student_id)
        key = ("juzulhali", None, int(page_number))
        st.session_state.today_sessions[key] = session["id"]
        st.session_state.pop("juzulhali_counts", None)
        st.session_state.pop("juzulhali_counts_session_id", None)
        st.rerun()
