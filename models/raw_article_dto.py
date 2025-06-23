# models/rawArticle.py
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class RawArticleDTO(BaseModel):
    id: UUID
    title: str
    contents: str
    original_article_url: str
    summary_img_url: str | None = None
    img_url: str | None = None
    img_desc: str | None = None
    video_url: str | None = None
    category: str | None = None
    create_date: datetime

    model_config = {
        "from_attributes": True,  # ORM 객체에서 속성으로 변환 가능하게 함
    }
