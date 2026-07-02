import sqlite3

conn = sqlite3.connect("bookings.db")
cursor = conn.cursor()

try:
    cursor.execute("""
        ALTER TABLE bookings
        ADD COLUMN amount INTEGER DEFAULT 0
    """)

    print("Amount column added successfully.")

except Exception as e:
    print(e)

conn.commit()
conn.close()