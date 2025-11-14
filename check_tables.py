import sqlite3

conn = sqlite3.connect('tekneat.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables:", tables)
cursor.execute("SELECT name FROM sqlite_master")
all_objects = cursor.fetchall()
print("All objects:", all_objects)
conn.close()
