from __future__ import annotations

import streamlit as st

from app.db import create_listening_session, get_session_counts, increment_mistake
from app.ui.shared import (
    back_home_button,
    mistake_buttons,
    show_previous_takhteet,
    ensure_today_sessions,
    render_header_with_homework,
    SIPARA_OPTIONS,
    SIPARA_TO_SURAH,
    SIPARA_NAMES,
)
from app.ui.student import current_student_badge


def render_juzulhali() -> None:
    student_id = st.session_state.get("student_id")
    if not student_id:
        back_home_button()
        st.subheader("Juzulhali")
        st.warning("Please select a student on Home first.")
        return

    # If the student changed, reset selected surah, page and active session
    if st.session_state.get("juzulhali_student_id") != student_id:
        st.session_state.pop("juzulhali_session_id", None)
        st.session_state.pop("juzulhali_sipara", None)
        st.session_state.pop("juzulhali_surah_id", None)
        st.session_state.pop("juzulhali_page_number", None)
        st.session_state.pop("juzulhali_surah", None)
        st.session_state.pop("juzulhali_page_widget", None)
        st.session_state.juzulhali_student_id = student_id

    # Render the sticky container wrapping header, student badge, navigation, and mistake cards
    sticky_container = st.container()
    with sticky_container:
        st.markdown('<div class="sticky-anchor"></div>', unsafe_allow_html=True)
        
        render_header_with_homework("Juzulhali", student_id)

        current_student_badge()

        # --- TIMER (Hidden in simple version, preserved in code) ---
        # from app.ui.timer import render_recitation_timer
        # timer_elapsed, is_timer_running, is_timer_overtime = render_recitation_timer(
        #     module_name="juzulhali",
        #     target_minutes=15,
        #     student_id=student_id,
        #     auto_start=bool(surah_id is not None)
        # )
        timer_elapsed, is_timer_running, is_timer_overtime = 0, False, False

        # --- SIPARA SELECTOR + SUBTRACTION TOGGLE (Compact 1-row layout) ---
        col_sipara, col_sub = st.columns([3.3, 0.7])
        with col_sipara:
            st.markdown("<div class='sipara-row-anchor' style='display: none;'></div>", unsafe_allow_html=True)
            selected_sipara = st.selectbox(
                "Select Sipara",
                options=SIPARA_OPTIONS,
                index=None,
                placeholder="Select a Sipara (1 — 30)...",
                format_func=lambda x: x[1] if x else "",
                key="juzulhali_sipara",
                label_visibility="collapsed"
            )
        with col_sub:
            st.toggle("Sub", value=False, key="sub_mode_toggle")
        
        sipara_num = selected_sipara[0] if selected_sipara else None
        surah_id = SIPARA_TO_SURAH.get(sipara_num) if sipara_num else None
        page_number = sipara_num

        # --- ORIGINAL SURAH/PAGE & PREV/NEXT BUTTONS (Preserved in code) ---
        # from app.ui.jadeed import load_quran_metadata
        # from app.db import list_surahs
        # quran_metadata = load_quran_metadata()
        # surahs = list_surahs()
        # options = [(s["id"], f'{s["number"]:03d} — {s["name_en"]} ({s["name_ar"]})') for s in surahs]
        # col_s, col_p, col_prev, col_next = st.columns([2, 1, 1, 1])
        # ...
        # --- END ORIGINAL NAVIGATION ---

    if sipara_num is not None:
        if (
            st.session_state.get("juzulhali_surah_id") != surah_id
            or st.session_state.get("juzulhali_page_number") != page_number
            or st.session_state.get("juzulhali_student_id") != student_id
            or not st.session_state.get("juzulhali_session_id")
        ):
            st.session_state.juzulhali_surah_id = surah_id
            st.session_state.juzulhali_page_number = page_number
            st.session_state.juzulhali_student_id = student_id
            # Check if there is an existing session for this student, mode, surah and page today using local cache
            ensure_today_sessions(student_id)
            key = ("juzulhali", int(surah_id), int(page_number))
            existing_id = st.session_state.today_sessions.get(key)
            if existing_id:
                st.session_state.juzulhali_session_id = existing_id
            else:
                st.session_state.juzulhali_session_id = None
            st.session_state.pop("juzulhali_counts", None)
            st.session_state.pop("juzulhali_counts_session_id", None)

        session_id = st.session_state.get("juzulhali_session_id")
        if session_id:
            if timer_elapsed > 0:
                from app.db import update_session_duration
                update_session_duration(session_id, timer_elapsed, is_timer_overtime)
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
            from app.db import MAKHARIJ_COLS, MUSAID_COLS
            for col in MAKHARIJ_COLS:
                counts[col] = 0
            for col in MUSAID_COLS:
                counts[col] = 0

    def _on_click(kind: str) -> None:
        if surah_id is None or page_number is None:
            return
        sid = st.session_state.get("juzulhali_session_id")
        if not sid:
            ensure_today_sessions(student_id)
            key = ("juzulhali", int(surah_id), int(page_number))
            existing_id = st.session_state.today_sessions.get(key)
            if existing_id:
                sid = existing_id
                st.session_state.juzulhali_session_id = sid
                st.session_state.juzulhali_counts = get_session_counts(sid)
                st.session_state.juzulhali_counts_session_id = sid
            else:
                session = create_listening_session(student_id=student_id, mode="juzulhali", surah_id=surah_id, page_number=page_number, force_new=True)
                sid = session["id"]
                st.session_state.today_sessions[key] = session["id"]
                st.session_state.juzulhali_session_id = sid
                
                # Initialize local counts with all 0s in memory without a network request!
                zero_counts = {
                    "talqeen": 0, "tanbeeh": 0, "repeat_mistake": 0, "mutashabehat": 0, "irab": 0, "awakhir_ul_ayat": 0,
                    "irab_talqeen": 0, "irab_tanbeeh": 0,
                    "repeat_mistake_talqeen": 0, "repeat_mistake_tanbeeh": 0,
                    "mutashabehat_talqeen": 0, "mutashabehat_tanbeeh": 0,
                    "awakhir_ul_ayat_talqeen": 0, "awakhir_ul_ayat_tanbeeh": 0,
                    "ikhfa": 0, "izhaar": 0, "qalqalah": 0, "ism_jalalah": 0, "tahreek_sakin": 0, "gunnah": 0,
                    "idgham": 0, "madd_lazim": 0, "madd_muttasil": 0, "mad_tabaiee": 0, "ikhfa_shafawi": 0, "iqlab": 0
                }
                from app.db import MAKHARIJ_COLS, MUSAID_COLS
                for col in MAKHARIJ_COLS:
                    zero_counts[col] = 0
                for col in MUSAID_COLS:
                    zero_counts[col] = 0
                st.session_state.juzulhali_counts = zero_counts
                st.session_state.juzulhali_counts_session_id = sid
            
        if "juzulhali_counts" not in st.session_state or st.session_state.get("juzulhali_counts_session_id") != sid:
            st.session_state.juzulhali_counts = get_session_counts(sid)
            st.session_state.juzulhali_counts_session_id = sid
            
        local_counts = st.session_state.juzulhali_counts
        sub_mode = st.session_state.get("sub_mode_toggle", False)
        diff = -1 if sub_mode else 1
        
        if kind == "is_zero_marks":
            local_counts["is_zero_marks"] = False if sub_mode else True
        elif kind == "talqeen":
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
        elif (
            kind in ("ikhfa", "izhaar", "qalqalah", "ism_jalalah", "tahreek_sakin", "gunnah", "idgham", "madd_lazim", "madd_muttasil", "mad_tabaiee", "ikhfa_shafawi", "iqlab")
            or kind.startswith("makhraj_")
            or kind.startswith("musaid_")
        ):
            local_counts[kind] = 1 if local_counts.get(kind, 0) == 0 else 0
            
        from app.db import increment_mistake_bg
        increment_mistake_bg(sid, kind, local_counts, duration_seconds=timer_elapsed, time_exceeded=is_timer_overtime)
        st.session_state.play_sound = True

    student_name = st.session_state.get("student_name", "Student")

    if sipara_num is None:
        st.info("Please select a Sipara to start Juzulhali recitation.")
        return

    mistake_buttons(session_id=session_id or "", counts=counts, on_click=_on_click)

    # --- HIDDEN SESSION CONTROLS IN SIMPLE VERSION (Preserved in code) ---
    # st.divider()
    # c1, _, c2 = st.columns([2, 5, 2])
    # with c1:
    #     if st.button("New session (Same Sipara)", width="stretch"):
    #         from app.db import update_session_duration
    #         if session_id and timer_elapsed > 0:
    #             update_session_duration(session_id, timer_elapsed, is_timer_overtime)
    #         session = create_listening_session(student_id=student_id, mode="juzulhali", surah_id=surah_id, page_number=int(page_number), force_new=True)
    #         st.session_state.juzulhali_session_id = session["id"]
    #         ensure_today_sessions(student_id)
    #         key = ("juzulhali", int(surah_id), int(page_number))
    #         st.session_state.today_sessions[key] = session["id"]
    #         st.session_state.pop("juzulhali_counts", None)
    #         st.session_state.pop("juzulhali_counts_session_id", None)
    #         st.rerun()
    # with c2:
    #     if st.button("Change Sipara", width="stretch"):
    #         from app.db import update_session_duration
    #         if session_id and timer_elapsed > 0:
    #             update_session_duration(session_id, timer_elapsed, is_timer_overtime)
    #         st.session_state.pop("juzulhali_session_id", None)
    #         st.session_state.pop("juzulhali_surah_id", None)
    #         st.session_state.pop("juzulhali_sipara", None)
    #         st.session_state.pop("juzulhali_page_number", None)
    #         st.rerun()
    # --- END HIDDEN SESSION CONTROLS ---
