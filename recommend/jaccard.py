import pandas as pd
import sys,os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import openai
from . import api
from openai.error import OpenAIError
from PyPDF2 import PdfReader
import time

def get_job(): # csv파일에 있는 직업 skill을 list화
    path = './csv/skills.csv'
    df = pd.read_csv(path)
    df.fillna('', inplace=True)
    jobs = df.values.tolist()
    result = list()
    for job in jobs:
        occu3 = str(job[0])
        jobsCd = str(job[2])
        if len(occu3) == 5:
            occu3 = "0" + occu3
        if len(jobsCd) == 5:
            jobsCd = "0" + jobsCd

        skill = job[3].replace("_", ",")
        skill = skill.replace('학력',"")
        skill = skill.replace('경력',"")
        skill = skill.replace('응시자격',"")
        skill = skill.replace('지역거주자',"")
        skill = skill.replace('사설학원',"")
        skills = skill.replace('독학',"")
        skills = api.getToken(skills.lower(), tk=',')
        ln = len(skills)
        for i in range(ln-1,-1,-1):
            if skills[i] == " ":
                skills.pop(i)
        skills = [tok.strip() for tok in skills]
        # print(skills)
        tmp = {
            "occupation3" : occu3,
            "occupation3Nm" : job[1],
            "jobsCd" : jobsCd,
            "skill" : skills
        }
        result.append(tmp)
    return result

def jaccard_distance(user_skills, job_skills): #자카드 유사도
    s1 = set(user_skills)
    s2 = set(job_skills)
    intersection = 0 # 교집합 
    for job_skill in job_skills: #문자열 전처리가 완벽히 되지 않아 find로 찾기 ex) 'java -8' , 'java'와는 같은 skill로 처리
        for user_skill in user_skills:
            if user_skill.find(job_skill) != -1:
                intersection = intersection + 1
                break
    return float(intersection / len(s2.union(s1)))


def getUserSkill_to_GPT_Chat(resume, API_KEY): # 이력서의 skill을 GPT를 활용하여 추출
    openai.api_key= API_KEY
    MODEL = "gpt-3.5-turbo"

    question = "\n Please extract skill, graduation department, and certificate from the corresponding sentence. I don't need another sentence, but please answer in Korean. For example, do it like 'java/C++/OOP'." #prompt
    try:
        response = openai.ChatCompletion.create(
            model = MODEL,
            messages = [
                {"role" : "user", "content" : resume+question}, #request
                {"role" : "assistant", "content" : "Help me extract skill from my resume.The response format divides each skill into."}
            ],
            temperature=0
        )
        return response.choices[0].message.content
    except OpenAIError as error:
        if error.status_code == 502:
            print(error)
            return error
        elif error.status_code == 429:
            retry = int(error.headers.get("Retry-After", 60))
            time.sleep(retry)
        else:
            print(error)
    
def getInfra_to_GPT(query, API_KEY):
    openai.api_key= API_KEY
    MODEL = "gpt-3.5-turbo"
    try:
        response = openai.ChatCompletion.create(
            model = MODEL,
            messages = [
                {"role" : "user", "content" : query + """응답은 4개의 문장 이내로 줘. 최종 평가로는 없음이 3개이상이면 라이프밸런스 나쁨, 없음이 2개가 없으면 라이프밸런스 보통, 없음이 1개 이하면 라이프밸런스가 좋다고 최종평가해줘."""}, #request
                {"role" : "assistant", "content" : """
                대중교통이 혼잡할만한 개수가 있으면 교통이 혼잡할 수 있다고 해줘. 각각 근처에 인프라의 시설이 없는 경우 주변 인프라가 별로 안좋다고 평가해줘.
                회사 주변 인프라에 대한 질문이라서, 좋고 나쁨을 평가해줘. 응답은 문장형식으로 해주고, 구체적인 인프라의 개수는 적지말고 좋고 나쁨만 평가해줘."""}
            ],
            temperature=0
        )
        return response.choices[0].message.content
    except OpenAIError as error:
        if error.status_code == 502:
            print(error)
            return error
        else:
            print(error)
    
def recommend_job(pdf,API_KEY): # 직업 추천
    try:
        resume = pdf_to_text(pdf) # 이력서 pdf -> text(string)
        jobs = get_job() # csv파일의 job list
        user_skill = getUserSkill_to_GPT_Chat(resume,API_KEY) 
        user_skill = user_skill.replace('/', ',')
        user_skill = api.getToken(user_skill.lower(), ",")
        user_skill = [tok.strip() for tok in user_skill]
        result = list()
        for job in jobs:
            distance = jaccard_distance(user_skill, job['skill'])
            tmp = [job, distance]
            if distance > 0:
                result.append(tmp)
        result.sort(key=lambda x:x[1], reverse=True) # 자카드 distance기준으로 내림차순 정렬
        return result[0]
    except Exception as e:
        print(e)
        

def recommend_similarity_job(result): #유사한 직업 추천하기
    if result is not None:
        occupation3 = result[0]['occupation3']
    else :
        occupation3 = '133200'
    jobs = get_job()
    result_similiarty = list()
    for job in jobs:
        similarity = jaccard_distance(result[0]['skill'], job['skill'])
        tmp = [job, similarity]
        if similarity > 0.1 and occupation3 != job['occupation3']:
            result_similiarty.append(tmp)
    result_similiarty.sort(key=lambda x:x[1], reverse=True)
    return result_similiarty


def pdf_to_text(pdf): # pdf -> text 
    reader = PdfReader(pdf)
    pages = reader.pages
    text = ""
    for page in pages:
        sub = page.extract_text()
        text += sub
    return text
    
