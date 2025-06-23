# models/rawArticle.py
from uuid import uuid4

from sqlalchemy import Column, Text, DateTime
from sqlalchemy.dialects.mysql import CHAR
from database.db import Base

class RawArticle(Base):
    __tablename__ = "raw_article"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid4()))
    title = Column(Text)
    contents = Column(Text)
    original_article_url = Column(Text)
    summary_img_url = Column(Text, nullable=True)
    img_url = Column(Text, nullable=True)
    img_desc = Column(Text, nullable=True)
    video_url = Column(Text, nullable=True)
    category = Column(Text, nullable=True)
    create_date = Column(DateTime)