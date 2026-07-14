from __future__ import annotations

import streamlit as st
from datetime import datetime, date, timedelta

from app.db import (
    fetch_monthly_report,
    get_student_current_jadeed,
    get_all_students_current_jadeed,
    fetch_collective_attendance_report,
    get_earliest_global_activity_date,
    fetch_ikhtebar_report
)
from app.report_pdf import (
    build_report_html,
    build_current_jadeed_report_html,
    build_collective_attendance_report_html,
    build_ikhtebar_report_html
)
from app.ui.shared import back_home_button
from app.ui.student import current_student_badge


@st.fragment
def render_holiday_picker(start_date: date, end_date: date) -> None:
    # Initialize lists in session state
    if "ikhtebar_holidays" not in st.session_state:
        st.session_state.ikhtebar_holidays = set()
    if "pending_exclusions" not in st.session_state:
        st.session_state.pending_exclusions = set()
        
    st.markdown("##### 📅 Exclude Holidays / Closed Days")

    col_picker, col_btn = st.columns([3, 1])
    with col_picker:
        # Default picker value is start_date (which is a single date object)
        if "holiday_picker_val" not in st.session_state:
            st.session_state.holiday_picker_val = start_date
            
        new_date = st.date_input(
            "Select a date using the calendar to queue for exclusion:",
            value=st.session_state.holiday_picker_val,
            min_value=start_date,
            max_value=end_date,
            key="holiday_calendar_picker"
        )
        
        # Check if selection changed and add to pending
        if new_date != st.session_state.holiday_picker_val:
            st.session_state.holiday_picker_val = new_date
            if isinstance(new_date, date):
                st.session_state.pending_exclusions.add(new_date)
            
    with col_btn:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("➕ Exclude All", use_container_width=True, key="add_holiday_btn"):
            if isinstance(new_date, date):
                st.session_state.pending_exclusions.add(new_date)
            st.session_state.ikhtebar_holidays.update(st.session_state.pending_exclusions)
            st.session_state.pending_exclusions.clear()
            st.session_state.holiday_picker_val = start_date
            st.rerun() # This will rerun the whole app to refresh the OPR report!

    # Render pending selections
    if st.session_state.pending_exclusions:
        st.markdown("**Pending Exclusions (Click '➕ Exclude All' to save):**")
        sorted_pending = sorted(st.session_state.pending_exclusions)
        pending_html = []
        for p in sorted_pending:
            pending_html.append(f"<code style='background-color: rgba(197, 168, 128, 0.15); border: 1px solid var(--gold); padding: 4px 8px; border-radius: 4px; margin-right: 5px; margin-bottom: 5px; display: inline-block;'>{p.strftime('%d %b %Y')}</code>")
        st.markdown("".join(pending_html), unsafe_allow_html=True)
        
        col_clear_pending, _ = st.columns([1, 4])
        with col_clear_pending:
            if st.button("Clear Pending", key="clear_pending_btn", use_container_width=True):
                st.session_state.pending_exclusions.clear()
                st.session_state.holiday_picker_val = start_date
                st.rerun()


