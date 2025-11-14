import sqlite3

# Connect to the database
conn = sqlite3.connect('d:/Kuliah/Pengantar Desain Teknik/Prototype/tekneat.db')
cursor = conn.cursor()

# Add the qris_string column to the toko table
cursor.execute('ALTER TABLE toko ADD COLUMN qris_string TEXT')

# Commit the changes and close the connection
conn.commit()
conn.close()

print("qris_string column added to toko table")
