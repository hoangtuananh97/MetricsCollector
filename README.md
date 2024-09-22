---

# MetricsCollector

## Introduction
The **MetricsCollector** project is designed to collect and store function execution metrics. It features asynchronous task management using Celery, and SQLite for long-term storage. Metrics such as execution time, call count, and error count are collected and processed either when a set limit is reached or after a fixed time interval.

### Key Features:
- **Function Metrics Collection**: Automatically collects execution time, call count, and error count for decorated functions.
- **Asynchronous Task Management**: Uses Celery for asynchronous task processing and periodic metrics saving.
- **Periodic Metrics Saving**: Periodically saves metrics to the database even if the limit is not reached.
- **Auto Metrics Saving**: Auto saves metrics to the database even if the limit is reached. After removing record that saved on redis.
- **Add calculate**: Calculate  `Number of calls`, `Average execution time`, `Number of errors` on `redis` Key `app:metrics:{func_name}`.
- **Add record metrics**: Add new metrics entry on `redis`. Key `metrics_list`.
- **Dockerized**: Easily deployable using Docker and Docker Compose for all components (Redis, Celery, and the application).
- **Configurable Environment Variables**: The project uses a `.env` file for customizable configuration.
- **Get Metric**:  `Number of calls`, `Average execution time`, `Number of errors` of a `Function`
---

## Prerequisites
Make sure you have the following software installed on your machine:

- **Python** (Version 3.11 or higher)
- **Docker** (Version 20.10 or higher)
- **Docker Compose** (Version 1.29 or higher)
- **Redis** (Version 6.0 or higher)
- **Celery** (Version 5.2 or higher)
- **SQLite** (Version 3.x or higher)

---

## Step Approach
```python
Entry = {
   'func_name': '<func_name>',
   'execution_time': '<execution_time>',
   'error_occurred': '<error_occurred>',
   'created_at': '<timestamp UTC>'
}
```

1. **Metrics Collection**: Automatically gathering function metrics helps analyze performance, identify bottlenecks, and spot potential issues (like error frequency).
2. **Temporary caching**: With `app:metrics:{func_name}` key, add or update `Number of calls`, `Average execution time`, `Number of errors` record and with `metrics_list` key add the metrics `entry` to `redis`. `metrics_list` key will be removed after saving database. This is to avoid memory overflow in Redis. It is good for large metrics.
3. **Asynchronous Task Management (Celery)**: Celery allows for efficient task handling, particularly useful when storing large amounts of data without blocking the main application.
4. **Periodic Saving**: This ensures that even if the function isn’t frequently called, metrics will still be stored at regular intervals, maintaining data integrity.
5. **Auto-saving on Threshold**: When a set number of metrics accumulate, they are automatically saved, preventing memory overload and ensuring timely data persistence.

Using **Singleton Pattern** in Metrics Storage

1. **Centralized Access**: A singleton ensures that there is only one instance of the metrics storage, which is essential for maintaining a consistent state across the application. Multiple instances could lead to conflicting or duplicated data.

2. **Global Access**: A singleton provides global access to the metrics storage, which means any part of the application can easily add or retrieve metrics without passing the instance around.

3. **Efficient Resource Management**: Having a single instance avoids excessive memory consumption, which would occur with multiple storage instances.

4. **Thread-Safety**: In a multi-threaded environment (like when using `threading.Timer`), a singleton ensures that only one instance is being accessed and modified, reducing race conditions and ensuring safe data handling. 

This setup ensures reliability, scalability, and real-time performance tracking.
Singleton pattern is critical for projects where centralized, consistent, and low-memory storage is required, particularly for in-memory storage like in this project.

### How it Works

