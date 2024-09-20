import os
import sqlite3
from datetime import timedelta

from celery import Celery
from dotenv import load_dotenv

from app.database import insert
from app.metrics_storage import metrics_storage

load_dotenv()
# Fetch environment variables
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')
DATABASE_NAME = os.getenv('DATABASE_NAME')
TIME_SCHEDULE = int(os.getenv('TIME_SCHEDULE', 3))

celery_app = Celery('MetricsCollector', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    beat_schedule={
        'save-metrics-every-interval': {
            'task': 'app.tasks.periodic_save_metrics',
            'schedule': timedelta(seconds=TIME_SCHEDULE),
        },
    }
)


@celery_app.task
def periodic_save_metrics():
    if metrics_storage.has_metrics():
        metrics = metrics_storage.get_all_metrics()
        insert(metrics)
        metrics_storage.clear_metrics()
