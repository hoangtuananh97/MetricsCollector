---

# MetricsCollector

## Introduction
The **MetricsCollector** project is designed to collect and store function execution metrics. It features asynchronous task management using Celery, a Redis backend for storing metrics in memory, and SQLite for long-term storage. Metrics such as execution time, call count, and error count are collected and processed either when a set limit is reached or after a fixed time interval.

### Key Features:
- **Function Metrics Collection**: Automatically collects execution time, call count, and error count for decorated functions.
- **In-Memory Storage via Redis**: Temporarily stores metrics in Redis for fast access before flushing to the SQLite database.
- **Asynchronous Task Management**: Uses Celery for asynchronous task processing and periodic metrics saving.
- **Periodic Metrics Saving**: Periodically saves metrics to the database even if the limit is not reached.
- **Dockerized**: Easily deployable using Docker and Docker Compose for all components (Redis, Celery, and the application).
- **Configurable Environment Variables**: The project uses a `.env` file for customizable configuration.

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

# Redis
REDIS_URL=redis://redis:6379/0

# Database name
DATABASE_NAME=metrics.db

# Time interval
TIME_SCHEDULE=5

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

### Step 3: Start Celery Beat (for periodic tasks)

Run Celery Beat in another terminal window to periodically trigger metrics saving tasks:

```bash
celery -A app.tasks.celery_app beat --loglevel=info
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

To run the test:

```bash
docker-compose run celery_worker python main.py
```

### How it Works

- Functions decorated with `@metrics_collector` will have their execution time, call count, and error count collected.
- These metrics will first be stored in **Redis**.
- After the configured time interval (via Celery Beat), the metrics are flushed to **SQLite** for persistent storage.

### Accessing the Metrics

To view collected metrics, open the SQLite database (`metrics.db`) and query the `metrics` table. You can use a tool like `sqlite3` or any database viewer.

---

## Troubleshooting

### Common Issues:

1. **Redis not connecting**:
   - Ensure Redis is running on `localhost:6379`. If you're using Docker, check if the Redis container is running properly by checking `docker ps`.

2. **Celery Worker/Beat not starting**:
   - Check for errors in the logs when running `celery worker` or `celery beat`. Often, the issue is with the broker URL or missing dependencies.
   - Ensure that your `.env` file is correctly configured with the Redis broker and backend URLs.

3. **SQLite file permissions issue**:
   - If you encounter file permission issues when writing to the SQLite database, ensure that the directory and file have appropriate write permissions.

4. **Docker: Unable to start services**:
   - If Docker services don’t start, ensure you’ve built the images properly using `docker-compose up --build` and that no other containers are conflicting on the same ports.

---

## Conclusion

With this project, you can seamlessly collect function execution metrics and store them both in-memory (via Redis) and in a persistent database (via SQLite). The asynchronous task handling and periodic saving ensure the system is scalable and efficient.