import openai
import streamlit as st
from openai.error import OpenAIError

import base64
from pathlib import Path
from streamlit_chat import message


def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded

def clear_submit():
    st.session_state["submit"] = False
    
def ask(q):
    message = """
    직업에 대하여 소개를 해줘.
    해당 직업이 주로 하는 일, 필요한 skill 및 역량, 전망에 대하여 말해줘.
    """
    messages=[{"role": "system", "content": message }]
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

GPT_KEY = st.secrets.KEY.GPT_KEY
openai.api_key = GPT_KEY

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
    
    <div style="font-weight:600; font-size: 20px; margin-top: 5%;"><p class="h1">JobsGPT를 통한 직업 상담</p></div>

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
    </style>
    """
st.markdown(htmlTitle, unsafe_allow_html=True)

if 'generated' not in st.session_state: # 초기화
    st.session_state['generated'] = [
                                        """ 웹 개발자는 인터넷 상에서 동작하는 웹사이트 및 애플리케이션을 개발하는 사람을 말합니다. 웹 개발자는 클라이언트 요구사항에 맞게 웹사이트를 구축하고, 기능을 개선하며, 유지보수를 담당합니다.


웹 개발자가 주로 하는 일은 다음과 같습니다:



웹사이트 및 애플리케이션의 디자인 및 개발

프론트엔드 개발: HTML, CSS, JavaScript 등을 사용하여 웹사이트의 외관과 사용자 경험을 개선

백엔드 개발: 데이터베이스, 서버, 알고리즘 등을 사용하여 웹사이트의 기능을 구현

테스트 및 디버깅: 웹사이트의 오류를 찾고 수정하여 품질을 유지


웹 개발자가 필요한 주요 스킬과 역량은 다음과 같습니다:



프로그래밍 언어: HTML, CSS, JavaScript, Python, Java, PHP 등 웹 개발 언어에 대한 이해와 숙련도가 필요

프레임워크 및 라이브러리: 웹 개발을 보다 효율적으로 할 수 있는 도구들에 대한 지식과 경험이 필요 (예: React, Angular, Django, Laravel 등)

데이터베이스 및 서버 관리: 데이터베이스 시스템 및 웹 서버에 대한 이해와 관리 능력이 필요

문제 해결능력: 복잡한 문제를 해결하고 논리적인 사고로 개발 과정에서 발생하는 오류를 해결할 수 있는 능력이 필요


웹 개발자의 전망은 매우 밝습니다. 인터넷 사용량이 증가하면서 온라인 비즈니스 및 웹앱 개발의 수요도 함께 증가하고 있습니다. 또한 모바일 기기의 보급도 웹 애플리케이션 개발을 더욱 중요하게 만들었습니다. 따라서 웹 개발자의 역할과 수요는 계속해서 증가할 것으로 예상됩니다. 또한, 새로운 기술과 프레임워크의 등장으로 개발자들은 항상 새로운 것을 배우고 발전해야만 합니다.
    """]

if 'past' not in st.session_state: # 초기화
    st.session_state['past'] = ["웹 개발자는 무슨 직업인지 설명해줘."]


query = st.text_area('LLM기반 AI 챗봇 프로그램을 통해 구직 상담을 진행하세요.', value="", on_change=clear_submit, placeholder="백엔드 개발자는 무슨 직업인지 설명해줘.")
button = st.button("submit")
if button or st.session_state.get("submit"):
    st.session_state["submit"] = True
    try:
        with st.spinner("Calling Job Description API..."):
                
            output = ask(query)
            st.session_state.past.append(query)
            st.session_state.generated.append(output)

    except OpenAIError as e:
        st.error(e._message)

if st.session_state['generated']:
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
        message(st.session_state["generated"][i], key=str(i))
with st.sidebar:
    htmlSide=f"""
        <ul>
            <li>ChatGPT를 이용해 직업의 상세 설명을 제공하는 페이지에요.</li>
            <li>궁금하거나 직업 추천을 통해 나온 결과를 입력해보세요!</li>
            <li>잠시 기다리면 직업에 대한 설명이 나올거에요!</li>
        </ul>
    """
    st.markdown(htmlSide, unsafe_allow_html=True)
