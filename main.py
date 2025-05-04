from fastapi import FastAPI, HTTPException
from datetime import datetime
from crawler import crawl
from background.task import run_crawling

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.get('/test')
async def test():
    data = await crawl.test('https://m.sports.naver.com/kbaseball/article/052/0002188831')
    return {"message": data}

@app.get('/crawl/{target_date}')
async def crawl_route(target_date: str):
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
        task = run_crawling.delay(
            f'https://news.naver.com/main/list.naver?mode=LSD&mid=sec&oid={v["oid"]}&date={target_date}',
            date_obj,
            v['press'],
        )

        result.append(f'{v["press"]}의 크롤링 작업이 백그라운드에서 시작됐습니다, task_id: ${task}')

    return {"message": result}