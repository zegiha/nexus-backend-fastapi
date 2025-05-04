import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from models.articles import Articles
from datetime import datetime
import httpx
import random
import time

async def test(
        url: str,
        # db: Session
):
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(url,timeout=None)
            if res.status_code == 200:
                soup = BeautifulSoup(res.content, "html.parser")
                c = soup.select_one('li.Nlist_item._LNB_ITEM.is_active > a > span')
                print(c)
                return 'success'
            else:
                return 'fetching failed'
        except httpx.RequestError as e:
            print(e)
            return 'request failed'

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
                    detail = await crawling_detail(article['originalArticleUrl'])
                    if detail == {}:
                        detail = await crawling_detail(article['originalArticleUrl'])
                    article.update(detail)


            if all(key in article for key in ['contents', 'title', 'originalArticleUrl']):
                db.add(Articles(
                    title=article['title'],
                    contents=article['contents'],
                    category=article['category'],
                    original_article_url=article['originalArticleUrl'],
                    summary_img_url=article.get('summary_img', None),
                    img_url=article.get('img_url', None),
                    img_desc=article.get('img_desc', None),
                    video_url=article.get('video_url', None),
                    create_date=create_date,
                ))

                db.commit()

                result.append(article)


    return result

async def crawling_detail(url):
    async with httpx.AsyncClient() as client:
        try:
            headers = [
                {
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br, zstd',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
                },
                {
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
                },
                {
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:62.0) Gecko/20100101 Firefox/62.0'
                },
                {
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; ASLJ; CIBA; rv:11.0) like Gecko'
                }
            ]

            res = await client.get(url, headers=random.choice(headers))
            if res.status_code == 200:
                soup = BeautifulSoup(res.content, 'html.parser')
                category = get_category(soup)
                if(category is None):
                    print(f'category is None: {url}')
                contents = soup.select_one('article').get_text(strip=True)
                photo_url, photo_desc = get_photo_info(soup)
                video_url = await get_video_url(soup)

                return {
                    'category': category,
                    'contents': contents,
                    'photo_url': photo_url,
                    'photo_desc': photo_desc,
                    'video_url': video_url,
                }
            else:
                # 상태 코드 출력
                print(f'crawling_detail fetching failed with status code: {res.status_code} for URL: {url}')
                # 응답 내용도 출력 (원하는 경우)
                print(f'Response content: {res.text[:500]}')  # 처음 500글자만 출력
                return {}
        except httpx.RequestError as e:
            time.sleep(20)
            print(f'crawling_detail request failed: {e}')
            return {}
        except Exception as e:
            print(f'An error occurred: {e}')
            return {}

def get_category(soup):
    e = soup.select_one('li.Nlist_item._LNB_ITEM.is_active > a > span')
    if e is not None:
        return e.get_text(strip=True)
    else:
        return None

def get_photo_info(soup):
    img_url = None
    img_desc = None

    photo_span = soup.select('span.end_photo_org')
    for span in photo_span:
        img_tag = span.select_one('img')
        desc_tag = span.select_one('em.img_desc')

        if img_tag and img_tag.get('src'):
            img_url = img_tag.get('src')

        if desc_tag:
            img_desc = desc_tag.get_text(strip=True)

    return [img_url, img_desc]


async def get_video_url(soup):
    video_info_tag = soup.select_one('div._VOD_PLAYER_WRAP')
    if video_info_tag:
        video_id = video_info_tag.get('data-video-id')
        video_key = video_info_tag.get('data-inkey')

        # print(f'video_id: {video_id}')
        # print(f'video_key: {video_key}')

        video_json_query_url = f'https://apis.naver.com/rmcnmv/rmcnmv/vod/play/v2.0/{video_id}?key={video_key}&sid=2006&nonce=1746276897832&devt=html5_pc&prv=N&aup=N&stpb=N&cpl=ko_KR&env=real&lc=ko_KR&adi=%5B%7B%22adSystem%22%3A%22null%22%7D%5D&adu=%2F'
        # print(f'video_json_query_url: {video_json_query_url}')
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
        }

        async with httpx.AsyncClient() as client:
            try:
                res = await client.get(video_json_query_url, headers=headers, timeout=None)

                if res.status_code != 200:
                    # print(f'get_video_url fetch failed: {res.status_code}')
                    return None

                video_url = None
                max_bitrate = 0
                video_json = res.json()
                for v in video_json['videos']['list']:
                    if v['encodingOption']['width'] == 1280 and v['bitrate']['video'] > max_bitrate:
                        max_bitrate = v['bitrate']['video']
                        video_url = v['source']

                return video_url
            except httpx.RequestError as e:
                # print(f'get_video_url request failed: {e}')
                return None
    else:
        return None