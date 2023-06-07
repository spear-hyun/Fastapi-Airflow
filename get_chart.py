import pandas as pd
from bs4 import BeautifulSoup as BS
import time
import pathlib
import airflow.utils.dates
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
import requests
from datetime import date, datetime 


dag = DAG(
    dag_id="get_chart",
    description="music chart data",
    start_date=datetime(2023, 5, 26, 0, 0),  # 시작 날짜 및 시간 설정
    schedule_interval='0 * * * *',  # 매 시간 정각에 실행 (cron 표현식)
)


def _vibe_chart():
    pathlib.Path("/home/airflow/data/").mkdir(parents=True, exist_ok=True)
    url = "https://apis.naver.com/vibeWeb/musicapiweb/vibe/v1/chart/track/total?start=1&display=100"
    r = requests.get(url)
    bs = BS(r.text, 'xml')
    vibe_list = []


    for idx, vibe in enumerate(bs.find("items").find("tracks").findAll("track")):
        vibe_dict = {}
        vibe_dict['Title'] = vibe.find("trackTitle").text
        vibe_dict['Artist'] = vibe.find("artists").find("artistName").text
        vibe_dict['Rank_score'] = 100 - idx
        vibe_dict['Img_src'] = vibe.find("imageUrl").text
        vibe_dict['Source'] = "vibe"

        vibe_list.append(vibe_dict)
    vibe_total = pd.DataFrame(vibe_list)
    vibe_total.to_csv("/home/airflow/data/vibe_chart.csv")

    

vibe_chart = PythonOperator(
    task_id="vibe_chart", python_callable=_vibe_chart, dag=dag
)

def _melon_chart():
    url = "https://www.melon.com/chart/index.htm"
    head = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    r = requests.get(url, headers= head)
    bs = BS(r.text)
    melon_list = []


    for idx, melon in enumerate(bs.findAll("tr", class_="lst50")):
        melon_dict = {}
        melon_dict['Title'] = melon.findAll("td")[5].findAll("a")[0].text
        melon_dict['Artist'] = melon.findAll("td")[5].findAll("a")[1].text
        if melon.findAll("td")[5].findAll("a")[2]:
            artists = melon.findAll("td")[5].findAll("a")[2].text
            melon_dict['Artist'] = melon_dict['Artist']+ f"& {artists}"
        melon_dict['Rank_score'] = 100 - idx
        melon_dict['Img_src'] = melon.find("img")['src']
        melon_dict['Source'] = "melon"

        melon_list.append(melon_dict)

    for idx, melon in enumerate(bs.findAll("tr", class_="lst100")):
        melon_dict = {}
        melon_dict['Title'] = melon.findAll("td")[5].findAll("a")[0].text
        melon_dict['Artist'] = melon.findAll("td")[5].findAll("a")[1].text
        if melon.findAll("td")[5].findAll("a")[2]:
            artists = melon.findAll("td")[5].findAll("a")[2].text
            melon_dict['Artist'] = melon_dict['Artist']+ f"& {artists}"
        melon_dict['Rank_score'] = 50 - idx
        melon_dict['Img_src'] = melon.find("img")['src']
        melon_dict['Source'] = "melon"

        melon_list.append(melon_dict)
    melon_total = pd.DataFrame(melon_list)
    melon_total.to_csv("/home/airflow/data/melon_chart.csv")

melon_chart = PythonOperator(
    task_id="melon_chart", python_callable=_melon_chart, dag=dag
)

def _flo_chart():
    url ="https://www.music-flo.com/api/display/v1/browser/chart/1/track/list?size=100"
    r = requests.get(url)
    flo_list = []

    for num in range(100):
        flo_dict={}
        flo_dict['Title'] = r.json()['data']['trackList'][num]['name']
        flo_dict['Artist'] = r.json()['data']['trackList'][num]['representationArtist']['name']
        flo_dict['Rank_score'] = 100 - num
        flo_dict['Img_src'] = r.json()['data']['trackList'][num]['album']['imgList'][1]['url']
        flo_dict['Source'] = "flo"

        flo_list.append(flo_dict)
    flo_total = pd.DataFrame(flo_list)
    flo_total.to_csv("/home/airflow/data/flo_chart.csv")


