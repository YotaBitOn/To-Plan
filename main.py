import sqlite3

print('Hello, World!')
conn = sqlite3.connect('users.db')
cursor = conn.cursor()