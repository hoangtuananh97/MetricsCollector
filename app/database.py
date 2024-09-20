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
                            call_count INTEGER, 
                            error_count INTEGER,
                            created_at TEXT
                      )''')
    conn.commit()
    return conn, cursor


def insert(metrics):
    """Insert metrics into the database."""
    conn, cursor = connect_db()  # Ensure the connection and table are ready
    # Insert each metric into the SQLite database
    for func_name, data in metrics.items():
        cursor.execute('''INSERT INTO metrics (func_name, execution_time, call_count, error_count, created_at)
                          VALUES (?, ?, ?, ?, ?)''',
                       (func_name, data['execution_time'], data['call_count'], data['error_count'], data['created_at']))
    conn.commit()
    conn.close()  # Always close the connection when done


def get_list():
    """Retrieve all metrics from the database as a list of dictionaries."""
    conn, cursor = connect_db()  # Ensure connection is established
    cursor.execute("SELECT * FROM metrics")

    # Fetch all rows from the metrics table
    rows = cursor.fetchall()

    # Convert rows to a list of dictionaries
    metrics = []
    for row in rows:
        metrics.append({
            "func_name": row[0],
            "execution_time": row[1],
            "call_count": row[2],
            "error_count": row[3],
        })

    conn.close()  # Always close the connection when done
    return metrics
