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
from sqlalchemy.ext.asyncio import AsyncSession
from models.articles import Articles
from datetime import datetime


async def crawling(url: str, create_date: datetime, db: AsyncSession):
    headers = {
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    headline = await crawling_all(soup.select_one('ul.type06_headline'), create_date, db)
    normal = await crawling_all(soup.select_one('ul.type06'), create_date, db)

    return {'headline': headline, 'normal': normal}

async def crawling_all(
        raw_data,
        create_date: datetime,
        db: AsyncSession,
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

            await db.commit()

            result.append(article)

    return result

def crawling_detail(url):
    res = {}

    # Chrome 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    # Chrome 드라이버 초기화
    driver = webdriver.Chrome(options=chrome_options)

    # 페이지 로드 및 로그 수집
    driver.get(url)

    try:
        category = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'li.Nlist_item._LNB_ITEM.is_active > a > span'))
        )
        res['category'] = category.text
        # article 태그가 로드될 때까지 최대 10초 기다림
        article = WebDriverWait(driver, 2).until(
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

        sw = True
        time.sleep(7)
        logs = driver.get_log('performance')

        for entry in logs:
            log = json.loads(entry['message'])['message']
            if log['method'] == 'Network.responseReceived':
                video_json_url = log['params']['response']['url']
                if 'https://apis.naver.com/rmcnmv/rmcnmv/vod/play/v2.0/' in video_json_url and '?key' in video_json_url:
                    video_json = requests.get(video_json_url).json()
                    res['video_url'] = get_video_url(video_json)
                    sw = False
                    break
        if(sw):
            print('영상이 수집되지 않았을 수 있습니다')

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
