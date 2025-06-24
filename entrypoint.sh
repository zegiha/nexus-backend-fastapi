#!/bin/bash

# Redis 서버 백그라운드로 실행
redis-server --daemonize yes

# Celery 워커 백그라운드로 실행 (로그는 /app/celery.log에 저장)
celery -A celery_app worker -Q crawling_queue --concurrency=1 --loglevel=info &> /app/celery.log &

# FastAPI 실행 (포그라운드)
exec uvicorn main:app --host 0.0.0.0 --port 8000
