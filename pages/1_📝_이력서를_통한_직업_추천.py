# -- import modules start --
import streamlit as st
import extra_streamlit_components as stx
from st_pages import add_page_title
from streamlit.components.v1 import html
from streamlit_extras.switch_page_button import switch_page

# customized modules
from recommend import jaccard
from recommend import region as r
from recommend import company as corp

import numpy as np
import pandas as pd

import sys,os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import base64
from pathlib import Path

# -- import modules end --
def set_variable():
    st.session_state.selected_region = None
    st.session_state.selected_job = None
    st.session_state.recommend_jobs = None
    st.session_state.similarity_jobs = None
    st.session_state.jobs = None
    st.session_state.score = None

def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded

def get_progress_score():
    st.session_state.barScore = 0
    if st.session_state.selectJob:
        st.session_state.barScore = 25
        if st.session_state.selectRegion:
            st.session_state.barScore = 50
            if st.session_state.selectCompany:
                st.session_state.barScore = 75
                if st.session_state.selectWLB:
                    st.session_state.barScore = 100

# func: save pdf file
def save_upload_file(dir, file):
    if not os.path.exists(dir):
        os.makedirs(dir)
    with open(os.path.join(dir, file.name), 'wb') as f:
        f.write(file.getbuffer())

# func: UI for Select Region
def showRegion(regions):
    regionsNm = [reg[1] for reg in regions]
    st.session_state.selected_region = st.radio(label = '', options= regionsNm)
    st.write("""<style>
            div.row-widget.stRadio {
                display: flex;
                justify-content: flex-start;
                align-items: center;
                padding: 1em;
                background-color: #f5f5f5;
                border-radius: 8px;
                box-shadow: 0px 2px 4px rgba(0,0,0,0.1);
            }

            div.row-widget.stRadio > div {
                flex-direction: row;
                flex-wrap: wrap;
                justify-content: flex-start;
                align-items: center;
                margin: 0.5em;
            }
        </style>
        """, unsafe_allow_html=True)

# func: UI for Select Job
def showJob(recommend_jobs, similarity_jobs):
    st.session_state.jobs = [[recommend_jobs[0]['occupation3'], recommend_jobs[0]['occupation3Nm']]]
    tmp2 = [[job[0]['occupation3'],job[0]['occupation3Nm']] for job in similarity_jobs]
    st.session_state.jobs.extend(tmp2)
    jobsNm = [job[1] for job in st.session_state.jobs]
    st.session_state.selected_job= st.radio(label='',options=jobsNm)
    st.write("""<style>
            div.row-widget.stRadio {
                display: flex;
                justify-content: flex-start;
                align-items: center;
                padding: 1em;
                background-color: #f5f5f5;
                border-radius: 8px;
                box-shadow: 0px 2px 4px rgba(0,0,0,0.1);
            }

            div.row-widget.stRadio > div {
                flex-direction: row;
                flex-wrap: wrap;
                justify-content: flex-start;
                align-items: center;
                margin: 0.5em;
            }
        </style>
        """, unsafe_allow_html=True)

#download resume
def download_link(data, file_name, file_label):
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{file_name}">{file_label}</a>'
    return href
    
set_variable()
get_progress_score()

