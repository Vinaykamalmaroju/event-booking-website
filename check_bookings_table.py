import sqlite3

conn = sqlite3.connect("bookings.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(bookings)")

print("\nBookings Table Columns:\n")

for column in cursor.fetchall():
    print(column)

conn.close()