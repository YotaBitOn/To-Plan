from datetime import datetime, timezone
import sqlite3
import os

from config.env_loader import drop_db_mode

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'user_data.db')

conn = sqlite3.connect(db_path)

cursor = conn.cursor()

#for test cases
if drop_db_mode:
    cursor.execute("""
    DROP TABLE IF EXISTS users
    """)

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    user TEXT,
    taskName TEXT,
    date TEXT,
    at_time INTEGER,
    due_time   INTEGER,
    difficulty TEXT,
    category TEXT,
    completed INTEGER,
    repeatable INTEGER,
    rep_option INTEGER,
    rep_vals TEXT,
    task_steps_infos TEXT, 
    description TEXT
)
""")

conn.commit()
#conn.close()
