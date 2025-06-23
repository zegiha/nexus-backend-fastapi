
import os
import httpx
from dotenv import load_dotenv
from models.article import article_contents_adapter
from models.raw_article_dto import RawArticleDTO


async def create_article(
        crawl_data: RawArticleDTO,
        llm_processed_data: dict,
        is_headline: bool,
        company_id: str
):
    load_dotenv()
    base_url = os.getenv("CORE_API_URL")

    try:
        async with httpx.AsyncClient() as client:
            contents_serializable = article_contents_adapter.dump_python(llm_processed_data['contents'])

            response = await client.post(
                base_url + '/article',
                json={
                    "category": crawl_data.category,
                    "title": llm_processed_data['title'],
                    "contents": contents_serializable,
                    "summary": {
                        "title": llm_processed_data['title'],
                        "contents": llm_processed_data['summary'],
                        "media": {
                            "mediaType": "image",
                            "url": crawl_data.summary_img_url,
                        }
                    },
                    "createdAt": crawl_data.create_date.isoformat(),
                    "isHeadline": is_headline,
                    "companyId": company_id,
                    "originalUrl": crawl_data.original_article_url
                }
            )

            # 상태 코드 확인 후 예외 처리
            response.raise_for_status()
            return response

    except httpx.HTTPStatusError as e:
        print(f"[HTTP Error] Status Code: {e.response.status_code}, Response: {e.response.text}")
        return None
    except httpx.RequestError as e:
        print(f"[Request Error] An error occurred while requesting: {e.request.url} -> {str(e)}")
        return None
    except Exception as e:
        print(f"[Unexpected Error] {str(e)}")
        return None
