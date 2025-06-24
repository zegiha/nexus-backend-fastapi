from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

celery_app = Celery(
    "tasks",
    broker=os.getenv('REDIS_URL')+'/0',
    backend=os.getenv('REDIS_URL')+'/0',
)

celery_app.conf.task_serializer = "json"

celery_app.conf.update(
    task_time_limit=None,
    task_soft_time_limit=None,
    broker_transport_options={'visibility_timeout': 7200},
    result_backend_transport_options={'visibility_timeout': 7200},
)

import background.task
