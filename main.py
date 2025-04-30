from fastapi import FastAPI
from pydantic.v1 import BaseModel

from crawler import crawl

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.get('/crawl/press')
async def crawl_press():
    oid = [
        {'press': 'kbs', 'oid': '056'},
        {'press': 'sbs', 'oid': '055'},
        {'press': 'mbc', 'oid': '214'},
        {'press': 'jtbc', 'oid': '437'},
        {'press': 'ytn', 'oid': '052'},
        {'press': '연합뉴스', 'oid': '001'},
        {'press': '조선일보', 'oid': '023'},
        {'press': '한국일보', 'oid': '469'},
        {'press': '중앙일보', 'oid': '025'},
        {'press': '동아일보', 'oid': '020'},
        {'press': '경향신문', 'oid': '032'},
        {'press': '한겨레', 'oid': '028'},
        {'press': '매일 경제', 'oid': '009'},
        {'press': '시사저널', 'oid': '586'},
    ]


    result = []

    result.append({
        'press': 'kbs',
        'articles': crawl.crawling(f'https://news.naver.com/main/list.naver?=056&date=20250428')
    })

    # for v in oid:
    #     result.append({
    #         'press': v['press'],
    #         'articles': crawl.crawling_all(f'https://news.naver.com/main/list.naver?={v["oid"]}&date=20250428')
    #     })

    return {"message": result}