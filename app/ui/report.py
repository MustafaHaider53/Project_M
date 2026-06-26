from __future__ import annotations

import streamlit as st

from app.db import fetch_monthly_report
from app.report_pdf import build_report_html
from app.ui.shared import back_home_button
from app.ui.student import current_student_badge


def render_report() -> None:
    back_home_button()
    st.subheader("Monthly Report")
    st.caption("Date-wise report with Murajat, Juzulhali, Jadeed, and Takhteet.")
    current_student_badge()

    student_id = st.session_state.get("student_id")
    student_name = st.session_state.get("student_name", "Student")
    if not student_id:
        st.warning("Please select a student on Home first.")
        return

    from datetime import datetime
    now = datetime.now()

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

    with st.spinner("Fetching monthly report data..."):
        rows = fetch_monthly_report(student_id=student_id, year=selected_year, month=selected_month_num)
    if not rows:
        st.info("No report data found.")
        return

    st.markdown("### Report Category Select")
    t1, t2, t3, t4 = st.tabs([
        "👥 Murajat Report",
        "📖 Juzulhali Report",
        "📝 Jadeed Report",
        "📋 Takhteet Report"
    ])
    
    with t1:
        html_murajat = build_report_html(student_name=student_name, rows=rows, report_type="murajat")
        st.iframe(html_murajat, height=700)
        
    with t2:
        html_juzulhali = build_report_html(student_name=student_name, rows=rows, report_type="juzulhali")
        st.iframe(html_juzulhali, height=700)
        
    with t3:
        html_jadeed = build_report_html(student_name=student_name, rows=rows, report_type="jadeed")
        st.iframe(html_jadeed, height=700)
        
    with t4:
        html_takhteet = build_report_html(student_name=student_name, rows=rows, report_type="takhteet")
        st.iframe(html_takhteet, height=700)

