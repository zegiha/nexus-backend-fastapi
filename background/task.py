from celery_app import celery_app
from crawler import crawl
from datetime import datetime

@celery_app.task(name='background.task.run_crawling')
def run_crawling(url: str, date: datetime, press: str):
    import asyncio
    from database import db


    async def run():
        session = next(db.get_db_session())
        return await crawl.crawling(url, date, press, session)

    result = asyncio.run(run())
    return result