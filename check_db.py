import sqlite3

conn = sqlite3.connect("bookings.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(bookings)")

for row in cursor.fetchall():
    print(row)

conn.close()