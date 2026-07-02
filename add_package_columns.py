import sqlite3

conn = sqlite3.connect("bookings.db")
cursor = conn.cursor()

try:
    cursor.execute("""
    ALTER TABLE providers
    ADD COLUMN basic_package INTEGER
    """)
except:
    print("basic_package Already Exists")

try:
    cursor.execute("""
    ALTER TABLE providers
    ADD COLUMN premium_package INTEGER
    """)
except:
    print("premium_package Already Exists")

try:
    cursor.execute("""
    ALTER TABLE providers
    ADD COLUMN luxury_package INTEGER
    """)
except:
    print("luxury_package Already Exists")

conn.commit()
conn.close()

print("Package columns added successfully.")