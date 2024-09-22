import os
import threading
from datetime import datetime, timezone

from dotenv import load_dotenv

from app.database import get_metrics
from app.redis_storage import metrics_redis_storage
from app.tasks import insert_redis_metrics

# Load environment variables from the .env file
load_dotenv()
# Max items to save database
MAX_ITEMS = int(os.getenv('MAX_ITEMS', 100))
# Max waiting time to save remaining metrics data if less than MAX_ITEMS
MAX_WAITING_TIME = int(os.getenv('MAX_WAITING_TIME', 60))


class SingletonMetricsStorage:
    """Metrics storage in-memory using Singleton pattern."""

    _instance = None

    def __init__(self):
        if not hasattr(self, 'timer'):
            self.timer = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SingletonMetricsStorage, cls).__new__(cls, *args, **kwargs)
            cls._instance.metrics = []
        return cls._instance

    def start_timer(self):
        """Start a timer only if it's not already running."""
        if self.timer is None or not self.timer.is_alive():
            self.timer = threading.Timer(MAX_WAITING_TIME, self.check_and_save_metrics)
            self.timer.start()

    def add_metrics(self, func_name, data):
        """Add or update metrics for the given function."""

        # Create new metrics entry
        metric = {
            'func_name': func_name,
            'execution_time': data['execution_time'],
            'error_occurred': data.get('error_occurred', 0),
            'created_at': datetime.now(timezone.utc).timestamp()
        }
        # Add to counter in redis
        self.save_redis_metrics(func_name, metric)

        # Add to record in redis
        metrics_redis_storage.add_metrics_list(metric)

        if metrics_redis_storage.get_len_metrics_list() >= MAX_ITEMS:
            self.save_metrics()

        # Start the timer to save metrics if the limit is not reached
        self.start_timer()

    def save_redis_metrics(self, func_name, metric):
        insert_redis_metrics(func_name, metric)

    def save_metrics(self):
        """Save the metrics to the database."""
        from app.tasks import insert_metrics
        insert_metrics.delay(metrics_redis_storage.get_all_metrics_list())
        self.clear_metrics()

    def check_and_save_metrics(self):
        """Check if there are metrics and save them periodically."""
        if 0 < metrics_redis_storage.get_len_metrics_list() < MAX_ITEMS:
            self.save_metrics()
        # Cancel the timer after saving metrics
        if self.timer is not None:
            self.timer.cancel()

    def get_metrics(self, func_name):
        data = metrics_redis_storage.get_metrics(func_name)
        if not data:
            data = get_metrics(func_name)
        return data

    def clear_metrics(self):
        """Clear all metrics."""
        metrics_redis_storage.clear_metrics_list()


# Singleton instance of SingletonMetricsStorage
singleton_storage = SingletonMetricsStorage()
