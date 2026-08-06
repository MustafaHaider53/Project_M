from __future__ import annotations

import json
import os
from typing import Any, Dict, List

import streamlit as st

from app.db import (
    insert_jadeed_rows,
    list_surahs,
    today_iso,
    get_today_jadeed_state,
)
from app.ui.shared import render_header_with_homework
from app.ui.student import current_student_badge


@st.cache_resource
def load_quran_metadata() -> Dict[str, Any]:
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "quran_metadata.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def on_surah_change():
    metadata = load_quran_metadata()
    new_surah = st.session_state.jadeed_surah
    s_num_str = str(new_surah["number"])
    pages_dict = metadata["surahs"][s_num_str]["pages"]
    page_options = sorted(list(pages_dict.keys()), key=int)
    first_page = page_options[0]
    
    st.session_state.jadeed_page = first_page
    
    ayah_options = sorted(pages_dict[first_page], key=int)
    st.session_state.jadeed_ayah = ayah_options[0]


def on_page_change():
    metadata = load_quran_metadata()
    new_surah = st.session_state.jadeed_surah
    s_num_str = str(new_surah["number"])
    pages_dict = metadata["surahs"][s_num_str]["pages"]
    selected_page = st.session_state.jadeed_page
    
    ayah_options = sorted(pages_dict[selected_page], key=int)
    st.session_state.jadeed_ayah = ayah_options[0]


