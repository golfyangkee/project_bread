import requests
import re
from urllib.parse import quote
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import csv

keyword = quote(input("Enter ur search keyword ! : "))

options = webdriver.EdgeOptions()
driver = webdriver.Edge(options=options)

url_serve = "https://m.place.naver.com/place/list?query="
search_url = url_serve + "{}" + "&level=top&sortingOrder=precision"
search_url = search_url.format(keyword)
print(search_url)

driver.get(search_url)

driver.switch_to.window(driver.current_window_handle)

wait = WebDriverWait(driver, 10)
body = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

session = requests.Session()
headers = {"User-Agent": "Edge 122 on Windows 11"}

retries = Retry(total=5,
                backoff_factor=0.1,
                status_forcelist=[500, 502, 503, 504])
session.mount('http://', HTTPAdapter(max_retries=retries))

body.click()

scroll_count = 200
for _ in range(scroll_count):
    body.send_keys(Keys.PAGE_DOWN)
    time.sleep(0.5)

html = driver.page_source
bs = BeautifulSoup(html, 'html.parser')

soup = bs.select_one('div.YluNG')  # 업체 리스트 출력 박스

naver_info = soup.select('li.VLTHu')  # 업체별 info 박스

with open('Store_info.csv', 'w', newline='', encoding='utf-8-sig') as file:
    writer = csv.writer(file)
    writer.writerow(['store_name', 'mart_cate', 'tel', 'address', 'link'])

    for info in naver_info:
        store_name = info.select_one(
            'li.VLTHu > div.qbGlu > div.ouxiq > a.P7gyV > div.ApCpt > div.place_bluelink > span.YwYLL').text
        mart_cate = info.select_one('span.YzBgS').text
        link = info.select_one('div.ouxiq').select_one('a').attrs['href']
        tel = info.select_one('span.JsCty a')['href']
        tel = tel.replace('tel:', '')
        if not re.match(r'^\d{2,4}-\d{3,4}-\d{4}$', tel):
            tel = ''
        address = info.select_one('a[data-line-description]')['data-line-description']

        print(store_name, mart_cate, tel, address, link)
        time.sleep(0.06)

        writer.writerow([store_name, mart_cate, tel, address, link])
print("successful save ଘ(੭ ᐛ )━☆ﾟ.*･｡ﾟ !")
