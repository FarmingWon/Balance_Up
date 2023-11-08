import certifi
import json
import csv
import pandas as pd
import api_key as ap
import os
import numpy as np
from PyPDF2 import PdfReader


def cos_similarity(v1, v2):
    dot_product = np.dot(v1, v2)
    l2_norm = (np.sqrt(sum(np.square(v1))) * np.sqrt(sum(np.square(v2))))
    similarity = dot_product / l2_norm     
    
    return similarity

def pdf_to_text(pdf): # pdf -> text 
    reader = PdfReader(pdf)
    pages = reader.pages
    text = ""
    for page in pages:
        sub = page.extract_text()
        text += sub
    return text


if __name__== '__main__':
    resume_path = ap.get_path('_pdf/')
    text = pdf_to_text(resume_path+'ws.pdf')
    text = text.upper()

    pr_path = ap.get_path('skills/expr_tfidf2/')
    job_list = list(os.listdir(pr_path))
    result = list()
    for job in job_list:
        df = pd.read_csv(pr_path+job) #idx,skill,tf,df,tfidf,pr 
        job_li = df.values.tolist()
        skill_list = list()
        job_skill_list = list()
        pr = 0
        # print(job_li)
        for li in job_li:
            point = 0
            if text.find(li[1]) != -1:
                point = li[4]
            skill_list.append(point)

            job_point = 0
            if li[2] != 0:
                job_point = li[4]
            job_skill_list.append(job_point)

        cos = cos_similarity(skill_list, job_skill_list)
        result.append([job[:len(job)-4], cos])
    result.sort(key=lambda x:x[1], reverse=True)
    print(result)