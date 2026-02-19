import sqlite3
from datetime import datetime, timezone

conn = sqlite3.connect("user_data.db")
cursor = conn.cursor()

cursor.execute("""
DROP TABLE IF EXISTS users 
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    taskName TEXT,
    start_time INTEGER,
    end_time   INTEGER,
    difficulty TEXT,
    category TEXT,
    completed INTEGER,
    repeatable INTEGER,
    next_occurrence INTEGER,
    task_steps INTEGER
    task_steps TEXT
    
)
""")

cur_time_in = int(datetime.now(timezone.utc).timestamp())
print(cur_time_in)

cursor.execute(f"""
INSERT INTO users (user, taskName, start_time, end_time, difficulty, category, completed, repeatable,next_occurrence,task_steps) VALUES ('Yasinets','DoThis', {cur_time_in}, {cur_time_in + 3600}, 'Free', 'Sport', 1,0,0,'')""")
conn.commit()
conn.close()
