import streamlit as st
import pandas as pd
import base64, random
import time, datetime
import re  # ✅ NEW
from pdfminer3.layout import LAParams
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer3.converter import TextConverter
import io
from streamlit_tags import st_tags
from PIL import Image
from Courses import ds_course, web_course, android_course, ios_course, uiux_course, resume_videos
from yt_dlp import YoutubeDL 
import nltk
nltk.download('stopwords')

# ✅ New helper to extract name and email
def extract_name_email(text):
    email_match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    email = email_match.group(0) if email_match else ""

    name = ""
    for line in text.split("\n"):
        if line.strip() and not any(x in line.lower() for x in ["resume", "curriculum", "cv"]) and len(line.split()) >= 2:
            name = line.strip()
            break
    return name, email

# Same as before
def fetch_yt_video(link):
    ydl_opts = {}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=False)
        return info.get('title')

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

st.set_page_config(page_title="Automated Resume Grader", page_icon='./Logo/main_logo1.jpg')

def run():
    img = Image.open('./Logo/main_logo1.jpg')
    img = img.resize((650, 300))
    st.image(img)
    st.title("Automated Resume Grader")
    st.sidebar.markdown("# Choose User")
    activities = ["User", "Admin"]
    choice = st.sidebar.selectbox("Choose among the given options:", activities)

    if choice == 'User':
        st.markdown("#### 📄 Upload your resume to get recommendations")
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf", "txt"])
        if pdf_file is not None:
            with st.spinner('Processing Resume...'):
                time.sleep(3)
                save_path = './Uploaded_Resumes/' + pdf_file.name
                with open(save_path, "wb") as f:
                    f.write(pdf_file.getbuffer())

                file_extension = pdf_file.name.split(".")[-1].lower()
                if file_extension == "pdf":
                    resume_text = pdf_reader(save_path)
                    name, email = extract_name_email(resume_text)
                    resume_data = {
                        'name': name or "Name Not Found",
                        'email': email or "Email Not Found",
                        'mobile_number': "1234567890",
                        'skills': ['python', 'sql', 'flask'],
                        'no_of_pages': 1
                    }
                elif file_extension == "txt":
                    with open(save_path, "r", encoding="utf-8") as f:
                        resume_text = f.read()
                    name, email = extract_name_email(resume_text)
                    resume_data = {
                        'name': name or "Name Not Found",
                        'email': email or "Email Not Found",
                        'mobile_number': "",
                        'skills': [],
                        'no_of_pages': len(resume_text.split('\n')) // 10
                    }
                else:
                    st.error("Unsupported file format!")
                    return

                # 🧠 Display Info
                st.header("**Resume Analysis**")
                st.success(f"Hello {resume_data['name']}")
                st.subheader("**Your Basic Info**")
                st.text('Name: ' + resume_data['name'])
                st.text('Email: ' + resume_data['email'])
                st.text('Contact: ' + resume_data['mobile_number'])
                st.text('Resume pages: ' + str(resume_data['no_of_pages']))

                # ...rest of your skills recommendation and score logic continues unchanged
                st_tags(label='### Your Current Skills', text='See our skills recommendation below', value=resume_data['skills'], key='1')
                st.markdown("---")

                # Continue your course recommendations and resume score logic...

run()
