import os
import pandas as pd
import api_key as ap
import csv
import json
import math
import numpy as np

# mongo
from pymongo import MongoClient
import certifi

# 각 직업 별로 SKILL 불러오기
# 각 직업별로 채용공고 불러오기 

def get_occuCd(): # 직업 json load 
    with open('./_json/occupation.json', "r", encoding="UTF8") as file:
        json_data = json.load(file)
    return json_data

def get_counts_skills(jobsNm):
    path = ap.get_path(f"skills/counts/{jobsNm}.csv")
    try:
        df = pd.read_csv(path)
        return df.values.tolist()
    except:
        return None
    
def get_tfidf_skills(jobsNm):
    path = ap.get_path(f"skills/tf_idf/{jobsNm}.csv")
    try:
        df = pd.read_csv(path)
        return df.values.tolist()
    except:
        return None
    
def get_job_skills(jobsNm):
    path = ap.get_path(f"skills/set/{jobsNm}.csv")
    try:
        df = pd.read_csv(path)
        return df.values.tolist()
    except:
        return None

def get_all_skills():
    path = ap.get_path(f"skills/all_skill.csv")
    try:
        df = pd.read_csv(path)
        return df.values.tolist()
    except:
        return None
    
def get_counts_skill():
    mongoKEY = ap.mongo_key()
    client = MongoClient(mongoKEY, tlsCAFile=certifi.where())
    db = client.job

    # json load
    occuCd = get_occuCd() # 직업정보 불러오기 

    occu1_keys = list(occuCd.keys())
    for occu1 in occu1_keys:
        occu2_keys = list(occuCd[occu1].keys())
        for occu2 in occu2_keys:
            occu3_keys = occuCd[occu1][occu2]['depth3']
            for occu3 in occu3_keys:
                skill_set = get_all_skills()
                if skill_set != None:
                    skill_tf = [0 for i in range(len(skill_set))]
                    dess =  list(db.employment.find({"occupation3" : occu3[0]},{'_id' : False}))
                    print(occu3[1])
                    for des in dess:
                        title = des['wantedInfo']['jobCont']
                        for idx, skill in enumerate(skill_set):
                            skill = str(skill[1])
                            # print(skill)
                            title = str(title)
                            title = title.upper()
                            tf = 0
                            cnt = 0
                            while title[cnt+1:].find(skill) != -1:
                                cnt = title[cnt+1:].find(skill) + cnt + 1
                                tf = tf + 1
                            skill_tf[idx] = skill_tf[idx] + tf
                            if skill_tf[idx] > 0:
                                print(skill, skill_tf[idx])
                            
                    

                    with open(f'C:/Users/DSL/Desktop/Balance_Up/skills/tf_idf/{occu3[1]}.csv', 'w', encoding='utf-8', newline="") as f:
                        write =csv.writer(f)
                        cols = ["idx","skill", "tf"]#[regNm, occuNm, skills]
                        write.writerow(cols)
                        for idx, skill_name in enumerate(skill_set):
                            write.writerow([idx, skill_name[1], skill_tf[idx]])