def render_jadeed() -> None:
    student_id = st.session_state.get("student_id")
    with st.container():
        st.markdown('<div class="sticky-anchor"></div>', unsafe_allow_html=True)
        render_header_with_homework("Jadeed", student_id)
        current_student_badge()

    if not student_id:
        st.warning("Please select a student on Home first.")
        return

    # One-time success/info message
    flash = st.session_state.pop("jadeed_flash", None)
    if flash:
        st.success(flash)

    # Load Surahs from database
    db_surahs = list_surahs()
    if not db_surahs:
        st.info("No Surahs found yet. Run the SQL in `supabase/schema.sql` first.")
        return

    # Load Quran page/ayah mapping metadata
    try:
        quran_metadata = load_quran_metadata()
    except Exception as e:
        st.error(f"Failed to load Quran metadata: {e}")
        return

    today = today_iso()
    
    # Fetch today's existing entries and status using lightweight function
    with st.spinner("Loading today's Jadeed status..."):
        summary = get_today_jadeed_state(student_id=student_id, date_str=today)
    
    todays_entries = summary.get("jadeed") or []
    no_jadeed_status = summary.get("no_jadeed") or False

    # 1. Title/Header Section
    st.markdown("### Today's Jadeed Recitations")
    
    # 2. Render Existing Entries styled beautifully
    if todays_entries:
        st.markdown("<div style='margin-bottom: 15px;'>", unsafe_allow_html=True)
        for idx, entry in enumerate(todays_entries):
            entry_id = entry.get("id")
            surah_info = entry.get("surahs") or {}
            surah_name = surah_info.get("name_en", "Unknown")
            surah_ar = surah_info.get("name_ar", "")
            surah_num = surah_info.get("number", 0)
            page_num = entry.get("page_number") or 0
            ayah_num = entry.get("ayah_number") or 0
            volume = entry.get("volume", "")
            
            # Premium card design for each entry
            card_html = f"""
            <div style='background-color: var(--card); border: 1.5px solid var(--border); padding: 15px; border-radius: 10px; margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 2px 5px rgba(0,0,0,0.02);'>
                <div>
                    <span style='font-size: 1.1rem; font-weight: bold; color: var(--emerald);'>📖 Surah {surah_num} — {surah_name} ({surah_ar})</span>
                    <div style='font-size: 0.9rem; color: var(--ink); opacity: 0.85; margin-top: 4px;'>
                        <span style='margin-right: 15px;'>📄 <b>Page:</b> {page_num}</span>
                        <span style='margin-right: 15px;'>🔢 <b>Ayah:</b> {ayah_num}</span>
                        <span>📊 <b>Volume:</b> {volume}</span>
                    </div>
                </div>
            </div>
            """
            c_card, c_btn = st.columns([5, 1])
            with c_card:
                st.markdown(card_html, unsafe_allow_html=True)
            with c_btn:
                # Vertical alignment centering the delete button
                st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
                if st.button("🗑️ Delete", key=f"del_entry_{idx}_{entry_id}", type="secondary", width="stretch"):
                    # Remove the item and update Supabase
                    payload = []
                    for e in todays_entries:
                        if e.get("id") != entry_id:
                            payload.append({
                                "surah_id": e.get("surah_id"),
                                "page_number": int(e.get("page_number") or 1),
                                "ayah_number": int(e.get("ayah_number") or 1),
                                "volume": e.get("volume") or "Kamil"
                            })
                    with st.spinner("Deleting entry..."):
                        insert_jadeed_rows(student_id=student_id, rows=payload)
                    st.session_state.pop("jadeed_state_init", None)
                    st.session_state.jadeed_flash = "Entry deleted successfully."
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        if no_jadeed_status:
            st.markdown(
                """
                <div style='background-color: rgba(197, 168, 128, 0.1); border: 1px solid #c5a880; color: #c5a880; padding: 15px; border-radius: 8px; margin-bottom: 20px; font-weight: 500;'>
                    🌙 Status: Marked as 'No Jadeed' for today.
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.info("No Jadeed entries recorded for today yet.")

    # 3. Add New Entry Section
    st.markdown("---")
    
    # Pre-build Surah options in sorted order
    surah_list = []
    for s_num_str, s_data in quran_metadata["surahs"].items():
        s_num = int(s_num_str)
        surah_list.append({
            "number": s_num,
            "name_en": s_data["name_en"],
            "name_ar": s_data["name_ar"],
            "label": f"{s_num:03d} — {s_data['name_en']} ({s_data['name_ar']})"
        })
    surah_list = sorted(surah_list, key=lambda x: x["number"])

    # Reset/Initialize session state keys to avoid cascading dropdown lags
    init_session_key = f"jadeed_state_init::{student_id}"
    if (
        st.session_state.get("jadeed_state_init") != init_session_key
        or "jadeed_surah" not in st.session_state
        or "jadeed_page" not in st.session_state
        or "jadeed_ayah" not in st.session_state
        or "jadeed_volume" not in st.session_state
    ):
        st.session_state.jadeed_state_init = init_session_key
        
        # Try to load last jadeed entry to pre-fill
        from app.db import list_jadeed_entries
        last_entries = list_jadeed_entries(student_id=student_id, limit=1)
        last_entry = last_entries[0] if last_entries else None
        
        default_surah = surah_list[0]
        if last_entry:
            last_surah_id = last_entry.get("surah_id")
            found_surah = next((s for s in surah_list if s["number"] == last_surah_id), None)
            if found_surah:
                default_surah = found_surah

        st.session_state.jadeed_surah = default_surah
        
        s_num_str = str(default_surah["number"])
        pages_dict = quran_metadata["surahs"][s_num_str]["pages"]
        page_options = sorted(list(pages_dict.keys()), key=int)
        
        default_page = page_options[0]
        if last_entry:
            last_page = str(last_entry.get("page_number"))
            if last_page in page_options:
                default_page = last_page
                
        st.session_state.jadeed_page = default_page
        
        ayah_options = sorted(pages_dict[default_page], key=int)
        
        default_ayah = ayah_options[0]
        if last_entry:
            last_ayah = str(last_entry.get("ayah_number"))
            if last_ayah in ayah_options:
                default_ayah = last_ayah
                
        st.session_state.jadeed_ayah = default_ayah
        st.session_state.jadeed_volume = last_entry.get("volume", "Kamil") if last_entry else "Kamil"

    # Outer container for form
    with st.container(border=True):
        st.markdown("<h4 style='margin-top: 0; margin-bottom: 15px; color: var(--emerald);'>➕ Add New Recitation</h4>", unsafe_allow_html=True)
        
        col_s, col_p, col_a, col_v = st.columns([2, 1, 1, 1])
        
        with col_s:
            selected_surah = st.selectbox(
                "Surah",
                options=surah_list,
                format_func=lambda x: x["label"],
                key="jadeed_surah",
                on_change=on_surah_change
            )
            
        with col_p:
            # Dynamically fetch pages for the selected Surah
            s_num_str = str(selected_surah["number"])
            pages_dict = quran_metadata["surahs"][s_num_str]["pages"]
            page_options = sorted(list(pages_dict.keys()), key=int)
            
            # Guard against out-of-bounds or uninitialized selection in state
            if "jadeed_page" not in st.session_state or st.session_state.jadeed_page not in page_options:
                st.session_state.jadeed_page = page_options[0]
                
            selected_page = st.selectbox(
                "Page",
                options=page_options,
                key="jadeed_page",
                on_change=on_page_change
            )
            
        with col_a:
            # Dynamically fetch ayahs on the selected page for the selected Surah
            ayah_options = sorted(pages_dict[selected_page], key=int)
            
            # Guard against out-of-bounds or uninitialized selection in state
            if "jadeed_ayah" not in st.session_state or st.session_state.jadeed_ayah not in ayah_options:
                st.session_state.jadeed_ayah = ayah_options[0]
                
            selected_ayah = st.selectbox(
                "Ayah",
                options=ayah_options,
                key="jadeed_ayah"
            )
            
        with col_v:
            # Guard against invalid or uninitialized selection in state
            if "jadeed_volume" not in st.session_state or st.session_state.jadeed_volume not in ["Kamil", "Ruba", "Nisf", "Sulus"]:
                st.session_state.jadeed_volume = "Kamil"
                
            selected_volume = st.selectbox(
                "Volume",
                options=["Kamil", "Ruba", "Nisf", "Sulus"],
                key="jadeed_volume"
            )
            
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        
        # Action buttons
        c_add, c_no = st.columns([2, 1])
        with c_add:
            if st.button("➕ Add Entry", type="primary", width="stretch"):
                # Find matching DB surah_id
                db_surah = next((s for s in db_surahs if int(s["number"]) == selected_surah["number"]), None)
                if not db_surah:
                    st.error("Selected Surah not found in database.")
                else:
                    new_row = {
                        "surah_id": db_surah["id"],
                        "page_number": int(selected_page),
                        "ayah_number": int(selected_ayah),
                        "volume": selected_volume
                    }
                    
                    # Prepare payload of all existing + new
                    payload = []
                    for e in todays_entries:
                        payload.append({
                            "surah_id": e.get("surah_id"),
                            "page_number": int(e.get("page_number") or 1),
                            "ayah_number": int(e.get("ayah_number") or 1),
                            "volume": e.get("volume") or "Kamil"
                        })
                    payload.append(new_row)
                    
                    with st.spinner("Saving new entry..."):
                        insert_jadeed_rows(student_id=student_id, rows=payload)
                    st.session_state.pop("jadeed_state_init", None)
                    st.session_state.jadeed_flash = "New Jadeed entry added successfully!"
                    st.rerun()
                    
        with c_no:
            # Show "No Jadeed today" button (disabled if entries exist)
            no_jadeed_disabled = len(todays_entries) > 0
            if st.button(
                "🌙 Mark 'No Jadeed'", 
                type="secondary", 
                disabled=no_jadeed_disabled, 
                width="stretch",
                help="Mark today as No Jadeed (only available if no entries are added)"
            ):
                with st.spinner("Marking as No Jadeed..."):
                    insert_jadeed_rows(student_id=student_id, rows=[])
                st.session_state.pop("jadeed_state_init", None)
                st.session_state.jadeed_flash = "Marked: No Jadeed for today."
                st.rerun()
