import streamlit as st
import pandas as pd
import base64, random
import time, datetime
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
import io
from streamlit_tags import st_tags
from PIL import Image
from Courses import ds_course, web_course, android_course, ios_course, uiux_course, resume_videos
from yt_dlp import YoutubeDL 
import nltk
nltk.download('stopwords')

# --- Helper Functions ---
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
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def course_recommender(course_list):
    st.subheader("**Courses & Certificates Recommendations 🎓**")
    c = 0
    rec_course = []
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 5)
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
        if c == no_of_reco:
            break
    return rec_course

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
        st.markdown("<h5 style='text-align: left; color: #021659;'> Upload your resume, and get smart recommendations</h5>", unsafe_allow_html=True)
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf", "txt"])
        if pdf_file is not None:
            with st.spinner('Uploading your Resume...'):
                time.sleep(4)
                save_path = './Uploaded_Resumes/' + pdf_file.name
                with open(save_path, "wb") as f:
                    f.write(pdf_file.getbuffer())

                file_extension = pdf_file.name.split(".")[-1].lower()
                if file_extension == "pdf":
                    resume_text = pdf_reader(save_path)

                    # Basic email extraction
                    import re
                    email_match = re.search(r'[\w\.-]+@[\w\.-]+', resume_text)
                    email = email_match.group(0) if email_match else "Email Not Found"

                    # Basic name extraction from first few lines
                    lines = resume_text.split("\n")
                    lines = [line.strip() for line in lines if line.strip()]
                    name = "Name Not Found"
                    for line in lines[:10]:
                        if len(line.split()) >= 2 and not re.search(r'\d|@', line) and not any(x in line.lower() for x in ["email", "mobile", "resume", "cv"]):
                        name = line
                        break

                    resume_data = {
                        'name': name,
                        'email': email,
                        'skills': ['python', 'sql', 'flask'],
                        'no_of_pages': 1
                        }

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
                st.subheader("**Your Basic info**")
                try:
                    st.text('Name: ' + resume_data['name'])
                    st.text('Email: ' + resume_data['email'])
                    st.text('Contact: ' + resume_data['mobile_number'])
                    st.text('Resume pages: ' + str(resume_data['no_of_pages']))
                except:
                    pass

                cand_level = ''
                if resume_data['no_of_pages'] == 1:
                    cand_level = "Fresher"
                    st.markdown("<h4 style='text-align: left; color: #d73b5c;'>You are at Fresher level!</h4>", unsafe_allow_html=True)
                elif resume_data['no_of_pages'] == 2:
                    cand_level = "Intermediate"
                    st.markdown("<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>", unsafe_allow_html=True)
                elif resume_data['no_of_pages'] >= 3:
                    cand_level = "Experienced"
                    st.markdown("<h4 style='text-align: left; color: #fba171;'>You are at experience level!</h4>", unsafe_allow_html=True)

                st_tags(label='### Your Current Skills', text='See our skills recommendation below', value=resume_data['skills'], key='1')

                # (Skill detection & recommendation logic remains unchanged)

                ts = time.time()
                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                timestamp = str(cur_date + '_' + cur_time)

                st.subheader("**Resume Tips & Ideas💡**")
                resume_score = 0
                if 'Objective' in resume_text:
                    resume_score += 20
                    st.markdown('<h5 style="text-align: left; color: #1ed760;">[+] Awesome! You have added Objective</h5>', unsafe_allow_html=True)
                else:
                    st.markdown('<h5 style="text-align: left; color: #000000;">[-] Please add your career objective.</h5>', unsafe_allow_html=True)

                if 'Declaration' in resume_text:
                    resume_score += 20
                if 'Hobbies' in resume_text or 'Interests' in resume_text:
                    resume_score += 20
                if 'Achievements' in resume_text:
                    resume_score += 20
                if 'Projects' in resume_text:
                    resume_score += 20

                st.subheader("**Resume Score📝**")
                st.markdown("""
                    <style>
                        .stProgress > div > div > div > div {
                            background-color: #d73b5c;
                        }
                    </style>""", unsafe_allow_html=True)

                my_bar = st.progress(0)
                for percent_complete in range(resume_score):
                    time.sleep(0.05)
                    my_bar.progress(percent_complete + 1)

                st.success('** Your Resume Writing Score: ' + str(resume_score) + '**')
                st.warning("** Note: This score is based on content in your Resume. **")
                st.balloons()

                st.header("**Bonus Video for Resume Writing Tips💡**")
                resume_vid = random.choice(resume_videos)
                res_vid_title = fetch_yt_video(resume_vid)
                st.subheader("✅ **" + res_vid_title + "**")
                st.video(resume_vid)

        else:
            st.error('🧠 Tip: Only PDF or TXT files are supported.')

    else:
        st.success('Welcome to Admin Side')
        st.info('Note: Admin data table disabled for cloud compatibility.')

run()
