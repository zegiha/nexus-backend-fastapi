import requests
from asyncmy.connection import Optional
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

def crawl_press(url: str):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    headline = crawling(soup.select_one('ul.type06_headline'))
    normal = crawling(soup.select_one('ul.type06'))

    return {'headline': headline, 'normal': normal}

def crawling(raw_data: Optional[BeautifulSoup]):
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
            dd = dl.find('dd')

            article = {}

            if dt_photo:
                a = dt_photo.find('a')
                img = a.find('img')
                if img and img.get('src'):
                    article['imgUrl'] = img['src']

            if dt_title:
                a = dt_title.find('a')
                if a:
                    article['title'] = a.get_text(strip=True)
                    article['originalArticleUrl'] = a['href']

            if dd:
                spans = dd.find_all('span')
                if len(spans) == 3:
                    summary, press, date = spans
                    article['summary'] = summary.get_text(strip=True)

            result.append(article)

    return result