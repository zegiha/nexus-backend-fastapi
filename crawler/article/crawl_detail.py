import httpx
import random
from bs4 import BeautifulSoup
import time

from crawler.article.get_category import get_category
from crawler.article.get_photo_info import get_photo_info
from crawler.article.get_video_url import get_video_url


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
                if category is None:
                    print(f'category is None: {url}')
                contents = soup.select_one('article').get_text(strip=True)
                photo_url, photo_desc = get_photo_info(soup)
                video_url = await get_video_url(soup)

                time.sleep(1)

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
                if "Redirecting" in res.text:
                    return None
                else:
                    return {}
        except httpx.RequestError as e:
            time.sleep(20)
            print(f'crawling_detail request failed: {e}')
            return {}
        except Exception as e:
            print(f'An error occurred: {e}')
            return {}
