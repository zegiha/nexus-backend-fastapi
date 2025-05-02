import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
import json
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy.orm import Session
from webdriver_manager.chrome import ChromeDriverManager

from models.articles import Articles
from datetime import datetime

async def crawling(
        url: str,
        create_date: datetime,
        press: str,
        db: Session,
):
    max_page = 1
    page = 1

    headline = []
    normal = []

    while page <= max_page:
        headers = {
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        res = requests.get(url + f'&page={page}', headers=headers, timeout=None)
        soup = BeautifulSoup(res.text, "html.parser")
        max_page = get_max_page(soup.select_one('div.paging'))
        print(f'max_page : {max_page}')
        print(f'page : {page}')
        new_headline = await crawling_all(soup.select_one('ul.type06_headline'), create_date, press, db)
        if new_headline:
            for v in new_headline: headline.append(v)
        new_normal = await crawling_all(soup.select_one('ul.type06'), create_date, press, db)
        if new_normal:
            for v in new_normal: normal.append(v)

        page += 1

    return {'headline': headline, 'normal': normal}


def get_max_page(paging):
    pages = paging.select('a')
    select_page = paging.select_one('strong')
    if pages[-1].get_text(strip=True) == '다음':
        # print(f'returning contents: {pages[-2].get_text(strip=True)}')
        res = pages[-2].get_text(strip=True)
    else:
        # print(f'returning contents: {pages[-1].get_text(strip=True)}')
        res = pages[-1].get_text(strip=True)
    return max(int(res), int(select_page.get_text(strip=True)))

async def crawling_all(
        raw_data,
        create_date: datetime,
        press: str,
        db: Session,
):
    if raw_data is None:
        return None

    result = []

    for li in raw_data.find_all('li'):
        for dl in li.find_all('dl'):
            if not dl:
                continue

            dt_list = dl.findAll('dt')
            dt_photo = None
            dt_title = None
            if len(dt_list) < 2:
                dt_title = dt_list[0]
            else:
                dt_photo = dt_list[0]
                dt_title = dt_list[1]

            article = {}

            if dt_photo:
                a = dt_photo.find('a')
                img = a.find('img')
                if img and img.get('src'):
                    article['summary_img'] = img['src']

            if dt_title:
                a = dt_title.find('a')
                if a:
                    article['title'] = a.get_text(strip=True)
                    article['originalArticleUrl'] = a['href']
                    article.update(crawling_detail(article['originalArticleUrl']))


            if all(key in article for key in ['contents', 'title', 'originalArticleUrl']):
                db.add(Articles(
                    title=article['title'],
                    contents=article['contents'],
                    original_article_url=article['originalArticleUrl'],
                    summary_img_url=article.get('summary_img', None),
                    img_url=article.get('imgUrl', None),
                    img_desc=article.get('imgDesc', None),
                    video_url=article.get('video_url', None),
                    create_date=create_date,
                ))

                db.commit()

                result.append(article)


    return result

def crawling_detail(url):
    res = {}

    # Chrome 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    # Chrome 드라이버 초기화
    driver = webdriver.Chrome(
        executable_path='/home/ubuntu/chromedriver-linux64',
        options=chrome_options
    )

    # 페이지 로드 및 로그 수집
    driver.get(url)

    try:
        category = WebDriverWait(driver, 1000).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'li.Nlist_item._LNB_ITEM.is_active > a > span'))
        )
        res['category'] = category.text
        # article 태그가 로드될 때까지 최대 10초 기다림
        article = WebDriverWait(driver, 1000).until(
            EC.presence_of_element_located((By.TAG_NAME, 'article'))
        )

        res['contents'] = article.text
        photo_span = article.find_elements(By.CSS_SELECTOR, 'span.end_photo_org')
        for span in photo_span:
            img = span.find_elements(By.TAG_NAME, 'img')
            desc = span.find_elements(By.CSS_SELECTOR, 'em.img_desc')

            for v in img:
                res['imgUrl'] = v.get_attribute('src')
            for v in desc:
                res['imgDesc'] = v.text

        time.sleep(7)
        logs = driver.get_log('performance')

        for entry in logs:
            log = json.loads(entry['message'])['message']
            if log['method'] == 'Network.responseReceived':
                video_json_url = log['params']['response']['url']
                if 'https://apis.naver.com/rmcnmv/rmcnmv/vod/play/v2.0/' in video_json_url and '?key' in video_json_url:
                    video_json = requests.get(video_json_url).json()
                    res['video_url'] = get_video_url(video_json)
                    break

    except Exception as e:
        print("Error occurred:", e)
    finally:
        driver.quit()
        return res

def get_video_url(video_json):
    if video_json is None:
        return None

    max_bitrate = 0
    res = None
    for v in video_json['videos']['list']:
        if v['encodingOption']['width'] == 1280 and v['bitrate']['video'] > max_bitrate:
            max_bitrate = v['bitrate']['video']
            res = v['source']

    return res
