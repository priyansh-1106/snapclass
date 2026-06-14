import streamlit as st
import numpy as np
from datetime import datetime
import pandas as pd
from src.ui.base_style import style_base_layout, style_background_dashboard
from src.components.header import header_dashboard
from src.database.db import login_teacher, create_teacher, check_teacher_exists, get_teacher_subjects, get_attendance_for_teacher
from src.components.dailog_create_subject import create_subject_dailog
from src.components.subject_card import subject_card
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dailog_add_photo import add_photos_dialog
from src.pipelines.face_pipeline import predict_attendance
from src.database.config import supabase
from src.components.dialog_attendance_result import attendance_result_dialog    
from src.components.dialog_voice_attendance import voice_attendance_dialog  

def teacher_screen():
    style_background_dashboard()
    style_base_layout()

    if "teacher_data" in st.session_state:
        teacher_dashboard()
    elif "teacher_login" not in st.session_state or st.session_state.teacher_login == "login":
        teacher_login()
    else:
        teacher_register()


def teacher_dashboard():
    teacher_data = st.session_state.teacher_data
    c1, c2 = st.columns([4,4], gap="xxsmall", vertical_alignment="center")

    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"Welcome, {teacher_data['name']}!", text_alignment="center")
        if st.button("Logout", type = "secondary", shortcut="control + backspace", key="loginout", width="stretch"):
            st.session_state['is_logged_in'] = False
            del st.session_state.teacher_data
            st.rerun()
    
    st.space()

    tab1, tab2, tab3 = st.columns(3, gap = 'xxsmall')
    if 'current_teacher_tab' not in st.session_state:
        st.session_state.current_teacher_tab = 'take_attendance'

    with tab1:
        type1 = 'primary' if st.session_state.current_teacher_tab == 'take_attendance' else 'tertiary'
        if st.button("Take Attendance", icon = ':material/ar_on_you:', width = 'stretch', type=type1):
            st.session_state.current_teacher_tab = 'take_attendance'
            st.rerun()

    with tab2:
        type2 = 'primary' if st.session_state.current_teacher_tab == 'manage_subjects' else 'tertiary'
        if st.button("Manage Subjects", icon = ':material/book_ribbon:', width = 'stretch', type=type2):
            st.session_state.current_teacher_tab = 'manage_subjects'
            st.rerun()

    with tab3:
        type3 = 'primary' if st.session_state.current_teacher_tab == 'attendance_records' else 'tertiary'
        if st.button("Attendance Records", icon = ':material/cards_stack:', width = 'stretch', type=type3):
            st.session_state.current_teacher_tab = 'attendance_records'
            st.rerun()
    st.divider()

    if st.session_state.current_teacher_tab == 'take_attendance':
        teacher_tab_take_attendance()
    if st.session_state.current_teacher_tab == 'manage_subjects':
        teacher_tab_manage_subjects()
    if st.session_state.current_teacher_tab == 'attendance_records':
        teacher_tab_attendance_records()

