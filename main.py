import os
import random
import time

from app.decorators import metrics_collector
from app.redis_storage import metrics_redis_storage
from app.singleton_storage import singleton_storage

MAX_WAITING_TIME = int(os.getenv('MAX_WAITING_TIME', 60))
TIME_SCHEDULE = int(os.getenv('TIME_SCHEDULE', 3))


# Example sync functions to test the decorator
@metrics_collector
def successful_function1(x, y):
    time.sleep(random.uniform(1, 3))
    return x + y


@metrics_collector
def successful_function2(x, y):
    time.sleep(random.uniform(1, 3))
    return x + y


@metrics_collector
def error_function():
    time.sleep(random.uniform(1, 3))
    raise ValueError("An error occurred")


# Example usage
def main():
    print("Run Function. Random time")
    try:
        successful_function1(2, 3)
        for _ in range(2):
            successful_function2(2, 3)
        error_function()
    except ValueError:
        pass

    print("Get Metrics")
    metrics_func1 = singleton_storage.get_metrics('successful_function1')
    metrics_func2 = singleton_storage.get_metrics('successful_function2')
    metrics_error = singleton_storage.get_metrics('error_function')
    print("metrics_func1", metrics_func1)
    print("metrics_func2", metrics_func2)
    print("metrics_error", metrics_error)

    print(
        f"To save all metrics. We will wait base on time interval ({TIME_SCHEDULE}s) that be set in .env file."
        f" This is to avoid memory overflow in Redis. It is good for large metrics."
    )

    # print("Reset redis")
    # metrics_redis_storage.clear_metrics('successful_function1')
    # metrics_redis_storage.clear_metrics('successful_function2')
    # metrics_redis_storage.clear_metrics('error_function')
    # print("Reset successfully")


# Run the example
if __name__ == "__main__":
    main()
