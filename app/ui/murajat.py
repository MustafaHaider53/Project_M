from __future__ import annotations

import streamlit as st

from app.db import create_listening_session, get_session_counts, increment_mistake, list_surahs
from app.ui.shared import back_home_button, mistake_buttons, surah_selector, show_previous_takhteet, ensure_today_sessions, render_header_with_homework
from app.ui.student import current_student_badge


def render_murajat() -> None:
    student_id = st.session_state.get("student_id")
    if not student_id:
        back_home_button()
        st.subheader("Murajat")
        st.warning("Please select a student on Home first.")
        return

    # If the student changed, reset selected surah, page and active session
    if st.session_state.get("murajat_student_id") != student_id:
        st.session_state.pop("murajat_session_id", None)
        st.session_state.pop("murajat_surah_id", None)
        st.session_state.pop("murajat_page_number", None)
        st.session_state.pop("murajat_surah", None)
        st.session_state.pop("murajat_page_widget", None)
        st.session_state.murajat_student_id = student_id

    from app.ui.jadeed import load_quran_metadata
    quran_metadata = load_quran_metadata()

    surahs = list_surahs()
    options = [(s["id"], f'{s["number"]:03d} — {s["name_en"]} ({s["name_ar"]})') for s in surahs]

    # Current selected Surah and page helper
    selected_option = st.session_state.get("murajat_surah")
    surah_id = None
    surah = None
    if selected_option in options:
        surah_id = selected_option[0]
        surah = next((s for s in surahs if s["id"] == surah_id), None)

    # Get page options for selected Surah
    page_options = []
    if surah:
        s_num_str = str(surah["number"])
        pages_dict = quran_metadata["surahs"][s_num_str]["pages"]
        page_options = sorted(list(pages_dict.keys()), key=int)
        
        # Check if selected page in widget state is valid for this Surah
        selected_page_widget = st.session_state.get("murajat_page_widget")
        if selected_page_widget not in page_options:
            selected_page_widget = page_options[0]
            st.session_state.murajat_page_widget = selected_page_widget

    # Define callbacks to modify widget session state before widget instantiation
    def click_prev():
        selected_option = st.session_state.get("murajat_surah")
        if selected_option in options:
            current_page_str = st.session_state.get("murajat_page_widget")
            if current_page_str in page_options:
                idx = page_options.index(current_page_str)
                if idx > 0:
                    st.session_state.murajat_page_widget = page_options[idx - 1]
                else:
                    # Go to previous Surah, last page
                    curr_surah_idx = options.index(selected_option)
                    if curr_surah_idx > 0:
                        prev_option = options[curr_surah_idx - 1]
                        st.session_state.murajat_surah = prev_option
                        # Fetch page options for prev Surah
                        prev_surah = next((s for s in surahs if s["id"] == prev_option[0]), None)
                        prev_s_num_str = str(prev_surah["number"])
                        prev_page_options = sorted(list(quran_metadata["surahs"][prev_s_num_str]["pages"].keys()), key=int)
                        st.session_state.murajat_page_widget = prev_page_options[-1]

    def click_next():
        selected_option = st.session_state.get("murajat_surah")
        if selected_option in options:
            current_page_str = st.session_state.get("murajat_page_widget")
            if current_page_str in page_options:
                idx = page_options.index(current_page_str)
                if idx < len(page_options) - 1:
                    st.session_state.murajat_page_widget = page_options[idx + 1]
                else:
                    # Go to next Surah, first page
                    curr_surah_idx = options.index(selected_option)
                    if curr_surah_idx < len(options) - 1:
                        next_option = options[curr_surah_idx + 1]
                        st.session_state.murajat_surah = next_option
                        # Fetch page options for next Surah
                        next_surah = next((s for s in surahs if s["id"] == next_option[0]), None)
                        next_s_num_str = str(next_surah["number"])
                        next_page_options = sorted(list(quran_metadata["surahs"][next_s_num_str]["pages"].keys()), key=int)
                        st.session_state.murajat_page_widget = next_page_options[0]

    curr_idx = options.index(selected_option) if selected_option in options else -1
    current_page_str = st.session_state.get("murajat_page_widget")
    page_idx = page_options.index(current_page_str) if (current_page_str and current_page_str in page_options) else -1
    
    has_prev = (curr_idx > 0 or page_idx > 0)
    has_next = (curr_idx < len(options) - 1 or page_idx < len(page_options) - 1)

    # Render the sticky container wrapping header, selectors, badge, and mistake cards
    sticky_container = st.container()
    with sticky_container:
        st.markdown('<div class="sticky-anchor"></div>', unsafe_allow_html=True)
        
        render_header_with_homework("Murajat", student_id)
            
        current_student_badge()
        
        col_s, col_p, col_prev, col_next = st.columns([2, 1, 1, 1])
        with col_s:
            selected = st.selectbox(
                "Surah",
                options=options,
                index=None,
                placeholder="Select a Surah...",
                format_func=lambda x: x[1] if x else "",
                label_visibility="collapsed",
                key="murajat_surah"
            )
            
        page_number = None
        with col_p:
            if selected:
                selected_page = st.selectbox(
                    "Page",
                    options=page_options,
                    label_visibility="collapsed",
                    key="murajat_page_widget"
                )
                if selected_page:
                    page_number = int(selected_page)
            else:
                st.selectbox(
                    "Page",
                    options=[],
                    disabled=True,
                    placeholder="Page",
                    label_visibility="collapsed",
                    key="murajat_page_widget_disabled"
                )
                
        with col_prev:
            st.button("◀ Prev", disabled=not has_prev, width="stretch", on_click=click_prev)
        with col_next:
            st.button("Next ▶", disabled=not has_next, width="stretch", on_click=click_next)

    if surah_id is not None and page_number is not None:
        with st.spinner("Preparing recitation session..."):
            if (
                st.session_state.get("murajat_surah_id") != surah_id
                or st.session_state.get("murajat_page_number") != page_number
                or st.session_state.get("murajat_student_id") != student_id
                or not st.session_state.get("murajat_session_id")
            ):
                st.session_state.murajat_surah_id = surah_id
                st.session_state.murajat_page_number = page_number
                st.session_state.murajat_student_id = student_id
                
                # Check if there is an existing session for this student, mode, surah and page today using local cache
                ensure_today_sessions(student_id)
                key = ("murajat", int(surah_id), int(page_number))
                existing_id = st.session_state.today_sessions.get(key)
                if existing_id:
                    st.session_state.murajat_session_id = existing_id
                else:
                    st.session_state.murajat_session_id = None
                st.session_state.pop("murajat_counts", None)
                st.session_state.pop("murajat_counts_session_id", None)

            session_id = st.session_state.get("murajat_session_id")

            if session_id:
                if "murajat_counts" not in st.session_state or st.session_state.get("murajat_counts_session_id") != session_id:
                    st.session_state.murajat_counts = get_session_counts(session_id)
                    st.session_state.murajat_counts_session_id = session_id
                counts = st.session_state.murajat_counts
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
        sid = st.session_state.get("murajat_session_id")
        if not sid:
            ensure_today_sessions(student_id)
            key = ("murajat", int(surah_id), int(page_number))
            existing_id = st.session_state.today_sessions.get(key)
            if existing_id:
                sid = existing_id
                st.session_state.murajat_session_id = sid
                st.session_state.murajat_counts = get_session_counts(sid)
                st.session_state.murajat_counts_session_id = sid
            else:
                session = create_listening_session(student_id=student_id, mode="murajat", surah_id=surah_id, page_number=page_number, force_new=True)
                sid = session["id"]
                st.session_state.today_sessions[key] = session["id"]
                st.session_state.murajat_session_id = sid
                
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
                st.session_state.murajat_counts = zero_counts
                st.session_state.murajat_counts_session_id = sid
            
        if "murajat_counts" not in st.session_state or st.session_state.get("murajat_counts_session_id") != sid:
            st.session_state.murajat_counts = get_session_counts(sid)
            st.session_state.murajat_counts_session_id = sid
            
        local_counts = st.session_state.murajat_counts
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
        elif kind in ("ikhfa", "izhaar", "qalqalah", "ism_jalalah", "tahreek_sakin", "gunnah", "idgham", "madd_lazim", "madd_muttasil", "mad_tabaiee", "ikhfa_shafawi", "iqlab"):
            local_counts[kind] = max(0, local_counts.get(kind, 0) + diff)
        elif kind.startswith("makhraj_") or kind.startswith("musaid_"):
            local_counts[kind] = 1 if local_counts.get(kind, 0) == 0 else 0
            
        from app.db import increment_mistake_bg
        increment_mistake_bg(sid, kind, local_counts)
        st.session_state.play_sound = True

    student_name = st.session_state.get("student_name", "Student")

    if surah_id is None or page_number is None:
        show_analytics = st.toggle("📊 View Student Mistake Analytics & Progress", value=False, key="murajat_show_student_analytics_toggle")
        if show_analytics:
            from app.ui.analytics import render_student_analytics
            render_student_analytics(student_id=student_id, student_name=student_name)
        st.info("Please select a Surah and Page to start Murajat recitation.")
        return

    # Render Musaid buttons & Toggles under Surah/Page selectors inside sticky_container
    with sticky_container:
        col_toggles, col_musaid = st.columns([1.5, 3.5])
        with col_toggles:
            show_analytics = st.toggle("📊 View Student Mistake Analytics", value=False, key="murajat_show_student_analytics_toggle")
            st.toggle("➖ **Subtraction Mode**", value=False, key="sub_mode_toggle")
        with col_musaid:
            st.markdown("<div style='font-size: 0.85rem; font-weight: bold; margin-bottom: 5px; color: var(--emerald); text-align: left;'>Musaid Analysis (One-time Tap)</div>", unsafe_allow_html=True)
            st.markdown("""
            <style>
            div[data-testid="stElementContainer"]:has(.musaid-active) + div[data-testid="stElementContainer"] button {
                background: linear-gradient(180deg, #15803d, #166534) !important;
                color: #ffffff !important;
                border-color: #14532d !important;
            }
            div[data-testid="stElementContainer"]:has(.musaid-active) + div[data-testid="stElementContainer"] button:hover {
                background: linear-gradient(180deg, #166534, #14532d) !important;
            }
            </style>
            """, unsafe_allow_html=True)
            MUSAID_BUTTONS = {
                "musaid_end_part": "🔚 End Part",
                "musaid_beg_part": "🔝 Beginning Part",
                "musaid_ayat_after_ayat": "🔗 Ayat Linkage",
                "musaid_page_after_page": "📖 Page Transition",
                "musaid_no_image": "🖼️ No Page Image",
                "musaid_lehen": "🎵 Lehen only"
            }
            musaid_cols = st.columns(3)
            for idx, (col_key, label) in enumerate(MUSAID_BUTTONS.items()):
                col_idx = idx % 3
                with musaid_cols[col_idx]:
                    is_active = counts.get(col_key, 0) == 1
                    active_class = "musaid-active" if is_active else "musaid-inactive"
                    st.markdown(f"<span class='{active_class}' style='display: none;'>active</span>", unsafe_allow_html=True)
                    btn_type = "primary" if is_active else "secondary"
                    display_label = f"✓ {label}" if is_active else label
                    if st.button(display_label, type=btn_type, key=f"btn_{col_key}", use_container_width=True):
                        _on_click(col_key)
                        st.rerun()

    if st.session_state.get("murajat_show_student_analytics_toggle", False):
        from app.ui.analytics import render_student_analytics
        render_student_analytics(student_id=student_id, student_name=student_name)

    mistake_buttons(session_id=session_id or "", counts=counts, on_click=_on_click)



    st.divider()
    # Show session controls when active
    c1, _, c2 = st.columns([2, 5, 2])
    with c1:
        if st.button("New session (Same Surah)", width="stretch"):
            session = create_listening_session(student_id=student_id, mode="murajat", surah_id=surah_id, page_number=page_number, force_new=True)
            st.session_state.murajat_session_id = session["id"]
            ensure_today_sessions(student_id)
            key = ("murajat", int(surah_id), int(page_number) if page_number is not None else None)
            st.session_state.today_sessions[key] = session["id"]
            st.session_state.pop("murajat_counts", None)
            st.session_state.pop("murajat_counts_session_id", None)
            st.rerun()
    with c2:
        if st.button("Change Surah", width="stretch"):
            st.session_state.pop("murajat_session_id", None)
            st.session_state.pop("murajat_surah_id", None)
            st.session_state.pop("murajat_surah", None)
            st.rerun()
