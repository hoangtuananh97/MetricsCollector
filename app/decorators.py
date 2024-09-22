import time
from functools import wraps
from dotenv import load_dotenv

from .singleton_storage import singleton_storage

load_dotenv()


# Initialize in-memory storage for metrics
def metrics_collector(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()

        # Initialize local metrics
        local_metrics = {'execution_time': 0, 'error_occurred': 0}

        try:
            result = func(*args, **kwargs)
        except Exception:
            local_metrics['error_occurred'] += 1
            raise
        finally:
            # Record execution time
            end_time = time.perf_counter()
            local_metrics['execution_time'] += (end_time - start_time)

            # Add metrics to the in-memory storage
            singleton_storage.add_metrics(func.__name__, local_metrics)

        return result

    return wrapper
