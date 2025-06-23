from pydantic import BaseModel, ConfigDict

from models.raw_article_dto import RawArticleDTO


class CreateArticleDTO(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)  # <== 이 줄 추가

    new_article: RawArticleDTO
    is_headline: bool
    press: str