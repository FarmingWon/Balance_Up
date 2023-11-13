from pymongo import MongoClient
import certifi
import json
import csv
import pandas as pd
import api_key as ap
import os
import numpy as np

def get_regionCd():
    with open('_json/region_only_seooul.json', "r", encoding="UTF8") as file:
        json_data = json.load(file)
    return json_data

def get_occuCd(): # 직업 json load 
    with open('./_json/occupation.json', "r", encoding="UTF8") as file:
        json_data = json.load(file)
    return json_data

def recommed(text): # 채용공고 불러왕 
    text = text.upper()
    pr_path = ap.get_path('skills/expr_tfidf001/')
    job_list = list(os.listdir(pr_path))
    result = list()
    for job in job_list:
        df = pd.read_csv(pr_path+job) #idx,skill,tf,df,tfidf,pr 
        job_li = df.values.tolist()
        pr = 0
        for li in job_li:
            if text.find(li[1]) != -1 and (len(li[1]) > 1 or li[1] == 'C') :
                pr = pr + np.log(li[5])
        if pr == 1 :
            pr = 0
        result.append([job[:len(job)-4], pr])
    result.sort(key=lambda x:x[1], reverse=True)
    return result

def eval():
    mongoKEY = ap.mongo_key()
    client = MongoClient(mongoKEY, tlsCAFile=certifi.where())
    db = client.job

    regionCd = get_regionCd()
    region_keys = list(regionCd.keys())

    # @15까지 측정 
    Precision_Total = [0 for i in range(15)] # Total
    Precision_T = [0 for i in range(15)] # 맞은 개수 

    Recall_Total = [0 for i in range(15)] # Total
    Recall_T = [0 for i in range(15)] # 맞은 개수 

    occuCd = get_occuCd()
    occu1_keys = list(occuCd.keys())
    for occu1 in occu1_keys:
        occu2_keys = list(occuCd[occu1].keys())
        for occu2 in occu2_keys:
            occu3_keys = occuCd[occu1][occu2]['depth3']
            for occu3 in occu3_keys:
                count = [0 for i in range(15)]
                tmp_t = [0 for i in range(15)]
                rec_count = [0 for i in range(15)]
                rec_t = [0 for i in range(15)]
                result = list()
                for regCd in region_keys:
                    for cd, name in regionCd[regCd]['depth2']: # 지역코드, 지역이름
                        try:
                            des =  list(db.employment.find({"occupation3" : occu3[0], "regionCd" : cd},{'_id' : False}))
                            if len(des) > 0:
                                for d in des: # 한 개의 채용공고 
                                    ment = d['wantedInfo']['jobCont']
                                    rec_jobs = recommed(ment) # 추천된 직업
                                    ans = d['wantedInfo']['jobsNm']
                                    ans = ans[:len(ans)-8]
                                    ans = ans.strip()
                                    sec_ans = d['wantedInfo']['relJobsNm']
                                    sec_ans = sec_ans.strip()
                                    print(ans, sec_ans)
                                    for i in range(15):
                                        rec1 = False
                                        rec2 = False
                                        for j in range(0, i+1):
                                            if ans == rec_jobs[j][0].strip() or sec_ans == rec_jobs[j][0].strip():
                                                Precision_T[i] = Precision_T[i] + 1
                                                tmp_t[i] = tmp_t[i] + 1
                                                if ans == rec_jobs[j][0].strip():
                                                    rec1= True
                                                else:
                                                    rec2 = True
                                            else:
                                                if j == 14:
                                                    result.append([rec_jobs[j][0],
                                                                sec_ans, 
                                                                ans])
                                            Precision_Total[i] = Precision_Total[i] + 1
                                            count[i] = count[i] + 1
                                        if sec_ans != '':
                                            Recall_Total[i] = Recall_Total[i] + 2 
                                            rec_count[i] = rec_count[i] + 2
                                        else:
                                            Recall_Total[i] = Recall_Total[i] + 1 
                                            rec_count[i] = rec_count[i] + 1
                                        point = 0
                                        if rec1 == True and rec2 == True:
                                            point = 2
                                        elif rec1 == True:
                                            point = 1
                                        elif rec2 == True:
                                            point = 1
                                        Recall_T[i] = Recall_T[i] + point
                                        rec_t[i] = rec_t[i] + point
                        except Exception as e:
                            continue
                try:
                    with open(f'C:/Users/DSL/Desktop/Balance_Up/result2/{occu3[1]}.csv', 'w', encoding='utf-8', newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow(['Precision'])
                        cols = ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T10', 'T11', 'T12', 'T13', 'T14', 'T15']
                        writer.writerow(cols)
                        writer.writerow(tmp_t)
                        writer.writerow(count)
                        writer.writerow([])

                        writer.writerow(['Recall'])
                        writer.writerow(cols)
                        writer.writerow(rec_t)
                        writer.writerow(rec_count)
                        writer.writerow([])

                        writer.writerow(['T1_ans','관련직업','정답직업'])
                        writer.writerows(result)
                except Exception as e:
                    print(e, occu3[1])
                    continue

    print(f"Precision_T : {Precision_T}")
    print(f"Precision_Total : {Precision_Total}")
    print(f"Recall_T : {Recall_T}")
    print(f"Recall_Total : {Recall_Total}")
    result_precision = [0 for i in range(15)]
    result_recall = [0 for i in range(15)]
    for i in range(15):
        result_precision[i] = Precision_T[i]/Precision_Total[i]
        result_recall[i] = Recall_T[i] / Recall_Total[i]
    with open(f'C:/Users/DSL/Desktop/Balance_Up/result/RESULT2.csv', 'w', encoding='utf-8', newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Precision_T", Precision_T])
        writer.writerow(['Precision_Total' , Precision_Total])
        writer.writerow(['Recall_T', Recall_T])
        writer.writerow(['Recall_Total', Recall_Total])
        writer = csv.writer(f)
        Precision_T.insert(0, "Precision_T")
        Precision_Total.insert(0,'Precision_Total')
        result_precision.insert(0, 'Result')
        writer.writerow(Precision_T)
        writer.writerow(Precision_Total)
        writer.writerow(result_precision)
        writer.writerow([])
        Recall_T.insert(0, "Recall_T")
        Recall_Total.insert(0,'Recall_Total')
        result_recall.insert(0, 'Result')
        writer.writerow(Recall_T)
        writer.writerow(Recall_Total) 
        writer.writerow(result_recall)
    

def cal():
    path = 'C:/Users/DSL/Desktop/Balance_Up/result/'
    li = list(os.listdir(path))

    total_precision = [0 for i in range(15)]
    total_recall = [0 for i in range(15)]
    ans_precision = [0 for i in range(15)]
    ans_recall = [0 for i in range(15)]

    # 파일 읽기
    try:
        for name in li:
            if name == "RESULT.csv":
                continue
            with open(path+name, "r") as f:
                lines = f.readlines()

            # Precision 부분 읽기
            header_precision = lines[1].strip().split(",")
            data_precision = [list(map(int, line.strip().split(","))) for line in lines[2:4]]

            df_precision = pd.DataFrame(data_precision, columns=header_precision)

            # Recall 부분 읽기
            header_recall = lines[6].strip().split(",")
            data_recall = [list(map(int, line.strip().split(","))) for line in lines[7:9]]

            df_recall = pd.DataFrame(data_recall, columns=header_recall)

            precisions = df_precision.values.tolist() # 0행 내가 맞춘거, 1행 Total
            recalls = df_recall.values.tolist()
            for i in range(15):
                # total_precision[i] = total_precision[i] + precisions[1][0]
                total_precision[i] = total_precision[i] + precisions[1][i]
                ans_precision[i] = ans_precision[i] + precisions[0][i]

                total_recall[i] = total_recall[i] + recalls[1][i]
                ans_recall[i] = ans_recall[i] + recalls[0][i]
        result_precision = [0 for i in range(15)]
        result_recall = [0 for i in range(15)]
        for i in range(15):
            result_precision[i] = ans_precision[i]/total_precision[i]
            result_recall[i] = ans_recall[i] / total_recall[i]

        with open(f'C:/Users/DSL/Desktop/Balance_Up/result/RESULT.csv', 'w', encoding='utf-8', newline="") as f:
            writer = csv.writer(f)
            ans_precision.insert(0, "Precision_T")
            total_precision.insert(0,'Precision_Total')
            result_precision.insert(0, 'Result')
            writer.writerow(ans_precision)
            writer.writerow(total_precision)
            writer.writerow(result_precision)
            writer.writerow([])
            ans_recall.insert(0, "Recall_T")
            total_recall.insert(0,'Recall_Total')
            result_recall.insert(0, 'Result')
            writer.writerow(ans_recall)
            writer.writerow(total_recall) 
            writer.writerow(result_recall)
    except Exception as e:
        print(name, e)



if __name__ == '__main__':
    eval()