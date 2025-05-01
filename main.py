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
    # oid = [
    #     '056',
    #     '055',
    #     '214',
    #     '437',
    #     '052',
    #     '001',
    #     '023',
    #     '469',
    #     '025',
    #     '020',
    #     '032',
    #     '028',
    #     '009',
    #     '586',
    # ]

    # 3사 + ytn만
    oid = [
        {'press': 'KBS', 'oid': '056'},
        {'press': 'SBS', 'oid': '055'},
        {'press': 'MBC', 'oid': '214'},
        {'press': 'YTN', 'oid': '052'},
    ]

    try:
        date_obj = datetime.strptime(target_date, "%Y%m%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="날짜 형식이 잘못되었습니다. YYYYMMDD 형식으로 입력해주세요.")

    result = []

    for v in oid:
        new_data = await crawl.crawling(
            f'https://news.naver.com/main/list.naver?mode=LSD&mid=sec&oid={v["oid"]}&date={target_date}',
            date_obj,
            v['press'],
            db=db
        )
        result.append({
            'press': v['press'],
            'articles': new_data
        })

    return {"message": result}