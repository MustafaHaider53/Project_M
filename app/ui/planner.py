from __future__ import annotations

import streamlit as st
import pandas as pd
import calendar
import threading
import textwrap
from datetime import datetime, date
from typing import Any, Dict, List, Tuple, Optional

from app.db import (
    list_surahs,
    get_student_current_jadeed,
    calculate_student_average_pace,
    get_student_position_before_month,
    get_student_monthly_actuals,
    get_student_email,
    SURAH_AYAH_COUNTS
)
from app.ui.shared import back_home_button
from app.ui.student import current_student_badge
from app.email_utils import send_takhteet_plan_email

# Pre-computed list of month names
MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

SURAH_START_PAGES = {
    1: 1, 2: 2, 3: 50, 4: 77, 5: 106, 6: 128, 7: 151, 8: 177, 9: 187, 10: 208,
    11: 221, 12: 235, 13: 249, 14: 255, 15: 262, 16: 267, 17: 282, 18: 293, 19: 305, 20: 312,
    21: 322, 22: 332, 23: 342, 24: 350, 25: 359, 26: 367, 27: 377, 28: 385, 29: 396, 30: 404,
    31: 411, 32: 415, 33: 418, 34: 428, 35: 434, 36: 440, 37: 446, 38: 453, 39: 458, 40: 467,
    41: 477, 42: 483, 43: 489, 44: 496, 45: 499, 46: 502, 47: 507, 48: 511, 49: 515, 50: 518,
    51: 520, 52: 523, 53: 526, 54: 528, 55: 531, 56: 534, 57: 537, 58: 542, 59: 545, 60: 549,
    61: 551, 62: 553, 63: 554, 64: 556, 65: 558, 66: 560, 67: 562, 68: 564, 69: 566, 70: 568,
    71: 570, 72: 572, 73: 574, 74: 575, 75: 577, 76: 578, 77: 580, 78: 582, 79: 583, 80: 585,
    81: 586, 82: 587, 83: 587, 84: 589, 85: 590, 86: 591, 87: 591, 88: 592, 89: 593, 90: 594,
    91: 595, 92: 595, 93: 596, 94: 596, 95: 597, 96: 597, 97: 598, 98: 598, 99: 599, 100: 599,
    101: 600, 102: 600, 103: 601, 104: 601, 105: 601, 106: 602, 107: 602, 108: 602, 109: 603, 110: 603,
    111: 603, 112: 604, 113: 604, 114: 604
}


def get_surah_page_length(surah_num: int) -> float:
    start_page = SURAH_START_PAGES.get(surah_num, 1)
    if surah_num == 114:
        end_page = 605
    else:
        end_page = SURAH_START_PAGES.get(surah_num + 1, start_page + 1)
    
    raw_length = end_page - start_page
    if raw_length == 0:
        sharing = sum(1 for p in SURAH_START_PAGES.values() if p == start_page)
        return 1.0 / max(sharing, 1)
    return float(raw_length)


@st.cache_data(show_spinner=False)
def get_locked_monthly_plan(*, student_id: str, year: int, month: int) -> Optional[pd.DataFrame]:
    from app.db import get_rest
    rest = get_rest()
    if rest is None:
        return None
    special_date = f"30{year % 100:02d}-{month:02d}-01"
    try:
        row = rest.select_single(
            "takhteet_daily",
            select="murajat_text_raw",
            params={"student_id": f"eq.{student_id}", "activity_date": f"eq.{special_date}"}
        )
        if row and row.get("murajat_text_raw"):
            import json
            data = json.loads(row["murajat_text_raw"])
            return pd.DataFrame(data)
    except Exception as e:
        print(f"[get_locked_monthly_plan error] {e}")
    return None


def save_locked_monthly_plan(*, student_id: str, year: int, month: int, plan_df: pd.DataFrame) -> bool:
    from app.db import get_rest, now_utc_iso
    rest = get_rest()
    if rest is None:
        return False
    special_date = f"30{year % 100:02d}-{month:02d}-01"
    plan_json = plan_df.to_json(orient="records")
    row = {
        "student_id": student_id,
        "activity_date": special_date,
        "murajat_text_raw": plan_json,
        "juzulhali_text_raw": "LOCKED_PLAN",
        "jadeed_text_raw": "",
        "murajat_text_clean": "",
        "juzulhali_text_clean": "",
        "jadeed_text_clean": "",
        "updated_at": now_utc_iso()
    }
    try:
        rest.upsert("takhteet_daily", [row], on_conflict="student_id,activity_date", returning="minimal")
        return True
    except Exception as e:
        print(f"[save_locked_monthly_plan error] {e}")
        return False


