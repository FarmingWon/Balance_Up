import streamlit as st
import extra_streamlit_components as stx
from st_pages import Page, add_page_title, show_pages
from streamlit_extras.switch_page_button import switch_page

# data analysis
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D
import matplotlib as mpl
import math
import plotly.express as px

import json
import requests

import sys
import base64
from pathlib import Path

from recommend import company as corp
from recommend import jaccard

def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded

def get_progress_score():
    st.session_state.barScore = 0
    if 'clicked_regionCd' not in st.session_state:
        st.session_state.barScore = 0
    else:
        st.session_state.barScore = 75

def set_csv():
  st.session_state.df_subway = pd.read_csv('csv/subway.csv')
  st.session_state.df_bus = pd.read_csv('csv/bus.csv')
  st.session_state.df_hospital = pd.read_csv('csv/hospital.csv')
  st.session_state.df_museum = pd.read_csv('csv/museum.csv')
  st.session_state.df_starbucks = pd.read_csv('csv/starbucks_busan.csv')
  st.session_state.df_exercise = pd.read_csv('csv/exercise.csv')
  st.session_state.df_oliveyoung = pd.read_csv('csv/oliveyoung.csv')

# func: address to lat, lon
def addr_to_lat_lon(addr):
    try:
        addr = addr.replace(",", "")
        addr = addr.split(" ")
        addr_tmp = addr[1:6]
        addr = ""
        for ad in addr_tmp:
            if ad != "":
                addr = addr + " " + ad
        url = f"https://dapi.kakao.com/v2/local/search/address.json?query={addr}"
        headers = {"Authorization": "KakaoAK " + st.secrets.KEY.KAKAO_KEY}
        result = json.loads(str(requests.get(url, headers=headers).text))
        match_first = result['documents'][0]['address']
        return float(match_first['y']), float(match_first['x'])
    except Exception as e:
      return None

# func: calculator distance
def calculate_distance(df, center_xy):
  df_distance = pd.DataFrame()
  distance_list = []
  for i in df['latlon']:
    if i != None or i != '':
      if type(i) == str:
        i = i[1:-1].split(', ')
        y = abs(float(center_xy[0]) - float(i[0])) * 111
        x = (math.cos(float(center_xy[0])) * 6400 * 2 * 3.14 / 360) * abs(float(center_xy[1]) - float(i[1]))
        distance = math.sqrt(x*x + y*y)
        if distance <= 3.0:
          df_distance = pd.concat([df_distance, df[df['latlon'] == ('(' + i[0] + ', ' + i[1] + ')')]])
          distance_list.append(distance)

  df_distance = df_distance.drop_duplicates()
  df_distance['distance'] = distance_list

  return df_distance # 만들어진 데이터프레임 리턴

def eval_infra(score_list):
    eval_list = list()
    for idx, score in enumerate(score_list):
        if score >= 20:
            eval_list.append("여유")
        elif score >= 6:
            if idx == 0:
                eval_list.append("혼잡")
            else:
                eval_list.append("보통")
        else:
            eval_list.append("없음")
    return eval_list

# EventListener: Button(Show More)
def on_more_click(show_more, idx):
    show_more[idx] = True
    st.session_state.show_more = show_more

def on_less_click(show_more, idx):
    show_more[idx] = False
    st.session_state.show_more = show_more

