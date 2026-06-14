import streamlit as st 
from PIL import Image

@st.dialog("Capture or upload photos")
def add_photos_dialog():
    st.write("Capture or upload photos for attendance:")

    if 'photo_tab' not in st.session_state:
        st.session_state.photo_tab = 'capture'
    
    tab1, tab2 = st.columns(2, gap = 'small')
    
    with tab1:
        type_capture = 'primary' if st.session_state.photo_tab == 'capture' else 'tertiary'
        if st.button("Capture Photo", icon = ':material/photo_camera:', width = 'stretch', type=type_capture):
            st.session_state.photo_tab = 'capture'
    with tab2:
        type_upload = 'primary' if st.session_state.photo_tab == 'upload' else 'tertiary'
        if st.button("Upload Photo", icon = ':material/photo_library:', width = 'stretch', type=type_upload):
            st.session_state.photo_tab = 'upload'
        
    st.divider()

    if st.session_state.photo_tab == 'capture':
        snapshot = st.camera_input("Take a photo", key="dialog_cam")
        if snapshot:
            st.session_state.attendance_image.append(Image.open(snapshot))
            st.toast("Photo captured successfully!")
            st.rerun()

    if st.session_state.photo_tab == 'upload':
        uploaded_files = st.file_uploader("Upload photos", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'], key="dialog_upload")
        if uploaded_files:
            for uploaded_file in uploaded_files:
                st.session_state.attendance_image.append(Image.open(uploaded_file))
            st.toast("Photos uploaded successfully!")
            st.rerun()

    st.divider()
    if st.button("Done", type="primary", width="stretch"):
        st.rerun()

    