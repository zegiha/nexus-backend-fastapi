import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from datetime import datetime

from crawler.article.crawl_detail_and_summary import crawl_detail_and_summary
from crawler.article.get_max_page import get_max_page


async def crawling_article(
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
        new_headline = await crawl_detail_and_summary(
            soup.select_one('ul.type06_headline'),
            create_date,
            True,
            press,
            db
        )
        if new_headline:
            for v in new_headline: headline.append(v)
        new_normal = await crawl_detail_and_summary(
            soup.select_one('ul.type06'),
            create_date,
            False,
            press,
            db
        )
        if new_normal:
            for v in new_normal: normal.append(v)

        page += 1



    return {'headline': headline, 'normal': normal}
