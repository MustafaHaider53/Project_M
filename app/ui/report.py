from __future__ import annotations

import streamlit as st
from datetime import datetime, date, timedelta

from app.db import (
    fetch_monthly_report,
    get_student_current_jadeed,
    get_all_students_current_jadeed,
    fetch_collective_attendance_report,
    get_earliest_global_activity_date,
    fetch_ikhtebar_report,
    fetch_jadeed_pages_summary_report,
    fetch_teacher_attendance_report,
    fetch_teacher_daywise_attendance,
    update_teacher_attendance_day,
    list_active_teachers,
)
from app.report_pdf import (
    build_report_html,
    build_unified_3in1_report_html,
    build_current_jadeed_report_html,
    build_collective_attendance_report_html,
    build_ikhtebar_report_html,
    build_jadeed_pages_summary_html,
    build_teacher_detailed_attendance_html,
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
        if st.button("➕ Exclude All", width="stretch", key="add_holiday_btn"):
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
            if st.button("Clear Pending", key="clear_pending_btn", width="stretch"):
                st.session_state.pending_exclusions.clear()
                st.session_state.holiday_picker_val = start_date
                st.rerun()


@st.fragment
def render_jadeed_pages_summary_fragment(now_date: date) -> None:
    st.markdown("### 📄 Jadeed Total Pages by Student (تقرير مجموع صفحات الجديد)")
    st.caption("Class-wide monthly breakdown and total Jadeed pages recited per student within any custom date range, ranked in descending order.")

    # Preset Quick Dates
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    with col_p1:
        if st.button("📅 Current Month", key="preset_current_month", width="stretch"):
            st.session_state.jpages_from = date(now_date.year, now_date.month, 1)
            st.session_state.jpages_to = now_date
            st.rerun(scope="fragment")
    with col_p2:
        if st.button("📅 Last 30 Days", key="preset_last_30", width="stretch"):
            st.session_state.jpages_from = now_date - timedelta(days=30)
            st.session_state.jpages_to = now_date
            st.rerun(scope="fragment")
    with col_p3:
        if st.button("📅 July – August 2026", key="preset_jul_aug", width="stretch"):
            st.session_state.jpages_from = date(2026, 7, 15)
            st.session_state.jpages_to = date(2026, 8, 22)
            st.rerun(scope="fragment")
    with col_p4:
        if st.button("📅 Year to Date (2026)", key="preset_ytd", width="stretch"):
            st.session_state.jpages_from = date(2026, 1, 1)
            st.session_state.jpages_to = now_date
            st.rerun(scope="fragment")

    # Date Pickers
    if "jpages_from" not in st.session_state:
        st.session_state.jpages_from = date(2026, 7, 15)
    if "jpages_to" not in st.session_state:
        st.session_state.jpages_to = now_date

    col_jfrom, col_jto, col_jbtn = st.columns([2, 2, 1])
    with col_jfrom:
        jp_from = st.date_input("Start Date", value=st.session_state.jpages_from, key="jpages_from_input")
        st.session_state.jpages_from = jp_from
    with col_jto:
        jp_to = st.date_input("End Date", value=st.session_state.jpages_to, key="jpages_to_input")
        st.session_state.jpages_to = jp_to
    with col_jbtn:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 Refresh", key="refresh_jpages_btn", width="stretch"):
            st.cache_data.clear()
            st.rerun(scope="fragment")

    if jp_from > jp_to:
        st.error("Error: Start Date must be before or equal to End Date.")
    else:
        with st.spinner("Loading Jadeed Pages Summary..."):
            jpages_data = fetch_jadeed_pages_summary_report(
                from_date=jp_from.isoformat(),
                to_date=jp_to.isoformat()
            )

        if not jpages_data or not jpages_data.get("students"):
            st.info("No student records found.")
        else:
            html_jpages = build_jadeed_pages_summary_html(jpages_data)
            st.iframe(html_jpages, height=780)


def render_report() -> None:
    back_home_button()
    
    col_title, col_ref = st.columns([3, 1])
    with col_title:
        st.subheader("Monthly Report")
        st.caption("Date-wise student progress and class-wide attendance report.")
    with col_ref:
        if st.button("🔄 Refresh Data", width="stretch", key="refresh_all_reports_btn"):
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

    def get_monthly_rows():
        with st.spinner("Fetching monthly report data..."):
            return fetch_monthly_report(
                student_id=student_id, 
                year=selected_year, 
                month=selected_month_num
            )

    def get_cached_current_jadeed():
        with st.spinner("Fetching current jadeed progress..."):
            curr_ent = get_student_current_jadeed(student_id=student_id)
            all_stud = get_all_students_current_jadeed()
            return curr_ent, all_stud

    def get_cached_attendance_report():
        with st.spinner("Fetching class attendance data..."):
            try:
                return fetch_collective_attendance_report(year=selected_year, month=selected_month_num)
            except Exception as e:
                st.error(f"Error fetching class attendance: {e}")
                return None

    def get_cached_ummul_banin_report():
        with st.spinner("Fetching Ummul Banin report data..."):
            try:
                from app.db import fetch_ummul_banin_report_data
                return fetch_ummul_banin_report_data()
            except Exception as e:
                st.error(f"Error fetching Ummul Banin report: {e}")
                return None

    st.markdown("### Report Category Select")
    categories = [
        "👥 Murajat Report",
        "📖 Juzulhali Report",
        "📝 Jadeed Report",
        "📑 Unified Summary Report",
        "📄 Jadeed Pages Summary",
        "📋 Takhteet Report",
        "🌟 Current Jadeed",
        "📊 Mistake Analytics",
        "📅 Class Attendance",
        "📖 Ummul Banin Ben Report",
        "🎓 OPR - One Page Report",
        "👨‍🏫 Teacher Attendance Report",
        "👪 Parent Views",
        "✉️ Email Log"
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

    elif selected_category == "📑 Unified Summary Report":
        rows = get_monthly_rows()
        if not rows:
            st.info("No recitation summary data found for this student in the selected month.")
        else:
            html_unified = build_unified_3in1_report_html(student_name=student_name, rows=rows)
            st.iframe(html_unified, height=750)

    elif selected_category == "📄 Jadeed Pages Summary":
        render_jadeed_pages_summary_fragment(now.date())
        
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

    elif selected_category == "📖 Ummul Banin Ben Report":
        st.markdown("### 📖 Ummul Banin Ben Report (تقرير أم البنين)")
        st.caption("Class-wide report showing each student's latest Jadeed recitation (today's latest, or their last historical entry if not entered/marked as 'no jadeed' today) along with today's complete homework (Jadeed, Juzulhali, and Murajat).")
        
        if st.button("🔄 Refresh Data", key="refresh_ummul_banin"):
            st.session_state.pop("ummul_banin_report_cache", None)
            st.rerun()
            
        data = get_cached_ummul_banin_report()
        if not data:
            st.info("No Ummul Banin report data found.")
        else:
            from app.report_pdf import build_ummul_banin_report_html
            html_ummul_banin = build_ummul_banin_report_html(data)
            st.iframe(html_ummul_banin, height=750)

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
                    if st.button("Clear All", width="stretch", key="ikhtebar_clear_holidays"):
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

    elif selected_category == "👨‍🏫 Teacher Attendance Report":
        render_teacher_attendance_dashboard()

    elif selected_category == "👪 Parent Views":
        render_parent_views_dashboard()
        
    elif selected_category == "✉️ Email Log":
        render_email_log_dashboard()


def render_parent_views_dashboard() -> None:
    from app.db import list_students, get_rest
    import calendar
    
    st.markdown("### 📅 Parent Views Monthly Report")
    st.caption("A monthly overview showing which parents viewed their child's daily progress report.")

    # Dropdown selectors for month and year
    now = datetime.today()
    
    col1, col2 = st.columns(2)
    with col1:
        months_list = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        selected_month_name = st.selectbox("Select Month", options=months_list, index=now.month - 1)
        selected_month = months_list.index(selected_month_name) + 1
    with col2:
        years_list = list(range(2025, now.year + 2))
        selected_year = st.selectbox("Select Year", options=years_list, index=years_list.index(now.year))

    # Calculate last day of the month
    last_day = calendar.monthrange(selected_year, selected_month)[1]
    start_date = f"{selected_year}-{selected_month:02d}-01"
    end_date = f"{selected_year}-{selected_month:02d}-{last_day:02d}"

    # Fetch students
    students = list_students()
    students = [s for s in students if "test" not in s["full_name"].lower()]
    if not students:
        st.info("No students found.")
        return

    # Fetch all report views for this month in exactly 1 query
    rest = get_rest()
    viewed_set = set() # Store tuples of (student_id_lower, date_str)

    if rest is not None:
        with st.spinner("Loading parent views..."):
            try:
                views = rest.select(
                    "parent_report_views",
                    select="student_id,activity_date",
                    params={
                        "and": f"(activity_date.gte.{start_date},activity_date.lte.{end_date})"
                    }
                )
                for v in views:
                    sid = v.get("student_id")
                    adate = v.get("activity_date")
                    if sid and adate:
                        viewed_set.add((sid.lower(), adate))
            except Exception as e:
                st.error(f"Error loading views: {e}")

    # Build the legend
    st.markdown(
        """
        <div style='display: flex; gap: 20px; font-size: 0.9rem; margin-top: 10px; margin-bottom: 10px;'>
            <div><span style='color: #10b981; font-weight: bold;'>🟢</span> Parent Logged In & Viewed</div>
            <div><span style='color: #ef4444; font-weight: bold;'>🔴</span> Parent Not Viewed</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Construct HTML Table
    days = list(range(1, last_day + 1))
    
    # Header row
    header_html = f'<th style="padding: 10px; font-weight: bold; position: sticky; left: 0; top: 0; background-color: #F7EFD8; z-index: 12; border-right: 2px solid var(--border); min-width: 180px;">👤 Student Name</th>'
    for d in days:
        header_html += f'<th style="padding: 6px; text-align: center; font-weight: bold; min-width: 28px; border-right: 1px solid var(--border); position: sticky; top: 0; background-color: #F7EFD8; z-index: 11;">{d}</th>'
        
    # Table rows
    rows_html = ""
    for s in students:
        student_id = s.get("id")
        name = s.get("full_name", "Unknown")
        if not student_id:
            continue
        student_id_lower = student_id.lower()
        
        row_cells = f'<td style="padding: 10px; font-weight: bold; position: sticky; left: 0; background-color: #F7EFD8; z-index: 9; border-right: 2px solid var(--border);">{name}</td>'
        for d in days:
            date_str = f"{selected_year}-{selected_month:02d}-{d:02d}"
            is_viewed = (student_id_lower, date_str) in viewed_set
            
            if is_viewed:
                cell_style = "background-color: rgba(16, 185, 129, 0.08); border-right: 1px solid var(--border); text-align: center; padding: 6px;"
                indicator = "🟢"
            else:
                cell_style = "background-color: rgba(239, 68, 68, 0.04); border-right: 1px solid var(--border); text-align: center; padding: 6px;"
                indicator = "🔴"
                
            row_cells += f'<td style="{cell_style}">{indicator}</td>'
            
        rows_html += f'<tr style="border-bottom: 1px solid var(--border);">{row_cells}</tr>'

    table_html = f"""
    <div style="overflow: auto; max-height: 70vh; width: 100%; border: 1px solid var(--border); border-radius: 8px; background-color: var(--card);">
      <table style="width: 100%; border-collapse: collapse; text-align: left; font-family: system-ui, -apple-system, sans-serif; font-size: 0.82rem; line-height: 1.2;">
        <thead>
          <tr style="background-color: var(--card); border-bottom: 2px solid var(--border);">
            {header_html}
          </tr>
        </thead>
        <tbody>
          {rows_html}
        </tbody>
      </table>
    </div>
    """
    
    st.markdown(table_html.replace("\n", " "), unsafe_allow_html=True)


def render_email_log_dashboard() -> None:
    from app.db import get_daily_email_status, send_single_student_daily_email

    st.markdown("### ✉️ Daily Email Dispatch Status & Actions")
    st.caption("Track daily recitation entries (Murajat, Juzulhali, Jadeed, Takhteet) and dispatch progress or absence emails directly.")

    # Select Date & Refresh
    col_date, col_btn = st.columns([2, 2])
    with col_date:
        selected_date = st.date_input(
            "Select Date:",
            value=date.today(),
            key="email_log_date_input"
        )
    with col_btn:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 Refresh Status", key="refresh_email_log_btn"):
            st.rerun()

    date_str = selected_date.isoformat()

    with st.spinner("Fetching email status & activity records..."):
        logs = get_daily_email_status(date_str)

    if not logs:
        st.info("No students found in the database.")
        return

    # Count statistics
    total = len(logs)
    sent_count = sum(1 for l in logs if l["sent"])
    not_sent_count = total - sent_count

    # Render summary cards
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    col_stats = st.columns(3)
    with col_stats[0]:
        st.markdown(
            f"""
            <div style='background-color: var(--card); border: 1.5px solid var(--border); padding: 14px; border-radius: 8px; text-align: center;'>
                <div style='font-size: 0.82rem; color: var(--ink); opacity: 0.7; font-weight: 500;'>Total Students</div>
                <div style='font-size: 1.7rem; font-weight: bold; color: var(--ink); margin-top: 4px;'>{total}</div>
            </div>
            """.replace("\n", " "),
            unsafe_allow_html=True
        )
    with col_stats[1]:
        st.markdown(
            f"""
            <div style='background-color: rgba(16, 185, 129, 0.08); border: 1.5px solid #10b981; padding: 14px; border-radius: 8px; text-align: center;'>
                <div style='font-size: 0.82rem; color: #0f766e; font-weight: 500;'>Sent Successfully</div>
                <div style='font-size: 1.7rem; font-weight: bold; color: #0f766e; margin-top: 4px;'>🟢 {sent_count}</div>
            </div>
            """.replace("\n", " "),
            unsafe_allow_html=True
        )
    with col_stats[2]:
        st.markdown(
            f"""
            <div style='background-color: rgba(239, 68, 68, 0.08); border: 1.5px solid #ef4444; padding: 14px; border-radius: 8px; text-align: center;'>
                <div style='font-size: 0.82rem; color: #b91c1c; font-weight: 500;'>Not Sent</div>
                <div style='font-size: 1.7rem; font-weight: bold; color: #b91c1c; margin-top: 4px;'>🔴 {not_sent_count}</div>
            </div>
            """.replace("\n", " "),
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    # Filter & Bulk Actions Bar
    col_filter, col_bulk = st.columns([3, 2])
    with col_filter:
        status_filter = st.pills(
            "Filter by Status:",
            options=[f"All ({total})", f"🔴 Unsent ({not_sent_count})", f"🟢 Sent ({sent_count})"],
            default=f"All ({total})",
            key="email_log_status_pills"
        )
    with col_bulk:
        unsent_with_email = [l for l in logs if not l["sent"] and l["has_email"]]
        if unsent_with_email:
            st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
            if st.button(f"⚡ Send to All Unsent ({len(unsent_with_email)})", type="primary", width="stretch", key="btn_bulk_send_all"):
                progress_bar = st.progress(0, text="Starting bulk email dispatch...")
                success_count = 0
                fail_count = 0
                for idx, item in enumerate(unsent_with_email):
                    progress_bar.progress(
                        (idx + 1) / len(unsent_with_email),
                        text=f"Sending email ({idx+1}/{len(unsent_with_email)}): {item['student_name']}..."
                    )
                    ok, _ = send_single_student_daily_email(student_id=item["student_id"], date_str=date_str)
                    if ok:
                        success_count += 1
                    else:
                        fail_count += 1
                progress_bar.empty()
                if fail_count == 0:
                    st.success(f"🎉 Successfully dispatched {success_count} emails!")
                else:
                    st.warning(f"Dispatched {success_count} emails successfully, {fail_count} failed.")
                st.rerun()

    # Search bar
    search_query = st.text_input("🔍 Search Student:", value="", key="email_log_search", placeholder="Type student name...")

    # Filter list
    filtered_logs = logs
    if status_filter == f"🔴 Unsent ({not_sent_count})":
        filtered_logs = [l for l in filtered_logs if not l["sent"]]
    elif status_filter == f"🟢 Sent ({sent_count})":
        filtered_logs = [l for l in filtered_logs if l["sent"]]

    if search_query.strip():
        q = search_query.strip().lower()
        filtered_logs = [l for l in filtered_logs if q in l["student_name"].lower()]

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    if not filtered_logs:
        st.info("No students found matching the selected filters.")
        return

    # Table Header
    st.markdown(
        """
        <div style="background-color: #F7EFD8; border: 1px solid var(--border); border-radius: 8px 8px 0 0; padding: 10px 14px; margin-bottom: 4px;">
            <div style="display: flex; align-items: center; font-size: 0.85rem; font-weight: bold; color: var(--ink);">
                <div style="flex: 2.6; min-width: 140px;">👤 Student Name</div>
                <div style="flex: 2.2; min-width: 130px;">✉️ Email Address</div>
                <div style="flex: 0.8; text-align: center;">Murajat</div>
                <div style="flex: 0.8; text-align: center;">Juzulhali</div>
                <div style="flex: 0.8; text-align: center;">Jadeed</div>
                <div style="flex: 0.8; text-align: center;">Takhteet</div>
                <div style="flex: 1.1; text-align: center;">Status</div>
                <div style="flex: 1.2; text-align: center;">Action</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Render Student Rows
    for l in filtered_logs:
        s_id = l["student_id"]
        s_name = l["student_name"]
        s_email = l["student_email"]
        has_email = l["has_email"]
        sent = l["sent"]
        is_absent = l["is_absent"]

        with st.container():
            c_name, c_email, c_m, c_jh, c_jd, c_t, c_status, c_act = st.columns([2.6, 2.2, 0.8, 0.8, 0.8, 0.8, 1.1, 1.2])
            
            with c_name:
                absent_badge = '<span style="background-color: rgba(239, 68, 68, 0.12); color: #dc2626; font-size: 10px; font-weight: bold; padding: 1px 5px; border-radius: 4px; margin-left: 4px;">Absent</span>' if is_absent else ''
                st.markdown(f"<div style='padding-top: 6px; font-weight: 600; font-size: 0.88rem;'>{s_name} {absent_badge}</div>", unsafe_allow_html=True)
                
            with c_email:
                if has_email:
                    st.markdown(f"<div style='padding-top: 6px; font-size: 0.82rem; opacity: 0.85; word-break: break-all;'>{s_email}</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div style='padding-top: 6px; font-size: 0.80rem; color: #ef4444; font-weight: 500;'>⚠️ No Email</div>", unsafe_allow_html=True)
                    
            with c_m:
                icon_m = "🟢" if l["has_murajat"] else "⚪"
                label_m = "Yes" if l["has_murajat"] else "No"
                color_m = "#10b981" if l["has_murajat"] else "gray"
                st.markdown(f"<div style='text-align: center; padding-top: 6px; font-size: 0.82rem; color: {color_m};'>{icon_m} {label_m}</div>", unsafe_allow_html=True)
                
            with c_jh:
                icon_jh = "🟢" if l["has_juzulhali"] else "⚪"
                label_jh = "Yes" if l["has_juzulhali"] else "No"
                color_jh = "#10b981" if l["has_juzulhali"] else "gray"
                st.markdown(f"<div style='text-align: center; padding-top: 6px; font-size: 0.82rem; color: {color_jh};'>{icon_jh} {label_jh}</div>", unsafe_allow_html=True)
                
            with c_jd:
                icon_jd = "🟢" if l["has_jadeed"] else "⚪"
                label_jd = "Yes" if l["has_jadeed"] else "No"
                color_jd = "#10b981" if l["has_jadeed"] else "gray"
                st.markdown(f"<div style='text-align: center; padding-top: 6px; font-size: 0.82rem; color: {color_jd};'>{icon_jd} {label_jd}</div>", unsafe_allow_html=True)
                
            with c_t:
                icon_t = "🟢" if l["has_takhteet"] else "⚪"
                label_t = "Yes" if l["has_takhteet"] else "No"
                color_t = "#10b981" if l["has_takhteet"] else "gray"
                st.markdown(f"<div style='text-align: center; padding-top: 6px; font-size: 0.82rem; color: {color_t};'>{icon_t} {label_t}</div>", unsafe_allow_html=True)
                
            with c_status:
                if sent:
                    st.markdown("<div style='text-align: center; padding-top: 6px;'><span style='background-color: rgba(16, 185, 129, 0.15); color: #10b981; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;'>🟢 Sent</span></div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div style='text-align: center; padding-top: 6px;'><span style='background-color: rgba(239, 68, 68, 0.15); color: #ef4444; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;'>🔴 Unsent</span></div>", unsafe_allow_html=True)
                    
            with c_act:
                if not has_email:
                    st.button("No Email", disabled=True, key=f"btn_no_email_{s_id}", width="stretch")
                elif not sent:
                    if st.button("✉️ Send", type="primary", key=f"btn_send_{s_id}", width="stretch"):
                        with st.spinner(f"Sending to {s_name}..."):
                            ok, msg = send_single_student_daily_email(student_id=s_id, date_str=date_str)
                            if ok:
                                st.toast(f"✅ Email sent to {s_name}!", icon="✉️")
                            else:
                                st.error(f"❌ Failed to send email to {s_name}: {msg}")
                            st.rerun()
                else:
                    if st.button("🔄 Resend", type="secondary", key=f"btn_resend_{s_id}", width="stretch"):
                        with st.spinner(f"Resending to {s_name}..."):
                            ok, msg = send_single_student_daily_email(student_id=s_id, date_str=date_str)
                            if ok:
                                st.toast(f"✅ Email resent to {s_name}!", icon="🔄")
                            else:
                                st.error(f"❌ Failed to resend email to {s_name}: {msg}")
                            st.rerun()

            st.markdown("<hr style='margin: 4px 0 6px 0; border: none; border-top: 1px solid rgba(184,137,23,0.15);'/>", unsafe_allow_html=True)


@st.fragment
def render_teacher_attendance_dashboard() -> None:
    st.markdown("### 👨‍🏫 Teacher Attendance & Productivity Report (تقرير حضور وإنتاجية المعلمين)")
    st.caption("Day-wise teacher attendance, manual attendance override, login time adjustment, and printable PDF reports.")

    # View Sub-mode Selector
    sub_mode = st.pills(
        "Teacher Attendance View Mode:",
        options=["📅 Detailed Day-Wise Teacher Report", "📊 All Teachers Summary Overview"],
        default="📅 Detailed Day-Wise Teacher Report",
        key="teacher_att_sub_mode"
    )

    today = date.today()
    if "teacher_att_from_date" not in st.session_state:
        st.session_state.teacher_att_from_date = date(today.year, today.month, 1)
    if "teacher_att_to_date" not in st.session_state:
        st.session_state.teacher_att_to_date = today

    # Date Range Pickers
    col_sd, col_ed = st.columns(2)
    with col_sd:
        picked_start = st.date_input("Start Date", value=st.session_state.teacher_att_from_date, key="teacher_att_start_picker")
        if picked_start != st.session_state.teacher_att_from_date:
            st.session_state.teacher_att_from_date = picked_start
            st.rerun(scope="fragment")
    with col_ed:
        picked_end = st.date_input("End Date", value=st.session_state.teacher_att_to_date, key="teacher_att_end_picker")
        if picked_end != st.session_state.teacher_att_to_date:
            st.session_state.teacher_att_to_date = picked_end
            st.rerun(scope="fragment")

    # Quick Preset Buttons
    col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns(5)
    with col_p1:
        if st.button("📅 Today", width="stretch", key="teacher_att_preset_today"):
            st.session_state.teacher_att_from_date = today
            st.session_state.teacher_att_to_date = today
            st.rerun(scope="fragment")
    with col_p2:
        if st.button("⏪ Yesterday", width="stretch", key="teacher_att_preset_yesterday"):
            st.session_state.teacher_att_from_date = today - timedelta(days=1)
            st.session_state.teacher_att_to_date = today - timedelta(days=1)
            st.rerun(scope="fragment")
    with col_p3:
        if st.button("📅 Current Month", width="stretch", key="teacher_att_preset_month"):
            st.session_state.teacher_att_from_date = date(today.year, today.month, 1)
            st.session_state.teacher_att_to_date = today
            st.rerun(scope="fragment")
    with col_p4:
        if st.button("📅 Last 30 Days", width="stretch", key="teacher_att_preset_30"):
            st.session_state.teacher_att_from_date = today - timedelta(days=30)
            st.session_state.teacher_att_to_date = today
            st.rerun(scope="fragment")
    with col_p5:
        if st.button("🔄 Refresh", width="stretch", key="teacher_att_btn_refresh"):
            st.cache_data.clear()
            st.rerun(scope="fragment")

    from_str = st.session_state.teacher_att_from_date.strftime("%Y-%m-%d")
    to_str = st.session_state.teacher_att_to_date.strftime("%Y-%m-%d")

    # ----------------------------------------------------
    # MODE 1: Detailed Day-Wise Teacher Report
    # ----------------------------------------------------
    if sub_mode == "📅 Detailed Day-Wise Teacher Report":
        all_teachers = list_active_teachers()
        if not all_teachers:
            st.warning("No active teachers found in the system.")
            return

        teacher_map = {str(t["id"]): t for t in all_teachers}
        teacher_display_options = {str(t["id"]): f"{t.get('full_name', t.get('username'))} ({t.get('username')})" for t in all_teachers}

        if "selected_daywise_teacher_id" not in st.session_state or st.session_state.selected_daywise_teacher_id not in teacher_map:
            st.session_state.selected_daywise_teacher_id = str(all_teachers[0]["id"])

        col_t_select, col_t_role = st.columns([3, 1])
        with col_t_select:
            chosen_tid = st.selectbox(
                "👨‍🏫 Select Teacher to View / Edit:",
                options=list(teacher_display_options.keys()),
                index=list(teacher_display_options.keys()).index(st.session_state.selected_daywise_teacher_id),
                format_func=lambda x: teacher_display_options.get(x, x),
                key="daywise_teacher_select_box"
            )
            if chosen_tid != st.session_state.selected_daywise_teacher_id:
                st.session_state.selected_daywise_teacher_id = chosen_tid
                st.rerun(scope="fragment")

        active_teacher_obj = teacher_map[st.session_state.selected_daywise_teacher_id]
        t_name = active_teacher_obj.get("full_name") or active_teacher_obj.get("username", "Teacher")
        t_user = active_teacher_obj.get("username", "")
        t_role = active_teacher_obj.get("role", "teacher").capitalize()

        with col_t_role:
            st.markdown(f"<div style='padding-top: 28px; font-weight: bold; color: var(--emerald);'>Role: <span style='background: rgba(14,107,80,0.1); padding: 4px 10px; border-radius: 6px;'>{t_role}</span></div>", unsafe_allow_html=True)

        with st.spinner(f"Loading day-wise attendance records for {t_name}..."):
            day_records = fetch_teacher_daywise_attendance(
                teacher_id=st.session_state.selected_daywise_teacher_id,
                from_date=from_str,
                to_date=to_str
            )

        if not day_records:
            st.info("No records found for the chosen date range.")
            return

        # Calculate metrics
        total_days = len(day_records)
        present_count = sum(1 for r in day_records if r.get("is_present"))
        absent_count = total_days - present_count
        att_rate = round((present_count / total_days * 100), 1) if total_days > 0 else 0

        # Metrics display
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Total Days (incl. Sundays)", f"{total_days}")
        with m2:
            st.metric("Present Days", f"{present_count} d", delta=f"{att_rate}% Rate", delta_color="normal")
        with m3:
            st.metric("Absent Days", f"{absent_count} d", delta=f"-{absent_count}" if absent_count > 0 else "0", delta_color="inverse")
        with m4:
            st.metric("Teacher Username", f"@{t_user}")

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        tab_log, tab_pdf = st.tabs(["📋 Day-Wise Log & Attendance Override", "📄 PDF Report Preview & Download"])

        with tab_log:
            st.caption("Review day-by-day attendance (including Sundays). Click **✏️ Edit** on any day to change status or adjust login time.")

            # Table Header
            st.markdown(
                """
                <div style="background-color: var(--card); border: 1px solid var(--border); border-radius: 8px 8px 0 0; padding: 10px 14px; font-weight: bold; font-size: 0.88rem; color: var(--emerald);">
                    <div style="display: flex; gap: 10px; align-items: center;">
                        <div style="flex: 0.5; text-align: center;">#</div>
                        <div style="flex: 2.2;">Day</div>
                        <div style="flex: 2.2;">Date</div>
                        <div style="flex: 1.8; text-align: center;">Status</div>
                        <div style="flex: 2.2; text-align: center;">Login / Tasmee Time</div>
                        <div style="flex: 1.5; text-align: center;">Action</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            for idx, r in enumerate(day_records, 1):
                cur_date_str = r["date"]
                day_name = r["day_name"]
                f_date = r["formatted_date"]
                is_sun = r["is_sunday"]
                is_pres = r["is_present"]
                login_time = r["login_time"]

                sun_badge_html = "<span style='background:#fef3c7; color:#92400e; font-size:10px; padding:1px 6px; border-radius:4px; font-weight:bold; margin-left:6px;'>Sunday</span>" if is_sun else ""
                bg_color = "rgba(254, 243, 199, 0.25)" if is_sun else "transparent"

                with st.container():
                    st.markdown(f"<div style='background-color: {bg_color}; border-bottom: 1px solid rgba(184,137,23,0.12); padding: 4px 6px;'>", unsafe_allow_html=True)
                    c_idx, c_day, c_date, c_status, c_time, c_action = st.columns([0.5, 2.2, 2.2, 1.8, 2.2, 1.5])
                    
                    with c_idx:
                        st.markdown(f"<div style='text-align: center; padding-top: 6px; color: gray; font-size: 0.85rem;'>{idx}</div>", unsafe_allow_html=True)
                    with c_day:
                        st.markdown(f"<div style='padding-top: 6px; font-weight: 600; font-size: 0.9rem;'>{day_name} {sun_badge_html}</div>", unsafe_allow_html=True)
                    with c_date:
                        st.markdown(f"<div style='padding-top: 6px; font-size: 0.88rem; color: #4a5568;'>{f_date}</div>", unsafe_allow_html=True)
                    with c_status:
                        if is_pres:
                            st.markdown("<div style='text-align: center; padding-top: 6px;'><span style='background-color: rgba(16, 185, 129, 0.15); color: #10b981; padding: 3px 10px; border-radius: 10px; font-size: 11.5px; font-weight: bold;'>🟢 Present</span></div>", unsafe_allow_html=True)
                        else:
                            st.markdown("<div style='text-align: center; padding-top: 6px;'><span style='background-color: rgba(239, 68, 68, 0.15); color: #ef4444; padding: 3px 10px; border-radius: 10px; font-size: 11.5px; font-weight: bold;'>🔴 Absent</span></div>", unsafe_allow_html=True)
                    with c_time:
                        time_color = "#0E6B50" if is_pres and login_time != "-" else "gray"
                        st.markdown(f"<div style='text-align: center; padding-top: 6px; font-weight: 600; color: {time_color}; font-size: 0.88rem;'>{login_time}</div>", unsafe_allow_html=True)
                    with c_action:
                        with st.popover("✏️ Edit", use_container_width=True):
                            st.markdown(f"**Adjust Attendance: {day_name}, {f_date}**")
                            radio_key = f"rad_status_{cur_date_str}_{st.session_state.selected_daywise_teacher_id}"
                            time_key = f"inp_time_{cur_date_str}_{st.session_state.selected_daywise_teacher_id}"
                            btn_key = f"btn_save_day_{cur_date_str}_{st.session_state.selected_daywise_teacher_id}"

                            new_status_sel = st.radio(
                                "Attendance Status:",
                                options=["Present", "Absent"],
                                index=0 if is_pres else 1,
                                key=radio_key
                            )
                            default_time_input = login_time if login_time not in ("-", "Present") else "08:00 AM"
                            new_time_val = st.text_input(
                                "Login / Tasmee Time:",
                                value=default_time_input,
                                key=time_key,
                                help="Enter time e.g. 08:30 AM, 09:15 AM, 08:00",
                                disabled=(new_status_sel == "Absent")
                            )
                            if st.button("💾 Save Record", type="primary", key=btn_key, use_container_width=True):
                                ok = update_teacher_attendance_day(
                                    teacher_id=st.session_state.selected_daywise_teacher_id,
                                    teacher_name=t_name,
                                    activity_date=cur_date_str,
                                    is_present=(new_status_sel == "Present"),
                                    login_time_str=new_time_val
                                )
                                if ok:
                                    st.toast(f"✅ Marked {new_status_sel} for {f_date}!", icon="💾")
                                    st.rerun(scope="fragment")
                                else:
                                    st.error("Failed to update record. Please try again.")

                    st.markdown("</div>", unsafe_allow_html=True)

        with tab_pdf:
            st.caption("Printable A4 report layout. Use the floating **🖨️ Print / Save as PDF** button inside the preview or the download button below.")
            html_teacher_report = build_teacher_detailed_attendance_html(
                teacher_name=t_name,
                teacher_username=t_user,
                from_date=from_str,
                to_date=to_str,
                records=day_records
            )

            col_down, _ = st.columns([2, 3])
            with col_down:
                st.download_button(
                    label="📥 Download HTML Report",
                    data=html_teacher_report,
                    file_name=f"Teacher_Attendance_{t_user}_{from_str}_{to_str}.html",
                    mime="text/html",
                    width="stretch"
                )

            st.iframe(html_teacher_report, height=750)

    # ----------------------------------------------------
    # MODE 2: All Teachers Summary Overview (Existing)
    # ----------------------------------------------------
    else:
        with st.spinner("Fetching teacher attendance for selected date range..."):
            report_data = fetch_teacher_attendance_report(from_date=from_str, to_date=to_str)

        if not report_data:
            st.info(f"No active teachers found in the system for range {from_str} to {to_str}.")
            return

        # Search / Filters
        col_st, col_ss = st.columns(2)
        with col_st:
            search_teacher = st.text_input("🔍 Search by Teacher Name", placeholder="Type teacher name to filter...", key="filter_teacher_name").strip().lower()
        with col_ss:
            search_student = st.text_input("🔍 Search by Student Handled", placeholder="Type student name to filter...", key="filter_student_name").strip().lower()

        # Filter data
        filtered_data = []
        for t in report_data:
            t_name = (t.get("teacher_name") or "").lower()
            t_user = (t.get("teacher_username") or "").lower()
            students = [s for s in t.get("students_handled", [])]

            if search_teacher and (search_teacher not in t_name and search_teacher not in t_user):
                continue
            if search_student and not any(search_student in s.lower() for s in students):
                continue
            filtered_data.append(t)

        # Aggregate top metrics
        total_teachers = len(report_data)
        is_multi_day = from_str != to_str
        total_working_days = report_data[0].get("total_working_days", 1) if report_data else 1
        
        total_present_days_sum = sum(r.get("present_days", 0) for r in report_data)
        total_absent_days_sum = sum(r.get("absent_days", 0) for r in report_data)
        present_teachers_count = sum(1 for r in report_data if r.get("is_present"))
        
        all_students_handled = set()
        for r in report_data:
            for s in r.get("students_handled", []):
                all_students_handled.add(s)

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Total Teachers", f"{total_teachers}")
        with m2:
            if is_multi_day:
                st.metric("Total Present Days", f"{total_present_days_sum} d", delta=f"{total_working_days} working days in range", delta_color="normal")
            else:
                st.metric("Present Today", f"{present_teachers_count}", delta=f"{present_teachers_count}/{total_teachers}", delta_color="normal")
        with m3:
            if is_multi_day:
                st.metric("Total Absent Days", f"{total_absent_days_sum} d", delta=f"-{total_absent_days_sum}" if total_absent_days_sum > 0 else "0", delta_color="inverse")
            else:
                absent_today = total_teachers - present_teachers_count
                st.metric("Absent Today", f"{absent_today}", delta=f"-{absent_today}" if absent_today > 0 else "0", delta_color="inverse")
        with m4:
            st.metric("Total Students Handled", f"{len(all_students_handled)}")

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        if not filtered_data:
            st.warning("No teachers matched your search criteria.")
            return

        # Table Header
        st.markdown(
            """
            <div style="background-color: var(--card); border: 1px solid var(--border); border-radius: 8px 8px 0 0; padding: 10px 14px; font-weight: bold; font-size: 0.88rem; color: var(--emerald);">
                <div style="display: flex; gap: 12px; align-items: center;">
                    <div style="flex: 2.3; min-width: 140px;">👨‍🏫 Teacher Name</div>
                    <div style="flex: 1.8; text-align: center;">Status (Present / Absent)</div>
                    <div style="flex: 1.4; text-align: center;">First Tasmee Time</div>
                    <div style="flex: 4.5;">Students Handled</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Render Teacher Rows
        for t in filtered_data:
            t_name = t.get("teacher_name", "Unknown")
            t_user = t.get("teacher_username", "")
            is_pres = t.get("is_present", False)
            pres_days = t.get("present_days", 0)
            abs_days = t.get("absent_days", 0)
            first_time = t.get("first_tasmee_at", "-")
            students = sorted(t.get("students_handled", []))

            with st.container():
                c_name, c_status, c_time, c_stud = st.columns([2.3, 1.8, 1.4, 4.5])
                
                with c_name:
                    st.markdown(f"<div style='padding-top: 6px; font-weight: 600; font-size: 0.92rem;'>{t_name} <span style='font-size: 0.78rem; opacity: 0.7; font-weight: normal;'>({t_user})</span></div>", unsafe_allow_html=True)
                    
                with c_status:
                    if not is_multi_day:
                        if is_pres:
                            st.markdown("<div style='text-align: center; padding-top: 6px;'><span style='background-color: rgba(16, 185, 129, 0.15); color: #10b981; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: bold;'>🟢 Present</span></div>", unsafe_allow_html=True)
                        else:
                            st.markdown("<div style='text-align: center; padding-top: 6px;'><span style='background-color: rgba(239, 68, 68, 0.15); color: #ef4444; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: bold;'>🔴 Absent</span></div>", unsafe_allow_html=True)
                    else:
                        st.markdown(
                            f"""
                            <div style='text-align: center; padding-top: 5px; display: flex; gap: 4px; justify-content: center; flex-wrap: wrap;'>
                                <span style='background-color: rgba(16, 185, 129, 0.15); color: #10b981; padding: 3px 8px; border-radius: 8px; font-size: 11px; font-weight: bold;'>🟢 {pres_days} Pres.</span>
                                <span style='background-color: rgba(239, 68, 68, 0.15); color: #ef4444; padding: 3px 8px; border-radius: 8px; font-size: 11px; font-weight: bold;'>🔴 {abs_days} Abs.</span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                with c_time:
                    time_color = "#0E6B50" if is_pres and first_time != "-" else "gray"
                    st.markdown(f"<div style='text-align: center; padding-top: 6px; font-size: 0.88rem; font-weight: 600; color: {time_color};'>{first_time}</div>", unsafe_allow_html=True)
                    
                with c_stud:
                    if students:
                        count_badge = f"<span style='font-weight: bold; color: var(--emerald); font-size: 0.82rem; margin-right: 6px;'>({len(students)}):</span>"
                        badges = "".join([f"<span style='background: rgba(14, 107, 80, 0.08); border: 1px solid rgba(14, 107, 80, 0.25); color: #0E6B50; padding: 3px 9px; border-radius: 6px; font-size: 0.84rem; font-weight: 600; margin-right: 6px; margin-bottom: 4px; display: inline-block;'>{s}</span>" for s in students])
                        st.markdown(f"<div style='padding-top: 4px; display: flex; align-items: center; flex-wrap: wrap;'>{count_badge} {badges}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div style='padding-top: 6px; font-size: 0.84rem; color: gray; font-style: italic;'>None</div>", unsafe_allow_html=True)

                st.markdown("<hr style='margin: 6px 0 8px 0; border: none; border-top: 1px solid rgba(184,137,23,0.15);'/>", unsafe_allow_html=True)


