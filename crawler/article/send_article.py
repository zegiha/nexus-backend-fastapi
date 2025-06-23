import os

import httpx
from dotenv import load_dotenv
from models.rawArticle import RawArticle
from models.raw_article_dto import RawArticleDTO


async def send_article(
        raw_article: RawArticle,
        is_headline: bool,
        press: str,
):
    load_dotenv()
    base_url = os.getenv('BASE_URL')
    dto = RawArticleDTO.model_validate(raw_article)
    payload = {
        "new_article": dto.model_dump(mode='json'),
        "is_headline": is_headline,
        "press": press,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(base_url + '/article', json=payload)
        print("응답 상태 코드:", response.status_code)
        print("응답 내용:", response.json())
