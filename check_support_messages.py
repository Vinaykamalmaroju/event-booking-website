import sqlite3

conn = sqlite3.connect("bookings.db")

cursor = conn.cursor()

cursor.execute("SELECT * FROM support_messages")

rows = cursor.fetchall()

for row in rows:

    print(row)

conn.close()