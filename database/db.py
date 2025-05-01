# db.py
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from fastapi import Depends

load_dotenv()

# DB 접속 정보 (적절히 바꿔줘)
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", 3306)
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"mysql+asyncmy://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 비동기 엔진 생성
engine = create_async_engine(DATABASE_URL, echo=False)

# 세션 클래스 생성
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 모델 정의를 위한 Base 클래스
Base = declarative_base()

# db.py 이어서

async def get_db_session():
    async with AsyncSessionLocal() as session:
        yield session
