import streamlit as st

from src.screens.teacher_screen import teacher_screen
from src.screens.home_screen import home_screen
from src.screens.student_screen import student_screen
from src.ui.base_style import style_base_layout, style_background_home
from src.components.header import header

def main():
    style_base_layout()
    style_background_home()
    
    if "login_type" not in st.session_state:
        st.session_state.login_type = None

    match st.session_state.login_type:
        case "teacher":
            teacher_screen()
        case "student":
            student_screen()
        case _:
            home_screen()


main()