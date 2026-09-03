from __future__ import annotations

import streamlit as st
import pandas as pd
import altair as alt
from typing import Optional
from datetime import datetime

from app.db import get_student_page_listening_history


def _format_date(d_str: str) -> str:
    """Formats 2026-08-06 to 2026 - August - 06 for clear readability."""
    try:
        dt = datetime.strptime(str(d_str), "%Y-%m-%d")
        return dt.strftime("%Y - %B - %d")
    except Exception:
        return str(d_str)


@st.fragment
def render_page_comparison(
    *, 
    student_id: str, 
    student_name: str, 
    page_number: int, 
    mode: str, 
    surah_name: str = ""
) -> None:
    """
    Renders an in-depth, side-by-side historical comparison and progression analysis
    for a specific page across all past listening sessions.
    """
    cache_key = f"page_history_cache_{student_id}_{page_number}"
    if cache_key not in st.session_state:
        st.session_state[cache_key] = get_student_page_listening_history(
            student_id=student_id, 
            page_number=page_number, 
            mode=None
        )
    history = st.session_state[cache_key]

    mode_label = "Murajat (مراجعة)" if mode == "murajat" else "Juzulhali (جزء الحالي)"

    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #1b4d3e 0%, #0f352a 100%); padding: 16px 20px; border-radius: 10px; color: white; margin: 15px 0; border: 1px solid #c5a880; box-shadow: 0 4px 12px rgba(0,0,0,0.04);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <h3 style="margin: 0; color: #c5a880; font-size: 1.25rem;">📈 Page {page_number} — Recitation History & Progress Analysis</h3>
                    <p style="margin: 3px 0 0 0; opacity: 0.85; font-size: 0.88rem;">Student: <b>{student_name}</b> • Active Context: <b>{mode_label}</b></p>
                </div>
                <div style="text-align: right; background: rgba(255,255,255,0.1); padding: 6px 14px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.15);">
                    <div style="font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.8;">Total Page Attempts</div>
                    <div style="font-size: 1.2rem; font-weight: bold; color: #f8fafc;">{len(history)} {"Session" if len(history) == 1 else "Sessions"}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if not history:
        st.info(f"ℹ️ No prior listening sessions recorded for **Page {page_number}**. This session will be saved as **Attempt #1**.")
        return

    # If only 1 session exists
    if len(history) == 1:
        s1 = history[0]
        st.info(
            f"📌 **First Attempt on Record** ({_format_date(s1['activity_date'])} in *{s1['mode'].capitalize()}*): Score was **{s1['score']}/10** with "
            f"**{s1['talqeen']}** Talqeen, **{s1['tanbeeh']}** Tanbeeh, **{s1['irab']}** I'rab, **{s1['awakhir']}** Awakhir, **{s1['repeat']}** Repeat, **{s1['mutashabehat']}** Mutashabihat. "
            f"Subsequent recitations of this page will automatically generate side-by-side progression graphs and improvement trends."
        )

    # 1. Executive Comparison KPI Cards (when 2+ attempts exist)
    if len(history) >= 2:
        latest = history[-1]
        prev = history[-2]
        first = history[0]
        
        score_diff = latest["score"] - prev["score"]
        mistakes_diff = latest["total_mistakes"] - prev["total_mistakes"]
        best_score = max(h["score"] for h in history)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            score_diff = latest["score"] - prev["score"]
            delta_str = f"{'+' if score_diff >= 0 else ''}{score_diff:.2f} vs Prev"
            st.metric(
                label=f"Latest Score (Attempt #{latest['attempt_number']})",
                value=f"{latest['score']:.2f} / 10",
                delta=delta_str,
                delta_color="normal"
            )

        with col2:
            mistakes_diff = latest["total_mistakes"] - prev["total_mistakes"]
            m_delta_str = f"{'+' if mistakes_diff > 0 else ''}{mistakes_diff} vs Prev"
            st.metric(
                label="Total Mistakes (Latest)",
                value=f"{latest['total_mistakes']} total",
                delta=m_delta_str,
                delta_color="inverse"
            )

        with col3:
            net_growth = latest["score"] - first["score"]
            growth_delta_str = f"{'+' if net_growth >= 0 else ''}{net_growth:.2f} vs 1st ({first['score']:.1f})"
            st.metric(
                label="Overall Page Growth",
                value=f"{'+' if net_growth > 0 else ''}{net_growth:.2f} Net",
                delta=growth_delta_str,
                delta_color="normal"
            )

        with col4:
            st.metric(
                label="Best Attempt on Page",
                value=f"{best_score:.2f} / 10",
                delta=f"Across {len(history)} attempts",
                delta_color="off"
            )

        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

        # 2. Altair Charts: Score Progression & Mistake Breakdown Evolution
        chart_col1, chart_col2 = st.columns([1, 1])

        df_history = pd.DataFrame(history)
        df_history["Attempt_Label"] = [f"#{h['attempt_number']} ({_format_date(h['activity_date'])})" for h in history]

        with chart_col1:
            st.markdown("##### 📈 Score Progression Curve")
            base_line = alt.Chart(df_history).encode(
                x=alt.X("Attempt_Label:N", title="Recitation Attempt", sort=None),
                y=alt.Y("score:Q", title="Score (out of 10)", scale=alt.Scale(domain=[0, 10.5]))
            )

            line = base_line.mark_line(color="#10b981", strokeWidth=3)
            points = base_line.mark_circle(size=85, color="#047857")
            text = base_line.mark_text(align="center", baseline="bottom", dy=-8, color="#1b4d3e", fontSize=11, fontWeight="bold").encode(
                text=alt.Text("score:Q", format=".2f")
            )

            # Target 10.0 reference line
            rule = alt.Chart(pd.DataFrame({"y": [10.0]})).mark_rule(color="#94a3b8", strokeDash=[4, 4]).encode(y="y:Q")

            score_chart = (rule + line + points + text).properties(height=260)
            st.altair_chart(score_chart, width="stretch")

        with chart_col2:
            st.markdown("##### 🔍 Mistake Breakdown Evolution")
            # Melt specific mistake types for grouped bar chart
            mistake_melt = []
            for h in history:
                label = f"#{h['attempt_number']} ({_format_date(h['activity_date'])})"
                mistake_melt.append({"Attempt": label, "Type": "Talqeen", "Count": h["talqeen"]})
                mistake_melt.append({"Attempt": label, "Type": "Tanbeeh", "Count": h["tanbeeh"]})
                mistake_melt.append({"Attempt": label, "Type": "I'rab", "Count": h["irab"]})
                mistake_melt.append({"Attempt": label, "Type": "Awakhir", "Count": h["awakhir"]})
                mistake_melt.append({"Attempt": label, "Type": "Repeat", "Count": h["repeat"]})
                mistake_melt.append({"Attempt": label, "Type": "Mutashabihat", "Count": h["mutashabehat"]})

            df_melt = pd.DataFrame(mistake_melt)
            if not df_melt.empty and df_melt["Count"].sum() > 0:
                bar_chart = alt.Chart(df_melt).mark_bar().encode(
                    x=alt.X("Type:N", title="Mistake Category", axis=alt.Axis(labelAngle=-25)),
                    y=alt.Y("Count:Q", title="Mistake Count"),
                    color=alt.Color("Attempt:N", title="Attempt", scale=alt.Scale(scheme="tableau10")),
                    xOffset="Attempt:N",
                    tooltip=["Attempt", "Type", "Count"]
                ).properties(height=260)
                st.altair_chart(bar_chart, width="stretch")
            else:
                st.success("🌟 Flawless Recitation: 0 mistakes recorded across all categories!")

    # 3. Side-by-Side Detailed Attempt Comparison Table
    st.markdown("##### 📋 Attempt-by-Attempt Comparison Matrix")
    
    table_rows = []
    for h in history:
        # Score Badge
        score_val = h["score"]
        if score_val >= 9.0:
            badge_style = "background: #dcfce7; color: #15803d; border: 1px solid #86efac;"
        elif score_val >= 7.5:
            badge_style = "background: #fef9c3; color: #854d0e; border: 1px solid #fde047;"
        else:
            badge_style = "background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5;"

        # Delta indicator
        if h["score_delta"] is not None:
            if h["score_delta"] > 0:
                delta_badge = f"<span style='color: #16a34a; font-weight: bold;'>▲ +{h['score_delta']:.2f}</span>"
            elif h["score_delta"] < 0:
                delta_badge = f"<span style='color: #dc2626; font-weight: bold;'>▼ {h['score_delta']:.2f}</span>"
            else:
                delta_badge = "<span style='color: #64748b;'>▬ 0.0</span>"
        else:
            delta_badge = "<span style='color: #94a3b8;'>— (1st Baseline)</span>"

        ahkam_str = ", ".join(h["ahkam_list"]) if h["ahkam_list"] else "—"
        makharij_str = ", ".join(h["makharij_list"]) if h["makharij_list"] else "—"
        rules_combined = []
        if ahkam_str != "—": rules_combined.append(f"Tajweed: {ahkam_str}")
        if makharij_str != "—": rules_combined.append(f"Makhraj: {makharij_str}")
        rules_display = "<br>".join(rules_combined) if rules_combined else "<span style='color: #16a34a;'>✓ Clean</span>"

        mode_badge = "<span style='background: #e0f2fe; color: #0369a1; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: 600;'>Murajat</span>" if h["mode"] == "murajat" else "<span style='background: #fef3c7; color: #92400e; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: 600;'>Juzulhali</span>"

        table_rows.append(f"""
        <tr style="border-bottom: 1px solid #e2e8f0; font-size: 12.5px;">
            <td style="padding: 10px 8px; font-weight: bold; color: #1e293b;">#{h['attempt_number']}</td>
            <td style="padding: 10px 8px; color: #334155; font-weight: 500;">{_format_date(h['activity_date'])}</td>
            <td style="padding: 10px 8px;">{mode_badge}</td>
            <td style="padding: 10px 8px; font-weight: bold;">{h['surah_name']}</td>
            <td style="padding: 10px 8px; text-align: center;">
                <span style="display: inline-block; padding: 3px 8px; border-radius: 12px; font-weight: bold; {badge_style}">
                    {score_val:.2f}/10
                </span>
            </td>
            <td style="padding: 10px 8px; text-align: center;">{delta_badge}</td>
            <td style="padding: 10px 8px; text-align: center; color: {'#dc2626' if h['talqeen'] > 0 else '#64748b'}; font-weight: {'bold' if h['talqeen'] > 0 else 'normal'};">{h['talqeen']}</td>
            <td style="padding: 10px 8px; text-align: center; color: {'#d97706' if h['tanbeeh'] > 0 else '#64748b'}; font-weight: {'bold' if h['tanbeeh'] > 0 else 'normal'};">{h['tanbeeh']}</td>
            <td style="padding: 10px 8px; text-align: center; color: {'#7c3aed' if h['irab'] > 0 else '#64748b'}; font-weight: {'bold' if h['irab'] > 0 else 'normal'};">{h['irab']}</td>
            <td style="padding: 10px 8px; text-align: center; color: {'#db2777' if h['awakhir'] > 0 else '#64748b'}; font-weight: {'bold' if h['awakhir'] > 0 else 'normal'};">{h['awakhir']}</td>
            <td style="padding: 10px 8px; text-align: center; color: {'#0284c7' if h['repeat'] > 0 else '#64748b'}; font-weight: {'bold' if h['repeat'] > 0 else 'normal'};">{h['repeat']}</td>
            <td style="padding: 10px 8px; text-align: center; color: {'#ea580c' if h['mutashabehat'] > 0 else '#64748b'}; font-weight: {'bold' if h['mutashabehat'] > 0 else 'normal'};">{h['mutashabehat']}</td>
            <td style="padding: 10px 8px; font-size: 11.5px; color: #475569;">{rules_display}</td>
        </tr>
        """)

    matrix_html = f"""
    <div style="overflow-x: auto; border: 1px solid #cbd5e1; border-radius: 8px; background: white; margin-bottom: 20px;">
        <table style="width: 100%; border-collapse: collapse; text-align: left;">
            <thead>
                <tr style="background: #f8fafc; border-bottom: 2px solid #cbd5e1; font-size: 12px; color: #475569; text-transform: uppercase; letter-spacing: 0.5px;">
                    <th style="padding: 10px 8px;">#</th>
                    <th style="padding: 10px 8px;">Date</th>
                    <th style="padding: 10px 8px;">Mode</th>
                    <th style="padding: 10px 8px;">Surah</th>
                    <th style="padding: 10px 8px; text-align: center;">Score</th>
                    <th style="padding: 10px 8px; text-align: center;">Delta vs Prev</th>
                    <th style="padding: 10px 8px; text-align: center;">🛑 Talqeen</th>
                    <th style="padding: 10px 8px; text-align: center;">⚠️ Tanbeeh</th>
                    <th style="padding: 10px 8px; text-align: center;">🔤 I'rab</th>
                    <th style="padding: 10px 8px; text-align: center;">🔚 Awakhir</th>
                    <th style="padding: 10px 8px; text-align: center;">🔁 Repeat</th>
                    <th style="padding: 10px 8px; text-align: center;">🔗 Mutashabihat</th>
                    <th style="padding: 10px 8px;">Tajweed / Letters</th>
                </tr>
            </thead>
            <tbody>
                {"".join(table_rows)}
            </tbody>
        </table>
    </div>
    """
    st.markdown(matrix_html.replace("\n", " "), unsafe_allow_html=True)

    # 4. Diagnostic & Teacher Focus Insight Box
    if len(history) >= 2:
        latest = history[-1]
        prev = history[-2]

        resolved_issues = []
        recurring_issues = []
        improved_issues = []

        for category, cat_name in [
            ("irab", "I'rab (Harakat/Vowels)"),
            ("awakhir", "Awakhir al-Ayat (Endings/Waqf)"),
            ("repeat", "Repetitions / Stutters"),
            ("mutashabehat", "Mutashabihat Confusions"),
            ("talqeen", "Talqeen Stops"),
            ("tanbeeh", "Tanbeeh Pauses")
        ]:
            l_val = latest[category]
            p_val = prev[category]

            if p_val > 0 and l_val == 0:
                resolved_issues.append(f"<b>{cat_name}</b> (completely fixed: 0 now vs {p_val} last time)")
            elif p_val > l_val > 0:
                improved_issues.append(f"<b>{cat_name}</b> (reduced from {p_val} down to {l_val})")
            elif l_val > 0 and p_val > 0:
                recurring_issues.append(f"<b>{cat_name}</b> ({l_val} mistakes repeated in both sessions)")
            elif l_val > p_val and l_val > 0:
                recurring_issues.append(f"<b>{cat_name}</b> (increased to {l_val})")

        insight_blocks = []
        if resolved_issues:
            insight_blocks.append(f"<div style='margin-bottom: 6px;'><span style='color: #16a34a; font-weight: bold;'>✅ Mastered / Fixed:</span> {', '.join(resolved_issues)}</div>")
        if improved_issues:
            insight_blocks.append(f"<div style='margin-bottom: 6px;'><span style='color: #0284c7; font-weight: bold;'>📈 Improved:</span> {', '.join(improved_issues)}</div>")
        if recurring_issues:
            insight_blocks.append(f"<div style='margin-bottom: 6px;'><span style='color: #ea580c; font-weight: bold;'>⚠️ Target Focus for Next Session:</span> {', '.join(recurring_issues)}</div>")

        if not insight_blocks:
            insight_blocks.append("<div>🌟 Performance has remained consistent and stable across sessions.</div>")

        st.markdown(
            f"""
            <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-left: 4px solid #10b981; border-radius: 6px; padding: 14px 18px; margin-top: 10px; font-size: 13px; line-height: 1.5;">
                <div style="font-weight: bold; color: #1e293b; margin-bottom: 8px; font-size: 13.5px;">💡 Teacher Diagnostic & Progression Summary</div>
                {"".join(insight_blocks)}
            </div>
            """,
            unsafe_allow_html=True
        )
