import streamlit as st
import sqlite3
import pandas as pd
import base64
import random
import time
import datetime
import io
from PIL import Image
from streamlit_tags import st_tags
from pdfminer3.layout import LAParams
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer3.converter import TextConverter
from Courses import ds_course, web_course, android_course, ios_course, uiux_course, resume_videos
from yt_dlp import YoutubeDL
import nltk
nltk.download('stopwords')

# === FIRST Streamlit command ===
st.set_page_config(page_title="Automated Resume Grader", page_icon="📄")

# === SQLite Database Setup ===
conn = sqlite3.connect('resume_data.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    resume_score TEXT,
    timestamp TEXT,
    page_no TEXT,
    predicted_field TEXT,
    user_level TEXT,
    actual_skills TEXT,
    recommended_skills TEXT,
    recommended_courses TEXT
)
""")
conn.commit()

def insert_data(name, email, res_score, timestamp, no_of_pages, reco_field, cand_level, skills, recommended_skills, courses):
    cursor.execute("""
        INSERT INTO user_data (
            name, email, resume_score, timestamp, page_no,
            predicted_field, user_level, actual_skills,
            recommended_skills, recommended_courses
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, email, res_score, timestamp, no_of_pages, reco_field, cand_level, skills, recommended_skills, courses))
    conn.commit()

def fetch_yt_video(link):
    ydl_opts = {}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=False)
        return info.get('title')

def get_table_download_link(df, filename, text):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            page_interpreter.process_page(page)
        text = fake_file_handle.getvalue()
    converter.close()
    fake_file_handle.close()
    return text

def course_recommender(course_list):
    st.subheader("**Courses & Certificates Recommendations \U0001F393**")
    rec_course = []
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 5)
    random.shuffle(course_list)
    for c, (c_name, c_link) in enumerate(course_list[:no_of_reco], start=1):
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
    return rec_course

def run():
    st.title("Automated Resume Grader")

    st.sidebar.markdown("# Choose User")
    activities = ["User", "Admin"]
    choice = st.sidebar.selectbox("Choose among the given options:", activities)

    if choice == 'User':
        st.markdown('''<h5>Upload your resume to get smart recommendations</h5>''', unsafe_allow_html=True)
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf", "txt"])

        if pdf_file is not None:
            with st.spinner('Uploading your Resume...'):
                time.sleep(2)
                save_path = './Uploaded_Resumes/' + pdf_file.name
                with open(save_path, "wb") as f:
                    f.write(pdf_file.getbuffer())

                file_extension = pdf_file.name.split(".")[-1].lower()
                if file_extension == "pdf":
                    resume_data = {
                        'name': "Extracted Name",
                        'email': "user@example.com",
                        'mobile_number': "1234567890",
                        'skills': ['python', 'sql', 'flask'],
                        'no_of_pages': 1
                    }
                    resume_text = pdf_reader(save_path)
                elif file_extension == "txt":
                    with open(save_path, "r", encoding="utf-8") as f:
                        resume_text = f.read()
                    resume_data = {
                        'name': "Extracted from TXT",
                        'email': "",
                        'mobile_number': "",
                        'skills': [],
                        'no_of_pages': len(resume_text.split('\n')) // 10
                    }
                else:
                    st.error("Unsupported file format!")
                    return

                st.header("**Resume Analysis**")
                st.success("Hello " + resume_data['name'])

                # Resume score logic
                resume_score = 0
                tips = {
                    'Objective': 20,
                    'Declaration': 20,
                    'Hobbies': 20,
                    'Achievements': 20,
                    'Projects': 20
                }

                for keyword, score in tips.items():
                    if keyword in resume_text:
                        resume_score += score

                st.subheader("**Resume Score**")
                st.progress(resume_score)
                st.success(f"Your Resume Score: {resume_score}")

                ts = time.time()
                timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H:%M:%S')

                # Simplified recommendation (example only)
                recommended_skills = ['Python', 'SQL', 'Data Analysis']
                recommended_courses = course_recommender(ds_course)

                insert_data(
                    resume_data['name'], resume_data['email'], str(resume_score), timestamp,
                    str(resume_data['no_of_pages']), 'Data Science', 'Fresher',
                    str(resume_data['skills']), str(recommended_skills), str(recommended_courses)
                )

                st.balloons()
                resume_vid = random.choice(resume_videos)
                st.subheader("Bonus: Resume Writing Video")
                st.video(resume_vid)

    else:
        st.success("Welcome to Admin Panel")
        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')
        if st.button('Login'):
            if ad_user == 'admin' and ad_password == 'admin123':
                cursor.execute("SELECT * FROM user_data")
                data = cursor.fetchall()
                df = pd.DataFrame(data, columns=['ID', 'Name', 'Email', 'Resume Score', 'Timestamp', 'Page No', 'Predicted Field', 'User Level', 'Actual Skills', 'Recommended Skills', 'Recommended Courses'])
                st.dataframe(df)
                st.markdown(get_table_download_link(df, 'User_Data.csv', '📥 Download Report'), unsafe_allow_html=True)
            else:
                st.error("Invalid credentials")

run()
