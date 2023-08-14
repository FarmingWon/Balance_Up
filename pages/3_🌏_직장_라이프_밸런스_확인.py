import streamlit as st
from streamlit_echarts import st_echarts
from streamlit_folium import st_folium
from st_pages import add_page_title
from streamlit_extras.switch_page_button import switch_page
import plotly.graph_objects as go

import folium

# requests data
import json
import requests

# data analysis
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D
import matplotlib as mpl
import math

import sys
import base64
from pathlib import Path

def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded

def get_progress_score():
    st.session_state.barScore = 0
    if st.session_state.selectJob or st.session_state.selectRegion:
        st.session_state.barScore = 25
        if st.session_state.selectJob and st.session_state.selectRegion:
            st.session_state.barScore = 50
            if st.session_state.selectCompany:
                st.session_state.barScore = 75
                if st.session_state.selectWLB:
                    st.session_state.barScore = 100

def get_min(df):
  min_val = df['distance'].min(0)
  if np.isnan(min_val): #nan check
     return 0 
  min_val = int(min_val*10)
  if min_val <= 3:
     min_val = 3
  return min_val

def get_max(df):
  max_val = df['distance'].max(0)
  if np.isnan(max_val): #nan check
     return 0 
  return int(max_val*10)

# func: address to lat, lon
def addr_to_lat_lon(addr):
  url = f"https://dapi.kakao.com/v2/local/search/address.json?query={addr}"
  headers = {"Authorization": "KakaoAK " + st.secrets.KEY.KAKAO_KEY}
  result = json.loads(str(requests.get(url, headers=headers).text))
  match_first = result['documents'][0]['address']
  return float(match_first['y']), float(match_first['x'])

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

