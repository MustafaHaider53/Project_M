from __future__ import annotations

import streamlit as st
import threading
from datetime import datetime
from app.db import get_student_daily_summary, today_iso, fetch_monthly_report
from app.ui.shared import back_home_button
from app.ui.student import current_student_badge
from app.email_utils import generate_progress_html, generate_absence_html, send_daily_report_email, send_monthly_report_email
from app.report_pdf import build_report_html


def render_email_page() -> None:
    back_home_button()
    st.subheader("Email Notifications")
    st.caption("Send today's recitation progress summary, absence warnings, or month-wise reports directly to the student's inbox.")
    current_student_badge()

    student_id = st.session_state.get("student_id")
    student_name = st.session_state.get("student_name", "Student")
    if not student_id:
        st.warning("Please select a student on Home first.")
        return

    # Fetch daily summary to get student's email and details
    today = today_iso()
    with st.spinner("Loading student daily summary..."):
        summary = get_student_daily_summary(student_id=student_id, date_str=today)
    
    # Check if student has email
    email = summary.get("student_email")
    email_display = f"**{email}**" if email else "⚠️ *No Email Registered*"

    # Display Student Info / Settings card
    st.markdown("---")
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown(f"#### Recipient Details")
        st.markdown(f"**Student Name**: {student_name}")
        st.markdown(f"**Email Address**: {email_display}")
    with c2:
        st.markdown("#### Date")
        st.info(f"📅 **{today}**")

    # Select box to toggle between Daily and Monthly email
    st.markdown("---")
    email_mode = st.selectbox(
        "Select Email Dispatch Mode",
        options=["✉️ Send Daily Progress / Absence Report", "📅 Send Monthly Report"],
        index=0
    )

    if email_mode == "✉️ Send Daily Progress / Absence Report":
        # Daily Report Logic
        # Determine status
        t = summary.get("takhteet") or {}
        t_has_hw = bool(t.get("murajat_text_raw", "").strip() or t.get("juzulhali_text_raw", "").strip() or t.get("jadeed_text_raw", "").strip())
        
        has_murajat = bool(summary.get("murajat"))
        has_juzulhali = bool(summary.get("juzulhali"))
        has_jadeed = bool(summary.get("jadeed") or summary.get("no_jadeed"))
        
        has_records = bool(has_murajat or has_juzulhali or has_jadeed or t_has_hw)
        is_absent = not has_records

        # Section 1: Checklist of inputs
        st.markdown("### Today's Activity Checklist")
        cols = st.columns(4)
        with cols[0]:
            st.checkbox("Murajat Recited", value=has_murajat, disabled=True)
        with cols[1]:
            st.checkbox("Juzulhali Recited", value=has_juzulhali, disabled=True)
        with cols[2]:
            st.checkbox("Jadeed Entered", value=has_jadeed, disabled=True)
        with cols[3]:
            st.checkbox("Takhteet (Homework) Saved", value=t_has_hw, disabled=True)

        # Section 2: Email Status Card
        st.markdown("### Email Dispatch Center")
        if is_absent:
            st.error("🚨 **Status: Absent (No Activity Recorded Today)**\nThe student has no recorded activities today. An **Absence Warning Notice** will be sent.")
            email_html = generate_absence_html(summary)
            btn_label = "✉️ Send Absence Warning Notice"
            btn_type = "secondary"
        else:
            st.success("🟩 **Status: Active**\nThe student has recitation activities today. A **Daily Progress Summary** will be sent.")
            email_html = generate_progress_html(summary)
            btn_label = "✉️ Send Daily Progress Report"
            btn_type = "primary"

        # Section 3: Send Action
        if not email:
            st.warning("⚠️ **Cannot send email**: The student does not have an email address in the database. Please add the student's email address to enable notifications.")
            st.button(btn_label, disabled=True, type=btn_type, use_container_width=True)
        else:
            email_secrets = st.secrets.get("email")
            if not email_secrets:
                st.warning("⚠️ **SMTP Configuration missing**: Please add your `[email]` SMTP settings to Streamlit secrets to enable sending.")
                st.button(btn_label, disabled=True, type=btn_type, use_container_width=True)
            else:
                if st.button(btn_label, type=btn_type, use_container_width=True):
                    def _send_bg():
                        success, msg = send_daily_report_email(summary=summary, is_absent=is_absent)
                        if not success:
                            print(f"[SMTP Error] {msg}")
                        else:
                            print(f"[SMTP Success] {msg}")
                    threading.Thread(target=_send_bg, daemon=True).start()
                    st.info(f"✉️ Email dispatch started in the background to {email}. It will send silently without locking the app.")

        # Section 4: HTML Live Preview
        st.markdown("---")
        with st.expander("👁️ View Email Preview", expanded=False):
            st.iframe(email_html, height=450)

    else:
        # Monthly Report Logic
        st.markdown("### Monthly Report Settings")
        now = datetime.now()
        col_y, col_m, col_c = st.columns(3)
        
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
            
        with col_c:
            categories = {
                "Murajat": "murajat",
                "Juzulhali": "juzulhali",
                "Jadeed": "jadeed",
                "Takhteet": "takhteet"
            }
            selected_category_name = st.selectbox("Report Category", options=list(categories.keys()))
            selected_category_val = categories[selected_category_name]

        # Fetch Monthly data
        with st.spinner("Fetching monthly report data..."):
            rows = fetch_monthly_report(student_id=student_id, year=selected_year, month=selected_month_num)
        
        if not rows:
            st.info("No report data found for this month.")
        else:
            # Build report HTML body and strip print button
            email_html = build_report_html(student_name=student_name, rows=rows, report_type=selected_category_val)
            email_html = email_html.replace('<button class="print-btn" onclick="window.print()">🖨️ Print / Save as PDF</button>', '')

            st.markdown("### Email Dispatch Center")
            btn_label = f"✉️ Send Monthly {selected_category_name} Report"
            btn_type = "primary"

            # Send action
            if not email:
                st.warning("⚠️ **Cannot send email**: The student does not have an email address in the database.")
                st.button(btn_label, disabled=True, type=btn_type, use_container_width=True)
            else:
                email_secrets = st.secrets.get("email")
                if not email_secrets:
                    st.warning("⚠️ **SMTP Configuration missing**: Please add your `[email]` SMTP settings to Streamlit secrets.")
                    st.button(btn_label, disabled=True, type=btn_type, use_container_width=True)
                else:
                    if st.button(btn_label, type=btn_type, use_container_width=True):
                        def _send_monthly_bg():
                            success, msg = send_monthly_report_email(
                                student_name=student_name,
                                recipient_email=email,
                                rows=rows,
                                report_type=selected_category_val,
                                year=selected_year,
                                month=selected_month_num
                            )
                            if not success:
                                print(f"[SMTP Error] {msg}")
                            else:
                                print(f"[SMTP Success] {msg}")
                        threading.Thread(target=_send_monthly_bg, daemon=True).start()
                        st.info(f"✉️ Monthly {selected_category_name} report dispatch started in the background to {email}.")

            # HTML Live Preview
            st.markdown("---")
            with st.expander("👁️ View Monthly Email Preview", expanded=False):
                st.iframe(email_html, height=450)
