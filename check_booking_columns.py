import sqlite3

conn = sqlite3.connect("bookings.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(bookings)")

columns = cursor.fetchall()

print("BOOKINGS TABLE COLUMNS:\n")

for column in columns:
    print(column)

conn.close()