# func: 지도 생성
def makeMap(address,corpNm):
  center_xy = list(addr_to_lat_lon(address))
  m = folium.Map(location=center_xy, zoom_start=16)
  folium.Marker(center_xy, 
                popup=corpNm,
                tooltip=corpNm,
                icon=(folium.Icon(color='blue', icon='building', prefix='fa'))
                ).add_to(m)

  df_subway_distance = calculate_distance(st.session_state.df_subway, center_xy)
  df_bus_distance = calculate_distance(st.session_state.df_bus, center_xy)
  df_hospital_distance = calculate_distance(st.session_state.df_hospital, center_xy)
  df_museum_distance = calculate_distance(st.session_state.df_museum, center_xy)
  df_starbucks_distance = calculate_distance(st.session_state.df_starbucks, center_xy)
  df_exercise_distance = calculate_distance(st.session_state.df_exercise, center_xy)
  df_oliveyoung_distance = calculate_distance(st.session_state.df_oliveyoung, center_xy)

  min_dis = list()
  sub_dis = get_min(df_subway_distance)
  bus_dis = get_min(df_bus_distance)
  
  min_dis.append(min(sub_dis,bus_dis))
  min_dis.append(get_min(df_hospital_distance))
  min_dis.append(get_min(df_museum_distance))
  min_dis.append(get_min(df_starbucks_distance))
  min_dis.append(get_min(df_exercise_distance))
  min_dis.append(get_min(df_oliveyoung_distance))

  max_dis = list()
  sub_dis = get_max(df_subway_distance)
  bus_dis = get_max(df_bus_distance)
  max_dis.append(max(sub_dis, bus_dis))
  max_dis.append(get_max(df_hospital_distance))
  max_dis.append(get_max(df_museum_distance))
  max_dis.append(get_max(df_starbucks_distance))
  max_dis.append(get_max(df_exercise_distance))
  max_dis.append(get_max(df_oliveyoung_distance))

  st.session_state.min_dis = min_dis
  st.session_state.max_dis = max_dis
    

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

  options = {
    "tooltip": {"trigger": "item"},
    "legend": {"top": "0%", "left": "center",},
    "series": [
      {
        "name": "500m",
        "type": "pie",
        "radius": ["20%", "40%"],
        "avoidLabelOverlap": False,
        "itemStyle": {
          "borderRadius": 10,
          "borderColor": "#fff",
          "borderWidth": 2,
        },
        "label": {"show": False, "position": "center"},
        "emphasis": {
          "label": {"show": True, "fontSize": "20", "fontWeight": "bold"}
        },
        "labelLine": {"show": False},
        "data": [
          {"value": int(df_graph.iloc[0]['subway']), "name": "지하철역"},
          {"value": int(df_graph.iloc[0]['bus']), "name": "버스정류장"},
          {"value": int(df_graph.iloc[0]['hospital']), "name": "병원"},
          {"value": int(df_graph.iloc[0]['museum']), "name": "박물관/미술관"},
          {"value": int(df_graph.iloc[0]['starbucks']), "name": "스타벅스"},
          {"value": int(df_graph.iloc[0]['exercise']), "name": "체육시설"},
          {"value": int(df_graph.iloc[0]['oliveyoung']), "name": "올리브영"},
],
      },
      {
        "name": "1km",
        "type": "pie",
        "radius": ["40%", "60%"],
        "avoidLabelOverlap": False,
        "itemStyle": {
          "borderRadius": 15,
          "borderColor": "#fff",
          "borderWidth": 2,
        },
        "label": {"show": False, "position": "center"},
        "emphasis": {
          "label": {"show": True, "fontSize": "20", "fontWeight": "bold"}
        },
        "labelLine": {"show": False},
        "data": [
          {"value": int(df_graph.iloc[1]['subway']), "name": "지하철역"},
          {"value": int(df_graph.iloc[1]['bus']), "name": "버스정류장"},
          {"value": int(df_graph.iloc[1]['hospital']), "name": "병원"},
          {"value": int(df_graph.iloc[1]['museum']), "name": "박물관/미술관"},
          {"value": int(df_graph.iloc[1]['starbucks']), "name": "스타벅스"},
          {"value": int(df_graph.iloc[1]['exercise']), "name": "체육시설"},
          {"value": int(df_graph.iloc[1]['oliveyoung']), "name": "올리브영"},
        ],
      },
      {
        "name": "3km",
        "type": "pie",
        "radius": ["60%", "80%"],
        "avoidLabelOverlap": False,
        "itemStyle": {
          "borderRadius": 20,
          "borderColor": "#fff",
          "borderWidth": 2,
        },
        "label": {"show": False, "position": "center"},
        "emphasis": {
          "label": {"show": True, "fontSize": "20", "fontWeight": "bold"}
        },
        "labelLine": {"show": False},
        "data": [
          {"value": int(df_graph.iloc[2]['subway']), "name": "지하철역"},
          {"value": int(df_graph.iloc[2]['bus']), "name": "버스정류장"},
          {"value": int(df_graph.iloc[2]['hospital']), "name": "병원"},
          {"value": int(df_graph.iloc[2]['museum']), "name": "박물관/미술관"},
          {"value": int(df_graph.iloc[2]['starbucks']), "name": "스타벅스"},
          {"value": int(df_graph.iloc[2]['exercise']), "name": "체육시설"},
          {"value": int(df_graph.iloc[2]['oliveyoung']), "name": "올리브영"},
        ],
      },
    ],
  }
  st_echarts(
    options=options, height=550
  )

  makeMarker(m, df_subway_distance, 'blue', 'train')
  makeMarker(m, df_bus_distance, 'lightgreen', 'bus')
  makeMarker(m, df_hospital_distance, 'black', 'plus')
  makeMarker(m, df_museum_distance, 'darkred', 'institution')
  makeMarker(m, df_starbucks_distance, 'lightblue', 'coffee')
  makeMarker(m, df_exercise_distance, 'green', 'soccer-ball-o')
  makeMarker(m, df_oliveyoung_distance, 'orange', 'meteor')
  return m

# func: make Marker in map
def makeMarker(m, df, color, icon):
  for idx, row in df.iterrows():
    loc = row['latlon'][1:-1].split(', ')
    folium.Marker(loc,
                  popup=folium.Popup(row['name'], max_width=300),
                  tooltip=row['name'],
                  icon=(folium.Icon(color=color, icon=icon, prefix='fa'))
                 ).add_to(m)

def get_color_list():
  color_list = list()
  eval_list = st.session_state.eval_list
  for eval in eval_list:
    color = None
    if eval == "없음": #ㅂ 빨강
      color = '#F05934'
    elif eval == '보통': # 보통
      color = '#FDA932 '
    elif eval == '여유': # 초록
      color = '#11FF3F'
    else: #혼잡, 빨강
      color = '#F05934'
    color_list.append(color)
  return color_list

