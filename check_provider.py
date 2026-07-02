import sqlite3

conn = sqlite3.connect("bookings.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM providers")

rows = cursor.fetchall()

print("Number of providers:", len(rows))

for row in rows:
    print(row)

conn.close()