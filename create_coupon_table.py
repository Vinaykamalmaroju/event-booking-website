import sqlite3

conn = sqlite3.connect("bookings.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS coupons(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    coupon_code TEXT UNIQUE,

    discount INTEGER,

    active INTEGER DEFAULT 1

)
""")

conn.commit()
conn.close()

print("Coupons table created successfully.")