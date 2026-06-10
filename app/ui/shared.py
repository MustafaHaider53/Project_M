from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import streamlit as st


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
    col_hifz, col_ahkam, col_makharij = st.columns([1, 1.15, 1.65])
    
    with col_hifz:
        with st.container(border=True):
            st.markdown("<div style='text-align: center; font-weight: bold; margin-bottom: 5px; color: var(--emerald);'>Hifz Mistakes</div>", unsafe_allow_html=True)
            
            # Row 1: Talqeen & Tanbeeh
            r1_c1, r1_c2 = st.columns(2)
            with r1_c1:
                st.button(f"🔴 Tq ({counts.get('talqeen', 0)})", use_container_width=True, on_click=on_click, kwargs={"kind": "talqeen"}, key="btn_talqeen")
            with r1_c2:
                st.button(f"🟡 Tb ({counts.get('tanbeeh', 0)})", use_container_width=True, on_click=on_click, kwargs={"kind": "tanbeeh"}, key="btn_tanbeeh")
            
            # Row 2: I'rab (split)
            r2_c1, r2_c2, r2_c3 = st.columns([4.5, 0.75, 0.75])
            with r2_c1:
                st.markdown(f"<div style='font-size: 0.8rem; font-weight: bold; line-height: 26px; white-space: nowrap;'>I'rab ({counts.get('irab_talqeen', 0)}-{counts.get('irab_tanbeeh', 0)})</div>", unsafe_allow_html=True)
            with r2_c2:
                st.button("🔴", on_click=on_click, kwargs={"kind": "irab_talqeen"}, key="btn_irab_tq")
            with r2_c3:
                st.button("🟡", on_click=on_click, kwargs={"kind": "irab_tanbeeh"}, key="btn_irab_tb")

            # Row 3: Repeat (split)
            r3_c1, r3_c2, r3_c3 = st.columns([4.5, 0.75, 0.75])
            with r3_c1:
                st.markdown(f"<div style='font-size: 0.8rem; font-weight: bold; line-height: 26px; white-space: nowrap;'>Repeat ({counts.get('repeat_mistake_talqeen', 0)}-{counts.get('repeat_mistake_tanbeeh', 0)})</div>", unsafe_allow_html=True)
            with r3_c2:
                st.button("🔴", on_click=on_click, kwargs={"kind": "repeat_mistake_talqeen"}, key="btn_repeat_tq")
            with r3_c3:
                st.button("🟡", on_click=on_click, kwargs={"kind": "repeat_mistake_tanbeeh"}, key="btn_repeat_tb")

            # Row 4: Mutashab. (split)
            r4_c1, r4_c2, r4_c3 = st.columns([4.5, 0.75, 0.75])
            with r4_c1:
                st.markdown(f"<div style='font-size: 0.75rem; font-weight: bold; line-height: 26px; white-space: nowrap;'>Mutashab. ({counts.get('mutashabehat_talqeen', 0)}-{counts.get('mutashabehat_tanbeeh', 0)})</div>", unsafe_allow_html=True)
            with r4_c2:
                st.button("🔴", on_click=on_click, kwargs={"kind": "mutashabehat_talqeen"}, key="btn_mutashab_tq")
            with r4_c3:
                st.button("🟡", on_click=on_click, kwargs={"kind": "mutashabehat_tanbeeh"}, key="btn_mutashab_tb")

            # Row 5: Awakhir (split)
            r5_c1, r5_c2, r5_c3 = st.columns([4.5, 0.75, 0.75])
            with r5_c1:
                st.markdown(f"<div style='font-size: 0.8rem; font-weight: bold; line-height: 26px; white-space: nowrap;'>Awakhir ({counts.get('awakhir_ul_ayat_talqeen', 0)}-{counts.get('awakhir_ul_ayat_tanbeeh', 0)})</div>", unsafe_allow_html=True)
            with r5_c2:
                st.button("🔴", on_click=on_click, kwargs={"kind": "awakhir_ul_ayat_talqeen"}, key="btn_awakhir_tq")
            with r5_c3:
                st.button("🟡", on_click=on_click, kwargs={"kind": "awakhir_ul_ayat_tanbeeh"}, key="btn_awakhir_tb")
                
    with col_ahkam:
        with st.container(border=True):
            st.markdown("<div style='text-align: center; font-weight: bold; margin-bottom: 5px; color: var(--emerald);'>Ahkam Mistakes</div>", unsafe_allow_html=True)
            
            # Row 1: Ikhfa & Izhaar
            ar1_c1, ar1_c2 = st.columns(2)
            with ar1_c1:
                st.button(f"Ikhfa ({counts.get('ikhfa', 0)})", use_container_width=True, on_click=on_click, kwargs={"kind": "ikhfa"}, key="btn_ikhfa")
            with ar1_c2:
                st.button(f"Izhaar ({counts.get('izhaar', 0)})", use_container_width=True, on_click=on_click, kwargs={"kind": "izhaar"}, key="btn_izhaar")
                
            # Row 2: Qalqalah & Ismul Jalalah
            ar2_c1, ar2_c2 = st.columns(2)
            with ar2_c1:
                st.button(f"Qalqalah ({counts.get('qalqalah', 0)})", use_container_width=True, on_click=on_click, kwargs={"kind": "qalqalah"}, key="btn_qalqalah")
            with ar2_c2:
                st.button(f"Ism Jalal ({counts.get('ism_jalalah', 0)})", use_container_width=True, on_click=on_click, kwargs={"kind": "ism_jalalah"}, key="btn_ism_jalalah")
                
            # Row 3: Tahreek Sakin & Gunnah
            ar3_c1, ar3_c2 = st.columns(2)
            with ar3_c1:
                st.button(f"Tahreek ({counts.get('tahreek_sakin', 0)})", use_container_width=True, on_click=on_click, kwargs={"kind": "tahreek_sakin"}, key="btn_tahreek_sakin")
            with ar3_c2:
                st.button(f"Gunnah ({counts.get('gunnah', 0)})", use_container_width=True, on_click=on_click, kwargs={"kind": "gunnah"}, key="btn_gunnah")
                
            # Row 4: Idgham & Madd Lazim
            ar4_c1, ar4_c2 = st.columns(2)
            with ar4_c1:
                st.button(f"Idgham ({counts.get('idgham', 0)})", use_container_width=True, on_click=on_click, kwargs={"kind": "idgham"}, key="btn_idgham")
            with ar4_c2:
                st.button(f"M. Lazim ({counts.get('madd_lazim', 0)})", use_container_width=True, on_click=on_click, kwargs={"kind": "madd_lazim"}, key="btn_madd_lazim")
                
            # Row 5: Madd Muttasil & Mad Tabaiee
            ar5_c1, ar5_c2 = st.columns(2)
            with ar5_c1:
                st.button(f"M. Mutta. ({counts.get('madd_muttasil', 0)})", use_container_width=True, on_click=on_click, kwargs={"kind": "madd_muttasil"}, key="btn_madd_muttasil")
            with ar5_c2:
                st.button(f"M. Tabai. ({counts.get('mad_tabaiee', 0)})", use_container_width=True, on_click=on_click, kwargs={"kind": "mad_tabaiee"}, key="btn_mad_tabaiee")

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
                        st.button(f"{char}", use_container_width=True, on_click=on_click, kwargs={"kind": kind}, key=f"btn_makhraj_{kind}")


def render_header_with_homework(title: str, student_id: Optional[str]) -> None:
    col_title, col_hw = st.columns([1.2, 5])
    with col_title:
        st.markdown(f"<h3 style='margin: 0; padding: 0;'>{title}</h3>", unsafe_allow_html=True)
    with col_hw:
        if student_id:
            from app.db import get_previous_takhteet
            try:
                prev = get_previous_takhteet(student_id=student_id)
            except Exception:
                prev = None
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

