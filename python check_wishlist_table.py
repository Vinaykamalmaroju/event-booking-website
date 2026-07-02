import sqlite3

conn = sqlite3.connect("bookings.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(wishlist)")

print(cursor.fetchall())

conn.close()