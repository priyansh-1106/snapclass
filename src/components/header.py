import streamlit as st

logo_image = "https://i.ibb.co/YTYGn5qV/logo.png"

def header():
    st.markdown(f"""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; margin-bottom: 30px; margin-top: 30px;">
        <img src="{logo_image}" alt="Logo" style="height: 100px;">
        <h1 style = "text-align: center; color: #E0E3FF">SNAP<br>CLASS</h1>
    </div>
    """, unsafe_allow_html=True)



def header_dashboard():
    st.markdown(f"""
    <div style="display: flex; justify-content: center; align-items: center; gap: 10px;">
        <img src="{logo_image}" alt="Logo" style="height: 80px;">
        <h2 style = "text-align: left; color: black; margin-top : 27px;">SNAP<br>CLASS</h2>
    </div>
    """, unsafe_allow_html=True)