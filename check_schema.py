import sqlite3

conn = sqlite3.connect('tekneat.db')
cursor = conn.cursor()
cursor.execute('SELECT sql FROM sqlite_master WHERE type="table" AND name="menu"')
schema = cursor.fetchone()
print('Menu table schema:')
print(schema[0])
conn.close()