# func: calculate score of company
def make_score(company_name,address,busisize,isShow=False): # 점수 계산
    set_csv()
    center_xy = addr_to_lat_lon(address)
    if center_xy != None:
        center_xy = list(center_xy)
    else:
        return 0
    df_subway_distance = calculate_distance(st.session_state.df_subway, center_xy)
    df_bus_distance = calculate_distance(st.session_state.df_bus, center_xy)
    df_hospital_distance = calculate_distance(st.session_state.df_hospital, center_xy)
    df_museum_distance = calculate_distance(st.session_state.df_museum, center_xy)
    df_starbucks_distance = calculate_distance(st.session_state.df_starbucks, center_xy)
    df_exercise_distance = calculate_distance(st.session_state.df_exercise, center_xy)
    df_oliveyoung_distance = calculate_distance(st.session_state.df_oliveyoung, center_xy)

    df_graph = pd.DataFrame({'distance': ['500m', '1km', '3km']})

    df_graph['subway'] = [len(df_subway_distance.loc[df_subway_distance['distance'] <= 0.5]),
                        len(df_subway_distance.loc[(df_subway_distance['distance'] > 0.5) & (df_subway_distance['distance'] <= 1.0)]),
                        len(df_subway_distance.loc[(df_subway_distance['distance'] > 1.0) & (df_subway_distance['distance'] <= 3.0)])]

    df_graph['bus'] = [len(df_bus_distance.loc[df_bus_distance['distance'] <= 0.5]),
                        len(df_bus_distance.loc[(df_bus_distance['distance'] > 0.5) & (df_bus_distance['distance'] <= 1.0)]),
                        len(df_bus_distance.loc[(df_bus_distance['distance'] > 1.0) & (df_bus_distance['distance'] <= 3.0)])]

    df_graph['hospital'] = [len(df_hospital_distance.loc[df_hospital_distance['distance'] <= 0.5]),
                        len(df_hospital_distance.loc[(df_hospital_distance['distance'] > 0.5) & (df_hospital_distance['distance'] <= 1.0)]),
                        len(df_hospital_distance.loc[(df_hospital_distance['distance'] > 1.0) & (df_hospital_distance['distance'] <= 3.0)])]

    df_graph['museum'] = [len(df_museum_distance.loc[df_museum_distance['distance'] <= 0.5]),
                        len(df_museum_distance.loc[(df_museum_distance['distance'] > 0.5) & (df_museum_distance['distance'] <= 1.0)]),
                        len(df_museum_distance.loc[(df_museum_distance['distance'] > 1.0) & (df_museum_distance['distance'] <= 3.0)])]
    
    df_graph['starbucks'] = [len(df_starbucks_distance.loc[df_starbucks_distance['distance'] <= 0.5]),
                        len(df_starbucks_distance.loc[(df_starbucks_distance['distance'] > 0.5) & (df_starbucks_distance['distance'] <= 1.0)]),
                        len(df_starbucks_distance.loc[(df_starbucks_distance['distance'] > 1.0) & (df_starbucks_distance['distance'] <= 3.0)])]
    
    df_graph['exercise'] = [len(df_exercise_distance.loc[df_exercise_distance['distance'] <= 0.5]),
                        len(df_exercise_distance.loc[(df_exercise_distance['distance'] > 0.5) & (df_exercise_distance['distance'] <= 1.0)]),
                        len(df_exercise_distance.loc[(df_exercise_distance['distance'] > 1.0) & (df_exercise_distance['distance'] <= 3.0)])]

    df_graph['oliveyoung'] = [len(df_oliveyoung_distance.loc[df_oliveyoung_distance['distance'] <= 0.5]),
                        len(df_oliveyoung_distance.loc[(df_oliveyoung_distance['distance'] > 0.5) & (df_oliveyoung_distance['distance'] <= 1.0)]),
                        len(df_oliveyoung_distance.loc[(df_oliveyoung_distance['distance'] > 1.0) & (df_oliveyoung_distance['distance'] <= 3.0)])]
    col_name = ['subway','bus','hospital','museum','starbucks','exercise','oliveyoung']
    score_weight = 2
    score_weight_list = list() # 만점 144
    score = 0
    minusList = [3,2,1]
    plusList = [2,1,0]
    for name in col_name:
        tp_score = 0
        total_cal_score = 0
        minus = 0
        plus = 0
        for i in range(3):
            tp_score = tp_score + df_graph.loc[i][name]
            if df_graph.loc[i][name] == 0:
                minus = minus + minusList[i]
            else:
                plus = plus + plusList[i]
        if tp_score > 6:
            tp_score = tp_score - minus + plus
        else:
            tp_score = tp_score + plus
        if tp_score < 0:
            tp_score = 0
        elif tp_score > 24:
            tp_score = 24
        if name == 'subway' or name == 'bus':
            if tp_score >= 100: # 혼잡 
                tp_score = score_weight * 3
            elif tp_score == 0:
                tp_score = score_weight * 0
            else:
                tp_score = score_weight * 6 
        elif name =='exercise':
            if tp_score >= 100:
                tp_score = score_weight * 12 
            elif tp_score == 0:
                tp_score = score_weight * 0
            else:
                tp_score = score_weight * 6
        else:
            if tp_score > 2:
                tp_score = score_weight * 12
            elif tp_score == 0:
                tp_score = score_weight * 0 
            else:
                tp_score = score_weight * 6
        total_cal_score = total_cal_score + tp_score
        if name == 'bus':
            score_weight_list[0] = score_weight_list[0] + total_cal_score
        else:
            score_weight_list.append(total_cal_score)
        score = score + total_cal_score
        
    if busisize == '강소기업':
        score = score + 16
    elif busisize == "중견기업" or busisize == "대기업":
        score = score + 8
    else:
        score = score + 4 
    st.session_state.score = score
    
    if isShow:
        st.session_state.score_weight_list = score_weight_list
        eval_list = eval_infra(score_weight_list)
        query = f"""
        현재 회사 근처에 대중교통 {eval_list[0]}, 병원 {eval_list[1]}, 박물관 {eval_list[2]}, 커피숍 {eval_list[3]}, 운동시설 {eval_list[4]}, 올리브영 {eval_list[5]} 인데 회사 주변의 라이프 밸런스를 평가해줘.
        """
        st.session_state.query = query
        st.session_state.busiSize = busisize
        st.session_state.infra = jaccard.getInfra_to_GPT(st.session_state.query,st.secrets.KEY.INFRA_GPT_KEY)
        st.session_state.df_graph = df_graph
        st.session_state.eval_list = eval_list
    return score

