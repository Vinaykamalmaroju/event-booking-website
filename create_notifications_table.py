import sqlite3

conn = sqlite3.connect("bookings.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS notifications(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_email TEXT,

    message TEXT,

    notification_type TEXT,

    status TEXT,

    created_at TEXT

)
""")

conn.commit()
conn.close()

print("Notifications table created successfully.")