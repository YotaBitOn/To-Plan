import sqlite3
from datetime import datetime, timezone

conn = sqlite3.connect("data/user_data.db")
cursor = conn.cursor()

cursor.execute("""
DROP TABLE IF EXISTS users 
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    taskName TEXT,
    date TEXT,
    at_time INTEGER,
    due_time   INTEGER,
    difficulty TEXT,
    category TEXT,
    completed INTEGER,
    repeatable INTEGER,
    rep_option TEXT,
    rep_vals TEXT,
    task_steps_ammo INTEGER,
    task_steps_infos TEXT, 
    
)
""")

conn.commit()
conn.close()
