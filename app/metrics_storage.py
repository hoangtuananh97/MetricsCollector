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
        if not hasattr(self, 'timer'):
            self.timer = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(InMemoryMetricsStorage, cls).__new__(cls, *args, **kwargs)
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

        # Start the timer to save metrics if the limit is not reached
        self.start_timer()

    def save_metrics(self):
        """Save the metrics to the database."""
        from app.tasks import insert_metrics
        insert_metrics.delay(self.metrics.copy())
        self.clear_metrics()

    def check_and_save_metrics(self):
        """Check if there are metrics and save them periodically."""
        if self.has_metrics() and len(self.metrics) < MAX_ITEMS:
            self.save_metrics()
        # Cancel the timer after saving metrics
        if self.timer is not None:
            self.timer.cancel()

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