def cal_df():
    mongoKEY = ap.mongo_key()
    client = MongoClient(mongoKEY, tlsCAFile=certifi.where())
    db = client.job
    path = ap.get_path("skills/")
    dataframe = pd.read_csv(path+'all_skill.csv')
    dataframe = dataframe.values.tolist()
    try:
        skill_df = [0 for i in range(len(dataframe))]
        max_value = len(dataframe) # 같아지면 break
        occuCd = get_occuCd() # 직업정보 불러오기 
        occu1_keys = list(occuCd.keys())
        for occu1 in occu1_keys:
            occu2_keys = list(occuCd[occu1].keys())
            for occu2 in occu2_keys:
                occu3_keys = occuCd[occu1][occu2]['depth3']
                for occu3 in occu3_keys:
                    dess =  list(db.employment.find({"occupation3" : occu3[0]},{'_id' : False}))
                    chk_count = 0
                    print(f"occu name : {occu3[1]}, chkcount : {skill_df}")
                    skill_chk = [False for i in range(len(dataframe))]
                    for des in dess:
                        title = des['wantedInfo']['jobCont']
                        title = title.upper()
                        for idx, skills in enumerate(dataframe):
                            if title.find(skills[1]) != -1 and skill_chk[idx] == False:
                                skill_df[idx] = skill_df[idx] + 1
                                skill_chk[idx] = True
                                chk_count = chk_count + 1
                                break
                        if max_value == chk_count:
                            break
        with open(f'C:/Users/DSL/Desktop/Balance_Up/skills/skill_df copy.csv', 'w', encoding='utf-8', newline="") as f:
            write =csv.writer(f)
            cols = ["idx","skill", "df"]#[regNm, occuNm, skills]
            write.writerow(cols)
            for idx, skill_name in enumerate(dataframe):
                write.writerow([idx, skill_name[1], skill_df[idx]])
    except :
        with open(f'C:/Users/DSL/Desktop/Balance_Up/skills/skill_df copy.csv', 'w', encoding='utf-8', newline="") as f:
                write =csv.writer(f)
                cols = ["idx","skill", "df"]#[regNm, occuNm, skills]
                write.writerow(cols)
                for idx, skill_name in enumerate(dataframe):
                    write.writerow([idx, skill_name[1], skill_df[idx]])


def get_tf_idf():
    occuCd = get_occuCd()
    occu1_keys = list(occuCd.keys())
    for occu1 in occu1_keys:
        occu2_keys = list(occuCd[occu1].keys())
        for occu2 in occu2_keys:
            occu3_keys = occuCd[occu1][occu2]['depth3']
            for occu3 in occu3_keys:
                tmp = get_counts_skills(occu3[1])
                if tmp != None:
                    skill_counts = list()
                    doc_num = None
                    for i in range(len(tmp)-1):
                        skill_counts.append(tmp[i])
                    doc_num = tmp[len(tmp)-1][2]

                    tf_idf = [None for i in range(len(skill_counts))]
                    for idx, skill in enumerate(skill_counts): # idx,skill_name, counts
                        tf = skill[3]
                        df = skill[2]
                        idf = math.log(doc_num/df+1)
                        tf_idf[idx] = float(tf) * idf
                        print(tf_idf[idx])
                    with open(f'C:/Users/DSL/Desktop/Balance_Up/skills/tf_idf/{occu3[1]}.csv', 'w', encoding='utf-8', newline="") as f:
                        write =csv.writer(f)
                        cols = ["idx","skill","df","tf", "tfidf"]#[regNm, occuNm, skills]
                        write.writerow(cols)
                        for idx, skill_name in enumerate(skill_counts):
                            write.writerow([idx, skill_name[1], skill_name[2], skill_name[3], tf_idf[idx]])
                    # print(skill_counts)
                    # print(occu3[1], doc_num)
                    

def cal_tf_idf(tf, df, D = 236):
    idf = np.log(D /(df+1))
    tfidf = tf * idf
    return tfidf

