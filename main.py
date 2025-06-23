from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from datetime import datetime
from background.task import run_crawling
from const.press.get_press import get_press
from crew.crew import llm_processing
from crew.llm_worker import llm_request_queue, llm_worker
from models.create_article_dto import CreateArticleDTO
import asyncio

llm_worker_tasks = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🔥 앱 시작 시 실행할 코드
    print("🚀 앱 시작: LLM 워커 실행")
    for _ in range(1):  # 워커 수 지정
        task = asyncio.create_task(llm_worker())
        llm_worker_tasks.append(task)

    yield

    # 🧹 앱 종료 시 실행할 코드
    print("🧹 앱 종료: 워커 취소 중")
    for task in llm_worker_tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    print("🧼 종료 완료")


app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post('/article')
async def article(req: CreateArticleDTO):
    try:
        await llm_request_queue.put(
            lambda: llm_processing(req.new_article, req.is_headline, req.press)
        )
        return {"message": "작업 큐에 등록됨"}
    except asyncio.CancelledError as e:
        print(e)
        return {"error": str(e)}

@app.get('/crawl/{target_date}')
async def crawl_route(target_date: str):
    # 3사 + ytn만
    oid = get_press()

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