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
    """Insert multiple metrics into the database at once using bulk insert with error handling."""
    conn, cursor = connect_db()  # Ensure the connection and table are ready
    try:
        # Prepare data for bulk insert
        bulk_data = [
            (data['func_name'], data['execution_time'], data['error_occurred'], data['created_at'])
            for data in metrics
        ]
        # Bulk insert using executemany
        cursor.executemany('''INSERT INTO metrics (func_name, execution_time, error_occurred, created_at)
                              VALUES (?, ?, ?, ?)''', bulk_data)
        conn.commit()
    except sqlite3.Error as e:
        # Handle any SQLite-related errors
        print(f"An error occurred while inserting metrics: {e}")
        conn.rollback()  # Rollback if any error occurs during insert
    finally:
        # Ensure that the connection is closed
        if conn:
            conn.close()


def get_metrics_list():
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


def get_metrics(func_name):
    """Retrieve metrics from the database as a name function."""
    conn, cursor = connect_db()  # Ensure connection is established
    cursor.execute(f"""
    SELECT func_name, 
       COUNT(*) AS call_count, 
       SUM(execution_time) AS total_execution_time, 
       SUM(error_occurred) AS total_errors
    FROM metrics
    WHERE func_name = '{func_name}'
    GROUP BY func_name;
    """)

    # Fetch all rows from the metrics table
    row = cursor.fetchone()

    # Convert rows to a list of dictionaries
    metrics = {
        "Function": row[0],
        "Number of calls": row[1],
        "Average execution time": row[2] / row[1],
        "Number of errors": row[3],
    }

    conn.close()  # Always close the connection when done

    return metrics