flo_chart = PythonOperator(
    task_id="flo_chart", python_callable=_flo_chart, dag=dag
)



def _genie_chart():
    today = str(date.today()).replace("-","")
    time_ = (str(datetime.now()).split()[1])[:2]
    url = f"https://www.genie.co.kr/chart/top200?ditc=D&ymd={today}3&hh={time_}&rtm=Y&pg=1"
    head = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    r = requests.get(url, headers= head)
    bs = BS(r.text)
    genie_list= []

    for num in range(2):
        for idx, genie in enumerate(bs.findAll("td", class_="info")):
            genie_dict={}
            genie_dict['Title'] = genie.find("a", class_="title ellipsis").text.strip()
            genie_dict['Artist'] = genie.find("a", class_="artist ellipsis").text.strip()
            if num == 1:
                genie_dict['Rank_score'] = 50 - idx    
            else:    
                genie_dict['Rank_score'] = 100 - idx
            genie_dict['Img_src'] = bs.findAll("tr", class_="list")[idx].find("img")['src'].replace("//","")
            genie_dict['Source'] = "genie"

            genie_list.append(genie_dict)
        url = f"https://www.genie.co.kr/chart/top200?ditc=D&ymd={today}3&hh={time_}&rtm=Y&pg=2"    
        r = requests.get(url, headers= head)
        bs = BS(r.text)

            
    genie_total = pd.DataFrame(genie_list)
    genie_total.to_csv("/home/airflow/data/genie_chart.csv")

genie_chart = PythonOperator(
    task_id="genie_chart", python_callable=_genie_chart, dag=dag
)

def _final_chart():
    ## 음악사이트별 차트 불러오기

    flo_total = pd.read_csv("/home/airflow/data/flo_chart.csv")
    genie_total = pd.read_csv("/home/airflow/data/genie_chart.csv")
    vibe_total = pd.read_csv("/home/airflow/data/vibe_chart.csv")
    melon_total = pd.read_csv("/home/airflow/data/melon_chart.csv")
   ## 일단 네 개의 차트 합치기
    total=pd.concat([flo_total,vibe_total,genie_total,melon_total], ignore_index=True)

    ## 인덱스를 초기화하고 점수로 정렬하고 100개만 저장
    total_group=total.groupby('Title', as_index=False).sum().sort_values(by='Rank_score', ascending=False).reset_index()[:100]

    ## index 컬럼 삭제
    total_group.drop("index", axis=1, inplace=True)

    ## total에서 제목, 가수 컬럼만 남기고 삭제
    total.drop("Rank_score", axis=1, inplace=True)
    total.drop("Source", axis=1, inplace=True)

    ## Title를 기준으로 merge
    merged = pd.merge(total_group, total, on='Title', how='inner')

    ## 컬럼 순서 변경
    merged = merged[['Title','Artist','Rank_score','Img_src']]

    ## 제목값을 기준으로 중복값 삭제
    music_chart = merged.drop_duplicates(subset='Title')

    ## 인덱스 초기화
    music_chart = music_chart.reset_index(drop=True)

    ## 순위 컬럼 추가 
    music_chart['Rank'] = "NULL"
    for num in range(100):
        music_chart['Rank'].iloc[num] = str(num+1) + "위"

    ## 컬럼 순서 변경 
    music_chart = music_chart[['Rank','Img_src','Title','Artist','Rank_score']]
    ## 파일 저장
    music_chart.to_csv("/home/airflow/data/music_chart.csv")

final_chart = PythonOperator(
    task_id="final_chart", python_callable=_final_chart, dag=dag
)


notify = BashOperator(
    task_id="notify",
    bash_command='uvicorn main:app --reload',
    dag=dag,
)

vibe_chart >> flo_chart >> genie_chart >> melon_chart >> final_chart >> notify