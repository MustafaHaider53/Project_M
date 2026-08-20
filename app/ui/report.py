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

    def get_cached_ummul_banin_report():
        if st.session_state.get("ummul_banin_report_cache") is None:
            with st.spinner("Fetching Ummul Banin report data..."):
                try:
                    from app.db import fetch_ummul_banin_report_data
                    data = fetch_ummul_banin_report_data()
                except Exception as e:
                    st.error(f"Error fetching Ummul Banin report: {e}")
                    data = None
                st.session_state.ummul_banin_report_cache = data
        return st.session_state.ummul_banin_report_cache

    st.markdown("### Report Category Select")
    categories = [
        "👥 Murajat Report",
        "📖 Juzulhali Report",
        "📝 Jadeed Report",
        "📋 Takhteet Report",
        "🌟 Current Jadeed",
        "📊 Mistake Analytics",
        "📅 Class Attendance",
        "📖 Ummul Banin Ben Report",
        "🎓 OPR - One Page Report",
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
    from app.db import get_daily_email_status
    
    st.markdown("### ✉️ Daily Email Dispatch Status")
    st.caption("Track which students have received their daily recitation progress or absence emails today.")

    # Select Date
    col_date, _ = st.columns([2, 2])
    with col_date:
        selected_date = st.date_input(
            "Select Date:",
            value=date.today(),
            key="email_log_date_input"
        )
        
    date_str = selected_date.isoformat()
    
    with st.spinner("Fetching email status..."):
        logs = get_daily_email_status(date_str)
        
    if not logs:
        st.info("No students found in the database.")
        return

    # Count statistics
    total = len(logs)
    sent_count = sum(1 for l in logs if l["sent"])
    not_sent_count = total - sent_count
    
    # Render premium summary cards
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    col_stats = st.columns(3)
    with col_stats[0]:
        st.markdown(
            f"""
            <div style='background-color: var(--card); border: 1.5px solid var(--border); padding: 15px; border-radius: 8px; text-align: center;'>
                <div style='font-size: 0.85rem; color: var(--ink); opacity: 0.7; font-weight: 500;'>Total Students</div>
                <div style='font-size: 1.8rem; font-weight: bold; color: var(--ink); margin-top: 5px;'>{total}</div>
            </div>
            """.replace("\n", " "),
            unsafe_allow_html=True
        )
    with col_stats[1]:
        st.markdown(
            f"""
            <div style='background-color: rgba(16, 185, 129, 0.08); border: 1.5px solid #10b981; padding: 15px; border-radius: 8px; text-align: center;'>
                <div style='font-size: 0.85rem; color: #0f766e; font-weight: 500;'>Sent Successfully</div>
                <div style='font-size: 1.8rem; font-weight: bold; color: #0f766e; margin-top: 5px;'>🟢 {sent_count}</div>
            </div>
            """.replace("\n", " "),
            unsafe_allow_html=True
        )
    with col_stats[2]:
        st.markdown(
            f"""
            <div style='background-color: rgba(239, 68, 68, 0.08); border: 1.5px solid #ef4444; padding: 15px; border-radius: 8px; text-align: center;'>
                <div style='font-size: 0.85rem; color: #b91c1c; font-weight: 500;'>Not Sent</div>
                <div style='font-size: 1.8rem; font-weight: bold; color: #b91c1c; margin-top: 5px;'>🔴 {not_sent_count}</div>
            </div>
            """.replace("\n", " "),
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    
    # Search / filter
    search_query = st.text_input("🔍 Search Student:", value="", key="email_log_search")
    
    filtered_logs = logs
    if search_query.strip():
        q = search_query.strip().lower()
        filtered_logs = [l for l in logs if q in l["student_name"].lower()]

    # Construct HTML Table
    header_html = """
    <th style="padding: 12px; font-weight: bold; text-align: left; background-color: #F7EFD8; border-bottom: 2px solid var(--border);">👤 Student Name</th>
    <th style="padding: 12px; font-weight: bold; text-align: left; background-color: #F7EFD8; border-bottom: 2px solid var(--border);">✉️ Email Address</th>
    <th style="padding: 12px; font-weight: bold; text-align: center; background-color: #F7EFD8; border-bottom: 2px solid var(--border);">🚦 Status</th>
    """
    
    rows_html = ""
    for l in filtered_logs:
        name = l["student_name"]
        email = l["student_email"]
        sent = l["sent"]
        
        # Format status indicator
        if sent:
            status_html = '<span style="background-color: rgba(16, 185, 129, 0.15); color: #10b981; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: bold;">🟢 Sent</span>'
        else:
            status_html = '<span style="background-color: rgba(239, 68, 68, 0.15); color: #ef4444; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: bold;">🔴 Not Sent</span>'
            
        rows_html += f"""
        <tr style="border-bottom: 1px solid var(--border); font-size: 0.88rem;">
            <td style="padding: 12px; font-weight: 600;">{name}</td>
            <td style="padding: 12px; opacity: 0.85;">{email}</td>
            <td style="padding: 12px; text-align: center;">{status_html}</td>
        </tr>
        """
        
    if not filtered_logs:
        rows_html = f"""
        <tr>
            <td colspan="3" style="padding: 20px; text-align: center; font-style: italic; color: var(--ink); opacity: 0.6;">
                No students found matching your search.
            </td>
        </tr>
        """
        
    table_html = f"""
    <div style="overflow: auto; border: 1px solid var(--border); border-radius: 8px; background-color: var(--card);">
      <table style="width: 100%; border-collapse: collapse; text-align: left; font-family: system-ui, -apple-system, sans-serif; line-height: 1.4;">
        <thead>
          <tr style="background-color: var(--card);">
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
