from src.database.config import supabase
import bcrypt

def hash_pass(pwd):
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()

def check_pass(pwd, hashed):
    return bcrypt.checkpw(pwd.encode(), hashed.encode())


def check_teacher_exists(username):
    response = supabase.table("teachers").select("username").eq("username", username).execute()
    return len(response.data) > 0


def create_teacher(username, name, password):
    data = {"username": username, "name": name, "password": hash_pass(password)}
    response = supabase.table("teachers").insert(data).execute()
    return response.data


def login_teacher(username, password):
    response = supabase.table("teachers").select("*").eq("username", username).execute()
    
    if response.data:
        teacher = response.data[0]
        if check_pass(password, teacher['password']):
            return teacher
    return None



def get_all_students():
    response = supabase.table('students').select('*').execute()
    return response.data

def create_student(name, face_embedding=None, voice_embedding=None):
    data = {
        "name": name,
        "face_embedding": face_embedding,
        "voice_embedding": voice_embedding
    }
    response = supabase.table("students").insert(data).execute()
    return response.data

def create_subject(subject_id, subject_name, subject_section, teacher_id):
    data = {
        "subject_code": subject_id,
        "name": subject_name,
        "section": subject_section,
        "teacher_id": teacher_id
    }
    response = supabase.table("subjects").insert(data).execute()
    return response.data

def get_teacher_subjects(teacher_id):
    response = supabase.table("subjects").select("*, subject_students(count), attendance_logs(timestamp)").eq("teacher_id", teacher_id).execute()
    subject = response.data

    for sub in subject:
        sub['total_students'] = sub.get('subject_students', [{}])[0].get('count', 0) if sub.get('subject_students') else 0
        attendance = sub.get('attendance_logs', [])
        unique_sessions = list(set(log['timestamp'] for log in attendance))
        sub['total_classes'] = len(unique_sessions)

        sub.pop('subject_students', None)
        sub.pop('attendance_logs', None)
    return subject