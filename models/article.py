from typing import List, Literal, Optional, Union
from pydantic import BaseModel, TypeAdapter

class BaseContent(BaseModel):
    type: str


class Subject(BaseContent):
    type: Literal["subject"]
    id: Optional[str] = None
    content: str


class Description(BaseContent):
    type: Literal["description"]
    id: Optional[str] = None
    content: str


class Footnote(BaseContent):
    type: Literal["footnote"]
    id: Optional[str] = None
    content: str


class ListItem(BaseModel):
    id: Optional[str] = None
    content: str


class ListContent(BaseContent):
    type: Literal["list"]
    contents: List[ListItem]


class Link(BaseContent):
    type: Literal["link"]
    content: str
    to: str


class Scroll(BaseContent):
    type: Literal["scroll"]
    content: str
    to: str


class MediaContent(BaseContent):
    type: Literal["media"]
    mediaType: Literal["video", "image"]
    url: str
    description: Optional[str] = None


# ✅ contents 전용 타입
Article_contents = List[
    Union[
        Subject,
        Description,
        Footnote,
        ListContent,
        Link,
        Scroll,
        MediaContent
    ]
]

article_contents_adapter = TypeAdapter(Article_contents)
