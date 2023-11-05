import os
import pandas as pd
import api_key as ap
import csv
import api_key as ap

def get_dir_name(path): # 전처리 전 skill.csv 파일 이름 얻기
    file_list = os.listdir(path)
    return file_list

def get_csv_info(path, file_name): # 파일 이름 받아서 skill return
    df = pd.read_csv(path+file_name)
    return df.values.tolist()

def get_skills(skill):
    # 전처리 해야됨 
    # 필요 없는 문자 없애기 
    if '활용 가능' in skill: 
        skill = skill.replace('활용 가능', "")
    if '/' in skill:
        skill = skill.replace('/', ',')
    if '(' in skill:
        skill = skill.replace('(', ',')
    if ')' in skill:
        skill = skill.replace(')', "")
    if 'skill' in skill or '없는' in skill or '입니다' in skill or '스킬' in skill:
        return None
    if '"' in skill:
        skill = skill.replace('"', '')
    if '및' in skill:
        skill = skill.replace('및', ',')
    if "&" in skill:
        skill = skill.replace("&", ',')
    return skill
    #각 스킬마다 맨 앞,뒤 공백제거 및 콤마 제거 

def get_token(skill): # ,로 나눠 토큰화
    return skill.split(',')

def save_csv(jobsNm, skills): # csv 저장 
    path = ap.get_path(f"skills/pre_processing_skills/{jobsNm}.csv")

    with open(path, 'w', encoding='UTF8', newline="") as f:
        print(skills)
        write =csv.writer(f)
        cols = ["num","skill"]
        write.writerow(cols)
        for idx, skill in enumerate(skills):
            print(idx, skill)
            if skill != '':
                write.writerow([idx, skill])

def skill_set_save_csv(jobsNm, skills):
    path = ap.get_path(f"skills/set/{jobsNm}.csv")
    skills = list(skills)
    with open(path, 'w', encoding='UTF8', newline="") as f:
        print(skills)
        write =csv.writer(f)
        cols = ["num","skill"]
        write.writerow(cols)
        for idx, skill in enumerate(skills):
            print(idx, skill)
            if skill != '':
                write.writerow([idx, skill])

def main():
    dir_name_list = get_dir_name()
    for name in dir_name_list:
        lists = get_csv_info(name) # 열 : 위치, 직종명, skills
        jobs_name = None
        skill_set = set()
        skill_list = list()
        for li in lists:
            try:
                jobs_name = li[1]
                skill = get_skills(li[2])
                if skill is None:
                    pass
                else:
                    skill_arr = get_token(skill)
                    for idx, arr in enumerate(skill_arr):
                        arr = arr.upper() # 영어 모두 대문자 
                        skill_arr[idx] = arr.strip() # 앞 뒤 공백제거
                        skill_set.add(arr.strip())
                    # print(f"{jobs_name} : {skill_arr}")
                    skill_list.extend(skill_arr)
            except:
                print("err 발생" + li )
                return
            
        if len(skill_list) != 0:
            save_csv(jobs_name, skill_list)
            skill_set_save_csv(jobs_name, skill_set)


def set_all_skills(): # 한 파일에 모든 직업의 skill 집합 만들기
    path = ap.get_path("skills/set/")
    li = get_dir_name(path)
    result = set()
    for name in li:
        print(path+name)
        sets = get_csv_info(path,name)
        print(sets)
        for s in sets:
            skill = s[1]
            result.add(skill)
    print(result)
    with open(f'C:/Users/DSL/Desktop/Balance_Up/skills/all_skill.csv', 'w', encoding='utf-8', newline="") as f:
                        write =csv.writer(f)
                        cols = ["idx","skill"]#[regNm, occuNm, skills]
                        write.writerow(cols)
                        for idx, skill_name in enumerate(result):
                            write.writerow([idx, skill_name])

def tf_pre_processing():
    path = ap.get_path("skills/tf_idf")
    print(path)
    li = get_dir_name(path)
    path = path + "/"
    for name in li:
        result = list()
        print(f"{name} 시작")
        no_preprocessing = get_csv_info(path,name)
        for cnt in no_preprocessing: # 0 : idx,1 : skill_name,2 : tf
            if cnt[2] > 0:
                if len(cnt[1]) != 1 or cnt[1] == 'C':
                    result.append([cnt[1],cnt[2]])
        if len(result) == 0:
            print(name)
        result.sort(key=lambda x:x[1], reverse=True)

        with open(f'C:/Users/DSL/Desktop/Balance_Up/skills/pre_processing_tf_idf/{name}', 'w', encoding='utf-8', newline="") as f:
                    write =csv.writer(f)
                    cols = ["idx","skill", "tf"]#[regNm, occuNm, skills]
                    write.writerow(cols)
                    for idx, skill_name in enumerate(result):
                        write.writerow([idx, skill_name[0], skill_name[1]])

if __name__=="__main__":
    tf_pre_processing()
