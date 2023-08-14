# -- import modules start --

import base64
import math
import sys
from pathlib import Path

#openai
import openai
from openai.error import OpenAIError

import pandas as pd

#streamlit
import streamlit as st
import extra_streamlit_components as stx
from st_pages import Page, add_page_title, show_pages
from streamlit_chat import message
from streamlit_extras.switch_page_button import switch_page
from streamlit_javascript import st_javascript

# -- import modules end --

# func: setting variable & files
def set_variable():
    st.session_state.selected_region = None
    st.session_state.selected_job = None
    st.session_state.recommend_jobs = None
    st.session_state.similarity_jobs = None
    st.session_state.jobs = None
    st.session_state.pageName = None
    st.session_state.query = None
    st.session_state.infra = None
    if 'score' not in st.session_state:
        st.session_state.score = None
    if 'selectJob' not in st.session_state:
        st.session_state.selectJob = False
    if 'selectRegion' not in st.session_state:
        st.session_state.selectRegion = False
    if 'selectCompany' not in st.session_state:
        st.session_state.selectCompany = False
    if 'selectWLB' not in st.session_state:
        st.session_state.selectWLB = False
    if 'barScore' not in st.session_state:
        st.session_state.barScore = False


def set_csv():
    st.session_state.df_subway = pd.read_csv('csv/subway.csv')
    st.session_state.df_bus = pd.read_csv('csv/bus.csv')
    st.session_state.df_hospital = pd.read_csv('csv/hospital.csv')
    st.session_state.df_museum = pd.read_csv('csv/museum.csv')
    st.session_state.df_starbucks = pd.read_csv('csv/starbucks_busan.csv')
    st.session_state.df_exercise = pd.read_csv('csv/exercise.csv')
    st.session_state.df_oliveyoung = pd.read_csv('csv/oliveyoung.csv')

def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded

def clear_submit():
    st.session_state["submit"] = False
    
def ask(q):
    message = """
    직업에 대하여 소개를 해줘. 질문에도 답하고,
    해당 직업이 주로 하는 일, 필요한 skill 및 역량, 전망에 대하여 말해줘.
    """
    messages=[{"role": "system", "content": q }, {"role" : "assistant", "content" : message}]
    q = {"role" : "user" , "content" : q}
    messages.append(q)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages = messages
    )

    bot_text  = response['choices'][0]['message']['content']
    bot_input = {"role": "assistant", "content": bot_text }

    messages.append(bot_input)

    return bot_text


