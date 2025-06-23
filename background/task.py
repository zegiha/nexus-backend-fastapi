from celery_app import celery_app
from datetime import datetime
from crawler.article import crawling_article

@celery_app.task(name='background.task.run_crawling', queue='crawling_queue')
def run_crawling(url: str, date: datetime, press: str):
    import asyncio
    from database import db

    async def run():
        session = next(db.get_db_session())
        return await crawling_article.crawling_article(url, date, press, session)

    result = asyncio.run(run())
    return result