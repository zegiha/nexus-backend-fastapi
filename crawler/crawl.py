import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import json

from selenium.webdriver.common.devtools.v133.network import WebSocketCreated
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def crawling(url: str):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    headline = crawling_all(soup.select_one('ul.type06_headline'))
    normal = crawling_all(soup.select_one('ul.type06'))

    return {'headline': headline, 'normal': normal}

def crawling_all(raw_data):
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

            result.append(article)
            print(len(result))

    return result

def crawling_detail(url):
    res = {}

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    driver = webdriver.Chrome(options=chrome_options)
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

        if res.get('imgUrl') is None:
            # video 태그도 로드될 때까지 기다리기 (선택적)
            videos = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, 'video'))
            )
            if len(videos) > 0:
                for v in videos:
                    ActionChains(driver).move_to_element(v).click().perform()
                    WebDriverWait(driver, 10).until(lambda d: len(d.get_log('performance')) > 0)
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
