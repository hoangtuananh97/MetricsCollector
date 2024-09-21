import os
import threading
from datetime import datetime, timezone

from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()
# Max items to save database
MAX_ITEMS = int(os.getenv('MAX_ITEMS', 100))
# Max waiting time to save remaining metrics data if less than MAX_ITEMS
MAX_WAITING_TIME = int(os.getenv('MAX_WAITING_TIME', 60))


class InMemoryMetricsStorage:
    """Metrics storage in-memory using Singleton pattern."""

    _instance = None

    def __init__(self):
        self.timer = None
        self.last_save_time = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(InMemoryMetricsStorage, cls).__new__(cls, *args, **kwargs)
            cls._instance.metrics = []
            cls._instance.last_save_time = datetime.now(timezone.utc)
            cls._instance.start_timer()
        return cls._instance

    def start_timer(self):
        """Start a timer to save metrics every minute if needed."""
        self.timer = threading.Timer(MAX_WAITING_TIME, self.check_and_save_metrics)
        self.timer.start()

    def add_metrics(self, func_name, data):
        """Add or update metrics for the given function."""

        # Create new metrics entry
        self.metrics.append(
            {
                'func_name': func_name,
                'execution_time': data['execution_time'],
                'error_occurred': data.get('error_occurred', 0),
                'created_at': datetime.now(timezone.utc).timestamp()  # Store as Unix timestamp
            }
        )

        if len(self.metrics) >= MAX_ITEMS:
            self.save_metrics()

    def save_metrics(self):
        """Save the metrics to the database."""
        from app.tasks import insert_metrics
        insert_metrics.delay(self.metrics.copy())
        self.clear_metrics()
        self.last_save_time = datetime.now(timezone.utc)

    def check_and_save_metrics(self):
        """Check if there are metrics and save them periodically."""
        if self.has_metrics() and len(self.metrics) < MAX_ITEMS:
            self.save_metrics()
        # Restart the timer
        self.start_timer()

    def get_all_metrics(self):
        """Return all stored metrics."""
        return self.metrics

    def has_metrics(self):
        """Check if there are any metrics stored."""
        return bool(self.metrics)

    def clear_metrics(self):
        """Clear all metrics."""
        self.metrics.clear()


# Singleton instance of InMemoryMetricsStorage
metrics_storage = InMemoryMetricsStorage()
