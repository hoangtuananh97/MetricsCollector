Here’s an example of a `README.md` file for your project that includes all the requested sections:

---

# MetricsCollector

## Introduction
This project is designed to [Brief description of the project's purpose]. It features asynchronous task management using Celery, a Redis backend for message brokering, and SQLite for database storage. The application uses decorators to collect function metrics (execution time, call count, and error count) and saves them in the database either when the storage limit is reached or after a fixed interval.

### Key Features:
- Collects function metrics using decorators.
- Saves metrics asynchronously via Celery tasks.
- Periodically saves metrics even when the storage limit is not reached.
- Configurable environment variables using `.env`.
- Dockerized for easy deployment.

---

## Prerequisites
Make sure you have the following software installed on your machine:

- **Python** (Version 3.8 or higher)
- **Docker** (Version 20.10 or higher)
- **Docker Compose** (Version 1.29 or higher)
- **Redis** (Version 6.0 or higher)
- **Celery** (Version 5.2 or higher)
- **SQLite** (Version 3.x or higher)

---

## Installation & Configuration

### Step 1: Clone the Repository

```bash
https://github.com/hoangtuananh97/MetricsCollector.git
cd MetricsCollector
```

### Step 2: Install Python Dependencies

You can install the necessary Python packages by running:

```bash
pip install -r requirements.txt
```

### Step 3: Configure the Environment Variables

Create a `.env` file in the project root and add the following content (you can adjust values based on your configuration):

```bash
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
METRICS_MAX_SIZE=3
```

---

## Database Setup

SQLite is used for this project and does not require any complex setup. The database will automatically be created when you first run the application. If needed, create migrations and apply them:

1. Create the SQLite database if not created already.
2. Migrations for database structure are not necessary for this small-scale usage, as SQLite handles database table creation automatically in the code.

---

## Running the Application

### Step 1: Running Celery Worker

Start the Celery worker in one terminal window:

```bash
celery -A app.tasks.celery_app worker --loglevel=info
```

### Step 2: Running Celery Beat (for periodic tasks)

In a separate terminal window, run Celery Beat:

```bash
celery -A celeryconfig.app beat --loglevel=info
```

### Step 3: Running Redis

Make sure Redis is running on your local machine or via Docker:

```bash
redis-server
```

---

## Docker Deployment

### Step 1: Build the Docker Images

Run the following command to build the Docker image:

```bash
docker-compose up --build
```

This will build the Docker containers for the application, Redis, and Celery.

### Step 2: Running the Docker Containers

After building the containers, you can start the services:

```bash
docker-compose up
```

This will start Redis, the Celery worker, and the Celery Beat scheduler in separate containers.

---

## Usage

After setting up the application, you can use the following example functions to test the metrics collection functionality:
In `main.py`
```python
@metrics_collector
def successful_function(x, y):
    time.sleep(0.1)  # Simulate some work
    return x + y


@metrics_collector
def error_function():
    time.sleep(0.1)  # Simulate some work
    raise ValueError("An error occurred")
```
To run test
```shell
docker-compose run celery_worker python main.py
```
These functions will simulate function calls and errors, allowing you to track the metrics (execution time, call count, and error count) asynchronously.

### Accessing the Metrics

To view metrics collected by the application, check the SQLite database (`metrics.db`). The metrics are stored in the `metrics` table.

---

## Troubleshooting

### Common Issues:

1. **Redis not connecting**:
   - Ensure Redis is running on `localhost:6379`. If you're using Docker, make sure the Redis container is running properly by checking with `docker ps`.

2. **Celery Worker/Beat not starting**:
   - Check for errors in the logs when running `celery worker` or `celery beat`. Often, the issue is with the broker URL or missing dependencies.
   - Ensure that your `.env` file is correctly configured with the Redis broker and backend URLs.

3. **SQLite file permissions issue**:
   - If you encounter file permission issues when writing to the SQLite database, ensure that the directory and file have appropriate write permissions.

4. **Docker: unable to start services**:
   - If Docker services don’t start, ensure you’ve built the images properly using `docker-compose up --build` and that no other containers are conflicting on the same ports.

---