def draw_radar():
  # Sample data for radar chart
  categories = ["대중교통", "병원", "문화시설", "커피숍", "운동시설", "올리브영"]
  min_dis = st.session_state.min_dis
  max_dis = st.session_state.max_dis
  # Create a radar chart using Plotly
  fig = go.Figure()
  fig.add_trace(go.Scatterpolar(
      r=max_dis, 
      theta=categories,
      fill='toself',
      name='가장 먼 도보시간(분)',
      line_color='dodgerblue',
      opacity=0.6,
  ))
  fig.add_trace(go.Scatterpolar(
      r=min_dis, 
      theta=categories,
      fill='toself',
      name='가장 가까운 도보시간(분)',
      line_color='tomato',
  ))
  
  fig.update_layout(
      polar=dict(
          radialaxis=dict(range=[0, 30])
      ),
      showlegend=True,
      width = 650,
      height = 650
  )

  # Display the radar chart in the Streamlit app
  st.plotly_chart(fig,use_container_width= True)
    
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
    
    <div class="container header" style="font-weight:600;"><p class="h3">🌏 기업 인프라 평가 + ELEI 차트</p></div>
    <div class="container">
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
            <li class="c-stepper-item completed" id="c-item4">
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
                        <i class="fas fa-city fa-lg text-primary fa-fw"></i>
                    </div>
                </div>
                <div class="flex-grow-1 ms-4">
                    <p class="mb-1">직장 주변 인프라를 확인할 수 있어요.</p>
                </div>
            </div>
            <br/>
            <div class="d-flex align-items-start">
                <div class="flex-shrink-0">
                    <div class="p-3 badge-primary rounded-4">
                        <i class="fas fa-arrow-left-long fa-lg text-primary fa-fw"></i>
                    </div>
                </div>
                <div class="flex-grow-1 ms-4">
                    <p class="mb-1">다른 직장이 궁금하다면 돌아가서 직장 선택을 다시 할 수 있어요.</p>
                </div>
            </div>
        </section>
    </div>
    """
    st.markdown(htmlSide, unsafe_allow_html=True)
    st.sidebar.markdown("---")
    bar = st.progress(st.session_state.barScore, text= f"진행률 {st.session_state.barScore}%")
    
# set_csv()
if 'company' in st.session_state:
    st.session_state.selectWLB = True
    get_progress_score()
    bar.progress(st.session_state.barScore, text= f"진행률 {st.session_state.barScore}%")
    company = st.session_state.company
    address = company['기업위치']
    company_name = company['기업명']
    html = f"""
    <div style="font-size:20px">
        선택한 채용공고는 <span style="color: #2A9DF4;">{company_name}</span>의 채용공고네요.<br>
        해당 회사에 대한 <strong>라이프 밸런스</strong>를 알려드릴게요 ! 
    </div><br>
    """
    st.markdown(html, unsafe_allow_html=True)

    html = f"""
    <h2>AI의 {company_name}회사 라이프 밸런스 평가</h2>
    """
    st.markdown(html, unsafe_allow_html=True)
    st.write(st.session_state.infra)
    col1, col2 = st.columns([0.55,0.4])
    con3,con4,con5,con6= st.columns([0.05,0.6,0.5,0.05])
    emp1,con6 = st.columns([0.01,0.99])
    color_list = get_color_list()
    

    with con5:
      m = makeMap(address, company_name)
      center_xy = list(addr_to_lat_lon(address))
      folium.Marker(center_xy, 
                popup=company_name,
                tooltip=company_name,
                icon=(folium.Icon(color='blue', icon='building', prefix='fa'))
                ).add_to(m)
      
      con3_html = """ 
        <h3 style="text-align:center">생활 편의시설 통계</h3>
      """
      st.markdown(con3_html, unsafe_allow_html=True)

    with con4:
      # if 'starbucks' in st.session_state.df_graph.columns:
      #   st.session_state.df_graph.rename(columns={'subway' : '지하철',
      #                                             'bus' : '버스',
      #                                             'hospital' : '병원',
      #                                             'museum' : '박물관/미술관',
      #                                             'starbucks' : '스타벅스',
      #                                             'exercise' : '체육시설',
      #                                             'oliveyoung' : '올리브영'}, inplace=True)
      print(st.session_state.df_graph)
      fig, ax = plt.subplots()
      ax.set_ylim(0,50)
      st.session_state.df_graph.plot.bar(x = 'distance', 
                                         y=['subway','bus','hospital','museum','starbucks','exercise','oliveyoung'] ,
                                         color = ['#5A6FC0', '#59A076', '#F2CA6B', '#DE6E6A', '#59A076', '#EC8A5D'],
                                         ax=ax,
                                         legend = False)
      fig.legend(prop={'size':10}, bbox_to_anchor=(1.05, 1))
      st.pyplot(fig)
      con4_html = """ 
        <h3 style="text-align:center">거리별 라이프 밸런스 시설 개수</h3>
        """
      st.markdown(con4_html, unsafe_allow_html=True)
        
    with con6:
      st_folium(m, width=2500, returned_objects=[])
      con4_html = """ 
        <h3 style="text-align:center">기업 주변 라이프 밸런스</h3>
        """
      st.markdown(con4_html, unsafe_allow_html=True)
    with col1:
      draw_radar()
      
    with col2:
       score_weight_list = st.session_state.score_weight_list
       htmlStyle="""
      <style>
        .box {
            border: 3px solid black;
            padding: 1em;
            border-radius: 10px;
            box-sizing: border-box;
            text-align: center;
            font-size: 17px;
            width: 110px;
            height: 60px;
            font-weight :bolder;
            display: inline-block;
          
        }
        .cololrBox {
            padding: 1em;
            box-sizing: border-box;
            text-align: center;
            font-size: 14px;
            width: 80px;
            height: 40px;
            font-weight: bolder;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            vertical-align: middle;
            margin-left: 40px; 
        }
    </style>
        """
       eval_list = st.session_state.eval_list
       busiScore = 0
       if st.session_state.busiSize == '강소기업':
        busiScore = 16
       elif st.session_state.busiSize == '대기업':
        busiScore = 8
       else:
        busiScore = 4 
       col1Html = f"""
       <div>
          <div style='font-size:20px'>AI가 평가하는 <span style='color : blue;'>{company_name}</span>의 <span style='color : red;'>라이프 밸런스 점수</span>는? </div>
          <h2>라이프 밸런스 점수는 {st.session_state.score}/160점</h2>
          <p style='font-size:20px'>&nbsp;&nbsp;해당 회사는 <span style='color : blue;'>{st.session_state.busiSize}</span>이므로 추가점 <span style='color : red;'>{busiScore}점</span> 이 부여되었습니다.</p>
          <span class="box">대중교통</span> 
          <span class="cololrBox" style="background-color: {color_list[0]};"></span>
          <span style="align-items: center; justify-content: center;vertical-align: middle; margin-top :5px; margin-left: 20px; font-weight: bold; font-size: 25px;">{eval_list[0]}({score_weight_list[0]}/24점)</span>
          <br><br>
          <span class="box"> 병원 </span>
          <span class="cololrBox" style="background-color: {color_list[1]};"></span>
          <span style="align-items: center; justify-content: center;vertical-align: middle; margin-top :5px; margin-left: 20px; font-weight: bold; font-size: 25px;">{eval_list[1]}({score_weight_list[1]}/24점)</span>
          <br><br>
          <span class="box">문화시설</span> 
          <span class="cololrBox" style="background-color: {color_list[2]}; "></span>
          <span style="align-items: center; justify-content: center;vertical-align: middle; margin-top :5px; margin-left: 20px; font-weight: bold; font-size: 25px;">{eval_list[2]}({score_weight_list[2]}/24점)</span>
          <br><br>
          <span class="box">커피숍</span> 
          <span class="cololrBox" style="background-color: {color_list[3]}; "></span>
          <span style="align-items: center; justify-content: center;vertical-align: middle; margin-top :5px; margin-left: 20px; font-weight: bold; font-size: 25px;">{eval_list[3]}({score_weight_list[3]}/24점)</span>
          <br><br>
          <span class="box">운동시설</span> 
          <span class="cololrBox" style="background-color:{color_list[4]}; "></span>
          <span style="align-items: center; justify-content: center;vertical-align: middle; margin-top :5px; margin-left: 20px; font-weight: bold; font-size: 25px;">{eval_list[4]}({score_weight_list[4]}/24점)</span>
          <br><br>
          <span class="box">올리브영</span> 
          <span class="cololrBox" style="background-color :{color_list[5]};"></span>
          <span style="align-items: center; justify-content: center;vertical-align: middle; margin-top :5px; margin-left: 20px; font-weight: bold; font-size: 25px;">{eval_list[5]}({score_weight_list[5]}/24점)</span>
          <br><br>
      </div>
    """
       st.markdown(htmlStyle, unsafe_allow_html=True)
       st.markdown(col1Html, unsafe_allow_html=True)
       st.markdown("<div>&nbsp;</div><div>&nbsp;</div>", unsafe_allow_html=True)
else:
    if 'clicked_regionCd' not in st.session_state:
      st.error('직업 추천을 먼저 진행해주세요')
      if st.button("< Prev"):
        switch_page("이력서를 통한 직업 추천")
    else:
       st.error('직장 선택을 먼저 진행해주세요')
       if st.button("< Prev"):
          switch_page("직장 선택")
