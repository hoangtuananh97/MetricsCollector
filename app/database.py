import os
import sqlite3

from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()
DATABASE_NAME = os.getenv('DATABASE_NAME')


# Establish connection and ensure the table exists
def connect_db():
    """Create a connection to the SQLite database and ensure the metrics table exists."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS metrics (
                            func_name TEXT, 
                            execution_time REAL, 
                            error_occurred INTEGER,
                            created_at INTEGER
                      )''')
    conn.commit()
    return conn, cursor


def insert(metrics):
    """Insert metrics into the database."""
    conn, cursor = connect_db()  # Ensure the connection and table are ready
    # Insert each metric into the SQLite database
    for data in metrics:
        cursor.execute('''INSERT INTO metrics (func_name, execution_time, error_occurred, created_at)
                          VALUES (?, ?, ?, ?)''',
                       (data['func_name'], data['execution_time'], data['error_occurred'], data['created_at']))
    conn.commit()
    conn.close()


def get_list():
    """Retrieve all metrics from the database as a list of dictionaries."""
    conn, cursor = connect_db()  # Ensure connection is established
    cursor.execute("""
    SELECT func_name, 
       COUNT(*) AS call_count, 
       SUM(execution_time) AS total_execution_time, 
       SUM(error_occurred) AS total_errors
    FROM metrics
    GROUP BY func_name;
    """)

    # Fetch all rows from the metrics table
    rows = cursor.fetchall()

    # Convert rows to a list of dictionaries
    metrics = []
    for row in rows:
        metrics.append({
            "Function": row[0],
            "Number of calls": row[1],
            "Average execution time": row[2] / row[1],
            "Number of errors": row[3],
        })

    conn.close()  # Always close the connection when done

    return {"count": len(metrics), "metrics": metrics}
