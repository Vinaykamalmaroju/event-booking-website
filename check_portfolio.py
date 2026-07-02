import sqlite3

conn = sqlite3.connect("bookings.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM provider_portfolio")

rows = cursor.fetchall()

print(rows)

conn.close()