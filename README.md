# Nexus

![](https://private-user-images.githubusercontent.com/118225985/467884349-246b1f2f-a87b-4885-8c67-2a224a44b90b.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTI4MTg5NzcsIm5iZiI6MTc1MjgxODY3NywicGF0aCI6Ii8xMTgyMjU5ODUvNDY3ODg0MzQ5LTI0NmIxZjJmLWE4N2ItNDg4NS04YzY3LTJhMjI0YTQ0YjkwYi5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzE4JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcxOFQwNjA0MzdaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT04YzFkNzU0MDFhZGIyNjM3YTI0MDQ1MGRkY2NhOTBjZWRjYWZjNThkZDM3YTRmNDc0NTY0Yzc0Yzc4M2U3MzJlJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.EsVgS9Qe97gw6kv90lBQBDxtyp0EmrnBMXNbuxc6lTY)

뉴스 기사 가독성 향상 서비스의 크롤러 및 AI 백엔드
Axios 뉴스레터를 참고하여 뉴스 기사의 가독성을 높여 사용자에게 더 잘 전달하는 서비스의 백엔드 시스템입니다.

## 주요 기능

- 네이버 뉴스 기사 크롤링
- LLM을 활용한 기사 내용 가독성 향상 처리
- 비동기 작업 큐를 통한 대용량 데이터 처리
- FastAPI 기반 REST API 제공

## 설치 및 실행

### 설치
```bash
pip install -r req.txt
```

### 환경 변수 설정
필요한 환경 변수를 설정해주세요:
- Redis URL
- 데이터베이스 연결 정보
- LLM API 키

### 개발 서버 실행
```bash
uvicorn main:app --reload
```
개발 모드로 실행하며, http://localhost:8000에서 확인할 수 있습니다.

### Celery 워커 실행
```bash
celery -A celery_app worker --loglevel=info
```

## API 엔드포인트

- `POST /article` - 기사 내용 가독성 향상 처리 요청
- `GET /crawl/{target_date}` - 특정 날짜의 뉴스 기사 크롤링 (YYYYMMDD 형식)

## 주요 구조

- `crawler/` - 뉴스 기사 크롤링 모듈
- `crew/` - LLM 기반 기사 처리 모듈
- `models/` - 데이터 모델 정의
- `background/` - Celery 백그라운드 작업
- `database/` - 데이터베이스 연결 및 관리