def delete_locked_monthly_plan(*, student_id: str, year: int, month: int) -> bool:
    from app.db import get_rest
    rest = get_rest()
    if rest is None:
        return False
    special_date = f"30{year % 100:02d}-{month:02d}-01"
    try:
        rest.delete("takhteet_daily", match={"student_id": student_id, "activity_date": special_date})
        return True
    except Exception as e:
        print(f"[delete_locked_monthly_plan error] {e}")
        return False


def render_planner() -> None:
    back_home_button()
    st.subheader("Takhteet Planner")
    st.caption("Auto-schedule monthly Jadeed lesson goals, manually customize days, and track live achievements.")
    current_student_badge()

    student_id = st.session_state.get("student_id")
    student_name = st.session_state.get("student_name", "Student")
    if not student_id:
        st.warning("Please select a student on Home first.")
        return

    # 1. Load Surah references
    surahs = list_surahs()
    if not surahs:
        st.info("No Surahs loaded in the database.")
        return

    # Maps for lookup
    surah_names = [s["name_en"] for s in surahs]
    num_to_name = {int(s["number"]): s["name_en"] for s in surahs}
    name_to_num = {s["name_en"]: int(s["number"]) for s in surahs}
    id_to_name = {int(s["id"]): s["name_en"] for s in surahs}
    
    # Fetch starting position (default to the absolute latest recited lesson in the database, cached in session state)
    start_pos_key = f"planner_start_pos::{student_id}"
    if start_pos_key not in st.session_state:
        from app.db import get_rest
        start_pos = None
        rest = get_rest()
        if rest is not None:
            try:
                rows = rest.select(
                    "jadeed_entries",
                    select="surah_id,page_number,ayah_number,volume",
                    params={
                        "student_id": f"eq.{student_id}",
                        "order": "activity_date.desc,created_at.desc",
                        "limit": "1",
                    },
                )
                if rows:
                    start_pos = rows[0]
            except Exception:
                pass
        st.session_state[start_pos_key] = start_pos
    else:
        start_pos = st.session_state[start_pos_key]

    # Initial start position variables
    if start_pos and "surah_id" in start_pos:
        default_surah_name = id_to_name.get(int(start_pos["surah_id"]), surah_names[0])
        default_ayah = int(start_pos.get("ayah_number") or 1)
    else:
        default_surah_name = surah_names[0]
        default_ayah = 1

    # Get average pace (cached in session state)
    avg_pace_key = f"planner_avg_pace::{student_id}"
    if avg_pace_key not in st.session_state:
        avg_pace = calculate_student_average_pace(student_id=student_id)
        st.session_state[avg_pace_key] = avg_pace
    else:
        avg_pace = st.session_state[avg_pace_key]

    # 2. Main Layout Placement
    dashboard_placeholder = st.container()
    
    st.markdown("---")
    
    # Split the main content: Left Column (13/19 width) for Grid/Preview, Right Column (6/19 width) for Settings
    col_left_layout, col_right_layout = st.columns([13, 6])

    # 3. Settings in the Right Column
    with col_right_layout:
        st.markdown("### ⚙️ Planner Settings")
        
        now = datetime.now()
        years = list(range(2025, now.year + 2))
        selected_year = st.selectbox("Plan Year", options=years, index=years.index(now.year))
        
        selected_month_name = st.selectbox("Plan Month", options=MONTHS, index=now.month - 1)
        selected_month_num = MONTHS.index(selected_month_name) + 1
        
        # Check if plan is locked in the database
        init_key = f"planner_init::{student_id}::{selected_year}::{selected_month_num}"
        if st.session_state.get("planner_init_key") != init_key:
            st.session_state.planner_init_key = init_key
            st.session_state.planner_data = None
            st.session_state.planner_is_locked = False

        if st.session_state.planner_data is None:
            locked_df = get_locked_monthly_plan(student_id=student_id, year=selected_year, month=selected_month_num)
            if locked_df is not None:
                st.session_state.planner_data = locked_df
                st.session_state.planner_is_locked = True
            else:
                st.session_state.planner_is_locked = False

        is_locked = bool(st.session_state.get("planner_is_locked", False))

        # Fetch starting position
        if is_locked and st.session_state.planner_data is not None:
            df_locked = st.session_state.planner_data
            active_rows = df_locked[df_locked["Include?"] == True]
            if not active_rows.empty:
                first_active = active_rows.iloc[0]
                locked_start_surah = first_active["Surah"]
                locked_start_ayah = max(1, int(first_active["From Ayah"] or 1) - 1)
            else:
                locked_start_surah = default_surah_name
                locked_start_ayah = default_ayah
        else:
            locked_start_surah = default_surah_name
            locked_start_ayah = default_ayah

        pace_basis = st.selectbox("Pace Basis", options=["Volume / Lines", "Ayahs"], index=0, disabled=is_locked)
        
        # Pace variable placeholders
        lines_per_day = 8
        pace_ayahs = 5
        selected_volume = "Nisf (8 lines / 0.5 Page)"
        
        if pace_basis == "Volume / Lines":
            volume_opts = {
                "Kamil (15 lines / 1 Page)": 15,
                "Sulus (12 lines)": 12,
                "Nisf (8 lines / 0.5 Page)": 8,
                "Ruba (4 lines / 0.25 Page)": 4,
                "Custom Lines": -1
            }
            selected_volume = st.selectbox("Target Volume", options=list(volume_opts.keys()), index=2, disabled=is_locked)
            if selected_volume == "Custom Lines":
                lines_per_day = st.number_input("Lines/Day", min_value=1, max_value=150, value=8, step=1, disabled=is_locked)
            else:
                lines_per_day = volume_opts[selected_volume]
        else:
            pace_ayahs = st.number_input("Target Pace (Ayahs/Day)", min_value=1, max_value=100, value=max(1, int(round(avg_pace))), step=1, disabled=is_locked)
            
        st.markdown("---")
        st.markdown("##### 📍 Starting Position")
        start_surah = st.selectbox("Start Surah", options=surah_names, index=surah_names.index(locked_start_surah) if locked_start_surah in surah_names else 0, disabled=is_locked)
        start_ayah = st.number_input("Start Ayah", min_value=1, max_value=286, value=locked_start_ayah, step=1, disabled=is_locked)
        st.caption(f"Historical Avg Pace: **{avg_pace:.1f} ayahs/day**")

    # 4. Generate Calendar logic (Computation only)
    if not is_locked:
        init_key = f"planner_init::{student_id}::{selected_year}::{selected_month_num}"
        if st.session_state.get("planner_init_key") != init_key:
            st.session_state.planner_init_key = init_key
            st.session_state.planner_data = None
            st.session_state.planner_edited_indices = set()

        if "planner_edited_indices" not in st.session_state:
            st.session_state.planner_edited_indices = set()

        if st.session_state.planner_data is None:
            _, num_days = calendar.monthrange(selected_year, selected_month_num)
            
            plan_rows = []
            for d in range(1, num_days + 1):
                curr_date = date(selected_year, selected_month_num, d)
                date_str = curr_date.isoformat()
                day_name = curr_date.strftime("%a")
                is_sunday = (curr_date.weekday() == 6)

                plan_rows.append({
                    "Date": date_str,
                    "Day": day_name,
                    "Include?": not is_sunday,
                    "Surah": "",
                    "From Ayah": 0,
                    "To Ayah": 0,
                    "Volume": ""
                })
            st.session_state.planner_data = pd.DataFrame(plan_rows)

        # Apply any pending edits from the data_editor widget state directly to planner_data
        if "planner_editor" in st.session_state:
            editor_state = st.session_state["planner_editor"]
            edited_rows = editor_state.get("edited_rows", {})
            if edited_rows:
                for idx_str, changes in edited_rows.items():
                    idx = int(idx_str)
                    if any(col in changes for col in ["Surah", "From Ayah", "To Ayah", "Volume"]):
                        st.session_state.planner_edited_indices.add(idx)
                    if "Include?" in changes and not changes["Include?"]:
                        st.session_state.planner_edited_indices.discard(idx)
                    for col, val in changes.items():
                        st.session_state.planner_data.at[idx, col] = val

        # Recalculate the lessons sequence dynamically on every run (using the current Include? state)
        df = st.session_state.planner_data.copy()
        
        current_surah_num = name_to_num.get(start_surah, 1)
        current_ayah = start_ayah

        recalculated_rows = []
        for idx, r in df.iterrows():
            is_included = bool(r["Include?"])
            if not is_included:
                recalculated_rows.append({
                    "Date": r["Date"],
                    "Day": r["Day"],
                    "Include?": False,
                    "Surah": "",
                    "From Ayah": 0,
                    "To Ayah": 0,
                    "Volume": ""
                })
            else:
                if idx in st.session_state.planner_edited_indices:
                    # User's manual values for this row
                    surah_name = r["Surah"]
                    from_ayah = int(r["From Ayah"] or 1)
                    to_ayah = int(r["To Ayah"] or 1)
                    volume_str = r["Volume"]
                    
                    # Update running position based on manual values
                    current_surah_num = name_to_num.get(surah_name, current_surah_num)
                    current_ayah = to_ayah
                    
                    recalculated_rows.append({
                        "Date": r["Date"],
                        "Day": r["Day"],
                        "Include?": True,
                        "Surah": surah_name,
                        "From Ayah": from_ayah,
                        "To Ayah": to_ayah,
                        "Volume": volume_str
                    })
                else:
                    # Calculate From Ayah
                    from_ayah = current_ayah + 1
                    total_ayahs = SURAH_AYAH_COUNTS.get(current_surah_num, 7)

                    if from_ayah > total_ayahs:
                        current_surah_num = max(current_surah_num - 1, 1)
                        from_ayah = 1
                        total_ayahs = SURAH_AYAH_COUNTS.get(current_surah_num, 7)

                    # Determine daily pace dynamically
                    if pace_basis == "Volume / Lines":
                        page_length = get_surah_page_length(current_surah_num)
                        average_ayahs_per_page = total_ayahs / page_length
                        pace_in_pages = lines_per_day / 15.0
                        daily_pace = max(1, round(pace_in_pages * average_ayahs_per_page))

                        if lines_per_day == 15:
                            volume_str = "Kamil"
                        elif lines_per_day == 12:
                            volume_str = "Sulus"
                        elif lines_per_day == 8:
                            volume_str = "Nisf"
                        elif lines_per_day == 4:
                            volume_str = "Ruba"
                        else:
                            volume_str = f"{lines_per_day} Lines"
                    else:
                        daily_pace = pace_ayahs
                        volume_str = "Kamil"

                    to_ayah = from_ayah + daily_pace - 1
                    if to_ayah > total_ayahs:
                        to_ayah = total_ayahs

                    recalculated_rows.append({
                        "Date": r["Date"],
                        "Day": r["Day"],
                        "Include?": True,
                        "Surah": num_to_name.get(current_surah_num, surah_names[0]),
                        "From Ayah": from_ayah,
                        "To Ayah": to_ayah,
                        "Volume": volume_str
                    })
                    # Update running position
                    current_ayah = to_ayah

        st.session_state.planner_data = pd.DataFrame(recalculated_rows)

    # 5. Interactive Grid inside Left Column
    with col_left_layout:
        st.markdown("### 📅 Monthly Calendar Planner")
        if is_locked:
            st.success("🔒 **This Study Plan is Locked.** Recitation progress is tracked against this locked schedule.")
        else:
            st.caption("You can edit any cell directly (e.g. modify Ayahs, choose Surahs) or uncheck 'Include?' to delete/skip that day.")
        
        df = st.session_state.planner_data

        if is_locked:
            st.data_editor(
                df,
                num_rows="fixed",
                width="stretch",
                column_config={
                    "Date": st.column_config.TextColumn("Date", disabled=True),
                    "Day": st.column_config.TextColumn("Day", disabled=True),
                    "Include?": st.column_config.CheckboxColumn("Include?", disabled=True),
                    "Surah": st.column_config.SelectboxColumn("Surah", disabled=True),
                    "From Ayah": st.column_config.NumberColumn("From Ayah", disabled=True),
                    "To Ayah": st.column_config.NumberColumn("To Ayah", disabled=True),
                    "Volume": st.column_config.SelectboxColumn("Volume", disabled=True),
                },
                disabled=True,
                key="planner_editor_locked"
            )
        else:
            st.data_editor(
                df,
                num_rows="fixed",
                width="stretch",
                column_config={
                    "Date": st.column_config.TextColumn("Date", disabled=True),
                    "Day": st.column_config.TextColumn("Day", disabled=True),
                    "Include?": st.column_config.CheckboxColumn("Include?", default=True),
                    "Surah": st.column_config.SelectboxColumn("Surah", options=surah_names),
                    "From Ayah": st.column_config.NumberColumn("From Ayah", min_value=0, step=1),
                    "To Ayah": st.column_config.NumberColumn("To Ayah", min_value=0, step=1),
                    "Volume": st.column_config.SelectboxColumn("Volume", options=["Ruba", "Nisf", "Sulus", "Kamil"]),
                },
                key="planner_editor"
            )

    # 6. Live Calculations & Comparisons (Computation only)
    actuals_key = f"planner_actuals::{init_key}"
    if actuals_key not in st.session_state:
        with st.spinner("Fetching monthly recitation logs..."):
            actuals = get_student_monthly_actuals(student_id=student_id, year=selected_year, month=selected_month_num)
        st.session_state[actuals_key] = actuals
    else:
        actuals = st.session_state[actuals_key]

    # Planned stats
    planned_rows = df[df["Include?"] == True]
    planned_days = len(planned_rows)
    planned_ayahs = 0
    for idx, r in planned_rows.iterrows():
        f = int(r["From Ayah"] or 0)
        t = int(r["To Ayah"] or 0)
        if t >= f and f > 0:
            planned_ayahs += (t - f + 1)

    if not planned_rows.empty:
        last_row = planned_rows.iloc[-1]
        planned_end = f"{last_row['Surah']}: {last_row['To Ayah']}"
    else:
        planned_end = "N/A"

    # Actual stats
    actual_days = len(actuals)
    actual_ayahs = 0

    if actuals:
        actuals_sorted = sorted(actuals, key=lambda x: (x.get("activity_date") or "", x.get("created_at") or ""))
        
        start_surah_num = name_to_num.get(start_surah, 1)
        start_ayah_num = start_ayah
        
        last_actual = actuals_sorted[-1]
        last_actual_surah = last_actual.get("surahs") or {}
        if isinstance(last_actual_surah, list): last_actual_surah = last_actual_surah[0] if last_actual_surah else {}
        end_surah_num = int(last_actual_surah.get("number") or last_actual.get("surah_id") or 1)
        end_ayah_num = int(last_actual.get("ayah_number") or 1)
        
        actual_end_name = last_actual_surah.get("name_en") or num_to_name.get(end_surah_num, "Surah")
        actual_end = f"{actual_end_name}: {end_ayah_num}"

        if end_surah_num == start_surah_num:
            actual_ayahs = max(0, end_ayah_num - start_ayah_num)
        elif end_surah_num < start_surah_num:
            actual_ayahs = SURAH_AYAH_COUNTS.get(start_surah_num, 7) - start_ayah_num
            for s in range(end_surah_num + 1, start_surah_num):
                actual_ayahs += SURAH_AYAH_COUNTS.get(s, 0)
            actual_ayahs += end_ayah_num
        else:
            actual_ayahs = end_ayah_num
    else:
        actual_end = "No recitation"
        actual_ayahs = 0

    completion_rate = (actual_ayahs / planned_ayahs * 100) if planned_ayahs > 0 else 0.0

    # 7. Render Progress Dashboard into top placeholder (already initialized, full width)
    with dashboard_placeholder:
        dashboard_html = (
            "<div style='background: linear-gradient(135deg, #1b4d3e 0%, #0f352a 100%); padding: 25px; border-radius: 12px; color: white; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border: 1px solid #c5a880;'>"
            "<div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 15px;'>"
            "<div>"
            "<h3 style='margin: 0; color: #c5a880; font-size: 20px; font-weight: 600; font-family: \"Outfit\", \"Segoe UI\", sans-serif;'>📊 Progress & Achievement Dashboard</h3>"
            f"<p style='margin: 3px 0 0 0; font-size: 13px; opacity: 0.8; font-family: \"Outfit\", \"Segoe UI\", sans-serif;'>Comparing planned lessons against student's actual Supabase records for this month.</p>"
            "</div>"
            "<div style='background-color: rgba(197, 168, 128, 0.2); border: 1px solid #c5a880; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; color: #c5a880;'>"
            "Live Sync"
            "</div>"
            "</div>"
            "<div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 20px;'>"
            "<div style='background-color: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08); text-align: center;'>"
            "<div style='font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.7; margin-bottom: 5px;'>Total Days Recited</div>"
            f"<div style='font-size: 22px; font-weight: bold; color: #ffffff;'>{actual_days} / {planned_days} Days</div>"
            "</div>"
            "<div style='background-color: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08); text-align: center;'>"
            "<div style='font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.7; margin-bottom: 5px;'>Total Ayahs Completed</div>"
            f"<div style='font-size: 22px; font-weight: bold; color: #ffffff;'>{actual_ayahs} / {planned_ayahs} Ayahs</div>"
            "</div>"
            "<div style='background-color: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08); text-align: center;'>"
            "<div style='font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.7; margin-bottom: 5px;'>Completion Rate</div>"
            f"<div style='font-size: 22px; font-weight: bold; color: #c5a880;'>{completion_rate:.1f}%</div>"
            "</div>"
            "</div>"
            "<div style='background-color: rgba(255,255,255,0.03); padding: 12px 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between; font-size: 13px;'>"
            "<div>"
            "<span style='opacity: 0.7;'>Planned Ending Position:</span>"
            f"<strong style='color: #c5a880; margin-left: 5px;'>{planned_end}</strong>"
            "</div>"
            "<div style='border-left: 1px solid rgba(255,255,255,0.1); padding-left: 15px;'>"
            "<span style='opacity: 0.7;'>Actual Ending Position:</span>"
            f"<strong style='color: #c5a880; margin-left: 5px;'>{actual_end}</strong>"
            "</div>"
            "</div>"
            "<div style='margin-top: 15px;'>"
            "<div style='display: flex; justify-content: space-between; font-size: 11px; opacity: 0.7;'>"
            "<span>MONTH PROGRESS RANGE</span>"
            f"<span>{completion_rate:.1f}% Target Achieved</span>"
            "</div>"
            "<div style='background-color: rgba(255,255,255,0.15); border-radius: 10px; height: 8px; width: 100%; margin-top: 5px; overflow: hidden;'>"
            f"<div style='background-color: #c5a880; height: 100%; width: {min(100.0, completion_rate):.1f}%; transition: width 0.5s ease-in-out;'></div>"
            "</div>"
            "</div>"
            "</div>"
        )
        st.markdown(dashboard_html, unsafe_allow_html=True)

    # 8. HTML Rendering & Action Line (inside Left Column)
    if is_locked and df is not None and not df.empty:
        active_rows = df[df["Include?"] == True]
        if not active_rows.empty:
            first_vol = active_rows.iloc[0].get("Volume")
            friendly_pace = str(first_vol) if first_vol else "Custom Plan"
        else:
            friendly_pace = "Custom Plan"
    else:
        if pace_basis == "Volume / Lines":
            friendly_pace = f"{selected_volume}"
        else:
            friendly_pace = f"{pace_ayahs} ayahs/day"

    html_content = build_planner_html(
        student_name=student_name,
        month_name=selected_month_name,
        year=selected_year,
        df=df,
        pace=friendly_pace
    )

    st.markdown("---")
    st.markdown("### 📋 Monthly Plan Preview")
    
    student_email_key = f"planner_student_email::{student_id}"
    if student_email_key not in st.session_state:
        recipient_email = get_student_email(student_id=student_id)
        st.session_state[student_email_key] = recipient_email
    else:
        recipient_email = st.session_state[student_email_key]
    
    col_btn_l, col_btn_m, col_btn_r = st.columns([1, 2, 1])
    with col_btn_m:
        if is_locked:
            if not recipient_email:
                st.warning("⚠️ No email registered for this student.")
                st.button("✉️ Send Study Plan", disabled=True, key="send_email_disabled", width="stretch")
            else:
                if st.button(f"✉️ Send Study Plan to {recipient_email}", type="primary", key="send_email_active", width="stretch"):
                    with st.spinner("Sending email..."):
                        def _send_bg():
                            success, msg = send_takhteet_plan_email(
                                student_name=student_name,
                                recipient_email=recipient_email,
                                plan_html=html_content,
                                year=selected_year,
                                month=selected_month_num
                            )
                            if success:
                                print(f"[SMTP Success] {msg}")
                            else:
                                print(f"[SMTP Error] {msg}")
                        
                        threading.Thread(target=_send_bg, daemon=True).start()
                        st.success("✉️ Send request dispatched!")
            
            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
            if st.button("🔓 Unlock / Edit Plan", type="secondary", key="unlock_plan", width="stretch"):
                if delete_locked_monthly_plan(student_id=student_id, year=selected_year, month=selected_month_num):
                    st.session_state.planner_is_locked = False
                    st.session_state.planner_data = None
                    if "planner_actuals" in locals() or "actuals_key" in locals():
                        k = locals().get("actuals_key")
                        if k and k in st.session_state:
                            del st.session_state[k]
                    # Also clear other student planner caches
                    for cache_key in list(st.session_state.keys()):
                        if cache_key.startswith("planner_actuals::") or cache_key.startswith("planner_start_pos::") or cache_key.startswith("planner_avg_pace::"):
                            del st.session_state[cache_key]
                    st.success("Plan unlocked successfully!")
                    st.rerun()
        else:
            if not recipient_email:
                st.warning("⚠️ No email registered for this student.")
                st.button("✉️ Send & Lock Study Plan", disabled=True, key="send_email_disabled", width="stretch")
            else:
                if st.button(f"✉️ Send & Lock Study Plan to {recipient_email}", type="primary", key="send_email_active", width="stretch"):
                    with st.spinner("Saving and sending..."):
                        if save_locked_monthly_plan(student_id=student_id, year=selected_year, month=selected_month_num, plan_df=df):
                            def _send_bg():
                                success, msg = send_takhteet_plan_email(
                                    student_name=student_name,
                                    recipient_email=recipient_email,
                                    plan_html=html_content,
                                    year=selected_year,
                                    month=selected_month_num
                                )
                                if success:
                                    print(f"[SMTP Success] {msg}")
                                else:
                                    print(f"[SMTP Error] {msg}")
                            
                            threading.Thread(target=_send_bg, daemon=True).start()
                            st.session_state.planner_is_locked = True
                            if "planner_actuals" in locals() or "actuals_key" in locals():
                                k = locals().get("actuals_key")
                                if k and k in st.session_state:
                                    del st.session_state[k]
                            # Also clear other student planner caches
                            for cache_key in list(st.session_state.keys()):
                                if cache_key.startswith("planner_actuals::") or cache_key.startswith("planner_start_pos::") or cache_key.startswith("planner_avg_pace::"):
                                    del st.session_state[cache_key]
                            st.success("✉️ Plan saved, locked, and email dispatched!")
                            st.rerun()
                        else:
                            st.error("Failed to save and lock plan in the database.")

    show_preview = st.checkbox("Show Study Plan Print Preview", value=True, key="planner_show_preview_toggle")
    if show_preview:
        st.iframe(html_content, height=800)
    else:
        st.info("💡 Study plan print preview is hidden to make editing instant and lag-free. Check 'Show Study Plan Print Preview' when you are ready to view or print the plan.")