def teacher_tab_take_attendance():
    teacher_id = st.session_state.teacher_data['teacher_id']
    st.header("Take AI Attendance")

    if 'attendance_image' not in st.session_state:
        st.session_state.attendance_image = []

    subjects = get_teacher_subjects(teacher_id)
    if not subjects:
        st.warning("No subjects found. Please create a subject first.")
        return 
    
    subject_options = {f"{sub['name']} - {sub['subject_code']}": sub['subject_id'] for sub in subjects}

    col1, col2 = st.columns([6,3], gap="xxsmall")
    with col1:
        selected_subject_label = st.selectbox("Select Subject", options=list(subject_options.keys()))

    with col2:
        if st.button("Upload Image", type = "primary", icon = ":material/photo_prints:", width = "stretch"):
            add_photos_dialog()

    selected_subject_id = subject_options[selected_subject_label]

    if st.session_state.attendance_image:
        st.header("Added Photos")
        cols = st.columns(4, gap="xsmall")
        for idx, img in enumerate(st.session_state.attendance_image):
            with cols[idx % 4]:
                st.image(img, width='stretch', caption=f"Photo {idx+1}")
        
        c1, c2, c3 = st.columns(3, gap="xxsmall")
        has_photos = bool(st.session_state.attendance_image)

        with c1:
            if st.button("Clear Photos", type="tertiary", icon = ":material/delete_forever:", width="stretch", disabled=not has_photos):
                st.session_state.attendance_image = []
                st.rerun()
        with c2:
            if st.button("Run Face Analysis", type="primary", icon = ":material/analytics:", width="stretch", disabled=not has_photos):
                with st.spinner("Analyzing photos..."):
                    all_detected_id = {}
                    for idx, img in enumerate(st.session_state.attendance_image):
                        img_np = np.array(img.convert('RGB'))
                        detected, _, _ = predict_attendance(img_np)
                        if detected:
                            for sid in detected.keys():
                                student_id = int(sid)
                                all_detected_id.setdefault(student_id, []).append(f"Photo {idx+1}")
                    enrolled_res = supabase.table("subject_students").select("*", "students(*)").eq("subject_id", selected_subject_id).execute()
                    enrolled_students = enrolled_res.data
                    if not enrolled_students:
                        st.warning("No students enrolled in this course.")
                    else:
                        results, attendance_to_log = [], []
                        current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                        for node in enrolled_students:
                            student = node['students']
                            sources = all_detected_id.get(student["student_id"], [])
                            is_present = len(sources) > 0

                            results.append({
                                'Name' : student['name'],
                                'ID' : student['student_id'],
                                'Sources' : ", ".join(sources) if sources else "-",
                                'Status' : "✅Present" if is_present else "❌Absent"
                            })

                            attendance_to_log.append({
                                "student_id": student['student_id'],
                                "subject_id": selected_subject_id,
                                "timestamp": current_timestamp,
                                "is_present": bool(is_present)
                            })
                            attendance_result_dialog(pd.DataFrame(results), attendance_to_log)



        with c3:
            if st.button("AI Voice Attendance", type="secondary", icon = ":material/camera_rear:", width="stretch"):
                voice_attendance_dialog(selected_subject_id)
        
        

def teacher_tab_manage_subjects():
    teacher_id = st.session_state.teacher_data['teacher_id']
    col1, col2 = st.columns(2, gap="xxsmall")
    with col1:
        st.header("Manage Subjects", width = 'stretch')
    with col2:
        if st.button('Create new subject', width = 'stretch'):
            create_subject_dailog(st.session_state.teacher_data['teacher_id'])
    
    subjects = get_teacher_subjects(teacher_id)
    if subjects:
        for sub in subjects:
            stats = [
                ("👥", "Students", sub['total_students']),
                ("🕰️", "Classes", sub['total_classes'])
            ]
            def share_btn():
                if st.button(f"Share Code : {sub['name']}", key = f"share_{sub['subject_code']}", icon = ':material/share:'):
                    share_subject_dialog(sub['name'], sub['subject_code'])
                st.space()
            
            subject_card(
                name = sub['name'],
                code = sub['subject_code'],
                section = sub['section'],
                stats = stats,
                footer_callback = share_btn
            )
    else:
        st.info("NO SUBJECTS FOUND. CREATE ONE ABOVE!")