htmlTitle = """
    <!-- Font Awesome -->
    <link
    href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
    rel="stylesheet"/>
    <!-- Google Fonts -->
    <link
    href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap"
    rel="stylesheet"/>
    <!-- MDB -->
    <link
    href="https://cdnjs.cloudflare.com/ajax/libs/mdb-ui-kit/6.4.0/mdb.min.css"
    rel="stylesheet"/>
    <!-- MDB -->
    <script
    type="text/javascript"
    src="https://cdnjs.cloudflare.com/ajax/libs/mdb-ui-kit/6.4.0/mdb.min.js"></script>
    
    <div class="container header" style="font-weight:600;"><p class="h3">📝이력서를 통한 직업 추천</p></div>
    <div class="container">
        <ol class="c-stepper">
            <li class="c-stepper-item completed" id="c-item1">
                <p class="c-stepper-title">이력서 파일 입력</p>
            </li>
            <li class="c-stepper-item" id="c-item2">
                <p class="c-stepper-title">개인 맞춤 직무 추천</p>
            </li>
            <li class="c-stepper-item" id="c-item3">
                <p class="c-stepper-title">기업의 직업/지역 선택</p>
            </li>
            <li class="c-stepper-item" id="c-item4">
                <p class="c-stepper-title">기업 인프라 평가 + ELEI 차트</p>
            </li>
        </ol>
    </div>
    <style type="text/css">
        @font-face {
            font-family: 'Pretendard-Regular';
            src: url('https://cdn.jsdelivr.net/gh/Project-Noonnu/noonfonts_2107@1.1/Pretendard-Regular.woff') format('woff');
            font-weight: 400;
            font-style: normal;
        }
        .container {
            font-family: 'Pretendard-Regular';
        }

        .c-stepper {
            display: flex;
            flex-wrap: wrap;
            margin: 0;
            padding: 0;
        }

        .c-stepper-title {
            margin-top:5px;
            font-size: small;
        }
        
        .c-stepper-item {
            flex: 1;
            display: flex;
            flex-direction: column;
            text-align: center;
        }
        
        .c-stepper-item:before {
            --size: 3rem;
            content: '';
            position: relative;
            z-index: 1;
            display: block;
            width: var(--size);
            height: var(--size);
            border-radius: 50%;
            border: 0.5px solid #0E3E89;
            margin: 0 auto;
            background-color: #ffffff;
        }
        .c-stepper-item:not(:last-child):after {
            content: '';
            position: relative;
            top: 1.5rem;
            left: 50%;
            height: 1.5px;
            background-color: #D1D1D1;
            order: -1;
        }
        .c-stepper-item.completed:before {
            --size: 3rem;
            content: '';
            position: relative;
            z-index: 1;
            display: block;
            width: var(--size);
            height: var(--size);
            border-radius: 50%;
            border: 0.5px solid #0E3E89;
            margin: 0 auto;
            background-color: #0E3E89
        }
    </style>
    """
st.markdown(htmlTitle, unsafe_allow_html=True)


with st.sidebar:
    htmlSide=f"""
    <div class="container sidebar">
        <section class="mb-5">
            <div class="d-flex align-items-start">
                <div class="flex-shrink-0">
                    <div class="p-3 badge-primary rounded-4">
                        <i class="fas fa-cloud-upload-alt fa-lg text-primary fa-fw"></i>
                    </div>
                </div>
                <div class="flex-grow-1 ms-4">
                    <p class="mb-1">이력서를 올려서 추천직업을 확인해보세요.</p>
                </div>
            </div>
            <br/>
            <div class="d-flex align-items-start">
                <div class="flex-shrink-0">
                    <div class="p-3 badge-primary rounded-4">
                        <i class="fas fa-briefcase fa-lg text-primary fa-fw"></i>
                    </div>
                </div>
                <div class="flex-grow-1 ms-4">
                    <p class="mb-1">가장 적합한 직업과 유사한 직업을 추천해드릴게요!</p>
                </div>
            </div>
            <br/>
            <div class="d-flex align-items-start">
                <div class="flex-shrink-0">
                    <div class="p-3 badge-primary rounded-4">
                        <i class="fas fa-earth-asia fa-lg text-primary fa-fw"></i>
                    </div>
                </div>
                <div class="flex-grow-1 ms-4">
                    <p class="mb-1">지역과 직업을 고르면 채용정보도 추천해드릴게요!</p>
                </div>
            </div>
        </section>
    </div>
    """
    st.markdown(htmlSide, unsafe_allow_html=True)
    st.sidebar.markdown("---")
    bar = st.progress(st.session_state.barScore, text= f"진행률 {st.session_state.barScore}%")

file_path = './_pdf/ws.pdf'
with open(file_path, 'rb') as file:
    pdf_data= file.read()