def render_report() -> None:
    back_home_button()
    
    col_title, col_ref = st.columns([3, 1])
    with col_title:
        st.subheader("Monthly Report")
        st.caption("Date-wise student progress and class-wide attendance report.")
    with col_ref:
        if st.button("🔄 Refresh Data", use_container_width=True, key="refresh_all_reports_btn"):
            keys_to_clear = [
                k for k in st.session_state.keys() 
                if k.startswith(("monthly_report", "current_jadeed", "attendance_report", "ikhtebar_report", "earliest_global_activity_date"))
            ]
            for k in keys_to_clear:
                del st.session_state[k]
            st.cache_data.clear()
            st.rerun()

    current_student_badge()

    student_id = st.session_state.get("student_id")
    student_name = st.session_state.get("student_name", "Student")
    if not student_id:
        st.warning("Please select a student on Home first to view monthly reports.")
        return

    now = datetime.now()

    # Month/Year Selection
    col_y, col_m = st.columns(2)
    with col_y:
        years = list(range(2025, now.year + 2))
        selected_year = st.selectbox("Year", options=years, index=years.index(now.year))
    with col_m:
        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        selected_month_name = st.selectbox("Month", options=months, index=now.month - 1)
        selected_month_num = months.index(selected_month_name) + 1

    # Clear monthly cache key if student, year, or month changes to optimize speed
    month_cache_key = f"{student_id}_{selected_year}_{selected_month_num}"
    if st.session_state.get("monthly_report_cache_key") != month_cache_key:
        st.session_state.monthly_report_cache_key = month_cache_key
        st.session_state.monthly_report_rows = None
        st.session_state.attendance_report_cache = None

    def get_monthly_rows():
        if st.session_state.get("monthly_report_rows") is None:
            with st.spinner("Fetching monthly report data..."):
                st.session_state.monthly_report_rows = fetch_monthly_report(
                    student_id=student_id, 
                    year=selected_year, 
                    month=selected_month_num
                )
        return st.session_state.monthly_report_rows

    def get_cached_current_jadeed():
        cache_key = f"current_jadeed_{student_id}"
        if cache_key not in st.session_state:
            with st.spinner("Fetching current jadeed progress..."):
                curr_ent = get_student_current_jadeed(student_id=student_id)
                all_stud = get_all_students_current_jadeed()
                st.session_state[cache_key] = (curr_ent, all_stud)
        return st.session_state[cache_key]

    def get_cached_attendance_report():
        if st.session_state.get("attendance_report_cache") is None:
            with st.spinner("Fetching class attendance data..."):
                try:
                    data = fetch_collective_attendance_report(year=selected_year, month=selected_month_num)
                except Exception as e:
                    st.error(f"Error fetching class attendance: {e}")
                    data = None
                st.session_state.attendance_report_cache = data
        return st.session_state.attendance_report_cache

    st.markdown("### Report Category Select")
    categories = [
        "👥 Murajat Report",
        "📖 Juzulhali Report",
        "📝 Jadeed Report",
        "📋 Takhteet Report",
        "🌟 Current Jadeed",
        "📊 Mistake Analytics",
        "📅 Class Attendance",
        "🎓 OPR - One Page Report"
    ]
    if "selected_report_category" not in st.session_state:
        st.session_state.selected_report_category = "👥 Murajat Report"
        
    selected_category = st.pills(
        "Select Report Category:",
        options=categories,
        default=st.session_state.selected_report_category,
        label_visibility="collapsed"
    )
    if selected_category:
        st.session_state.selected_report_category = selected_category
    else:
        selected_category = st.session_state.selected_report_category

    if selected_category == "👥 Murajat Report":
        rows = get_monthly_rows()
        if not rows:
            st.info("No Murajat report data found for this student in the selected month.")
        else:
            html_murajat = build_report_html(student_name=student_name, rows=rows, report_type="murajat")
            st.iframe(html_murajat, height=700)
            
    elif selected_category == "📖 Juzulhali Report":
        rows = get_monthly_rows()
        if not rows:
            st.info("No Juzulhali report data found for this student in the selected month.")
        else:
            html_juzulhali = build_report_html(student_name=student_name, rows=rows, report_type="juzulhali")
            st.iframe(html_juzulhali, height=700)
        
    elif selected_category == "📝 Jadeed Report":
        rows = get_monthly_rows()
        if not rows:
            st.info("No Jadeed report data found for this student in the selected month.")
        else:
            html_jadeed = build_report_html(student_name=student_name, rows=rows, report_type="jadeed")
            st.iframe(html_jadeed, height=700)
        
    elif selected_category == "📋 Takhteet Report":
        rows = get_monthly_rows()
        if not rows:
            st.info("No Takhteet report data found for this student in the selected month.")
        else:
            html_takhteet = build_report_html(student_name=student_name, rows=rows, report_type="takhteet")
            st.iframe(html_takhteet, height=700)

    elif selected_category == "🌟 Current Jadeed":
        current_entry, all_students_data = get_cached_current_jadeed()
        html_current = build_current_jadeed_report_html(
            student_name=student_name,
            current_entry=current_entry,
            all_students_data=all_students_data
        )
        st.iframe(html_current, height=700)

    elif selected_category == "📊 Mistake Analytics":
        from app.ui.analytics import render_student_analytics
        render_student_analytics(student_id=student_id, student_name=student_name)

    elif selected_category == "📅 Class Attendance":
        data = get_cached_attendance_report()
        if data:
            if not data.get("students"):
                st.info("No class attendance data found.")
            else:
                html_collective = build_collective_attendance_report_html(data)
                st.iframe(html_collective, height=750)

    elif selected_category == "🎓 OPR - One Page Report":
        st.markdown("### 🎓 OPR - One Page Report")
        st.caption("Class-wide cumulative report covering recitation starting/ending points, total pages recited, and attendance since the software inception.")

        # Cache earliest global activity date
        if "earliest_global_activity_date" not in st.session_state:
            with st.spinner("Initializing dates..."):
                st.session_state.earliest_global_activity_date = get_earliest_global_activity_date()
        earliest_date_str = st.session_state.earliest_global_activity_date

        try:
            earliest_date = datetime.strptime(earliest_date_str, "%Y-%m-%d").date()
        except Exception:
            earliest_date = date(2025, 1, 1)

        # Default start date is the 1st of the current month (e.g. July 1, 2026)
        default_start_date = date(now.year, now.month, 1)

        col_sd, col_ed = st.columns(2)
        with col_sd:
            start_date = st.date_input("Start Date", value=default_start_date, min_value=date(2020, 1, 1))
        with col_ed:
            end_date = st.date_input("End Date", value=now.date(), min_value=date(2020, 1, 1))

        if start_date > end_date:
            st.error("Error: Start Date must be before or equal to End Date.")
        else:
            # Calculate working days (Monday - Saturday) up to today
            working_days = []
            curr = start_date
            limit_date = min(end_date, date.today())
            while curr <= limit_date:
                if curr.weekday() != 6: # Sunday is 6
                    working_days.append(curr)
                curr += timedelta(days=1)

            # Initialize holidays list in session state
            if "ikhtebar_holidays" not in st.session_state:
                st.session_state.ikhtebar_holidays = set()

            # Keep only holidays within active date range
            st.session_state.ikhtebar_holidays = {
                h for h in st.session_state.ikhtebar_holidays 
                if start_date <= h <= end_date
            }

            render_holiday_picker(start_date, end_date)

            # Render selected holidays list
            if st.session_state.ikhtebar_holidays:
                st.markdown("**Excluded Holidays:**")
                sorted_holidays = sorted(st.session_state.ikhtebar_holidays)
                
                badges_html = []
                for h in sorted_holidays:
                    badges_html.append(f"<code style='background-color: var(--card); border: 1px solid var(--border); padding: 4px 8px; border-radius: 4px; margin-right: 5px; margin-bottom: 5px; display: inline-block;'>{h.strftime('%a, %d %b %Y')}</code>")
                st.markdown("".join(badges_html), unsafe_allow_html=True)
                
                col_c1, _ = st.columns([1, 4])
                with col_c1:
                    if st.button("Clear All", use_container_width=True, key="ikhtebar_clear_holidays"):
                        st.session_state.ikhtebar_holidays.clear()
                        st.rerun()
            else:
                st.caption("No custom holidays excluded yet. Use the calendar picker above to select days.")

            # Filter out holidays
            actual_working_days = [d for d in working_days if d not in st.session_state.ikhtebar_holidays]

            st.info(f"📅 **Total Working Days calculated**: {len(actual_working_days)} day(s) (Sunday and custom holidays excluded)")

            # Cache the report data fetching in session state to prevent database query on every holiday selection
            report_data_key = f"ikhtebar_report_{start_date.isoformat()}_{end_date.isoformat()}"
            if report_data_key not in st.session_state:
                with st.spinner("Fetching assessment report data..."):
                    try:
                        report_data = fetch_ikhtebar_report(from_date=start_date.isoformat(), to_date=end_date.isoformat())
                    except Exception as e:
                        st.error(f"Error fetching assessment report: {e}")
                        report_data = None
                    st.session_state[report_data_key] = report_data
            else:
                report_data = st.session_state[report_data_key]

            if report_data:
                show_preview = st.checkbox("Show One Page Report Preview", value=True, key="show_opr_preview_toggle")
                if show_preview:
                    html_assessment = build_ikhtebar_report_html(
                        data=report_data,
                        working_days_list=actual_working_days,
                        holidays_list=list(st.session_state.ikhtebar_holidays)
                    )
                    st.iframe(html_assessment, height=800)
                else:
                    st.info("💡 Report preview is hidden to make calendar selections instant and lag-free. Check 'Show One Page Report Preview' when you are ready to view/print the report.")
