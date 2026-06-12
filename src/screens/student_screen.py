import numpy as np
import time
import streamlit as st
from PIL import Image
from src.ui.base_style import style_base_layout, style_background_dashboard
from src.components.header import header_dashboard
from src.database.db import create_student, get_all_students, get_student_subjects, get_student_attendance, enroll_student_to_subject, unenroll_student_to_subject
from src.pipelines.face_pipeline import predict_attendance, get_face_embeddings, trained_classifier
from src.pipelines.voice_pipeline import get_voice_embedding
from src.components.dialog_enroll import enroll_dialog
from src.components.subject_card import subject_card


def student_dashboard():
    student_data = st.session_state.student_data
    c1, c2 = st.columns([4,4], gap="xxsmall", vertical_alignment="center")

    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"Welcome, {student_data['name']}!", text_alignment="center")
        if st.button("Logout", type = "secondary", shortcut="control + backspace", key="loginout", width="stretch"):
            st.session_state['is_logged_in'] = False
            del st.session_state.student_data
            st.rerun()
    
    st.space()

    c1, c2 = st.columns(2, gap="xxsmall", vertical_alignment="center")
    with c1:
        st.header("Enrolled subjects")
    with c2:
        if st.button("Enroll in new subject", type = "primary", width="stretch"):
            enroll_dialog()
    st.divider()

    with st.spinner("Loading your subjects..."):
        subject = get_student_subjects(student_data['student_id'])
        logs = get_student_attendance(student_data['student_id'])

    stat_map = {}
    for log in logs:
        sid = log['subject_id']
        if sid not in stat_map:
            stat_map[sid] = {
                "total": 0,
                "attended": 0
            }
        stat_map[sid]['total'] += 1

        if log.get("is_present"):
            stat_map[sid]['attended'] += 1

    cols = st.columns(2)        

    for i, sub_node in enumerate(subject):
        sub = sub_node['subjects']
        sid = sub['subject_id']
        stats = stat_map.get(sid, {"total": 0, "attended": 0})

        def unenroll_btn():
            if st.button("Unenroll from this Course", type="tertiary", width="stretch", icon = ":material/delete_forever:", key=f"unenroll_{sid}"):
                unenroll_student_to_subject(student_data['student_id'], sid)
                st.toast(f"Unenrolled from {sub['name']} successfully!")
                st.rerun()

        with cols[i % 2]:
            subject_card(
                name = sub['name'],
                code = sub['subject_code'],
                section = sub['section'],
                stats = {
                    ("📅", "Total", stats['total']),
                    ("✅", "Attended", stats['attended'])
                },
                footer_callback = unenroll_btn
            )
        




def student_screen():
    style_background_dashboard()
    style_base_layout()

    if 'student_data' in st.session_state:
        student_dashboard()
        return

    c1, c2 = st.columns([4,4], gap="xxsmall", vertical_alignment="center")
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go to homepage", type = "secondary", shortcut="control + backspace", key="loginbckbtn", width="stretch"):
            st.session_state['login_type'] = None
            st.rerun()

    st.header("Login using Face Recognition", text_alignment="center")
    st.space()
    st.space()
    show_registration = False
    photo = st.camera_input("Position your face in centre")
    if photo:
        img = np.array(Image.open(photo))

        with st.spinner("Processing..."):
            detected, all_ids, num_faces = predict_attendance(img)

            if num_faces == 0:
                st.warning("No face detected") 
            elif num_faces > 1:
                st.warning("Multiple faces detected")
            else:
                if detected:
                    student_id = list(detected.keys())[0]
                    all_students = get_all_students()
                    student = next((s for s in all_students if s['student_id'] == student_id), None)
                    if student:
                        st.session_state.is_logged_in = True
                        st.session_state.user_role = 'student'
                        st.session_state.student_data =  student
                        st.toast(f"Welcome Back! {student['name']}!")
                        time.sleep(1)
                        st.rerun()
    
                else:
                    show_registration = True

        
    if show_registration:
        with st.container(border = True):
            st.header("Register new profile")
            name = st.text_input("Enter your name : ", placeholder="E.g. Virat Kohli")
            st.subheader("Optional : Voice Enrollment")
            st.info("Enroll your for voice only attendance")
            try:
                audio_data = st.audio_input("Record a short phrase like Hello, this is Pranjal and I am present...")
            except Exception as e:
                st.error("Audio input failed!")
            
            if st.button("Register", type = "primary", key="registerbtn", width="stretch"):
                if name:
                    with st.spinner("Registering..."):
                        img = np.array(Image.open(photo))
                        encoding = get_face_embeddings(img)
                        if encoding:
                            face_embedding = encoding[0].tolist()

                            voice_emb = None
                            if audio_data:
                                voice_emb = get_voice_embedding(audio_data.read())

                            response_data = create_student(name, face_embedding, voice_emb)
                            if response_data:
                                trained_classifier()
                                st.session_state.is_logged_in = True
                                st.session_state.user_role = 'student'
                                st.session_state.student_data =  response_data[0]
                                st.toast(f'Profile created! Hi {name}!')
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.error("Face encoding failed. Please try again with a clearer photo.")

                        
                else:
                    st.error("Please enter your name")