def all_score():
    li = list()
    idx = st.session_state.companys.shape[0]
    for row in range(idx):
        score = make_score(st.session_state.companys.loc[row]['기업명'], st.session_state.companys.loc[row]['기업위치'], st.session_state.companys.loc[row]['기업규모'])
        li.append(score)
    df = pd.DataFrame(li, columns=['score'])
    st.session_state.companys['score'] = li
    st.session_state.companys =st.session_state.companys.sort_values(by='score',ascending=False) # 내림차순



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
    
    <div class="container header" style="font-weight:600;"><p class="h3">👜기업의 직업/지역 선택</p></div>
    <div class="container" style="margin-top: 5px;">
        <ol class="c-stepper">
            <li class="c-stepper-item completed" id="c-item1">
                <p class="c-stepper-title">이력서 파일 입력</p>
            </li>
            <li class="c-stepper-item completed" id="c-item2">
                <p class="c-stepper-title">개인 맞춤 직무 추천</p>
            </li>
            <li class="c-stepper-item completed" id="c-item3">
                <p class="c-stepper-title">기업의 직업/지역 선택</p>
            </li>
            <li class="c-stepper-item" id="c-item4">
                <p class="c-stepper-title">기업 라이프 밸런스 평가 + ELEI 차트</p>
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
                        <i class="fas fa-building fa-lg text-primary fa-fw"></i>
                    </div>
                </div>
                <div class="flex-grow-1 ms-4">
                    <p class="mb-1">현재 채용중인 기업정보에 대하여 확인이 가능해요.</p>
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
                    <p class="mb-1">버튼을 누른 뒤, 마음에 드는 회사를 선택해봐요.</p>
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
                    <p class="mb-1">라이프 밸런스 확인 버튼을 누르면 라이프 밸런스를 확인할수 있어요!</p>
                </div>
            </div>
        </section>
    </div>
    """
    st.markdown(htmlSide, unsafe_allow_html=True)
    st.sidebar.markdown("---")
    bar = st.progress(st.session_state.barScore, text= f"진행률 {st.session_state.barScore}%")
    
if 'clicked_regionCd' not in st.session_state:
    st.error('직업 추천을 먼저 진행해주세요')
    if st.button("< Prev"):
        switch_page("이력서를_통한_직업_추천")
elif st.session_state.clicked_regionCd != None and st.session_state.clicked_regionNm != None and st.session_state.clicked_jobCd != None and st.session_state.clicked_jobNm != None:
    st.session_state.gangso, st.session_state.recommend_company = corp.find_company(st.session_state.clicked_regionCd, st.session_state.clicked_jobCd, st.secrets.KEY.MONGO_KEY)
    html = f"""
        <div class="container" style="margin-top: 10px;">
            <span><strong>{st.session_state.clicked_regionNm}</strong>지역의 <strong>{st.session_state.clicked_jobNm}</strong> 채용공고가 </span>
            <span style='color:blue; font-weight:bold'>{len(st.session_state.gangso) + len(st.session_state.recommend_company)}</span>개의 채용공고가 있네요.
            <br>잠시만 기다리시면 라이프 밸런스 점수와 함께 보여드리겠습니다!
        </div>
        <div class="container" style="margin-top: 10px;">
            <p style="font-weight: 600; font-size: 32px;">기업 목록</p>
        </div>
    """
    st.markdown(html,unsafe_allow_html=True)
    
    fields = ['기업명','기업규모','근로계약','기업위치','근무시간' ,'URL']
    if len(st.session_state.gangso) != 0:
        gangso_df = pd.DataFrame(st.session_state.gangso, columns=fields)
    if len(st.session_state.recommend_company) != 0:
        company_df = pd.DataFrame(st.session_state.recommend_company, columns=fields)
    if len(st.session_state.gangso) == 0 and len(st.session_state.recommend_company) == 0:
        st.write("회사 없음.")
    else:
        if len(st.session_state.gangso) != 0 and len(st.session_state.recommend_company) != 0:
            st.session_state.companys = pd.merge(gangso_df, company_df, how='outer')
        elif len(st.session_state.gangso) == 0:
            st.session_state.companys = company_df
        else:
            st.session_state.companys = gangso_df
    
        if 'show_more' not in st.session_state or st.session_state.show_more == None or len(st.session_state.show_more) != len(st.session_state.companys):
            st.session_state.show_more = dict.fromkeys([i for i in range(len(st.session_state.companys))], False)
        show_more = st.session_state.show_more
                
        cols = st.columns(3)
        rows = ['기업명', '상세정보', '라이프 밸런스 점수']
    
        # table header
        for col, field in zip(cols, rows):
            col.write("**"+field+"**")

        with st.spinner("채용정보 불러오는 중..."):
            all_score()
            # table rows
            for idx, row in st.session_state.companys.iterrows():
              col1, col2,col3 = st.columns(3)
              col1.write(row['기업명'])
              placeholder = col2.empty()
              if show_more[int(idx)]:
                  placeholder.button(
                      "less", key=str(idx) + "_", on_click=on_less_click, args=[show_more, idx]
                  )
                  make_score(row['기업명'], row['기업위치'], row['기업규모'], isShow= True)
                  subcol1, subcol2 = st.columns(2)
                  with subcol1:
                        html = """
                            <div style='height:50px'></div>
                        """
                        st.markdown(html,unsafe_allow_html=True)
                        st.write('기업규모 : ' + row['기업규모'])
                        st.write('근로계약 : ' + row['근로계약'])
                        st.write('근무시간 : ' + row['근무시간'])
                        url = row['URL']
                        st.write("공고 URL : [%s](%s)" % (url, url))
                        st.write("라이프 밸런스 점수 : " + str(st.session_state.score) + "/160점")
                  with subcol2:
                        columns_name = ['대중교통','병원','문화시설','커피숍','운동시설','올리브영']
                        score_weight_list = st.session_state.score_weight_list
                        merge_data = list()
                        for i in range(6):
                            merge_data.append([columns_name[i],score_weight_list[i]])
                        df = pd.DataFrame(merge_data, columns=['라이프 밸런스','점수'])
                        fig1 = px.pie(df, values='점수' ,names='라이프 밸런스', title='라이프 밸런스 점수 비율 차트')
                        fig1.update_traces(textposition='outside',textinfo='label+percent', textfont_size=20,textfont_color="black")
                        st.plotly_chart(fig1)  
                      
                  subcol3,subcol4 = st.columns(2)    
                  with subcol4:
                      st.success('아래의 버튼을 눌러 라이프 밸런스를 확인하세요')         
                      if st.button('라이프밸런스 상세보기'):
                          st.session_state.selectCompany = True
                          get_progress_score()
                          bar.progress(st.session_state.barScore, text= f"진행률 {st.session_state.barScore}%")
                          st.session_state.company = row
                          switch_page("직장_라이프_밸런스_확인")
                      
                  st.write("---")
              else:
                    placeholder.button(
                      "more",
                      key=idx,
                      on_click=on_more_click,
                      args=[show_more, idx],
                      type="primary",
                    )
              col3.write(f"{row['score']}/160점")