def cal_tf_df():
    path = ap.get_path("skills/")
    tp = pd.read_csv(path+"skill_df.csv")
    skill_df = tp.values.tolist() # col 0 : idx, col 1: skill_name, col 2 : df

    job_list = list(os.listdir(path+'pre_processing_tf'))
    for job_name in job_list:
        tp = pd.read_csv(path+'pre_processing_tf/'+job_name)
        job_skills = tp.values.tolist() # idx, skill_name, tf
        tf_idf_list = list()
        for idx, df in enumerate(skill_df):
            tf_idf = -1
            last_tf = None
            for j_skills in job_skills:
                if df[1] == j_skills[1]:
                    tf_idf = cal_tf_idf(j_skills[2], df[2])
                    last_tf = j_skills[2]
                    if tf_idf == 0:
                        if j_skills[2] == 0:
                            tf_idf = cal_tf_idf(00.1, df[2])
                            last_tf = 0.01
                        else:
                            tf_idf = cal_tf_idf(j_skills[2], df[2]-1)
                    break
            if tf_idf == -1: # tf가 0
                tf_idf = cal_tf_idf(0.01, df[2])
                last_tf = 0.01
            tf_idf_list.append([df[1], last_tf, df[2], tf_idf]) # skillname, tf, df, tfidf
        tf_idf_list.sort(key=lambda x:x[3], reverse=True)
        print(tf_idf_list)
        with open(f'C:/Users/DSL/Desktop/Balance_Up/skills/expr_tfidf001/{job_name}', 'w', encoding='utf-8', newline="") as f:
            write =csv.writer(f)
            cols = ["idx","skill", "tf", "df", "tfidf"]#[regNm, occuNm, skills]
            write.writerow(cols)
            for idx, li in enumerate(tf_idf_list):
                write.writerow([idx, li[0],li[1], li[2], li[3]])



def cal_tfidf_pr():
    # path = ap.get_path("skills/tf_idf/C언어 및 그 외 프로그래밍 언어 전문가.csv")
    # df = pd.read_csv(path)
    # sum = df['tfidf'].sum()
    # df['pr'] = df['tfidf'] / sum
    # print(df)
    # path = ap.get_path('skills/tfidf_pr/')
    # df.to_csv(path+'C언어 및 그 외 프로그래밍 언어 전문가.csv', mode='w', index=False)

    path = ap.get_path("skills/expr_tfidf001/")
    save_path = ap.get_path('skills/expr_tfidf001/')
    job_list = list(os.listdir(path))
    for job in job_list:
        df = pd.read_csv(path+job)
        tfidf_sum = df['tfidf'].sum()
        df['pr'] = df['tfidf'] / tfidf_sum
        df.to_csv(save_path+job, mode='w', index=False)











def soft_max(a):
    # 기본 구하는 방법
    # exp_a = np.exp(a)
    # sum_exp_a = np.sum(exp_a)
    # y = exp_a / sum_exp_a
    # return y

    # 값이 커지면 구하는 방법  RuntimeWarning: invalid value encountered in divide 이런거 날 때
    f = np.exp(a- np.max(a))
    return f / f.sum(axis=0)

def get_soft_max():
    occuCd = get_occuCd()
    occu1_keys = list(occuCd.keys())
    for occu1 in occu1_keys:
        occu2_keys = list(occuCd[occu1].keys())
        for occu2 in occu2_keys:
            occu3_keys = occuCd[occu1][occu2]['depth3']
            for occu3 in occu3_keys:
                tfidf_list = get_tfidf_skills(occu3[1])
                if tfidf_list != None:
                    tf_idf = list()
                    for i in tfidf_list:
                        tf_idf.append(i[4])
                    sfm = soft_max(tf_idf)

                    with open(f'C:/Users/DSL/Desktop/Balance_Up/skills/soft_max/{occu3[1]}.csv', 'w', encoding='utf-8', newline="") as f:
                        write =csv.writer(f)
                        cols = ["idx","skill","df","tf", "tfidf",'softmax']#[regNm, occuNm, skills]
                        write.writerow(cols)
                        for idx, skill_name in enumerate(tfidf_list):
                            write.writerow([idx, skill_name[1], skill_name[2], skill_name[3],skill_name[4], sfm[idx]])

if __name__ == '__main__':
    cal_tfidf_pr()
    # li = get_tfidf_skills("직업상담사")
    # tf_idf = list()
    # for i in li:
    #     tf_idf.append(i[4])
    # print(tf_idf)
    # print(soft_max(tf_idf))
    # skill_set = get_job_skills('직업상담사')
    # skill_count = [0 for i in range(len(skill_set))]
    # print(len(skill_set))
    # print(len(skill_count))