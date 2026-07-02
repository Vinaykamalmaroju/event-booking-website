import sqlite3

conn = sqlite3.connect("bookings.db")
cursor = conn.cursor()

# Add payment_id column
try:
    cursor.execute("""
        ALTER TABLE bookings
        ADD COLUMN payment_id TEXT
    """)
    print("payment_id column added.")
except Exception as e:
    print("payment_id:", e)

# Add payment_status column
try:
    cursor.execute("""
        ALTER TABLE bookings
        ADD COLUMN payment_status TEXT DEFAULT 'Paid'
    """)
    print("payment_status column added.")
except Exception as e:
    print("payment_status:", e)

conn.commit()
conn.close()

print("Database updated successfully.")