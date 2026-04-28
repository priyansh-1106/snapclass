import numpy as np
import streamlit as st
from PIL import Image
from src.ui.base_style import style_base_layout, style_background_dashboard
from src.components.header import header_dashboard
from src.database.db import login_teacher, create_teacher, check_teacher_exists


def student_screen():
    style_background_dashboard()
    style_base_layout()

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
    photo = st.camera_input("Position your face in centre")
    if photo:
        np.array(Image.open(photo))
