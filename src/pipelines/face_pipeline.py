import dlib
import numpy as np
import face_recognition_models
import streamlit as st
from sklearn.svm import SVC
from src.database.db import get_all_students


@st.cache_resource
def load_dlib_models():
    detector = dlib.get_frontal_face_detector()

    sp = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )

    facerec = dlib.face_recognition_model_v1(
        face_recognition_models.face_recognition_model_location()
    )

    return detector, sp, facerec


def get_face_embeddings(image_np):
    detector, sp, facerec = load_dlib_models()

    encodings = []
    faces = detector(image_np, 1)

    for face in faces:
        shape = sp(image_np, face)
        face_descriptor = facerec.compute_face_descriptor(image_np, shape, 1)
        encodings.append(np.array(face_descriptor))
    
    return encodings


@st.cache_resource
def get_trained_model():
    X = []
    y = []

    students = get_all_students()
    if not students:
        return None

    for student in students:
        embeddings = student.get('face_embedding')
        if embeddings:
            X.append(np.array(embeddings))
            y.append(student.get('student_id'))

    if len(X) == 0:
        return None

    model = SVC(kernel='linear', probability=True, class_weight='balanced')
    try:
        model.fit(X, y)
    except ValueError:
        pass

    return {"Clf" : model, "X" : X, "y" : y}


def trained_classifier():
    st.cache_resource.clear()
    model_data = get_trained_model()
    return bool(model_data)

def predict_attendance(class_image_np):
    model_data = get_trained_model()
    encodings = get_face_embeddings(class_image_np)
    detected_students = {}

    if not model_data:
        return detected_students, [], len(encodings)
    
    clf = model_data["Clf"]
    X_train = model_data["X"]
    y_train = model_data["y"]

    all_student = sorted(list(set(y_train)))

    for encoding in encodings:
        if len(all_student) >= 2:
            predicted_id = int(clf.predict([encoding])[0])
        else:
            predicted_id = int(all_student[0])

        student_embedding = X_train[y_train.index(predicted_id)]
        resemblance_threshold = 0.6
        best_match_score = np.linalg.norm(student_embedding-encoding)

        if best_match_score < resemblance_threshold:
            detected_students[predicted_id] = True
        
    return detected_students, encodings, len(encodings)