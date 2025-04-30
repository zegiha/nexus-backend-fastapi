from fastapi import FastAPI, HTTPException, Depends
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import AsyncSession
from database.db import get_db_session
from crawler import crawl

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.get('/test')
async def test():
    return {"message": crawl.crawling_detail('https://n.news.naver.com/mnews/article/660/0000084394')}

@app.get('/crawl/{target_date}')
async def crawl_route(target_date: str, db: AsyncSession = Depends(get_db_session)):
    oid = [
        '056',
        '055',
        '214',
        '437',
        '052',
        '001',
        '023',
        '469',
        '025',
        '020',
        '032',
        '028',
        '009',
        '586',
    ]

    # oid = [
    #     {'press': 'kbs', 'oid': '056'},
    #     {'press': 'sbs', 'oid': '055'},
    #     {'press': 'mbc', 'oid': '214'},
    #     {'press': 'jtbc', 'oid': '437'},
    #     {'press': 'ytn', 'oid': '052'},
    #     {'press': '연합뉴스', 'oid': '001'},
    #     {'press': '조선일보', 'oid': '023'},
    #     {'press': '한국일보', 'oid': '469'},
    #     {'press': '중앙일보', 'oid': '025'},
    #     {'press': '동아일보', 'oid': '020'},
    #     {'press': '경향신문', 'oid': '032'},
    #     {'press': '한겨레', 'oid': '028'},
    #     {'press': '매일 경제', 'oid': '009'},
    #     {'press': '시사저널', 'oid': '586'},
    # ]

    try:
        date_obj = datetime.strptime(target_date, "%Y%m%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="날짜 형식이 잘못되었습니다. YYYYMMDD 형식으로 입력해주세요.")

    result = []

    for v in oid:
        new_data = await crawl.crawling(
            f'https://news.naver.com/main/list.naver?={v}&date={target_date}',
            date_obj,
            db=db
        )
        result.append({
            'articles': new_data
        })

    return {"message": result}