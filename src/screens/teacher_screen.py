import streamlit as st

from src.ui.base_style import style_base_layout, style_background_dashboard
from src.components.header import header_dashboard
from src.database.db import login_teacher, create_teacher, check_teacher_exists

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
    st.header(f"Welcome, {teacher_data['name']}!", text_alignment="center")




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