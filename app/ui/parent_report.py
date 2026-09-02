import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, date
from typing import Dict, Any, List, Optional
from app.db import (
    get_rest,
    today_iso,
    list_surahs,
    get_student_monthly_actuals,
    log_parent_view,
    SURAH_AYAH_COUNTS
)
from app.ui.planner import get_locked_monthly_plan, get_surah_page_length


def get_comparison_status(plan_row, actual_entries, no_jadeed, name_to_num):
    """
    Evaluates whether the student was On Track, Ahead, Behind, Missed, or Rest Day.
    """
    # If not included in the plan
    if plan_row is None or not plan_row.get("Include?"):
        if actual_entries:
            return "Ahead", "⭐ Extra Recitation"
        else:
            return "Rest Day", "😴 Rest Day"

    # If included in plan but no actual recitations
    if not actual_entries:
        if no_jadeed:
            return "Rest Day", "🌙 Excused / No Jadeed"
        else:
            return "Missed", "❌ Missed Lesson"

    # Compare first actual entry with planned lesson
    act = actual_entries[0]
    act_surah_info = act.get("surahs") or {}
    if isinstance(act_surah_info, list):
        act_surah_info = act_surah_info[0] if act_surah_info else {}
        
    act_surah_name = act_surah_info.get("name_en", "")
    act_surah_num = int(act_surah_info.get("number") or act.get("surah_id") or 1)
    act_ayah = int(act.get("ayah_number") or 1)
    act_vol = act.get("volume", "Kamil")

    plan_surah_name = plan_row.get("Surah", "")
    plan_surah_num = name_to_num.get(plan_surah_name, 1)
    plan_from_ayah = int(plan_row.get("From Ayah") or 1)
    plan_to_ayah = int(plan_row.get("To Ayah") or 1)
    plan_vol = plan_row.get("Volume", "Kamil")

    # Volume mappings to normalize
    vol_map = {
        "kamil": 1.0, "full": 1.0,
        "sulus": 0.8,
        "nisf": 0.5, "half": 0.5,
        "ruba": 0.25
    }
    act_vol_val = vol_map.get(act_vol.lower(), 0.5)
    plan_vol_val = vol_map.get(plan_vol.lower(), 0.5)

    # Estimate actual end ayah based on volume
    try:
        act_page_len = get_surah_page_length(surah_num=act_surah_num)
        act_avg_ayahs_per_page = SURAH_AYAH_COUNTS.get(act_surah_num, 7) / max(act_page_len, 1.0)
        act_ayahs_completed = max(1, round(act_vol_val * act_avg_ayahs_per_page))
    except Exception:
        act_ayahs_completed = 5 # fallback

    act_end_ayah = act_ayah + act_ayahs_completed - 1
    max_act_ayahs = SURAH_AYAH_COUNTS.get(act_surah_num, 7)
    if act_end_ayah > max_act_ayahs:
        act_end_ayah = max_act_ayahs

    # Smaller Surah number is ahead (since we recite from 114 down to 1)
    is_ahead = False
    is_behind = False
    is_on_track = False

    if act_surah_num < plan_surah_num:
        is_ahead = True
    elif act_surah_num > plan_surah_num:
        is_behind = True
    else:
        # Same Surah
        if act_end_ayah >= plan_to_ayah:
            is_on_track = True
        else:
            is_behind = True

    if is_ahead:
        return "Ahead", "🎉 Ahead of Plan"
    elif is_on_track:
        return "On Track", "✅ On Track"
    else:
        # Calculate gap (ayahs and pages)
        # Reverse cumulative map
        reverse_surahs = list(range(114, 0, -1))
        cumulative_ayahs = {}
        total = 0
        for s in reverse_surahs:
            cumulative_ayahs[s] = total
            total += SURAH_AYAH_COUNTS.get(s, 7)

        pos_plan = cumulative_ayahs.get(plan_surah_num, 0) + plan_to_ayah
        pos_act = cumulative_ayahs.get(act_surah_num, 0) + act_end_ayah

        gap_ayahs = pos_plan - pos_act
        if gap_ayahs > 0:
            try:
                plan_page_len = get_surah_page_length(surah_num=plan_surah_num)
                plan_avg_ayahs_per_page = SURAH_AYAH_COUNTS.get(plan_surah_num, 7) / max(plan_page_len, 1.0)
                gap_pages = gap_ayahs / max(plan_avg_ayahs_per_page, 1.0)
            except Exception:
                gap_pages = gap_ayahs / 15.0

            if gap_pages < 0.1:
                return "Behind", f"⚠️ Behind Plan (by {gap_ayahs} ayahs)"
            else:
                return "Behind", f"⚠️ Behind Plan (by {gap_pages:.1f} pages / {gap_ayahs} ayahs)"
        else:
            return "Behind", "⚠️ Behind Plan"