def teacher_tab_attendance_records():
    st.header("Attendance Records")
    teacher_id = st.session_state.teacher_data['teacher_id']
    records = get_attendance_for_teacher(teacher_id)
    if not records:
        return
    data = []
    for rec in records:
        ts = rec.get('timestamp')

        data.append({
            "ts_group" : ts.split(".")[0] if ts else None,
            "Time" : datetime.fromisoformat(ts).strftime("%Y-%m-%d %I:%M %p") if ts else 'N/A',
            "Subject" : rec['subjects']['name'],
            "Subject Code" : rec['subjects']['subject_code'],
            "is_present" : bool(rec.get("is_present", False))
        })

    df = pd.DataFrame(data)

    summary = (
        df.groupby(['ts_group', 'Time', 'Subject', 'Subject Code'])
        .agg(
            Present_Count = ('is_present', 'sum'),
            Total_Count = ('is_present', 'count')
        ).reset_index()
    )

    summary['Attendance Stats'] = (
        "✅" + summary['Present_Count'].astype(str) + '/' + summary['Total_Count'].astype(str) + "Students"
    )

    display_df = (summary.sort_values(by='ts_group', ascending = False)
                  [['Time', 'Subject', 'Subject Code', 'Attendance Stats']])

    st.dataframe(display_df, width = 'stretch', hide_index = True)




def register_teacher(username, name, password, confirm_password):
    if not username or not name or not password or not confirm_password:
        return False, "All fields are required."
    if password != confirm_password:
        return False, "Passwords do not match."
    if check_teacher_exists(username):
        return False, "Username already exists."
    try:
        create_teacher(username, name, password)
        return True, "Teacher registered successfully."
    except Exception as e:
        return False, "Unexpected error occurred."
    
def verify_teacher_login(username, password):
    if not username or not password:
        return False, "Both fields are required."
    teacher = login_teacher(username, password)
    if teacher:
        st.session_state.teacher_data = teacher
        st.session_state.user_role = "teacher"
        st.session_state.is_logged_in = True
        return True, "Login successful."
    else:
        return False, "Invalid username or password."

def teacher_register(): 
    c1, c2 = st.columns([4,4], gap="xxsmall", vertical_alignment="center")

    with c1:
        header_dashboard()
    with c2:
        if st.button("Go to homepage", type = "secondary", shortcut="control + backspace", key="loginbckbtn", width="stretch"):
            st.session_state['login_type'] = None
            st.rerun()
    st.header("Register your teacher profile", text_alignment="center")
    st.space()
    teacher_username = st.text_input("Enter username", placeholder="@john")
    teacher_name = st.text_input("Enter your name", placeholder="John Snow")
    teacher_password = st.text_input("Enter password", placeholder="Enter your password", type='password')
    teacher_confirm_password = st.text_input("Enter password", placeholder="Confirm your password", type='password')
    st.divider()
    cl1, cl2 = st.columns(2)
    with cl1:
        if st.button("Register Now", type='primary', icon=":material/passkey:", width="stretch", shortcut="control + enter"):
            success, message = register_teacher(teacher_username, teacher_name, teacher_password, teacher_confirm_password)
            if success:
                st.success(message)
                import time
                time.sleep(2)
                st.session_state.teacher_login = "login"
                st.rerun()
            else:
                st.error(message)
    
    with cl2:
        if st.button("Login Instead", type="secondary", icon=":material/passkey:",width="stretch"):
            st.session_state.teacher_login = "login"
            st.rerun()


def teacher_login(): 
    c1, c2 = st.columns([4,4], gap="xxsmall", vertical_alignment="center")

    with c1:
        header_dashboard()
    with c2:
        if st.button("Go to homepage", type = "secondary", shortcut="control + backspace", key="loginbckbtn", width="stretch"):
            st.session_state['login_type'] = None
            st.rerun()
    st.header("Login using password", text_alignment="center")
    st.space()
    teacher_username = st.text_input("Enter username", placeholder="@john")
    teacher_password = st.text_input("Enter password", placeholder="Enter your password", type='password')
    st.divider()
    cl1, cl2 = st.columns(2, gap='xxsmall')
    with cl1:
        if st.button("Login", type="secondary", icon=":material/passkey:", shortcut="control + enter", key="loginbtn", width="stretch"):
            success, message = verify_teacher_login(teacher_username, teacher_password)
            if success:
                st.toast("Welcome back", icon = "👋")
                import time
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid username or password.")
    
    with cl2:
        if st.button("Register Instead", type='primary', icon=":material/passkey:", width="stretch"):
            st.session_state.teacher_login = "register"
            st.rerun()