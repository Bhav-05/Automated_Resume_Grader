import streamlit as st
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

import pymysql

# --- MySQL Connection ---
try:
    root_conn = pymysql.connect(host='localhost', user='root', password='S@mbhav0519')
    root_cursor = root_conn.cursor()
    root_cursor.execute("CREATE DATABASE IF NOT EXISTS cv")
    root_conn.commit()
    root_cursor.close()
    root_conn.close()

    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='S@mbhav0519',
        db='cv',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.Cursor
    )
    cursor = connection.cursor()
except Exception as e:
    st.error(f"❌ Database connection failed: {e}")

# Insert user data into the database
def insert_data(name, email, res_score, timestamp, no_of_pages, reco_field, cand_level, skills, recommended_skills, courses):
    DB_table_name = 'user_data'
    insert_sql = f"""
        INSERT INTO {DB_table_name}
        VALUES (0, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    rec_values = (
        name, email, res_score, timestamp, no_of_pages,
        reco_field, cand_level, skills, recommended_skills, courses
    )
    cursor.execute(insert_sql, rec_values)
    connection.commit()

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

def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def course_recommender(course_list):
    st.subheader("**Courses & Certificates Recommendations 🎓**")
    rec_course = []
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 5)
    random.shuffle(course_list)
    for c, (c_name, c_link) in enumerate(course_list[:no_of_reco], start=1):
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
    return rec_course

# Set Streamlit page config
st.set_page_config(
    page_title="Automated Resume Grader",
    page_icon='./Logo/main_logo1.jpg'
)

def run():
    img = Image.open('./Logo/main_logo1.jpg')
    img = img.resize((650, 300))
    st.image(img)
    st.title("Automated Resume Grader")

    st.sidebar.markdown("# Choose User")
    activities = ["User", "Admin"]
    choice = st.sidebar.selectbox("Choose among the given options:", activities)

    # Create DB table
    DB_table_name = 'user_data'
    table_sql = f"""CREATE TABLE IF NOT EXISTS {DB_table_name} (
        ID INT NOT NULL AUTO_INCREMENT,
        Name VARCHAR(500) NOT NULL,
        Email_ID VARCHAR(500) NOT NULL,
        resume_score VARCHAR(8) NOT NULL,
        Timestamp VARCHAR(50) NOT NULL,
        Page_no VARCHAR(5) NOT NULL,
        Predicted_Field BLOB NOT NULL,
        User_level BLOB NOT NULL,
        Actual_skills BLOB NOT NULL,
        Recommended_skills BLOB NOT NULL,
        Recommended_courses BLOB NOT NULL,
        PRIMARY KEY (ID)
    );"""
    cursor.execute(table_sql)

    if choice == 'User':
        st.markdown('<h5>Upload your resume to get smart recommendations</h5>', unsafe_allow_html=True)
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf", "txt"])
        if pdf_file is not None:
            with st.spinner('Uploading your Resume...'):
                time.sleep(4)
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

                # [The rest of your resume analysis logic continues here...]
                # Including skill detection, recommendation, and final insertion

    else:
        st.success("Welcome to Admin Side")
        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')
        if st.button('Login'):
            if ad_user == 'admin' and ad_password == 'admin123':
                st.success("Welcome Admin!")
                cursor.execute(f"SELECT * FROM {DB_table_name}")
                data = cursor.fetchall()
                df = pd.DataFrame(data, columns=[
                    'ID', 'Name', 'Email', 'Resume Score', 'Timestamp', 'Total Page',
                    'Predicted Field', 'User Level', 'Actual Skills',
                    'Recommended Skills', 'Recommended Course'
                ])
                st.dataframe(df)
                st.markdown(get_table_download_link(df, 'User_Data.csv', '📥 Download Report'), unsafe_allow_html=True)
            else:
                st.error("Wrong ID & Password Provided")

run()
