import sqlite3

conn=sqlite3.connect("bookings.db")

cursor=conn.cursor()

cursor.execute("SELECT * FROM coupons")

for row in cursor.fetchall():

    print(row)

conn.close()