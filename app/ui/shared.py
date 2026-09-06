from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import streamlit as st
import hmac
import hashlib


def generate_session_signature(user_role: str, student_id: str) -> str:
    # Use the Supabase Key as a server-side secret key for HMAC signatures
    secret_key = st.secrets.get("SUPABASE_KEY", "mukhayyam-secure-fallback-key-53")
    # For admin/teachers, student_id is dynamic, so we do not include it in the signature message
    sig_student_id = "" if user_role == "admin" else student_id
    message = f"{user_role}:{sig_student_id}"
    return hmac.new(secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()


def verify_session_signature(user_role: str, student_id: str, sig: str) -> bool:
    if not sig:
        return False
    expected = generate_session_signature(user_role, student_id)
    return hmac.compare_digest(expected, sig)


def back_home_button() -> None:
    pass


def surah_selector(*, surahs: List[Dict[str, Any]], key: str) -> Tuple[Optional[int], Optional[Dict[str, Any]]]:
    if not surahs:
        st.info("No Surahs found yet. Run the SQL in `supabase/schema.sql` (it includes a seed list).")
        return None, None

    options = [(s["id"], f'{s["number"]:03d} — {s["name_en"]} ({s["name_ar"]})') for s in surahs]
    selected = st.selectbox(
        "Surah",
        options=options,
        index=None,
        placeholder="Select a Surah...",
        format_func=lambda x: x[1] if x else "",
        key=key
    )
    if not selected:
        return None, None
    surah_id = selected[0]
    surah = next((s for s in surahs if s["id"] == surah_id), None)
    return surah_id, surah


def mistake_buttons(*, session_id: str, counts: Dict[str, int], on_click) -> None:
    # Trigger auditory/visual feedback when a button is clicked
    if st.session_state.pop("play_sound", False):
        is_sub = st.session_state.get("sub_mode_toggle", False)
        is_sub_js = "true" if is_sub else "false"
        color = "#c53030" if is_sub else "#0E6B50"
        st.markdown(
            f"""
            <div class="tap-indicator-dot"></div>
            <style>
            @keyframes dot-pulse {{
                0% {{
                    transform: scale(0.5);
                    opacity: 1;
                    box-shadow: 0 0 0 0px {color}88;
                }}
                100% {{
                    transform: scale(2);
                    opacity: 0;
                    box-shadow: 0 0 0 10px {color}00;
                }}
            }}
            .tap-indicator-dot {{
                position: fixed;
                top: 15px;
                right: 15px;
                width: 10px;
                height: 10px;
                background-color: {color};
                border-radius: 50%;
                z-index: 999999;
                animation: dot-pulse 0.4s ease-out forwards;
                pointer-events: none;
            }}
            </style>
            <script>
                (function() {{
                    try {{
                        const AudioContext = window.AudioContext || window.webkitAudioContext;
                        if (!AudioContext) return;
                        const audioCtx = new AudioContext();
                        const osc = audioCtx.createOscillator();
                        const gain = audioCtx.createGain();
                        
                        osc.connect(gain);
                        gain.connect(audioCtx.destination);
                        
                        const isSubtract = {is_sub_js};
                        if (isSubtract) {{
                            osc.type = 'triangle';
                            osc.frequency.setValueAtTime(523.25, audioCtx.currentTime); // C5
                            osc.frequency.exponentialRampToValueAtTime(261.63, audioCtx.currentTime + 0.12); // C4
                            gain.gain.setValueAtTime(0.15, audioCtx.currentTime);
                            gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.12);
                            osc.start();
                            osc.stop(audioCtx.currentTime + 0.12);
                        }} else {{
                            osc.type = 'sine';
                            osc.frequency.setValueAtTime(659.25, audioCtx.currentTime); // E5
                            osc.frequency.exponentialRampToValueAtTime(880, audioCtx.currentTime + 0.08); // A5
                            gain.gain.setValueAtTime(0.12, audioCtx.currentTime);
                            gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.08);
                            osc.start();
                            osc.stop(audioCtx.currentTime + 0.08);
                        }}
                    }} catch (e) {{
                        console.error("Audio play error", e);
                    }}
                }})();
            </script>
            """,
            unsafe_allow_html=True
        )

    # Read Subtraction Mode from session state
    sub_mode = st.session_state.get("sub_mode_toggle", False)
    
    tq_ico = "➖" if sub_mode else "🔴"
    tb_ico = "➖" if sub_mode else "🟡"
    prefix = "➖ " if sub_mode else ""
    
    col_hifz, col_ahkam, col_makharij = st.columns([1, 1.15, 1.65])
    
    with col_hifz:
        with st.container(border=True):
            st.markdown("<div style='text-align: center; font-weight: bold; margin-bottom: 5px; color: var(--emerald);'>Hifz Mistakes</div>", unsafe_allow_html=True)
            
            # Row 1: Talqeen & Tanbeeh
            r1_c1, r1_c2 = st.columns(2)
            with r1_c1:
                st.button(f"{tq_ico} Tq ({counts.get('talqeen', 0)})", width="stretch", on_click=on_click, kwargs={"kind": "talqeen"}, key="btn_talqeen")
            with r1_c2:
                st.button(f"{tb_ico} Tb ({counts.get('tanbeeh', 0)})", width="stretch", on_click=on_click, kwargs={"kind": "tanbeeh"}, key="btn_tanbeeh")
            
            # Row 2: I'rab (symmetrical)
            r2_c1, r2_c2, r2_c3 = st.columns([0.75, 4.5, 0.75])
            with r2_c1:
                st.button(tq_ico, on_click=on_click, kwargs={"kind": "irab_talqeen"}, key="btn_irab_tq")
            with r2_c2:
                st.markdown(f"<div style='font-size: 0.8rem; font-weight: bold; line-height: 26px; text-align: center; width: 100%; white-space: nowrap;'>I'rab ({counts.get('irab_talqeen', 0)}-{counts.get('irab_tanbeeh', 0)})</div>", unsafe_allow_html=True)
            with r2_c3:
                st.button(tb_ico, on_click=on_click, kwargs={"kind": "irab_tanbeeh"}, key="btn_irab_tb")

            # Row 3: Repeat (symmetrical)
            r3_c1, r3_c2, r3_c3 = st.columns([0.75, 4.5, 0.75])
            with r3_c1:
                st.button(tq_ico, on_click=on_click, kwargs={"kind": "repeat_mistake_talqeen"}, key="btn_repeat_tq")
            with r3_c2:
                st.markdown(f"<div style='font-size: 0.8rem; font-weight: bold; line-height: 26px; text-align: center; width: 100%; white-space: nowrap;'>Repeat ({counts.get('repeat_mistake_talqeen', 0)}-{counts.get('repeat_mistake_tanbeeh', 0)})</div>", unsafe_allow_html=True)
            with r3_c3:
                st.button(tb_ico, on_click=on_click, kwargs={"kind": "repeat_mistake_tanbeeh"}, key="btn_repeat_tb")

            # Row 4: Mutashab. (symmetrical)
            r4_c1, r4_c2, r4_c3 = st.columns([0.75, 4.5, 0.75])
            with r4_c1:
                st.button(tq_ico, on_click=on_click, kwargs={"kind": "mutashabehat_talqeen"}, key="btn_mutashab_tq")
            with r4_c2:
                st.markdown(f"<div style='font-size: 0.75rem; font-weight: bold; line-height: 26px; text-align: center; width: 100%; white-space: nowrap;'>Mutashab. ({counts.get('mutashabehat_talqeen', 0)}-{counts.get('mutashabehat_tanbeeh', 0)})</div>", unsafe_allow_html=True)
            with r4_c3:
                st.button(tb_ico, on_click=on_click, kwargs={"kind": "mutashabehat_tanbeeh"}, key="btn_mutashab_tb")

            # Row 5: Awakhir (symmetrical)
            r5_c1, r5_c2, r5_c3 = st.columns([0.75, 4.5, 0.75])
            with r5_c1:
                st.button(tq_ico, on_click=on_click, kwargs={"kind": "awakhir_ul_ayat_talqeen"}, key="btn_awakhir_tq")
            with r5_c2:
                st.markdown(f"<div style='font-size: 0.8rem; font-weight: bold; line-height: 26px; text-align: center; width: 100%; white-space: nowrap;'>Awakhir ({counts.get('awakhir_ul_ayat_talqeen', 0)}-{counts.get('awakhir_ul_ayat_tanbeeh', 0)})</div>", unsafe_allow_html=True)
            with r5_c3:
                st.button(tb_ico, on_click=on_click, kwargs={"kind": "awakhir_ul_ayat_tanbeeh"}, key="btn_awakhir_tb")

            # Row 6: Zero Marks Override
            st.divider()
            is_zero_active = bool(counts.get("is_zero_marks", False))
            if sub_mode:
                st.button(
                    "↩️ Remove Zero Marks" if is_zero_active else "Remove Zero Marks (No-op)",
                    disabled=not is_zero_active,
                    width="stretch",
                    on_click=on_click,
                    kwargs={"kind": "is_zero_marks"},
                    key="btn_remove_zero_marks"
                )
            else:
                st.button(
                    "⚠️ Mark Zero Marks" if not is_zero_active else "✅ Zero Marks Applied",
                    type="primary" if is_zero_active else "secondary",
                    width="stretch",
                    on_click=on_click,
                    kwargs={"kind": "is_zero_marks"},
                    key="btn_mark_zero_marks"
                )
                
    with col_ahkam:
        with st.container(border=True):
            st.markdown("<div style='text-align: center; font-weight: bold; margin-bottom: 5px; color: var(--emerald);'>Ahkam Mistakes</div>", unsafe_allow_html=True)
            
            ahkam_buttons_layout = [
                [("ikhfa", "Ikhfa"), ("izhaar", "Izhaar")],
                [("qalqalah", "Qalqalah"), ("ism_jalalah", "Ism Jalal")],
                [("tahreek_sakin", "Tahreek"), ("gunnah", "Gunnah")],
                [("idgham", "Idgham"), ("madd_lazim", "M. Lazim")],
                [("madd_muttasil", "M. Mutta."), ("mad_tabaiee", "M. Tabai.")],
                [("ikhfa_shafawi", "Ikh. Shaf."), ("iqlab", "Iqlab")],
            ]

            for row in ahkam_buttons_layout:
                ar_c1, ar_c2 = st.columns(2)
                for col_idx, (kind, label) in enumerate(row):
                    target_col = ar_c1 if col_idx == 0 else ar_c2
                    with target_col:
                        is_active = counts.get(kind, 0) == 1
                        active_class = "ahkam-active" if is_active else "ahkam-inactive"
                        st.markdown(f"<span class='{active_class}' style='display: none;'>active</span>", unsafe_allow_html=True)
                        st.button(label, width="stretch", on_click=on_click, kwargs={"kind": kind}, key=f"btn_{kind}")

    with col_makharij:
        with st.container(border=True):
            st.markdown("<div class='makharij-card-anchor' style='text-align: center; font-weight: bold; margin-bottom: 8px; color: var(--emerald);'>Makharij Mistakes</div>", unsafe_allow_html=True)
            
            # 4 rows of 7 columns, right-to-left layout matching the image:
            makharij_rows = [
                # Row 1 (right-to-left): ا, ب, ت, ث, ج, ح, خ -> represented in python list left-to-right as: خ, ح, ج, ث, ت, ب, ا
                [
                    {"char": "خ", "kind": "makhraj_khaa"},
                    {"char": "ح", "kind": "makhraj_haa"},
                    {"char": "ج", "kind": "makhraj_jeem"},
                    {"char": "ث", "kind": "makhraj_thaa"},
                    {"char": "ت", "kind": "makhraj_taa"},
                    {"char": "ب", "kind": "makhraj_baa"},
                    {"char": "ا", "kind": "makhraj_alif"},
                ],
                # Row 2 (right-to-left): د, ذ, ر, z, s, sh, s -> represented in python list left-to-right as: ص, sh, s, z, r, th, d
                [
                    {"char": "ص", "kind": "makhraj_saad"},
                    {"char": "ش", "kind": "makhraj_sheen"},
                    {"char": "س", "kind": "makhraj_seen"},
                    {"char": "ز", "kind": "makhraj_zaa"},
                    {"char": "ر", "kind": "makhraj_raa"},
                    {"char": "ذ", "kind": "makhraj_thaal"},
                    {"char": "د", "kind": "makhraj_daal"},
                ],
                # Row 3 (right-to-left): ض, ط, ظ, ع, gh, f, q -> represented in python list left-to-right as: q, f, gh, a, z, t, d
                [
                    {"char": "ق", "kind": "makhraj_qaaf"},
                    {"char": "ف", "kind": "makhraj_faa"},
                    {"char": "غ", "kind": "makhraj_ghain"},
                    {"char": "ع", "kind": "makhraj_ain"},
                    {"char": "ظ", "kind": "makhraj_zaa_thick"},
                    {"char": "ط", "kind": "makhraj_taa_thick"},
                    {"char": "ض", "kind": "makhraj_daad"},
                ],
                # Row 4 (right-to-left): k, l, m, n, h, w, y -> represented in python list left-to-right as: y, w, h, n, m, l, k
                [
                    {"char": "ي", "kind": "makhraj_yaa"},
                    {"char": "و", "kind": "makhraj_waw"},
                    {"char": "هـ", "kind": "makhraj_haa_weak"},
                    {"char": "ن", "kind": "makhraj_noon"},
                    {"char": "م", "kind": "makhraj_meem"},
                    {"char": "ل", "kind": "makhraj_laam"},
                    {"char": "ك", "kind": "makhraj_kaaf"},
                ]
            ]
            


            for row_idx, row_letters in enumerate(makharij_rows):
                cols = st.columns(7)
                for col_idx, letter in enumerate(row_letters):
                    with cols[col_idx]:
                        char = letter["char"]
                        kind = letter["kind"]
                        active_class = "makhraj-active" if counts.get(kind, 0) == 1 else "makhraj-inactive"
                        st.markdown(f"<span class='{active_class}' style='display: none;'>active</span>", unsafe_allow_html=True)
                        st.button(f"{char}", width="stretch", on_click=on_click, kwargs={"kind": kind}, key=f"btn_makhraj_{kind}")


def render_header_with_homework(title: str, student_id: Optional[str]) -> None:
    col_title, col_hw = st.columns([1.2, 5])
    with col_title:
        st.markdown(f"<h3 style='margin: 0; padding: 0;'>{title}</h3>", unsafe_allow_html=True)
    with col_hw:
        if student_id:
            cache_key = f"prev_takhteet_{student_id}"
            if cache_key not in st.session_state:
                from app.db import get_previous_takhteet
                try:
                    st.session_state[cache_key] = get_previous_takhteet(student_id=student_id)
                except Exception:
                    st.session_state[cache_key] = None
            prev = st.session_state[cache_key]
            if prev:
                jadeed = prev.get("jadeed_text_raw", "").strip() or "-"
                juzulhali = prev.get("juzulhali_text_raw", "").strip() or "-"
                murajat = prev.get("murajat_text_raw", "").strip() or "-"
                
                jadeed_inline = jadeed.replace("\n", " ")
                juzulhali_inline = juzulhali.replace("\n", " ")
                murajat_inline = murajat.replace("\n", " ")
                
                st.markdown(f"""
                <div style="display: flex; gap: 12px; justify-content: flex-end; align-items: center; height: 100%; padding-top: 6px; font-size: 0.82rem; flex-wrap: wrap;">
                  <span style="color: var(--ink); opacity: 0.6; font-weight: bold; white-space: nowrap;">Prev HW:</span>
                  <span style="color: var(--emerald); font-weight: bold; white-space: nowrap;">Jadeed:</span>
                  <span style="color: var(--ink); font-weight: 500; white-space: nowrap;">{jadeed_inline}</span>
                  <span style="color: var(--border); font-weight: bold;">|</span>
                  <span style="color: var(--emerald); font-weight: bold; white-space: nowrap;">Juzulhali:</span>
                  <span style="color: var(--ink); font-weight: 500; white-space: nowrap;">{juzulhali_inline}</span>
                  <span style="color: var(--border); font-weight: bold;">|</span>
                  <span style="color: var(--emerald); font-weight: bold; white-space: nowrap;">Murajat:</span>
                  <span style="color: var(--ink); font-weight: 500; white-space: nowrap;">{murajat_inline}</span>
                </div>
                """, unsafe_allow_html=True)


def show_previous_takhteet(student_id: str) -> None:
    pass


def ensure_today_sessions(student_id: str) -> None:
    if "today_sessions" not in st.session_state or st.session_state.get("today_sessions_student_id") != student_id:
        from app.db import get_today_listening_sessions
        sessions = get_today_listening_sessions(student_id=student_id)
        # Store in dict: key is (mode, surah_id, page_number)
        today_dict = {}
        for s in sessions:
            surah_id = int(s["surah_id"]) if s["surah_id"] is not None else None
            page_number = int(s["page_number"]) if s["page_number"] is not None else None
            key = (s["mode"], surah_id, page_number)
            if key not in today_dict:  # Keep the most recent one (since sorted by created_at desc)
                today_dict[key] = s["id"]
        st.session_state.today_sessions = today_dict
        st.session_state.today_sessions_student_id = student_id

