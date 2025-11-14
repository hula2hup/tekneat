import sqlite3

conn = sqlite3.connect('tekneat.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(menu)")
columns = cursor.fetchall()
print('Menu columns:', [col[1] for col in columns])
conn.close()
