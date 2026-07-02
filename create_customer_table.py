import sqlite3

conn = sqlite3.connect("bookings.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS customers(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    email TEXT UNIQUE NOT NULL,

    password TEXT NOT NULL,

    phone TEXT
)
""")

conn.commit()
conn.close()

print("Customers table created successfully.")