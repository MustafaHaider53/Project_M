from __future__ import annotations

import streamlit as st

from app.db import create_student, list_students


def require_student() -> str | None:
    """
    Renders the student selector + add form.
    Returns selected student_id or None if not selected yet.
    """
    st.markdown("### Student")

    students = list_students()
    options = [(s["id"], s["full_name"]) for s in students]

    if options:
        selected = st.selectbox(
            "Select student",
            options=options,
            format_func=lambda x: x[1],
            key="selected_student_option",
        )
        st.session_state.student_id = selected[0]
        st.session_state.student_name = selected[1]
    else:
        st.info("No students yet. Add the first student below.")

    with st.expander("Add new student", expanded=not bool(options)):
        name = st.text_input("Full name", key="new_student_name")
        if st.button("Add student", type="primary"):
            s = create_student(full_name=name)
            st.session_state.student_id = s["id"]
            st.session_state.student_name = s["full_name"]
            st.success(f"Added: {s['full_name']}")
            st.rerun()

    return st.session_state.get("student_id")


def current_student_badge() -> None:
    name = st.session_state.get("student_name")
    if name:
        st.markdown(f"**Selected student:** {name}")

