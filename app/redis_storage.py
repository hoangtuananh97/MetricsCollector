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

    def _get_key_metrics_list(self):
        """Returns the Redis key for storing metrics for all function."""
        return "metrics_list"

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

    def add_metrics_list(self, metric):
        """Add metrics to list. Time complexity O(1)"""
        redis_client.rpush(self._get_key_metrics_list(), str(metric))

    def get_all_metrics_list(self):
        """Get all metrics list."""
        return [eval(item) for item in redis_client.lrange(self._get_key_metrics_list(), 0, -1)]

    def get_len_metrics_list(self):
        """Get length metrics list."""
        return redis_client.llen('metrics_list')

    def get_metrics(self, func_name):
        """Return all stored metrics for the given function. Time complexity O(1)"""
        metrics = redis_client.get(self._get_redis_key(func_name))
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

    def clear_metrics_list(self):
        """Clear all metrics."""
        redis_client.delete(self._get_key_metrics_list())


# Create an instance of RedisMetricsStorage
metrics_redis_storage = RedisMetricsStorage()
