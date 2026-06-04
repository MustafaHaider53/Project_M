from __future__ import annotations

import streamlit as st

from app.db import create_student, list_students


def require_student() -> str | None:
    """
    Renders the student selector + add form.
    Returns selected student_id or None if not selected yet.
    """
    st.markdown("### Student Selection")

    if "student_success_msg" in st.session_state and st.session_state.student_success_msg:
        st.success(st.session_state.student_success_msg)
        st.session_state.student_success_msg = None

    students = list_students()
    options = [(s["id"], s["full_name"]) for s in students]

    if options:
        formatted_options = [("", "Select a student...")] + options
        
        default_index = 0
        current_id = st.session_state.get("student_id")
        if current_id:
            for idx, opt in enumerate(formatted_options):
                if opt[0] == current_id:
                    default_index = idx
                    break
                    
        selected = st.selectbox(
            "Select student",
            options=formatted_options,
            format_func=lambda x: x[1],
            index=default_index,
            key="selected_student_option_raw",
        )
        if selected[0]:
            if st.session_state.get("student_id") != selected[0]:
                st.session_state.student_id = selected[0]
                st.session_state.student_name = selected[1]
                st.rerun()
        else:
            if st.session_state.get("student_id") is not None:
                st.session_state.student_id = None
                st.session_state.student_name = None
                st.rerun()
    else:
        st.info("No students yet. Add the first student below.")

    with st.expander("Add new student", expanded=not bool(options)):
        name = st.text_input("Full name", key="new_student_name")
        if st.button("Add student", type="primary"):
            if name.strip():
                s = create_student(full_name=name.strip())
                st.session_state.student_id = s["id"]
                st.session_state.student_name = s["full_name"]
                st.session_state.student_success_msg = f"🎉 Successfully added student: {s['full_name']}!"
                st.rerun()
            else:
                st.error("Please enter a valid name.")

    return st.session_state.get("student_id")


def current_student_badge(force: bool = False) -> None:
    if not force:
        return
    name = st.session_state.get("student_name")
    if name:
        st.markdown(
            f"""
            <div style="background-color: var(--card); border: 1.5px solid var(--border); border-radius: 14px; padding: 12px; margin-bottom: 20px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.02);">
                <span style="color: var(--ink); font-size: 11pt; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px;">Active Student Profile:</span>
                <span style="color: var(--emerald); font-size: 18pt; font-weight: 800; margin-left: 10px;">{name}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

