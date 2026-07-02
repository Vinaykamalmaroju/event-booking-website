import sqlite3

conn = sqlite3.connect("bookings.db")
cursor = conn.cursor()

# Delete old providers table
cursor.execute("DROP TABLE IF EXISTS providers")

# Create new providers table
cursor.execute("""
CREATE TABLE providers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    password TEXT,
    phone TEXT,
    service TEXT,
    experience TEXT,
    description TEXT,
    image TEXT,
    status TEXT DEFAULT 'Pending'
)
""")

conn.commit()
conn.close()

print("Provider table recreated successfully!")