import streamlit as st 
from src.database.db import create_attendance
from src.database.config import supabase
import time

def show_attendance_result(df, logs):
    st.write("Please review the attendance before confirming:")
    st.dataframe(df, hide_index=True, width = 'stretch')

    c1, c2 = st.columns(2, gap="small")
    with c1:
        if st.button("Discard", type="secondary", width="stretch", icon = ":material/delete:"):
            st.session_state.attendance_image = []
            st.session_state.voice_attendance_result = None
            st.toast("Attendance discarded.")
            st.rerun()
      
    with c2:
        if st.button("Confirm & Save", type="primary", width="stretch", icon = ":material/save:"):
            try:
                create_attendance(logs)
                st.toast("Attendance logged successfully!")
                st.session_state.attendance_image = []
                st.session_state.voice_attendance_result = None
                st.rerun()
            except Exception as e:
                st.error("Attendace Sync Failed. Please try again.")

@st.dialog("Attendance Results")
def attendance_result_dialog(df, logs):
    show_attendance_result(df, logs)