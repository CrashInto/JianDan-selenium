from selenium import webdriver
from pyquery import PyQuery as pq
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from config import *
import pymongo
import requests
client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]
browser = webdriver.Chrome()
wait = WebDriverWait(browser,10)

#对目标站点发起请求，返回页数
def search():
    print('正在对目标站点发起访问...')
    try:
        html = browser.get('http://jandan.net/ooxx')
        page_number = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR,'#comments > div:nth-child(4) > div > span'))
        ).text[1:-1]
        get_resource()
        return int(page_number)
    except TimeoutException:
        print('目标站点请求失败...')

#翻页动作
def next_page(num):
    print('---正在获取第'+str(num)+'页---')
    try:
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR,'#comments > div:nth-child(4) > div > a.previous-comment-page'))
        )
        submit.click()
        wait.until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR,'#comments > div:nth-child(4) > div > span'),str(num))
        )
        get_resource()
    except TimeoutException:
        print('翻页失败，请求超时...')
#捕获资源
def get_resource():
    html = browser.page_source
    doc = str(pq(html))
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#comments > ol')))
    soup = BeautifulSoup(doc,'lxml')
    list = soup.select(".text p img")
    for each in list:
        img_link = each.attrs['src']
        if img_link[-3:] == 'jpg':
            sigle_img = {
                'img-link' : img_link
            }
            save_2_mongo(sigle_img)
            save_2_local(img_link)

#存储到MONGODB
def save_2_mongo(result):
    try:
        if db[MONGO_TABLE].insert(result):
            print('存储到MONGO成功...')
    except:
        print('----------存储到MONGO失败...------------')
#存储到本地
def save_2_local(link):
    response = requests.get(link).content
    filename = link.split('/')[-1]
    with open("D:/pythondown/煎蛋网/"+filename ,'wb') as img:
        img.write(response)
        img.close()

def main():
    page_number = search()
    for num in range(page_number):
        next_page(page_number-(num+1))

if __name__ == '__main__':
    try:
        main()
    except Exception:
        print('某些位置出错了...')
    finally:
        browser.close()
