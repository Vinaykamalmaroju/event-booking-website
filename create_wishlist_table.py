import sqlite3
import os

print("Database:", os.path.abspath("bookings.db"))

conn = sqlite3.connect("bookings.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS wishlist(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    provider_id INTEGER NOT NULL
)
""")

conn.commit()

cursor.execute("""
SELECT name
FROM sqlite_master
WHERE type='table'
""")

print(cursor.fetchall())

conn.close()