def build_planner_html(
    *,
    student_name: str,
    month_name: str,
    year: int,
    df: pd.DataFrame,
    pace: str
) -> str:
    """Builds a beautiful premium-designed A4 print-ready HTML page for the monthly plan."""
    
    # Generate rows
    rows_html = ""
    for idx, r in df.iterrows():
        is_included = bool(r["Include?"])
        date_obj = datetime.strptime(r["Date"], "%Y-%m-%d")
        formatted_date = date_obj.strftime("%d-%b")
        
        if not is_included:
            # skipped/weekend/deleted
            rows_html += f"""
            <tr style="background-color: #faf9f6; color: #aaa; font-style: italic;">
                <td>{formatted_date}</td>
                <td>{r['Day']}</td>
                <td colspan="4" style="text-align: center; letter-spacing: 1px; font-size: 11px;">RELAX / SKIP DAY</td>
            </tr>
            """
        else:
            rows_html += f"""
            <tr>
                <td style="font-weight: bold; color: #1b4d3e;">{formatted_date}</td>
                <td>{r['Day']}</td>
                <td style="font-weight: 500;">{r['Surah']}</td>
                <td style="text-align: center;">{r['From Ayah']}</td>
                <td style="text-align: center; font-weight: bold; color: #1b4d3e;">{r['To Ayah']}</td>
                <td style="text-align: center; font-weight: 500; color: #b8860b;">{r.get('Volume') or 'Kamil'}</td>
            </tr>
            """

    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    :root {{
      --emerald: #1b4d3e;
      --gold: #c5a880;
      --bg: #f4f2eb;
      --text: #333333;
    }}
    body {{
      font-family: 'Outfit', 'Inter', 'Segoe UI', sans-serif;
      margin: 0;
      padding: 0;
      background-color: #ffffff;
      color: var(--text);
    }}
    .planner-card {{
      max-width: 800px;
      margin: 20px auto;
      padding: 30px;
      border: 1px solid #e2dcd0;
      border-radius: 12px;
      background-color: #ffffff;
      box-shadow: 0 4px 20px rgba(0,0,0,0.03);
      position: relative;
    }}
    .header {{
      text-align: center;
      border-bottom: 3px double var(--gold);
      padding-bottom: 20px;
      margin-bottom: 25px;
    }}
    .header h1 {{
      margin: 0;
      font-size: 24px;
      color: var(--emerald);
      text-transform: uppercase;
      letter-spacing: 1.5px;
    }}
    .header p {{
      margin: 5px 0 0 0;
      font-size: 14px;
      color: var(--gold);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 1px;
    }}
    .metadata-section {{
      display: flex;
      justify-content: space-between;
      margin-bottom: 25px;
      background-color: #faf8f5;
      padding: 15px 20px;
      border-left: 4px solid var(--emerald);
      border-radius: 6px;
    }}
    .metadata-item {{
      font-size: 13px;
    }}
    .metadata-item strong {{
      color: var(--emerald);
      display: block;
      margin-bottom: 2px;
    }}
    .table-container {{
      width: 100%;
      overflow-x: auto;
      margin-bottom: 20px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}
    th {{
      background-color: var(--emerald);
      color: white;
      text-align: left;
      padding: 10px 12px;
      font-weight: 600;
      border: 1px solid var(--emerald);
      text-transform: uppercase;
      font-size: 11px;
      letter-spacing: 0.5px;
    }}
    td {{
      padding: 9px 12px;
      border: 1px solid #e0dbd1;
    }}
    tr:nth-child(even) {{
      background-color: #faf9f6;
    }}
    .footer {{
      margin-top: 30px;
      text-align: center;
      font-size: 11px;
      color: #888;
      border-top: 1px solid #e2dcd0;
      padding-top: 15px;
      font-style: italic;
    }}
    .print-btn {{
      position: absolute;
      top: 30px;
      right: 30px;
      background: linear-gradient(180deg, var(--emerald), #0f352a);
      color: white;
      border: none;
      padding: 8px 16px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: bold;
      cursor: pointer;
      box-shadow: 0 4px 6px rgba(0,0,0,0.1);
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s;
    }}
    .print-btn:hover {{
      transform: translateY(-1px);
      box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }}
    @media print {{
      .print-btn {{
        display: none !important;
      }}
      body {{
        background-color: white;
      }}
      .planner-card {{
        border: none !important;
        box-shadow: none !important;
        margin: 0 !important;
        padding: 0 !important;
      }}
    }}
  </style>
</head>
<body>
  <div class="planner-card">
    <button class="print-btn" onclick="window.print()">🖨️ Print / Save as PDF</button>
    
    <div class="header">
      <h1>Al Madrasa-tus-Saifiyah-tul-Burhaniyah</h1>
      <p>Monthly Jadeed Takhteet Plan</p>
    </div>
    
    <div class="metadata-section">
      <div class="metadata-item">
        <strong>Student Name</strong>
        {student_name}
      </div>
      <div class="metadata-item">
        <strong>Month / Year</strong>
        {month_name} {year}
      </div>
      <div class="metadata-item">
        <strong>Assigned Pace</strong>
        {pace}
      </div>
    </div>
    
    <div style="font-family: 'Outfit', 'Inter', 'Segoe UI', sans-serif; background-color: #faf8f5; padding: 18px; border-left: 4px solid #1b4d3e; border-radius: 6px; margin-bottom: 20px; font-size: 14px; line-height: 1.5; color: #333;">
      <p style="margin: 0 0 8px 0; font-size: 15px; color: #1b4d3e;"><b>Dear Parent & Student, Salaam Jameel!</b></p>
      <p style="margin: 0;">This is your monthly Jadeed Takhteet study plan. Consistent daily recitation builds strength and success in Hifz. Stay dedicated, keep reciting, and aim high!</p>
    </div>

    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Day</th>
            <th>Surah Target</th>
            <th style="text-align: center;">From Ayah</th>
            <th style="text-align: center;">To Ayah</th>
            <th style="text-align: center;">Volume</th>
          </tr>
        </thead>
        <tbody>
          {rows_html}
        </tbody>
      </table>
    </div>
    
    <div class="footer">
      Generated automatically by Madrasa Recitation App. Keep reciting and aiming high!
    </div>
  </div>
</body>
</html>
"""
