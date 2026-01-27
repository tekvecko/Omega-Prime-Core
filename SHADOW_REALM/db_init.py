import sqlite3
import datetime

DB_NAME = 'omega.db'

def init_db():
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Create logs table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                message TEXT NOT NULL
            )
        ''')

        # Insert a test record
        test_message = "Database initialized and first log entry added."
        timestamp = datetime.datetime.now().isoformat()
        cursor.execute("INSERT INTO logs (timestamp, message) VALUES (?, ?)", (timestamp, test_message))

        conn.commit()
        print(f"[{timestamp}] Database '{DB_NAME}' initialized and 'logs' table created with a test record.")

    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    init_db()