def main():
    #side
  with st.sidebar:
      htmlSide=f"""
      <div class="container sidebar">
          <a href="#" style="text-decoration:center; color:inherit;"><p>✔ What is BalanceUP?</p></a>
          <a href="#" style="text-decoration:center; color:inherit;"><p>🔔 How To Use</p></a>
          <a href="#" style="text-decoration:center; color:inherit;"><p>❓ Why BalanceUP?</p></a>
          <a href="#" style="text-decoration:center; color:inherit;"><p>📝Feature</p></a>
      </div>
      """
      st.markdown(htmlSide, unsafe_allow_html=True)

  #main
  htmlHeader = f"""
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
  <script src="//cdnjs.cloudflare.com/ajax/libs/jquery-easing/1.3/jquery.easing.min.js"></script>
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
  <script src="./script/jquery-fadethis-master/dist/jquery.fadethis.js"></script>
  """
  st.markdown(htmlHeader, unsafe_allow_html=True)
  
  html1=f"""
  <div class="container wrap">
      <div class="container title">
          <div class="row" style="margin-top: 0%;">
              <div class="col-md-4"></div>
              <div class="col-md-5 d-flex justify-content-center">
                  <img src="data:image/png;base64,{img_to_bytes("./img/logo.png")}" style="width: 700; height: 250px;">
              </div>
              <div class="col-md-4"></div>
          </div>
      </div>
      <div class="container">
          <div class="subtitle" id="subtitle">
              <p class="h3 text-center">이력서만 등록해도 맞춤 포지션 추천과 기업 평가까지!!</p>
              <br/>
              <p class="text-center" style="margin-bottom:0px;">
                  내 이력서를 분석하여 연관성이 높은 포지션들을 알려드려요.
              </p>
              <p class="text-center">
                  기업 평가는 기업 주변 인프라의 접근성과 다양성을 기준으로 제공됩니다.
              </p>
          </div>
      </div>
      <br/>
      <div class="container slide-bottom">
          <ol class="c-stepper">
              <li class="c-stepper-item">
                  <p class="c-stepper-title">이력서 파일 입력</p>
              </li>
              <li class="c-stepper-item">
                  <p class="c-stepper-title">개인 맞춤 직무 추천</p>
              </li>
              <li class="c-stepper-item">
                  <p class="c-stepper-title">기업의 직업/지역 선택</p>
              </li>
              <li class="c-stepper-item">
                  <p class="c-stepper-title">기업 인프라 평가 + ELEI 차트</p>
              </li>
          </ol>
      </div>
  </div>
  <div class="container" style="margin-bottom: 5%"></div>
  """ + """
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
      .container.wrap{
          overflow: hidden;
          #height: 700px;
          padding: 450px 0px 0px 0px;
          top:100%;
          left: 50%;
          position: relative;
          transform: translate(-50%, -50%);
          transition: transform 300ms, box-shadow 300ms;
          display: contents;
      }
      .container.wrap:after {
          left: 80%;
          bottom: -24%;
          background-color: rgb(255 67 67 / 20%);
          animation: wawes 7s infinite;
      }
      .container.wrap::before {
          left: 79%;
          bottom: -20%;
          background-color: rgb(255 0 0 / 21%);
      
          animation: wawes 6s infinite linear;
      }
      .container.wrap::before,
      .container.wrap::after {
          content: '';
          position: absolute;
          width: 500px;
          height: 500px;
          border-top-left-radius: 40%;
          border-top-right-radius: 45%;
          border-bottom-left-radius: 35%;
          border-bottom-right-radius: 40%;
          z-index: 0;
      }

      @keyframes wawes {
          from {
              transform: rotate(0);
          }
      
          to {
              transform: rotate(360deg);
          }
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
  st.markdown(html1, unsafe_allow_html=True)

  m = st.markdown("""
  <style>
      div.stButton > button:first-child {
          background-color: #2A9DF4;
          color: #ffffff;
          width: 60%;
          height: 60px;
          margin-top: 0%;
    margin-left : 20%;
        font-size : large;
      }
  </style>""", unsafe_allow_html=True)
#0C377A
  col1, col2, col3 = st.columns([1,3,1])
  with col2:
      if st.button("구직 직업 상담"):
          switch_page("이력서를_통한_직업_추천")

  m = st.markdown("""
  <style>
      div.stButton > button:first-child {
          background-color: #0C377A;
          color: #ffffff;
          width: 60%;
          height: 60px;
          margin-top: 0%;
          margin-left : 20%;
          font-size : large;
      }
  </style>""", unsafe_allow_html=True)
  col4, col5, col6 = st.columns([1,3,1])
  with col5:
      if st.button("AI 잡케어 이용하기"):    
        switch_page("JobsGPT_직업소개") 

  html3 = f"""
      <div class="contain">
        <div class="slide-bottom">
            <div class="container" style="margin-top: 10%; height: auto;">
                <div class="row">
                    <div class="col">
                        <h2 class="slide-bottom">개인 맞춤 직무 추천과<br/>관련 기업의 인프라 평가까지</h2> 
                        <p>거대언어모델을 활용한 <strong>개인 커스텀 AI 직무 추천</strong>과<br/>밸런스업의 내부 평가 모델을 통한 ELEI 차트를 제공합니다.</p>
                        <br/>
                        <p style="align-items-bottom"><small>*ELEI(Enterprise Living Environment Index): 기업 생활 환경 지수로MZ 세대가 선호하는 인프라 환경을 기반으로 해당 기업에 대한 평가를 진행합니다.</small></p>
                    </div>
                    <div class="col">
                        <img src="data:image/png;base64,{img_to_bytes("img/elei.png")}"  style="height: 300px; width: 300px; margin-left: 10%;">
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="container" style="margin-top: 10%"></div>
    <div class="container">
        <h5>Powered by</h5>
        <div class="row d-flex justify-content-center">
            <div class="col">
                <div class="card">
                    <div class="card-body">
                        <div class="d-flex justify-content-center align-items-center" id="logo">
                            <img src="data:image/png;base64,{img_to_bytes("./img/openai_logo-removebg.png")}" style="width:180px; height:60px;">
                        </div>
                    </div>
                </div>
            </div>
            <div class="col">
                <div class="card">
                    <div class="card-body">
                        <div class="d-flex justify-content-center align-items-center" id="logo">
                            <img src="data:image/png;base64,{img_to_bytes("./img/mongodb logo.png")}" style="width:200px; height:60px;">
                        </div>
                    </div>
                </div>
            </div>
            <div class="col">
                <div class="card">
                    <div class="card-body">
                        <div class="d-flex justify-content-center align-items-center" id="logo">
                            <img src="data:image/png;base64,{img_to_bytes("./img/Neo4j-logo_color.png")}" style="width:180px; height:60px;">
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="row d-flex justify-content-center" style="margin-top: 5%">
            <div class="col">
                <div class="card">
                    <div class="card-body">
                        <div class="d-flex justify-content-center align-items-center" id="logo">
                            <img src="data:image/png;base64,{img_to_bytes("./img/kakaomap_logo.jpg")}" style="width:180px; height:60px;">
                        </div>
                    </div>
                </div>
            </div>
            <div class="col">
                <div class="card">
                    <div class="card-body">
                        <div class="d-flex justify-content-center align-items-center" id="logo">
                            <img src="data:image/png;base64,{img_to_bytes("./img/vworld_logo.png")}" style="width:180px; height:59px;">
                        </div>
                    </div>
                </div>
            </div>
            <div class="col">
                <div class="card">
                    <div class="card-body">
                        <div class="d-flex justify-content-center align-items-center" id="logo">
                            <img src="data:image/png;base64,{img_to_bytes("./img/worknet_logo.png")}" style="width:180px; height:60px;">
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
"""
  st.markdown(html3, unsafe_allow_html=True)

if __name__ == "__main__":
    set_variable()
    set_csv()
    st.set_page_config(page_title="BalanceUp", layout="wide")
    main()
