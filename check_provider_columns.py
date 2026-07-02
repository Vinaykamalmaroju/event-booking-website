import sqlite3

conn = sqlite3.connect("bookings.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(providers)")
columns = cursor.fetchall()

for column in columns:
    print(column)

conn.close()