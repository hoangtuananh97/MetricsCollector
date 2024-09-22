import json
import os

import redis
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Fetch the REDIS_URL from the environment
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')  # Redis URL

# Initialize Redis client
redis_client = redis.StrictRedis.from_url(REDIS_URL)


class RedisMetricsStorage:
    """Metrics storage backed by Redis."""

    def _get_redis_key(self, func_name):
        """Returns the Redis key for storing metrics for a specific function."""
        return f"app:metrics:{func_name}"

    def add_metrics(self, func_name, data):
        """Add or update metrics for the given function."""
        redis_key = self._get_redis_key(func_name)

        # Fetch existing metrics for the specific function from Redis
        existing_metrics = redis_client.get(redis_key)
        if existing_metrics:
            metrics = json.loads(existing_metrics)
            # Update metrics
            metrics['execution_time'] += data['execution_time']
            metrics['call_count'] += 1
            metrics['error_count'] += data.get('error_occurred', 0)
        else:
            metrics = {
                'execution_time': data['execution_time'],
                'call_count': 1,
                'error_count': data.get('error_occurred', 0),
            }

        # Save updated metrics back to Redis
        redis_client.set(redis_key, json.dumps(metrics))

    def get_metrics(self, func_name):
        """Return all stored metrics for the given function."""
        redis_key = self._get_redis_key(func_name)
        metrics = redis_client.get(redis_key)
        data = {}
        if metrics:
            data_json = json.loads(metrics)
            data["Function"] = func_name
            data["Number of calls"] = data_json['call_count']
            data["Average execution time"] = data_json["execution_time"] / data_json["call_count"]
            data["Number of errors"] = data_json['error_count']
        return data

    def has_metrics(self, func_name):
        """Check if there are any metrics stored for the function."""
        redis_key = self._get_redis_key(func_name)
        return redis_client.exists(redis_key)

    def clear_metrics(self, func_name):
        """Clear the metrics for a specific function from Redis."""
        redis_key = self._get_redis_key(func_name)
        redis_client.delete(redis_key)


# Create an instance of RedisMetricsStorage
metrics_redis_storage = RedisMetricsStorage()
