from __future__ import annotations

import streamlit as st
import pandas as pd
import altair as alt
from typing import Any, Dict, List

from app.db import get_student_sessions_with_counts


def render_student_analytics(student_id: str, student_name: str) -> None:
    st.markdown(f"#### 📊 Recitation & Mistake Analytics — {student_name}")
    
    with st.spinner("Analyzing student recitation history..."):
        sessions = get_student_sessions_with_counts(student_id=student_id)
        
    if not sessions:
        st.info("No recitation sessions recorded yet. Start testing the student to see analytics.")
        return
        
    surah_mistakes = []
    page_mistakes = []
    
    total_sessions = len(sessions)
    total_talqeen = 0
    total_tanbeeh = 0
    total_marks = 0.0
    
    secondary_counts = {
        "I'rab": 0,
        "Mutashabihat": 0,
        "Repeat": 0,
        "Awakhir": 0
    }
    
    ahkam_display_names = {
        "ikhfa": "Ikhfa",
        "izhaar": "Izhaar",
        "qalqalah": "Qalqalah",
        "ism_jalalah": "Ism Jalalah",
        "tahreek_sakin": "Tahreek Sakin",
        "gunnah": "Gunnah",
        "idgham": "Idgham",
        "madd_lazim": "Madd Lazim",
        "madd_muttasil": "Madd Muttasil",
        "mad_tabaiee": "Madd Taba'iee",
        "ikhfa_shafawi": "Ikhfa Shafawi",
        "iqlab": "Iqlab"
    }
    
    from app.db import MAKHARIJ_COLS
    makhraj_display_names = {
        "makhraj_alif": "Alif (أ)",
        "makhraj_baa": "Baa (ب)",
        "makhraj_taa": "Taa (ت)",
        "makhraj_thaa": "Thaa (ث)",
        "makhraj_jeem": "Jeem (ج)",
        "makhraj_haa": "Haa (ح)",
        "makhraj_khaa": "Khaa (خ)",
        "makhraj_daal": "Daal (د)",
        "makhraj_thaal": "Thaal (ذ)",
        "makhraj_raa": "Raa (ر)",
        "makhraj_zaa": "Zaa (ز)",
        "makhraj_seen": "Seen (س)",
        "makhraj_sheen": "Sheen (ش)",
        "makhraj_saad": "Saad (ص)",
        "makhraj_daad": "Daad (ض)",
        "makhraj_taa_thick": "Taa (ط)",
        "makhraj_zaa_thick": "Zaa (ظ)",
        "makhraj_ain": "Ain (ع)",
        "makhraj_ghain": "Ghain (غ)",
        "makhraj_faa": "Faa (ف)",
        "makhraj_qaaf": "Qaaf (ق)",
        "makhraj_kaaf": "Kaaf (ك)",
        "makhraj_laam": "Laam (ل)",
        "makhraj_meem": "Meem (م)",
        "makhraj_noon": "Noon (ن)",
        "makhraj_haa_weak": "Haa (هـ)",
        "makhraj_waw": "Waw (و)",
        "makhraj_yaa": "Yaa (ي)"
    }
    
    musaid_display_names = {
        "musaid_end_part": "🔚 End Part",
        "musaid_beg_part": "🔝 Beginning Part",
        "musaid_ayat_after_ayat": "🔗 Ayat Linkage",
        "musaid_page_after_page": "📖 Page Transition",
        "musaid_no_image": "🖼️ No Page Image",
        "musaid_lehen": "🎵 Lehen only"
    }
    
    ahkam_counts = {name: 0 for name in ahkam_display_names.values()}
    makharij_counts = {name: 0 for name in makhraj_display_names.values()}
    musaid_counts = {name: 0 for name in musaid_display_names.values()}
    daily_data = {} # key: activity_date, value: {talqeen, tanbeeh}
    
    for s in sessions:
        date_str = s.get("activity_date")
        mode = s.get("mode")
        
        counts = s.get("mistake_counts") or {}
        if isinstance(counts, list):
            counts = counts[0] if counts else {}
            
        tq = int(counts.get("talqeen", 0) or 0)
        tb = int(counts.get("tanbeeh", 0) or 0)
        
        total_talqeen += tq
        total_tanbeeh += tb
        
        # Marks calculation
        is_zero = bool(counts.get("is_zero_marks", False))
        if is_zero:
            marks = 0.0
        else:
            marks = 10.0 - (0.5 * tq) - (0.25 * tb)
            if marks < 0:
                marks = 0.0
        total_marks += marks
        
        # Secondary mistakes
        irab = int(counts.get("irab", 0) or 0)
        mutashab = int(counts.get("mutashabehat", 0) or 0)
        repeat = int(counts.get("repeat_mistake", 0) or 0)
        awakhir = int(counts.get("awakhir_ul_ayat", 0) or 0)
        
        secondary_counts["I'rab"] += irab
        secondary_counts["Mutashabihat"] += mutashab
        secondary_counts["Repeat"] += repeat
        secondary_counts["Awakhir"] += awakhir
        
        # Ahkam mistakes
        for key, disp in ahkam_display_names.items():
            ahkam_counts[disp] += int(counts.get(key, 0) or 0)
            
        # Makharij mistakes
        for key, disp in makhraj_display_names.items():
            makharij_counts[disp] += int(counts.get(key, 0) or 0)
            
        # Musaid indicators
        for key, disp in musaid_display_names.items():
            musaid_counts[disp] += int(counts.get(key, 0) or 0)
            
        # Group by daily trend
        if date_str:
            if isinstance(date_str, str):
                d_key = date_str[:10]
            else:
                d_key = str(date_str)
                
            if d_key not in daily_data:
                daily_data[d_key] = {"Talqeen": 0, "Tanbeeh": 0}
            daily_data[d_key]["Talqeen"] += tq
            daily_data[d_key]["Tanbeeh"] += tb
            
        # Group by Surah (for Murajat)
        if mode == "murajat" and s.get("surahs"):
            surah = s["surahs"]
            if isinstance(surah, list):
                surah = surah[0] if surah else {}
            s_num = surah.get("number", 0)
            s_num_val = int(s_num or 0)
            s_en = surah.get("name_en", "")
            p_num = int(s.get("page_number") or 0)
            if p_num > 0:
                surah_display = f"{s_num_val:03d} — {s_en} (p. {p_num})"
            else:
                s_ar = surah.get("name_ar", "")
                surah_display = f"{s_num_val:03d} — {s_en} ({s_ar})"
            
            surah_mistakes.append({"Surah": surah_display, "Mistake Type": "Talqeen", "Count": tq})
            surah_mistakes.append({"Surah": surah_display, "Mistake Type": "Tanbeeh", "Count": tb})
                
        # Group by Page (for Juzulhali)
        if mode == "juzulhali":
            surah = s.get("surahs")
            p_num = int(s.get("page_number") or 0)
            if surah:
                if isinstance(surah, list):
                    surah = surah[0] if surah else {}
                s_num = surah.get("number", 0)
                s_num_val = int(s_num or 0)
                s_en = surah.get("name_en", "")
                page_display = f"{s_num_val:03d} — {s_en} (p. {p_num})"
            else:
                page_display = f"Page {p_num:02d}"
            page_mistakes.append({"Page": page_display, "Mistake Type": "Talqeen", "Count": tq})
            page_mistakes.append({"Page": page_display, "Mistake Type": "Tanbeeh", "Count": tb})

    avg_marks = total_marks / total_sessions if total_sessions > 0 else 0.0
    
    # Modern KPI Dashboard using the Progress & Achievement green theme
    dashboard_html = f"""
    <div style='background: linear-gradient(135deg, #1b4d3e 0%, #0f352a 100%); padding: 25px; border-radius: 12px; color: white; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border: 1px solid #c5a880; font-family: "Outfit", "Segoe UI", sans-serif;'>
        <div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 15px;'>
            <div>
                <h3 style='margin: 0; color: #c5a880; font-size: 20px; font-weight: 600;'>📊 Recitation & Mistake Analytics Dashboard</h3>
                <p style='margin: 3px 0 0 0; font-size: 13px; opacity: 0.8;'>Aggregated metrics and visual reports for student {student_name}.</p>
            </div>
            <div style='background-color: rgba(197, 168, 128, 0.2); border: 1px solid #c5a880; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; color: #c5a880;'>
                Live Data
            </div>
        </div>
        <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 20px;'>
            <div style='background-color: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08); text-align: center;'>
                <div style='font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.7; margin-bottom: 5px;'>Total Sessions</div>
                <div style='font-size: 24px; font-weight: bold; color: #ffffff;'>{total_sessions}</div>
            </div>
            <div style='background-color: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08); text-align: center;'>
                <div style='font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.7; margin-bottom: 5px;'>Average Grade</div>
                <div style='font-size: 24px; font-weight: bold; color: #ffffff;'>{avg_marks:.2f} / 10</div>
            </div>
            <div style='background-color: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08); text-align: center;'>
                <div style='font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.7; margin-bottom: 5px;'>Total Talqeen</div>
                <div style='font-size: 24px; font-weight: bold; color: #ff6b6b;'>{total_talqeen} 🔴</div>
            </div>
            <div style='background-color: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08); text-align: center;'>
                <div style='font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.7; margin-bottom: 5px;'>Total Tanbeeh</div>
                <div style='font-size: 24px; font-weight: bold; color: #ffd257;'>{total_tanbeeh} 🟡</div>
            </div>
        </div>
    </div>
    """
    st.markdown(dashboard_html, unsafe_allow_html=True)

    # 1. Prepare Surah Mistakes Chart
    has_surah_data = False
    if surah_mistakes:
        df_surah = pd.DataFrame(surah_mistakes)
        df_surah_totals = df_surah.groupby("Surah")["Count"].sum().reset_index()
        df_surah_totals = df_surah_totals[df_surah_totals["Count"] > 0]
        if not df_surah_totals.empty:
            has_surah_data = True
            top_surahs = df_surah_totals.sort_values(by="Count", ascending=False).head(10)["Surah"].tolist()
            df_surah_plot = df_surah[df_surah["Surah"].isin(top_surahs)]
            
            surah_chart = alt.Chart(df_surah_plot).mark_bar().encode(
                y=alt.Y("Surah:N", sort=top_surahs, title="Surah", axis=alt.Axis(labelLimit=300)),
                x=alt.X("Count:Q", title="Mistakes Count"),
                color=alt.Color(
                    "Mistake Type:N",
                    scale=alt.Scale(domain=["Talqeen", "Tanbeeh"], range=["#E53E3E", "#D4AF37"]),
                    title="Mistake Type"
                ),
                tooltip=["Surah", "Mistake Type", "Count"]
            ).properties(
                title="Top 10 Surahs with Most Mistakes (Murajat)",
                height=300
            )

    # 2. Prepare Page Mistakes Chart
    has_page_data = False
    if page_mistakes:
        df_page = pd.DataFrame(page_mistakes)
        df_page_totals = df_page.groupby("Page")["Count"].sum().reset_index()
        df_page_totals = df_page_totals[df_page_totals["Count"] > 0]
        if not df_page_totals.empty:
            has_page_data = True
            top_pages = df_page_totals.sort_values(by="Count", ascending=False).head(10)["Page"].tolist()
            df_page_plot = df_page[df_page["Page"].isin(top_pages)]
            
            page_chart = alt.Chart(df_page_plot).mark_bar().encode(
                y=alt.Y("Page:N", sort=top_pages, title="Page", axis=alt.Axis(labelLimit=300)),
                x=alt.X("Count:Q", title="Mistakes Count"),
                color=alt.Color(
                    "Mistake Type:N",
                    scale=alt.Scale(domain=["Talqeen", "Tanbeeh"], range=["#E53E3E", "#D4AF37"]),
                    title="Mistake Type"
                ),
                tooltip=["Page", "Mistake Type", "Count"]
            ).properties(
                title="Top 10 Pages with Most Mistakes (Juzulhali)",
                height=300
            )

    # Render Row 1: Top Mistakes (Surah vs Page)
    col_left, col_right = st.columns(2)
    with col_left:
        if has_surah_data:
            st.altair_chart(surah_chart, width="stretch")
        else:
            st.info("No Murajat (Surah) mistakes recorded yet for this student.")
            
    with col_right:
        if has_page_data:
            st.altair_chart(page_chart, width="stretch")
        else:
            st.info("No Juzulhali (Page) mistakes recorded yet for this student.")
            
    st.divider()

    # 3. Top 5 Ahkam Mistakes Chart
    has_ahkam_data = False
    ahkam_list = [{"Category": k, "Count": v} for k, v in ahkam_counts.items() if v > 0]
    if ahkam_list:
        df_ahkam = pd.DataFrame(ahkam_list)
        top_ahkam = df_ahkam.sort_values(by="Count", ascending=False).head(5)
        if not top_ahkam.empty:
            has_ahkam_data = True
            ahkam_chart = alt.Chart(top_ahkam).mark_bar(color="#0E6B50").encode(
                y=alt.Y("Category:N", sort=top_ahkam["Category"].tolist(), title="Rule / Hukm"),
                x=alt.X("Count:Q", title="Mistake Count"),
                tooltip=["Category", "Count"]
            ).properties(
                title="Top 5 Ahkam (Rules) Mistakes",
                height=220
            )

    # 4. Top 5 Makharij Mistakes Chart
    has_makharij_data = False
    makharij_list = [{"Letter": k, "Count": v} for k, v in makharij_counts.items() if v > 0]
    if makharij_list:
        df_makharij = pd.DataFrame(makharij_list)
        top_makharij = df_makharij.sort_values(by="Count", ascending=False).head(5)
        if not top_makharij.empty:
            has_makharij_data = True
            makharij_chart = alt.Chart(top_makharij).mark_bar(color="#B88917").encode(
                y=alt.Y("Letter:N", sort=top_makharij["Letter"].tolist(), title="Makhraj (Articulation Point)"),
                x=alt.X("Count:Q", title="Mistake Count"),
                tooltip=["Letter", "Count"]
            ).properties(
                title="Top 5 Makharij (Pronunciation) Mistakes",
                height=220
            )

    # Render Row 2: Top 5 Ahkam vs Top 5 Makharij
    col_ahkam, col_makharij = st.columns(2)
    with col_ahkam:
        if has_ahkam_data:
            st.altair_chart(ahkam_chart, width="stretch")
        else:
            st.info("No Ahkam (rules) mistakes recorded yet for this student.")
            
    with col_makharij:
        if has_makharij_data:
            st.altair_chart(makharij_chart, width="stretch")
        else:
            st.info("No Makharij (articulation point) mistakes recorded yet for this student.")
            
    st.divider()
    
    # 5. Prepare Secondary Mistakes Chart with Inside labels and premium colors
    secondary_list = [{"Category": k, "Count": v} for k, v in secondary_counts.items() if v > 0]
    df_sec = pd.DataFrame(secondary_list)
    df_sec_total = df_sec["Count"].sum() if not df_sec.empty else 0
    
    has_secondary_data = df_sec_total > 0
    if has_secondary_data:
        base = alt.Chart(df_sec).encode(
            theta=alt.Theta("Count:Q", stack=True),
            color=alt.Color(
                "Category:N",
                scale=alt.Scale(
                    domain=["I'rab", "Mutashabihat", "Repeat", "Awakhir"],
                    range=["#0E6B50", "#D4AF37", "#8C7853", "#1E1A12"]
                ),
                title="Category"
            )
        )
        arcs = base.mark_arc(innerRadius=45, outerRadius=90)
        text = base.mark_text(radius=68, size=12, fontWeight="bold", fill="white").encode(
            text="Count:Q"
        )
        sec_chart = (arcs + text).properties(
            title="Secondary Mistake Category Distribution (Ratios)",
            height=300
        )

    # 6. Prepare Trend Chart
    has_trend_data = False
    if daily_data:
        has_trend_data = True
        trend_list = []
        for d_str, counts in sorted(daily_data.items()):
            trend_list.append({"Date": d_str, "Mistake Type": "Talqeen", "Count": counts["Talqeen"]})
            trend_list.append({"Date": d_str, "Mistake Type": "Tanbeeh", "Count": counts["Tanbeeh"]})
        
        df_trend = pd.DataFrame(trend_list)
        df_trend["Date"] = pd.to_datetime(df_trend["Date"])
        
        trend_chart = alt.Chart(df_trend).mark_line(point=True).encode(
            x=alt.X("Date:T", title="Date", axis=alt.Axis(format="%Y-%m-%d")),
            y=alt.Y("Count:Q", title="Mistake Count"),
            color=alt.Color(
                "Mistake Type:N",
                scale=alt.Scale(domain=["Talqeen", "Tanbeeh"], range=["#E53E3E", "#D4AF37"]),
                title="Mistake Type"
            ),
            tooltip=["Date:T", "Mistake Type", "Count"]
        ).properties(
            title="Recitation Mistakes Trend Over Time",
            height=300
        )

    # Render Row 3: Secondary Ratios vs daily Trend
    col_breakdown, col_trend = st.columns(2)
    with col_breakdown:
        if has_secondary_data:
            st.altair_chart(sec_chart, width="stretch")
        else:
            st.info("No secondary mistakes (I'rab, Mutashabihat, Repeat, Awakhir) recorded yet.")
            
    with col_trend:
        if has_trend_data:
            st.altair_chart(trend_chart, width="stretch")
        else:
            st.info("No trend data available yet.")
            
    st.divider()

    # 7. Prepare Musaid Analysis Chart
    has_musaid_data = False
    musaid_list = [{"Indicator": k, "Count": v} for k, v in musaid_counts.items() if v > 0]
    if musaid_list:
        df_musaid = pd.DataFrame(musaid_list)
        if not df_musaid.empty:
            has_musaid_data = True
            musaid_chart = alt.Chart(df_musaid).mark_bar(color="#5C3A21").encode(
                y=alt.Y("Indicator:N", sort="-x", title="Musaid Indicator"),
                x=alt.X("Count:Q", title="Sessions Check Count", axis=alt.Axis(tickMinStep=1)),
                tooltip=["Indicator", "Count"]
            ).properties(
                title="Musaid Analysis Indicators Count",
                height=220
            )

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        if has_musaid_data:
            st.altair_chart(musaid_chart, width="stretch")
        else:
            st.info("No Musaid analysis indicators recorded yet for this student.")
