from pymongo import MongoClient
import certifi
import json
import csv
import pandas as pd
import openai
import api_key as ky

def get_regionCd(): # 서울 제외 지역코드 얻어오기
    with open('./_json/region_non_seoul.json', "r", encoding="UTF8") as file:
        json_data = json.load(file)
    return json_data

def get_occuCd(): # 직업 json load 
    with open('./_json/occupation.json', "r", encoding="UTF8") as file:
        json_data = json.load(file)
    return json_data

def getSkill_to_GPT_Chat(ment): # skill을 GPT를 활용하여 추출

    openai.api_key= ky.finetuned_gpt_key() # fine tunes
    prompt = ment + '\n 해당 문장에서 skill을 추출해줘.'
    model = ky.get_model()
    response = openai.ChatCompletion.create(
        model= model, # fine_tuned_model 
        messages=[
            {"role": "system", "content": "너는 Skill을 추출하는 assistant야."},
            {"role": "user","content": prompt},
        ],
        temperature=0,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].message.content


def extraction_data(des_list, regNm, occuNm, curLn): # 설명, 지역이름, 직업이름
    if len(des_list) > 0: # 채용공고 있는 경우 
        result = list()
        ln = len(des_list)
        if ln + curLn > 10:
            ln = 10 - curLn
            if ln < 0:
                ln = 0
        try:
            for i in range(ln):
                if des_list[i] is None:
                    continue
                else:
                    print(regNm, occuNm)
                    ment = des_list[i]['wantedInfo']['jobCont']
                    ln = ment.split(' ')
                    if len(ln) > 200:
                        ment = ment[int(len(ment)/2):]
                    skills = getSkill_to_GPT_Chat(ment)
                    result.append([regNm, occuNm, skills])
            if len(result) == 0: 
                return None
            else : 
                return result
        except :
            with open(f'C:/Users/DSL/Desktop/Balance_Up/skills/{occuNm}.csv', 'w', encoding='utf-8', newline="") as f:
                    write =csv.writer(f)
                    cols = ["지역", "직업", "skill"]#[regNm, occuNm, skills]
                    write.writerow(cols)
                    write.writerows(result)
    else : # 채용공고 없는 경우 
        return None


def main():
    # DB load
    mongoKEY = ky.mongo_key()
    client = MongoClient(mongoKEY, tlsCAFile=certifi.where())
    db = client.job

    # json load
    regionCd = get_regionCd() # 지역정보 불러오기 
    occuCd = get_occuCd() # 직업정보 불러오기 

    # extraction
    occu1_keys = list(occuCd.keys())
    region_keys = list(regionCd.keys())
    for occu1 in occu1_keys:
        occu2_keys = list(occuCd[occu1].keys())
        for occu2 in occu2_keys:
            occu3_keys = occuCd[occu1][occu2]['depth3']
            for occu3 in occu3_keys:
                result = list() # 결과 저장
                for regCd in region_keys:
                    if len(regionCd[regCd]['depth2']) == 0: # 세종 예외
                        des = list(db.employment.find({"occupation3" : occu3[0], "regionCd" : regCd},{'_id' : False}))
                        tmp_result = extraction_data(des, regionCd[regCd]['depth1'], occu3[1], len(result))
                        if tmp_result != None:
                            result.extend(tmp_result)
                    else : # 세종 외 지역
                        for cd, name in regionCd[regCd]['depth2']: # 지역코드, 지역이름
                            des =  list(db.employment.find({"occupation3" : occu3[0], "regionCd" : cd},{'_id' : False}))
                            tmp_result = extraction_data(des,name, occu3[1], len(result))
                            if tmp_result != None:
                                result.extend(tmp_result)
                with open(f'C:/Users/DSL/Desktop/Balance_Up/skills/{occu3[1]}.csv', 'w', encoding='utf-8', newline="") as f:
                    write =csv.writer(f)
                    cols = ["지역", "직업", "skill"]#[regNm, occuNm, skills]
                    write.writerow(cols)
                    write.writerows(result)

if __name__ == "__main__":
    main()
