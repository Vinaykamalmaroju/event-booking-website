import sqlite3

conn = sqlite3.connect("bookings.db")
cursor = conn.cursor()

try:
    cursor.execute("""
    ALTER TABLE providers
    ADD COLUMN basic_package INTEGER DEFAULT 0
    """)
    print("basic_package added")
except:
    print("basic_package already exists")

try:
    cursor.execute("""
    ALTER TABLE providers
    ADD COLUMN premium_package INTEGER DEFAULT 0
    """)
    print("premium_package added")
except:
    print("premium_package already exists")

try:
    cursor.execute("""
    ALTER TABLE providers
    ADD COLUMN luxury_package INTEGER DEFAULT 0
    """)
    print("luxury_package added")
except:
    print("luxury_package already exists")

conn.commit()
conn.close()

print("Done")