download_btn = download_link(pdf_data, "sample_data.pdf", "여기")
html= f"""
샘플 파일을 다운하고싶으면 {download_btn}를 눌러봐요.
"""
st.markdown(html, unsafe_allow_html=True)
uploaded_file = st.file_uploader("이력서를 올려보세요!", type="pdf")
st.session_state.regions = r.getRegion()


if uploaded_file:
    htmlcode='''
        <script type="text/javascript">
        $('#c-item2').addClass("completed");
        </script>
        '''
    st.markdown(htmlcode, unsafe_allow_html=True)
    with st.spinner():
        if 'recommend_jobs' not in st.session_state or st.session_state.recommend_jobs is None:
            save_upload_file('_pdf', uploaded_file)
            GPT_KEY = st.secrets.KEY.GPT_KEY
            st.session_state.recommend_jobs = jaccard.recommend_job(uploaded_file, GPT_KEY)
    if st.session_state.recommend_jobs :
        recommend_jobs = st.session_state.recommend_jobs
        if 'similarity_jobs' not in st.session_state or st.session_state.similarity_jobs is None:
            st.session_state.similarity_jobs = jaccard.recommend_similarity_job(recommend_jobs)
        jobsHtml = f"""
            <p>가장 적합한 직업은 <strong style='color:blue;'>{recommend_jobs[0]['occupation3Nm']}</strong>이네요. 유사한 직업도 같이 보여드릴게요.</p>
        """
        st.markdown(jobsHtml, unsafe_allow_html=True)
        st.write(f"")

clickedJob = None
if uploaded_file and  'selected_job' not in st.session_state or st.session_state.selected_job is None:
    with st.expander(label = '직업 선택', expanded=True):
        if st.session_state.recommend_jobs is not None and st.session_state.similarity_jobs is not None:
            showJob(st.session_state.recommend_jobs, st.session_state.similarity_jobs)
            clickedJob = st.button("직업 선택")
    with st.spinner():
        if clickedJob:
            st.session_state.selectJob = True
            st.session_state.clicked_jobCd = None
            st.session_state.clicked_jobNm = None
            if st.session_state.jobs is not None:
                for job in st.session_state.jobs:
                    if st.session_state.selected_job == job[1]:
                        st.session_state.clicked_jobCd = job[0]
                        st.session_state.clicked_jobNm = job[1]
                        st.session_state.selectJob = True
                        get_progress_score()
                        bar.progress(st.session_state.barScore, text= f"진행률 {st.session_state.barScore}%")
                        break
if 'clicked_jobNm' in st.session_state and st.session_state.clicked_jobNm != None:
    selectJobHtml = f"""
        <strong style='color:blue;'>{st.session_state.clicked_jobNm}</strong>직업을 선택하셨네요.<br>
        해당 직업을 가지고 보고싶은 채용공고의 지역을 선택해주세요. 
    """
    st.markdown(selectJobHtml, unsafe_allow_html=True)


if 'selectJob' in st.session_state and st.session_state.selectJob:
    with st.expander(label="지역 선택", expanded=True):
        showRegion(st.session_state.regions)
        regionBtn_clicked = st.button("지역 선택")
    if regionBtn_clicked:
        st.session_state.clicked_regionCd = None
        st.session_state.clicked_regionNm = None
        
        for region in st.session_state.regions:
            if st.session_state.selected_region == region[1]:
                st.session_state.clicked_regionCd = region[0]
                st.session_state.clicked_regionNm = region[1]
                st.session_state.selectRegion = True
                get_progress_score()
                break
        bar.progress(st.session_state.barScore, text= f"진행률 {st.session_state.barScore}%")

if st.session_state.selectRegion:
    st.success('Next 버튼을 눌러 다음 페이지로 이동하세요!')
    next_col1,next_col2,next_col3 = st.columns([0.45,0.45,0.1])
    with next_col3:
        jobs_btn = st.button("Next >")
        if jobs_btn:
            switch_page("직장_선택")