def render_parent_report() -> None:
    student_id = st.session_state.get("student_id")
    student_name = st.session_state.get("student_name", "Student")

    if not student_id:
        st.warning("Please log in again.")
        return

    # Always fetch for current day (today)
    now = datetime.now()
    selected_year = now.year
    selected_month_num = now.month
    date_str = now.strftime("%Y-%m-%d")
    formatted_date = now.strftime("%B %d, %Y")
    day_name = now.strftime("%a")

    st.markdown(
        f"""
        <div style='background: linear-gradient(135deg, #1b4d3e 0%, #0f352a 100%); padding: 20px; border-radius: 12px; color: white; margin-bottom: 20px; border: 1px solid #c5a880;'>
            <h2 style='margin: 0; font-size: 1.6rem; color: #c5a880;'>👪 Parent Progress Portal</h2>
            <p style='margin: 5px 0 0 0; opacity: 0.8; font-size: 0.95rem;'>Viewing progress comparison report for: <b>{student_name}</b></p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Log view for today in a background thread to prevent UI block, cached per session
    cache_key = f"parent_logged_today_{student_id}_{date_str}"
    if not st.session_state.get(cache_key):
        import threading
        t = threading.Thread(target=log_parent_view, kwargs={"student_id": student_id, "date_str": date_str})
        t.daemon = True
        t.start()
        st.session_state[cache_key] = True

    # Fetch data
    locked_df = get_locked_monthly_plan(student_id=student_id, year=selected_year, month=selected_month_num)
    
    # Query today's actuals and daily status in parallel
    from app.db import get_rest
    rest = get_rest()
    actuals = []
    no_jadeed = False
    if rest is not None:
        import concurrent.futures
        
        def fetch_actuals():
            try:
                return rest.select(
                    "jadeed_entries",
                    select="activity_date,surah_id,page_number,ayah_number,volume,surahs(number,name_en,name_ar)",
                    params={
                        "student_id": f"eq.{student_id}",
                        "activity_date": f"eq.{date_str}",
                        "order": "created_at.asc"
                    }
                )
            except Exception:
                return []

        def fetch_daily_row():
            try:
                return rest.select_single(
                    "jadeed_daily",
                    select="no_jadeed",
                    params={"student_id": f"eq.{student_id}", "activity_date": f"eq.{date_str}"}
                )
            except Exception:
                return None

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_actuals = executor.submit(fetch_actuals)
            future_daily_row = executor.submit(fetch_daily_row)
            
            actuals = future_actuals.result()
            daily_row = future_daily_row.result()
            if daily_row:
                no_jadeed = bool(daily_row.get("no_jadeed"))

    surahs = list_surahs()
    name_to_num = {s["name_en"]: int(s["number"]) for s in surahs}

    has_plan = locked_df is not None and not locked_df.empty

    if has_plan:
        # Find today's plan row
        today_plan = None
        for _, r in locked_df.iterrows():
            if r["Date"] == date_str:
                today_plan = r
                break

        if today_plan is None:
            today_plan = {
                "Date": date_str,
                "Day": day_name,
                "Include?": False,
                "Surah": "",
                "From Ayah": 0,
                "To Ayah": 0,
                "Volume": ""
            }

        # Evaluate comparison for today
        status_key, status_label = get_comparison_status(today_plan, actuals, no_jadeed, name_to_num)

        # Color-coded badge styling
        badge_color = "var(--border)"
        badge_text_color = "var(--ink)"
        if status_key == "On Track":
            badge_color = "rgba(16, 185, 129, 0.15)"
            badge_text_color = "var(--emerald)"
        elif status_key == "Ahead":
            badge_color = "rgba(30, 58, 138, 0.15)"
            badge_text_color = "#3b82f6"
        elif status_key == "Behind":
            badge_color = "rgba(217, 119, 6, 0.15)"
            badge_text_color = "#d97706"
        elif status_key == "Missed":
            badge_color = "rgba(153, 27, 27, 0.15)"
            badge_text_color = "#ef4444"

        # Format plan text
        if today_plan.get("Include?"):
            plan_text = f"📖 <b>{today_plan.get('Surah')}</b>: {today_plan.get('From Ayah')} – {today_plan.get('To Ayah')} ({today_plan.get('Volume')})"
        else:
            plan_text = "😴 No lesson planned (Rest Day / Weekend)"

        # Format actual text
        if actuals:
            act_texts = []
            for act in actuals:
                s_info = act.get("surahs") or {}
                if isinstance(s_info, list): s_info = s_info[0] if s_info else {}
                act_texts.append(f"✅ <b>{s_info.get('name_en', 'Unknown')}</b> (Ayah {act.get('ayah_number')} – {act.get('volume')})")
            actual_text = "<br>".join(act_texts)
        elif no_jadeed:
            actual_text = "🌙 Marked: No Jadeed lesson today"
        else:
            actual_text = "❌ No recitation recorded"

        # Show single beautiful today's card
        st.markdown("### 🗓️ Today's Progress vs. Plan")
        st.caption("Here is how your child's recitation today compares to their daily target:")

        html_str = f"""
        <div style='background-color: rgba(16, 185, 129, 0.03); border: 2px solid var(--emerald); padding: 25px; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.02);'>
            <div style='display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 12px; margin-bottom: 15px;'>
                <div>
                    <span style='font-weight: bold; font-size: 1.25rem; color: var(--ink);'>🗓️ {formatted_date}</span>
                    <span style='font-size: 1.05rem; opacity: 0.7; margin-left: 5px;'>({day_name})</span>
                </div>
                <span style='background-color: {badge_color}; color: {badge_text_color}; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: bold;'>
                    {status_label}
                </span>
            </div>
            <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 10px;'>
                <div style='background-color: var(--card); border: 1px solid var(--border); padding: 15px; border-radius: 8px;'>
                    <div style='font-size: 0.8rem; text-transform: uppercase; opacity: 0.6; margin-bottom: 6px; font-weight: bold;'>🎯 Planned Target</div>
                    <div style='font-size: 1rem; color: var(--ink);'>{plan_text}</div>
                </div>
                <div style='background-color: var(--card); border: 1px solid var(--border); padding: 15px; border-radius: 8px;'>
                    <div style='font-size: 0.8rem; text-transform: uppercase; opacity: 0.6; margin-bottom: 6px; font-weight: bold;'>✨ Actual Progress</div>
                    <div style='font-size: 1rem; color: var(--ink);'>{actual_text}</div>
                </div>
            </div>
        </div>
        """
        st.markdown(html_str.replace("\n", " "), unsafe_allow_html=True)
        st.divider()
    else:
        st.info("ℹ️ No monthly lesson plan has been set/locked by the teacher for this month yet. Your child's recitation & mistake analytics are available below.")

    # Render Mistake Analytics inside an expander (expanded by default if no plan exists)
    with st.expander("📊 View Recitation & Mistake Analytics", expanded=not has_plan):
        st.markdown("### 📊 Recitation & Mistake Analytics")
        st.caption("Visual analysis of mistake categories, pronunciation articulation points, rules, and daily trend.")
        from app.ui.analytics import render_student_analytics
        render_student_analytics(student_id=student_id, student_name=student_name, skip_kpi_dashboard=True)