- Functions decorated with `@metrics_collector` will have their execution time, call count, and error count collected.
- Auto save the `Number of calls`, `Average execution time`, `Number of errors` record to `redis`.
- Auto save the metrics `entry` to `redis`.
- Auto saves metrics to the database even if the limit is reached. the limit be set `MAX_ITEMS`. After removing Key `metrics_list` in `redis`.
- Periodically saves metrics to the database even if the limit is not reached after schedule time be set `MAX_WAITING_TIME`.

### Accessing the Metrics

To view collected metrics, open the SQLite database (`metrics.db`) and query the `metrics` table. You can use a tool like `sqlite3` or any database viewer.

---

## Installation & Configuration

### Step 1: Clone the Repository

```bash
git clone https://github.com/hoangtuananh97/MetricsCollector.git
cd MetricsCollector
```

### Step 2: Install Python Dependencies

Install the necessary Python packages by running:

```bash
pip install -r requirements.txt
```

### Step 3: Configure the Environment Variables

Create a `.env` file in the project root and add the following content (you can adjust values based on your configuration):

```bash
PYTHONUNBUFFERED=1

# Redis broker URL
CELERY_BROKER_URL=redis://redis:6379/0

# Redis result backend URL
CELERY_RESULT_BACKEND=redis://redis:6379/0

# REDIS_URL
REDIS_URL=redis://redis:6379/0

# Database name
DATABASE_NAME=metrics.db

# Max items to save database
MAX_ITEMS=3

# Max waiting time to save remaining metrics data if less than MAX_ITEMS
MAX_WAITING_TIME=5

```

---

## Database Setup

SQLite is used for persistent metrics storage in this project. The SQLite database (`metrics.db`) will automatically be created when you first run the application. No manual setup or migrations are needed.

---

## Running the Application

### Step 1: Start Redis

Ensure Redis is running. You can run Redis either locally or through Docker. To run Redis using Docker:

```bash
docker run -d -p 6379:6379 redis
```

### Step 2: Start Celery Worker

Run the Celery worker in one terminal window to process the tasks:

```bash
celery -A app.tasks.celery_app worker --loglevel=info
```

---

## Docker Deployment

You can also deploy the entire stack (Redis, Celery, and the application) using Docker Compose.

### Step 1: Build the Docker Images

Run the following command to build the Docker image:

```bash
docker-compose up --build
```

This command builds the Docker containers for the application, Redis, and Celery.

### Step 2: Running the Docker Containers

After building the containers, start the services:

```bash
docker-compose up
```

This will start Redis, the Celery worker, and the Celery Beat scheduler in separate containers.

---

## Usage

After setting up the application, you can use the following example functions to test the metrics collection functionality:

### Example in `main.py`

```python
from app.decorators import metrics_collector

@metrics_collector
def successful_function(x, y):
    time.sleep(0.1)  # Simulate some work
    return x + y

@metrics_collector
def error_function():
    time.sleep(0.1)  # Simulate some work
    raise ValueError("An error occurred")
```

To run the test by docker:

```bash
docker-compose run celery_worker python main.py
```

To run the test by console:

```bash
./main.py
```

---

## Troubleshooting

### Common Issues:

1. **Redis not connecting**:
   - Ensure Redis is running on `localhost:6379`. If you're using Docker, check if the Redis container is running properly by checking `docker ps`.

2. **Celery Worker not starting**:
   - Check for errors in the logs when running `celery worker` . Often, the issue is with the broker URL or missing dependencies.
   - Ensure that your `.env` file is correctly configured with the Redis broker and backend URLs.

3. **SQLite file permissions issue**:
   - If you encounter file permission issues when writing to the SQLite database, ensure that the directory and file have appropriate write permissions.

4. **Docker: Unable to start services**:
   - If Docker services don’t start, ensure you’ve built the images properly using `docker-compose up --build` and that no other containers are conflicting on the same ports.

---
## Conclusion

With this project, you can seamlessly collect function execution metrics and store them both in-memory and in a persistent database (via SQLite). The asynchronous task handling and periodic saving ensure the system is scalable and efficient.

