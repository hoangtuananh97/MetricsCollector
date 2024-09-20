import os
import time
from functools import wraps
from dotenv import load_dotenv
from .metrics_storage import SyncMetricsStorage
from .tasks import save_metrics_task

load_dotenv()
# Max size of object in-memory storage temporary. If it exceed max size will bulk insert to database
# if it not exceed max size, it save database after 2 second.
MAX_SIZE = int(os.getenv('METRICS_MAX_SIZE', 3))
# Initialize in-memory storage for metrics
metrics_storage = SyncMetricsStorage()


def metrics_collector(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()

        # Initialize local metrics
        local_metrics = {'execution_time': 0, 'call_count': 1, 'error_count': 0}

        try:
            result = func(*args, **kwargs)
        except Exception:
            local_metrics['error_count'] += 1
            raise
        finally:
            # Record execution time
            end_time = time.perf_counter()
            local_metrics['execution_time'] += (end_time - start_time)

            # Add metrics to the in-memory storage
            metrics_storage.add_metrics(func.__name__, local_metrics)

            # If the metrics storage reaches its max size, send to Celery for async saving
            if metrics_storage.is_full(MAX_SIZE):
                save_metrics_task.delay(metrics_storage.get_all_metrics())
                metrics_storage.clear_metrics()  # Clear local storage after sending to Celery

        return result

    return wrapper
