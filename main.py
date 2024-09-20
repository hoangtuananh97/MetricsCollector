import time

from app.decorators import metrics_collector


# Example sync functions to test the decorator
@metrics_collector
def successful_function(x, y):
    time.sleep(0.1)  # Simulate some work
    return x + y


@metrics_collector
def successful_function1(x, y):
    time.sleep(0.1)  # Simulate some work
    return x + y


@metrics_collector
def successful_function2(x, y):
    time.sleep(0.1)  # Simulate some work
    return x + y


@metrics_collector
def successful_function3(x, y):
    time.sleep(0.1)  # Simulate some work
    return x + y


@metrics_collector
def error_function():
    time.sleep(0.1)  # Simulate some work
    raise ValueError("An error occurred")


@metrics_collector
def error_function1():
    time.sleep(0.1)  # Simulate some work
    raise ValueError("An error occurred")


@metrics_collector
def error_function2():
    time.sleep(0.1)  # Simulate some work
    raise ValueError("An error occurred")


# Example usage
def main():
    try:
        print("Start")
        successful_function(1, 2)
        successful_function1(2, 3)
        for _ in range(3):
            successful_function2(2, 3)
        successful_function3(2, 3)
        error_function()
        error_function1()
        error_function2()
        print("End")
    except ValueError:
        pass


# Run the example
if __name__ == "__main__":
    main()
