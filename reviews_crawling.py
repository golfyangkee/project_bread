import re
import time
import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

links = []

with open('Store_info.csv', 'r', encoding='utf-8-sig') as file:
    csv_reader = csv.reader(file)
    next(csv_reader)
    for row in csv_reader:
        links.append(row[4])

options = webdriver.EdgeOptions()
driver = webdriver.Edge(options=options)

reviews_data = []

total_links = len(links)
for index, link in enumerate(links[:3]):  # 동작 수행을 테스트 하고 싶다면 [:n]
    print(f"Processing link {index + 1}/{total_links}({(index + 1)/total_links * 100:.2f}%)")

    rvw_link = link.replace('/place/', '/restaurant/')
    rvw_link = rvw_link.replace('?entry=ple', '/review/visitor?entry=ple')
    print(rvw_link)
    driver.get(rvw_link)

    try:
        more_buttons = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".xHaT3"))
        )
    except TimeoutException:
        print("Timed out waiting for more buttons to load")
        continue

    for button in more_buttons:
        try:
            button.click()
            time.sleep(1)
        except Exception as e:
            print("Error clicking more button:", e)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    store_name = soup.find_all("span", class_="Fc1rA")[0].text
    print(store_name)

    mart_cate = soup.find_all("span", class_="DJJvD")[0].text
    print(mart_cate)

    for element in soup.find_all('li', class_='owAeM'):
        try:
            # element.find('a', class_="xHaT3")['aria-expanded'] = 'true'
            # print(element.find('a', class_="xHaT3")['aria-expanded'])
            a_tag = element.find('a', class_="xHaT3")
            if a_tag:
                a_tag['aria-expanded'] = 'true'
            review = element.find('div', class_='vg7Fp').find('a').find('span', class_='zPfVt').text
            print(review, ";;*")

            visit_date_tag = element.find("div", class_="jxc2b").find("span", class_="CKUdu")
            visit_date = visit_date_tag.find_all('span', class_="place_blind")[1].text
            print(visit_date)

            CKUdu_tag = element.find("div", class_="jxc2b").find_all("span", class_="CKUdu")
            visit_count_tag = CKUdu_tag[1].text
            visit_count = re.findall(r'\d+', visit_count_tag)[0]
            print(visit_count)

            reviews_data.append((store_name, mart_cate, visit_date, visit_count, review))
        except Exception as e:
            print(f"An error occurred while processing an element: {e}")
            continue

# with open('reviews_total.csv', 'w', newline='', encoding='utf-8-sig') as file:
#     writer = csv.writer(file)
#     writer.writerow(["store_name", "category", "visit_date", "visit_count", "review"])
#     writer.writerows(reviews_data)
#
# print("Success to save ' ^'/")
