from celery import Celery

celery_app = Celery(
    "tasks",
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
)

celery_app.conf.task_serializer = "json"

celery_app.conf.update(
    task_time_limit=None,
    task_soft_time_limit=None,
    broker_transport_options={'visibility_timeout': 7200},
    result_backend_transport_options={'visibility_timeout': 7200},
)

# ✅ Task 모듈 import (중요!)
import background.task
