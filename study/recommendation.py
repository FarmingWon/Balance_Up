from PyPDF2 import PdfReader
import api_key as ap
import os
import pandas as pd
import numpy as np
from concurrent.futures import ProcessPoolExecutor
import time

def pdf_to_text(pdf): # pdf -> text 
    reader = PdfReader(pdf)
    pages = reader.pages
    text = ""
    for page in pages:
        sub = page.extract_text()
        text += sub
    return text

def process_job(job):
    df = pd.read_csv(pr_path + job) # idx,skill,tf,df,tfidf,pr 
    job_li = df.values.tolist()
    pr = 0
    local_skills = set()  # local set for each process
    for li in job_li:
        if text.find(li[1]) != -1 and (len(li[1]) > 1 or li[1] == 'C'):
            pr += np.log(li[5])
            local_skills.add(li[1])
    if pr == 1:
        pr = 0
    return job[:len(job)-4], pr, local_skills


def main():
    resume_path = ap.get_path('_pdf/')
    text = pdf_to_text(resume_path+'tmp.pdf')
    text = text.upper()

    # 직업 스킬 확률 불러오기
    pr_path = ap.get_path('skills/expr_tfidf001/')
    # pr_path = ap.get_path('skills/tfidf_pr/')
    job_list = list(os.listdir(pr_path))
    result = list()
    user_skills = set()
    for job in job_list:
        df = pd.read_csv(pr_path+job) #idx,skill,tf,df,tfidf,pr 
        job_li = df.values.tolist()
        pr = 0
        for li in job_li:
            if text.find(li[1]) != -1 and (len(li[1]) > 1 or li[1] == 'C'):
                pr = pr + np.log(li[5])
                user_skills.add(li[1])
        if pr == 1 :
            pr = 0
        result.append([job[:len(job)-4], pr])
    result.sort(key=lambda x:x[1], reverse=True)
    print(result)
    print(user_skills)
    print(len(user_skills))

pr_path = ap.get_path('skills/expr_tfidf001/')
resume_path = ap.get_path('_pdf/')
text = pdf_to_text(resume_path+'ws.pdf')
text = text.upper()

if __name__ == "__main__":
    
    start = time.time()
    job_list = list(os.listdir(pr_path))
    user_skills = set()
    results = []
    
    with ProcessPoolExecutor(max_workers=8) as executor:
        for job, pr, local_skills in executor.map(process_job, job_list):
            results.append([job, pr])
            user_skills.update(local_skills)

    results.sort(key=lambda x:x[1], reverse=True)
    print(results)
    # print(user_skills)
    end = time.time()
    print(end-start)

    start = time.time()
    main()
    end = time.time()
    print(end-start)