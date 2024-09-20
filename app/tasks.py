import os
import sqlite3

from celery import Celery
from dotenv import load_dotenv

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


# Celery task for saving metrics to the database asynchronously
@celery_app.task
def save_metrics_task(metrics):
    with sqlite3.connect('metrics.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS metrics (
                                func_name TEXT, 
                                execution_time REAL, 
                                call_count INTEGER, 
                                error_count INTEGER
                          )''')

        # Insert each metric into the SQLite database
        for func_name, data in metrics.items():
            cursor.execute('''INSERT INTO metrics (func_name, execution_time, call_count, error_count)
                              VALUES (?, ?, ?, ?)''',
                           (func_name, data['execution_time'], data['call_count'], data['error_count']))
        conn.commit()
