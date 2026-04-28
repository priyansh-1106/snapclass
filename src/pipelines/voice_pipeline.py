import streamlit as st 
import numpy as np 
import librosa
from resemblyzer import VoiceEncoder, preprocess_wav
import io

@st.cache_resource
def load_voice_encoder():
    return VoiceEncoder()

def get_voice_embedding(audio_bytes):
    try:
        encoder = load_voice_encoder()
        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
        wav = preprocess_wav(audio)
        embedding = encoder.embed_utterance(wav)
        return embedding.tolist()
    
    except Exception as e:
        st.error("Voice recognition error")
        return None

def identify_voice(new_embedding, candidate_dict, threshold = 0.65):
    if new_embedding is None or not candidate_dict:
        return None, 0.0
    
    best_score = -1
    best_sid = None

    for sid, stored_embedding in candidate_dict.items():
        if stored_embedding:
            score = np.dot(new_embedding, stored_embedding)
            if score > best_score:
                best_score = score
                best_sid = sid
            
    if best_score >= threshold:
        return best_sid, best_score
    
    return None, best_score


def process_bulk_audio(audio, student_dict, threshold=0.65):
    
    try:
        encoder = load_voice_encoder()
        audio, sr = librosa.load(io.BytesIO(audio), sr=16000)
        segments = librosa.effects.split(audio, top_db=30)

        identified_students = {}

        for start, end in segments:
            if (end-start) < sr*0.5:
                continue

            segment_audio = audio[start:end]
            wav = preprocess_wav(segment_audio)
            embedding = encoder.embed_utterance(wav)

            sid, score = identify_voice(embedding, student_dict, threshold)

            if sid:
                if sid not in identified_students or score > identified_students[sid]:
                    identified_students[sid] = score 
        return identified_students
    except Exception as e:
        st.error("Error processing audio")
        return {}