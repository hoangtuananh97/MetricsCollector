import os
import redis
from collections import defaultdict
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables from the .env file
load_dotenv()

# Fetch the MAX_SIZE and REDIS_URL from the environment
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')  # Redis URL

# Initialize Redis client
redis_client = redis.StrictRedis.from_url(REDIS_URL)


class RedisMetricsStorage:
    """Metrics storage backed by Redis."""

    def _get_redis_key(self):
        """Returns the Redis key used for storing metrics."""
        return "app:metrics"

    def add_metrics(self, func_name, data):
        """Add or update metrics for the given function."""
        redis_key = self._get_redis_key()

        # Get existing metrics from Redis
        existing_metrics = redis_client.get(redis_key)
        if existing_metrics:
            metrics = json.loads(existing_metrics)
        else:
            metrics = defaultdict(lambda: {
                'execution_time': 0,
                'call_count': 0,
                'error_count': 0,
                'created_at': str(datetime.now().isoformat())  # Default created_at time for new metrics
            })

        # If func_name exists, update the metrics
        if func_name in metrics:
            metrics[func_name]['execution_time'] += data['execution_time']
            metrics[func_name]['call_count'] += data['call_count']
            metrics[func_name]['error_count'] += data['error_count']
        else:
            # If func_name does not exist, create a new metric with created_at timestamp
            metrics[func_name] = {
                'execution_time': data['execution_time'],
                'call_count': data['call_count'],
                'error_count': data['error_count'],
                'created_at': str(datetime.now().isoformat())
            }

        # Save updated metrics back to Redis
        redis_client.set(redis_key, json.dumps(metrics))

    def get_all_metrics(self):
        """Return all stored metrics."""
        redis_key = self._get_redis_key()
        metrics = redis_client.get(redis_key)

        if metrics:
            return json.loads(metrics)
        return {}

    def has_metrics(self):
        """Check if there are any metrics stored."""
        return bool(self.get_all_metrics())

    def clear_metrics(self):
        """Clear the top 10 oldest metrics from Redis based on created_at timestamp."""
        redis_key = self._get_redis_key()
        redis_client.delete(redis_key)


# Create an instance of RedisMetricsStorage
metrics_storage = RedisMetricsStorage()
