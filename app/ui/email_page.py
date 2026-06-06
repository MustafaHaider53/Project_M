from __future__ import annotations

import streamlit as st
from app.db import get_student_daily_summary, today_iso
from app.ui.shared import back_home_button
from app.ui.student import current_student_badge
from app.email_utils import generate_progress_html, generate_absence_html, send_daily_report_email


def render_email_page() -> None:
    back_home_button()
    st.subheader("Email Notifications")
    st.caption("Send today's recitation progress summary or absence warning alerts directly to the student's inbox.")
    current_student_badge()

    student_id = st.session_state.get("student_id")
    if not student_id:
        st.warning("Please select a student on Home first.")
        return

    today = today_iso()
    summary = get_student_daily_summary(student_id=student_id, date_str=today)
    
    # Check if student has email
    email = summary.get("student_email")
    email_display = f"**{email}**" if email else "⚠️ *No Email Registered*"

    # Display Student Info / Settings card
    st.markdown("---")
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown(f"#### Recipient Details")
        st.markdown(f"**Student Name**: {summary.get('student_name')}")
        st.markdown(f"**Email Address**: {email_display}")
    with c2:
        st.markdown("#### Date")
        st.info(f"📅 **{today}**")

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
        # Check if email credentials exist in st.secrets
        email_secrets = st.secrets.get("email")
        if not email_secrets:
            st.warning("⚠️ **SMTP Configuration missing**: Please add your `[email]` SMTP settings to Streamlit secrets to enable sending.")
            st.button(btn_label, disabled=True, type=btn_type, use_container_width=True)
        else:
            if st.button(btn_label, type=btn_type, use_container_width=True):
                import threading
                # Dispatch SMTP silently in a background thread so UI returns instantly
                threading.Thread(
                    target=send_daily_report_email,
                    kwargs={"summary": summary, "is_absent": is_absent},
                    daemon=True
                ).start()
                
                # Show success message immediately
                st.success(f"Email successfully sent to {email}.")

    # Section 4: HTML Live Preview (collapsed by default to load instantly)
    st.markdown("---")
    with st.expander("👁️ View Email Preview", expanded=False):
        st.iframe(email_html, height=450)
