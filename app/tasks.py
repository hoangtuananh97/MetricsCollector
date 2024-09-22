import os

from celery import Celery
from dotenv import load_dotenv

from app.database import insert
from app.redis_storage import metrics_redis_storage

load_dotenv()
# Fetch environment variables
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')

celery_app = Celery('MetricsCollector', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
)


@celery_app.task
def insert_metrics(metrics):
    insert(metrics)


@celery_app.task
def insert_redis_metrics(func_name, metrics):
    metrics_redis_storage.add_metrics(func_name, metrics)
