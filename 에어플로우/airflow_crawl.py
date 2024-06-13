from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import pandas as pd

import json
from airflow import DAG
from pendulum import yesterday
from datetime import timedelta
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.sensors.filesystem import FileSensor

dag = DAG(
    dag_id="crawl",
    schedule_interval=None,
    start_date=yesterday("Asia/Seoul"),
    catchup=False
)

def python_task():
    # 브라우저 꺼짐 방지 옵션
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(options=chrome_options)

    # 저장 df 만들기
    data=[]

    # 주소 및 실행
    url = "https://m.place.naver.com/restaurant/248457052/review/visitor?entry=ple&reviewSort=recent"
    driver.get(url)
    time.sleep(5)

    # 웹페이지의 가장 하단까지 내려라
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')

    # 무한 루프를 시작합니다.
    while True:
        try:
            # 요소를 찾습니다.
            element = driver.find_element(By.CLASS_NAME, 'TeItc')
            driver.find_element(By.CLASS_NAME, value='TeItc').click()
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')

        except Exception as e:
            # 요소가 존재하지 않으면 멈춥니다.
            break

    time.sleep(3)
    print('wait')

    html = driver.page_source
    soup=BeautifulSoup(html, 'html.parser')

    # 매장명, 카테고리
    store = soup.select_one("#_title > div > span.Fc1rA").text
    category = soup.select_one("#_title > div > span.DJJvD").text

    items = soup.select('.YlrAu')
    today=datetime.now().strftime("%Y.%m.%d")
    for item in items:
        nickname = item.select_one(".P9EZi").text
        review = item.select_one(".xHaT3 > span").text
        date = item.select_one(".CKUdu > time").text

        if date.startswith(today):
            data.append([store, category, nickname, review, date])


    time.sleep(3)

    # 데이터 프레임 만들기
    df= pd.DataFrame(data, columns=[store, category, nickname, review, date])

    # 엑셀 저장
    today_str = datetime.now().strftime('%Y-%m-%d')
    filename = f'/home/big/temp/result_{today_str}.csv'
    df.to_csv(filename, index=False)

    print('finished!')

    driver.quit()
#############################################

crawling = PythonOperator(
    task_id="crawling",
    python_callable=python_task,
    dag=dag
)

exists = FileSensor(
    task_id="exists",
    filepath="/home/big/temp/result_{today_str}.csv",
    poke_interval=30,
    dag=dag
)

upload=BashOperator(
    task_id="upload",
    global filename
    global today_str
    bash_command=f'hdfs dfs -put {filename} /review_{today_str}.csv',
    dag=dag
)


prn = BashOperator(
    task_id="prn",
    bash_command='echo "success makefile & upload"',
    dag=dag
)

crawling >> [make_file, exists] >> upload >> prn



