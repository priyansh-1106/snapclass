import streamlit as st 
from src.database.db import enroll_student_to_subject
from src.database.config import supabase
import time

@st.dialog("Quick Enrollment")
def auto_enroll_dialog(join_code):

    student_id = st.session_state.student_data['student_id']

    res = supabase.table("subjects").select("subject_id, name").eq("subject_code", join_code).execute()

    if not res.data:
        st.error("Invalid subject code.")
        if st.button("Close", type="primary", width="stretch"):
            st.query_params.clear()
            st.rerun()
        return
    
    subject = res.data[0]
    check = supabase.table("subject_students").select("*").eq("student_id", student_id).eq("subject_id", subject['subject_id']).execute()
    if check.data:
        st.info(f"You are already enrolled in {subject['name']}.")
        if st.button("Got it!", type="primary", width="stretch"):
            st.query_params.clear()
            st.rerun()
        return

    st.markdown(f"Do you want to enroll in **{subject['name']}**?")
    col1, col2 = st.columns(2, gap="small")

    with col1:
        if st.button("No Thanks", width="stretch", type="secondary"):
            st.query_params.clear()
            st.rerun()
    with col2:
        if st.button("Enroll Me!", type="primary", width="stretch"):
            enroll_student_to_subject(student_id, subject['subject_id'])
            st.success(f"Joined successfully!")
            st.query_params.clear()
            time.sleep(1)
            st.rerun()
