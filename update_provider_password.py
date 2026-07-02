import sqlite3

conn = sqlite3.connect("bookings.db")
cursor = conn.cursor()

try:
    cursor.execute("""
        ALTER TABLE providers
        ADD COLUMN password TEXT
    """)
    print("Password column added successfully.")
except Exception as e:
    print("Error:", e)

conn.commit()
conn.close()