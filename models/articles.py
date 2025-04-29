# models/articles.py
import uuid
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.dialects.mysql import CHAR
from database.db import Base
from datetime import datetime

class Articles(Base):
    __tablename__ = "articles"

    id = Column(CHAR(36), primary_key=True, default=str(uuid.uuid4()))
    # title = Column(String(255))
    tmp = Column(String(255))
    link = Column(String(255))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
